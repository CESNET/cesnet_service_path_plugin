/**
 * segment_path_editor.js — Leaflet draw/edit engine for segment path drawing.
 *
 * Manages click-to-add, drag-to-move, right-click-to-delete vertices, undo
 * stack, and live polyline rendering.  Has no knowledge of the save mechanism,
 * toolbar buttons, or API — that belongs in segment_path_editor_ui.js.
 *
 * Depends on Leaflet (L) being present as a global.
 *
 * Usage:
 *   const editor = new SegmentPathEditor(map);
 *   editor.enter([[lat, lng], ...]);  // [] for new path, existing coords to edit
 *   editor.exit();
 *   editor.getCoordinates();          // → [[lat, lng], ...]  (Leaflet order)
 *   editor.clear();
 *   editor.undo();
 *   editor.on('change', () => { ... });
 */

(function (root, factory) {
    'use strict';
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = factory();
    } else {
        root.SegmentPathEditor = factory().SegmentPathEditor;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';

    // Visual style constants
    const POLYLINE_STYLE = {
        color: '#e65100',
        weight: 3,
        opacity: 0.9,
        dashArray: null,
    };

    const VERTEX_STYLE = {
        radius: 6,
        color: '#e65100',
        fillColor: '#fff',
        fillOpacity: 1,
        weight: 2,
    };

    const VERTEX_HOVER_COLOR = '#e65100';

    class SegmentPathEditor {
        constructor(map) {
            this._map      = map;
            this._coords   = [];   // [[lat, lng], ...]
            this._history  = [];   // snapshots for undo — each entry is a coords array copy
            this._active   = false;

            this._polyline = null;
            this._handles  = [];   // L.circleMarker per vertex
            this._listeners = { change: [] };

            // Bound so we can remove them later
            this._onMapClick = this._onMapClick.bind(this);
        }

        // ------------------------------------------------------------------
        // Public API
        // ------------------------------------------------------------------

        /** Enter edit mode, optionally pre-loading existing coordinates. */
        enter(initialCoords = []) {
            if (this._active) this.exit();
            this._active  = true;
            this._coords  = initialCoords.map(c => [c[0], c[1]]);
            this._history = [];

            this._map.on('click', this._onMapClick);
            this._map.getContainer().style.cursor = 'crosshair';

            this._render();
        }

        /** Exit edit mode and clean up all editor layers and event listeners. */
        exit() {
            this._active = false;
            this._map.off('click', this._onMapClick);
            this._map.getContainer().style.cursor = '';

            this._clearLayers();
            this._coords  = [];
            this._history = [];
        }

        /** Return a copy of the current coordinate array ([[lat, lng], ...]). */
        getCoordinates() {
            return this._coords.map(c => [c[0], c[1]]);
        }

        /** Remove all points but stay in edit mode. */
        clear() {
            if (!this._active) return;
            this._pushHistory();
            this._coords = [];
            this._render();
            this._emit('change');
        }

        /** Remove the last added point. */
        undo() {
            if (!this._active) return;
            if (this._history.length === 0) return;
            this._coords = this._history.pop();
            this._render();
            this._emit('change');
        }

        /** Register an event listener.  Currently only 'change' is supported. */
        on(event, cb) {
            if (this._listeners[event]) this._listeners[event].push(cb);
            return this;
        }

        /** Return true if the editor is currently active. */
        isActive() {
            return this._active;
        }

        // ------------------------------------------------------------------
        // Internal — event handlers
        // ------------------------------------------------------------------

        _onMapClick(e) {
            this._pushHistory();
            this._coords.push([e.latlng.lat, e.latlng.lng]);
            this._render();
            this._emit('change');
        }

        // ------------------------------------------------------------------
        // Internal — history
        // ------------------------------------------------------------------

        _pushHistory() {
            this._history.push(this._coords.map(c => [c[0], c[1]]));
        }

        // ------------------------------------------------------------------
        // Internal — rendering
        // ------------------------------------------------------------------

        _render() {
            this._clearLayers();

            if (this._coords.length === 0) return;

            // Draw polyline
            this._polyline = L.polyline(this._coords, POLYLINE_STYLE).addTo(this._map);

            // Draw vertex handles
            this._coords.forEach((coord, idx) => {
                this._addHandle(coord, idx);
            });
        }

        _addHandle(coord, idx) {
            const handle = L.circleMarker(coord, {
                ...VERTEX_STYLE,
                draggable: false,  // We implement drag manually via mousedown
            }).addTo(this._map);

            // Drag support via mousedown → mousemove → mouseup on the map
            handle.on('mousedown', (e) => {
                L.DomEvent.stop(e);
                this._startDrag(handle, idx);
            });

            // Right-click → delete vertex
            handle.on('contextmenu', (e) => {
                L.DomEvent.stop(e);
                this._deleteVertex(idx);
            });

            // Hover feedback
            handle.on('mouseover', () => {
                handle.setStyle({ fillColor: VERTEX_HOVER_COLOR });
                this._map.getContainer().style.cursor = 'grab';
            });
            handle.on('mouseout', () => {
                handle.setStyle({ fillColor: '#fff' });
                this._map.getContainer().style.cursor = 'crosshair';
            });

            this._handles.push(handle);
        }

        _startDrag(handle, idx) {
            // Temporarily disable map click so the drag end doesn't add a point
            this._map.off('click', this._onMapClick);
            this._map.dragging.disable();
            this._map.getContainer().style.cursor = 'grabbing';

            this._pushHistory();

            const onMove = (e) => {
                const latlng = e.latlng;
                handle.setLatLng(latlng);
                this._coords[idx] = [latlng.lat, latlng.lng];
                if (this._polyline) this._polyline.setLatLngs(this._coords);
            };

            const onUp = () => {
                this._map.off('mousemove', onMove);
                this._map.off('mouseup',   onUp);
                this._map.dragging.enable();
                this._map.getContainer().style.cursor = 'crosshair';

                // Re-enable click after a short delay so the mouseup doesn't
                // immediately trigger a click event on some browsers.
                setTimeout(() => {
                    this._map.on('click', this._onMapClick);
                }, 10);

                this._emit('change');
            };

            this._map.on('mousemove', onMove);
            this._map.on('mouseup',   onUp);
        }

        _deleteVertex(idx) {
            this._pushHistory();
            this._coords.splice(idx, 1);
            this._render();
            this._emit('change');
        }

        // ------------------------------------------------------------------
        // Internal — cleanup
        // ------------------------------------------------------------------

        _clearLayers() {
            if (this._polyline) {
                this._polyline.remove();
                this._polyline = null;
            }
            this._handles.forEach(h => h.remove());
            this._handles = [];
        }

        // ------------------------------------------------------------------
        // Internal — events
        // ------------------------------------------------------------------

        _emit(event) {
            (this._listeners[event] || []).forEach(cb => cb());
        }
    }

    return { SegmentPathEditor };
}));
