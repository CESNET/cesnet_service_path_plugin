/**
 * edit_mode_marker.js — Draggable Leaflet marker used during edit mode.
 *
 * Thin wrapper: creates one marker at a time, notifies on drag, removes on demand.
 * Depends on Leaflet (L) being present as a global.
 *
 * Usage:
 *   const em = new EditModeMarker(map);
 *   em.place(lat, lng, onDrag);   // onDrag(lat, lng) called on every dragend
 *   em.moveTo(lat, lng);          // snap marker without firing onDrag
 *   em.remove();                  // remove from map
 */

(function (root, factory) {
    'use strict';
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = factory();
    } else {
        root.EditModeMarker = factory().EditModeMarker;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';

    class EditModeMarker {
        constructor(map) {
            this._map    = map;
            this._marker = null;
        }

        /**
         * Place a draggable marker.  Calls onDrag(lat, lng) after every dragend.
         * If a marker already exists it is removed first.
         */
        place(lat, lng, onDrag) {
            this.remove();
            this._marker = L.marker([lat, lng], {
                draggable: true,
                autoPan:   true,
                icon: L.divIcon({
                    className: 'edit-mode-marker',
                    html: '<i class="mdi mdi-map-marker" style="font-size:28px;color:#e65100;text-shadow:0 1px 3px rgba(0,0,0,.5);"></i>',
                    iconSize:   [28, 28],
                    iconAnchor: [14, 28],
                }),
            });
            this._marker.addTo(this._map);
            this._marker.on('dragend', () => {
                const pos = this._marker.getLatLng();
                if (onDrag) onDrag(pos.lat, pos.lng);
            });
        }

        /** Move the marker to new coordinates without triggering onDrag. */
        moveTo(lat, lng) {
            if (this._marker) this._marker.setLatLng([lat, lng]);
        }

        /** Remove the marker from the map. */
        remove() {
            if (this._marker) {
                this._marker.remove();
                this._marker = null;
            }
        }

        /** Return true if the marker is currently on the map. */
        isActive() {
            return this._marker !== null;
        }
    }

    return { EditModeMarker };
}));
