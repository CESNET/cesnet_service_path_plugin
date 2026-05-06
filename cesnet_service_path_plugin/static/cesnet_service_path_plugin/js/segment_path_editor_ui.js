/**
 * segment_path_editor_ui.js — Toolbar orchestration for the segment path editor.
 *
 * Wires DOM toolbar buttons to SegmentPathEditor and SegmentPathGeometry,
 * handles the blocking proximity confirmation dialog, the beforeunload guard,
 * and the PATCH API call on save.
 *
 * Depends on:
 *   - SegmentPathEditor  (segment_path_editor.js)
 *   - SegmentPathGeometry (segment_path_geometry.js)
 *   - Leaflet (L) global
 *
 * Usage — called from segment_map.html after map initialisation:
 *
 *   const ui = new SegmentPathEditorUI(map, {
 *     segmentId:      42,
 *     apiUrl:         '/api/plugins/cesnet-service-path-plugin/segments/42/',
 *     clearPathUrl:   '/plugins/cesnet-service-path-plugin/segments/42/clear-path/',
 *     siteA:          { lat: 50.0, lng: 14.0, name: 'Site A' },  // null if unpositioned
 *     siteB:          { lat: 49.0, lng: 16.0, name: 'Site B' },  // null if unpositioned
 *     existingCoords: [[50.0, 14.0], [49.5, 15.0], [49.0, 16.0]],  // Leaflet [lat,lng], [] if none
 *     isTooComplex:   false,
 *   });
 */

(function (root, factory) {
    'use strict';
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = factory();
    } else {
        root.SegmentPathEditorUI = factory().SegmentPathEditorUI;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';

    // -------------------------------------------------------------------------
    // CSRF helper — mirrors edit_mode_api.js pattern
    // -------------------------------------------------------------------------

    function getCsrfToken() {
        if (typeof window !== 'undefined' && window.CSRF_TOKEN) return window.CSRF_TOKEN;
        const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    // -------------------------------------------------------------------------
    // Main class
    // -------------------------------------------------------------------------

    class SegmentPathEditorUI {

        constructor(map, config) {
            this._map    = map;
            this._cfg    = config;
            this._editor = new SegmentPathEditor(map);
            this._geo    = SegmentPathGeometry;
            this._dirty  = false;

            this._beforeUnloadHandler = (e) => {
                e.preventDefault();
                e.returnValue = '';
            };

            this._bindToolbar();

            if (config.isTooComplex) {
                this._showComplexWarning();
            }
        }

        // ------------------------------------------------------------------
        // Toolbar wiring
        // ------------------------------------------------------------------

        _bindToolbar() {
            this._btn('path-edit-btn',   () => this._enterEditMode());
            this._btn('path-save-btn',   () => this._save());
            this._btn('path-cancel-btn', () => this._cancel());
            this._btn('path-undo-btn',   () => { this._editor.undo(); });
            this._btn('path-clear-btn',  () => { this._editor.clear(); });
            this._btn('path-delete-btn', () => this._deletePath());
        }

        _btn(id, handler) {
            const el = document.getElementById(id);
            if (el) el.addEventListener('click', handler);
        }

        // ------------------------------------------------------------------
        // Edit mode enter / exit
        // ------------------------------------------------------------------

        _enterEditMode() {
            this._editor.enter(this._cfg.existingCoords || []);
            this._editor.on('change', () => { this._dirty = true; });
            this._dirty = false;

            this._swapToolbar(true);
            window.addEventListener('beforeunload', this._beforeUnloadHandler);
        }

        _cancel() {
            this._editor.exit();
            this._dirty = false;
            this._swapToolbar(false);
            window.removeEventListener('beforeunload', this._beforeUnloadHandler);
        }

        // ------------------------------------------------------------------
        // Save
        // ------------------------------------------------------------------

        async _save() {
            const coords = this._editor.getCoordinates();

            if (coords.length < 2) {
                alert('Please place at least 2 points before saving.');
                return;
            }

            // Proximity check — only if both sites are positioned
            if (this._cfg.siteA && this._cfg.siteB) {
                // Convert Leaflet [lat, lng] to GeoJSON [lng, lat] for geometry module
                const geoCoords = coords.map(c => [c[1], c[0]]);
                const prox = this._geo.checkSiteProximity(
                    geoCoords,
                    this._cfg.siteA,
                    this._cfg.siteB,
                );

                if (prox.warnA || prox.warnB) {
                    const lines = [];
                    if (prox.warnA) {
                        lines.push(
                            `Path start is ${prox.distA} m from "${this._cfg.siteA.name}" (threshold: 100 m).`
                        );
                    }
                    if (prox.warnB) {
                        lines.push(
                            `Path end is ${prox.distB} m from "${this._cfg.siteB.name}" (threshold: 100 m).`
                        );
                    }
                    lines.push('\nSave anyway?');
                    if (!window.confirm(lines.join('\n'))) return;
                }
            }

            // Convert Leaflet [lat, lng] → GeoJSON [lng, lat]
            const geoJsonCoords = coords.map(c => [c[1], c[0]]);

            const saveBtn = document.getElementById('path-save-btn');
            if (saveBtn) { saveBtn.disabled = true; saveBtn.textContent = 'Saving…'; }

            try {
                const resp = await fetch(this._cfg.apiUrl, {
                    method:      'PATCH',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type':     'application/json',
                        'Accept':           'application/json',
                        'X-CSRFToken':      getCsrfToken(),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify({
                        path_geometry: {
                            type:        'LineString',
                            coordinates: geoJsonCoords,
                        },
                    }),
                });

                if (!resp.ok) {
                    const data = await resp.json().catch(() => ({}));
                    const msg  = this._extractError(data) || `HTTP ${resp.status}`;
                    throw new Error(msg);
                }

                // Success — remove guard and reload to show new path
                this._dirty = false;
                window.removeEventListener('beforeunload', this._beforeUnloadHandler);
                window.location.reload();

            } catch (err) {
                alert(`Save failed: ${err.message}`);
                if (saveBtn) { saveBtn.disabled = false; saveBtn.textContent = 'Save'; }
            }
        }

        // ------------------------------------------------------------------
        // Delete entire path
        // ------------------------------------------------------------------

        async _deletePath() {
            if (!window.confirm('Delete the stored path geometry for this segment?')) return;

            const deleteBtn = document.getElementById('path-delete-btn');
            if (deleteBtn) { deleteBtn.disabled = true; deleteBtn.textContent = 'Deleting…'; }

            try {
                const resp = await fetch(this._cfg.clearPathUrl, {
                    method:      'POST',
                    credentials: 'same-origin',
                    headers: {
                        'X-CSRFToken':      getCsrfToken(),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });

                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

                this._dirty = false;
                window.removeEventListener('beforeunload', this._beforeUnloadHandler);
                window.location.reload();

            } catch (err) {
                alert(`Delete failed: ${err.message}`);
                if (deleteBtn) { deleteBtn.disabled = false; deleteBtn.textContent = 'Delete Path'; }
            }
        }

        // ------------------------------------------------------------------
        // Toolbar visibility swap
        // ------------------------------------------------------------------

        _swapToolbar(editMode) {
            const viewEls = document.querySelectorAll('.path-view-toolbar');
            const editEls = document.querySelectorAll('.path-edit-toolbar');

            viewEls.forEach(el => el.classList.toggle('d-none', editMode));
            editEls.forEach(el => el.classList.toggle('d-none', !editMode));
        }

        // ------------------------------------------------------------------
        // "Too complex" banner
        // ------------------------------------------------------------------

        _showComplexWarning() {
            const banner = document.getElementById('path-complex-warning');
            if (banner) banner.classList.remove('d-none');

            const editBtn = document.getElementById('path-edit-btn');
            if (editBtn) {
                editBtn.disabled = true;
                editBtn.title = 'Path geometry is too complex to edit here (disconnected segments).';
            }
        }

        // ------------------------------------------------------------------
        // Helpers
        // ------------------------------------------------------------------

        _extractError(data) {
            if (typeof data === 'string') return data;
            if (data && data.detail) return data.detail;
            if (data && data.path_geometry) return data.path_geometry.join(' ');
            // Collect first error message from any field
            for (const key of Object.keys(data || {})) {
                const val = data[key];
                if (Array.isArray(val) && val.length) return `${key}: ${val[0]}`;
            }
            return null;
        }
    }

    return { SegmentPathEditorUI };
}));
