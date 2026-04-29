/**
 * edit_mode_state_machine.js — Edit mode state machine for the Network Map.
 *
 * Pure logic: no DOM, no Leaflet, no fetch.  All side-effects are communicated
 * outward via an EventEmitter passed at construction time.
 *
 * Usage in the browser (object_map.js):
 *   const sm = new EditModeStateMachine(eventBus);
 *
 * Usage in Node tests:
 *   const { EditModeStateMachine } = require('./edit_mode_state_machine');
 */

(function (root, factory) {
    'use strict';
    if (typeof module !== 'undefined' && module.exports) {
        // Node / CommonJS — for Jest tests
        module.exports = factory();
    } else {
        // Browser global
        root.EditModeStateMachine = factory().EditModeStateMachine;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';

    // -------------------------------------------------------------------------
    // Valid states
    // -------------------------------------------------------------------------
    const STATES = Object.freeze({
        VIEW:                     'view',
        EDIT_IDLE:                'edit_idle',
        SITE_SELECTED:            'site_selected',
        PLACING_UNPOSITIONED:     'placing_unpositioned',
        PLACING_NEW_SITE:         'placing_new_site',
        NEW_SITE_FORM:            'new_site_form',
        PICKING_SEGMENT_START:    'picking_segment_start',
        PICKING_SEGMENT_END:      'picking_segment_end',
        NEW_SEGMENT_FORM:         'new_segment_form',
        PICKING_CIRCUIT_START:    'picking_circuit_start',
        PICKING_CIRCUIT_END:      'picking_circuit_end',
        NEW_CIRCUIT_FORM:         'new_circuit_form',
        EDITING_CONNECTION:       'editing_connection',
        PICKING_REPLACEMENT_SITE: 'picking_replacement_site',
    });

    // States from which Escape returns to edit_idle
    const ESCAPABLE = new Set([
        STATES.SITE_SELECTED,
        STATES.PLACING_UNPOSITIONED,
        STATES.PLACING_NEW_SITE,
        STATES.NEW_SITE_FORM,
        STATES.PICKING_SEGMENT_START,
        STATES.PICKING_SEGMENT_END,
        STATES.NEW_SEGMENT_FORM,
        STATES.PICKING_CIRCUIT_START,
        STATES.PICKING_CIRCUIT_END,
        STATES.NEW_CIRCUIT_FORM,
        STATES.EDITING_CONNECTION,
        STATES.PICKING_REPLACEMENT_SITE,
    ]);

    // -------------------------------------------------------------------------
    // Valid transitions: { fromState: Set<toState> }
    // -------------------------------------------------------------------------
    const VALID_TRANSITIONS = {
        [STATES.VIEW]: new Set([
            STATES.EDIT_IDLE,
        ]),
        [STATES.EDIT_IDLE]: new Set([
            STATES.VIEW,
            STATES.SITE_SELECTED,
            STATES.PLACING_UNPOSITIONED,
            STATES.PLACING_NEW_SITE,
            STATES.PICKING_SEGMENT_START,
            STATES.PICKING_CIRCUIT_START,
            STATES.EDITING_CONNECTION,
        ]),
        [STATES.SITE_SELECTED]: new Set([
            STATES.EDIT_IDLE,
        ]),
        [STATES.PLACING_UNPOSITIONED]: new Set([
            STATES.SITE_SELECTED,
            STATES.EDIT_IDLE,
        ]),
        [STATES.PLACING_NEW_SITE]: new Set([
            STATES.NEW_SITE_FORM,
            STATES.EDIT_IDLE,
        ]),
        [STATES.NEW_SITE_FORM]: new Set([
            STATES.EDIT_IDLE,
        ]),
        [STATES.PICKING_SEGMENT_START]: new Set([
            STATES.PICKING_SEGMENT_END,
            STATES.EDIT_IDLE,
        ]),
        [STATES.PICKING_SEGMENT_END]: new Set([
            STATES.NEW_SEGMENT_FORM,
            STATES.EDIT_IDLE,
        ]),
        [STATES.NEW_SEGMENT_FORM]: new Set([
            STATES.EDIT_IDLE,
        ]),
        [STATES.PICKING_CIRCUIT_START]: new Set([
            STATES.PICKING_CIRCUIT_END,
            STATES.EDIT_IDLE,
        ]),
        [STATES.PICKING_CIRCUIT_END]: new Set([
            STATES.NEW_CIRCUIT_FORM,
            STATES.EDIT_IDLE,
        ]),
        [STATES.NEW_CIRCUIT_FORM]: new Set([
            STATES.EDIT_IDLE,
        ]),
        [STATES.EDITING_CONNECTION]: new Set([
            STATES.PICKING_REPLACEMENT_SITE,
            STATES.EDIT_IDLE,
        ]),
        [STATES.PICKING_REPLACEMENT_SITE]: new Set([
            STATES.EDITING_CONNECTION,
            STATES.EDIT_IDLE,
        ]),
    };

    // -------------------------------------------------------------------------
    // Class definition
    // -------------------------------------------------------------------------

    /**
     * @param {object} events  EventEmitter with .emit(name, data) method.
     *                         May be null for tests that don't care about events.
     */
    class EditModeStateMachine {
        constructor(events) {
            this._events = events || { emit() {} };
            this.state = STATES.VIEW;

            // Payload: site being moved / placed / created
            this.pendingSite = null;
            // {
            //   id: number | null,          null when creating a new site
            //   name: string,
            //   isNew: boolean,
            //   isUnpositioned: boolean,
            //   originalLat: number | null,
            //   originalLng: number | null,
            //   currentLat: number,
            //   currentLng: number,
            // }

            // Payload: connection (segment or circuit) being created or edited
            this.pendingConnection = null;
            // {
            //   objectType: 'segment' | 'circuit',
            //   mode: 'create' | 'edit',
            //   existingId: number | null,
            //   siteA: { id, name, lat, lng } | null,
            //   siteB: { id, name, lat, lng } | null,
            //   endToChange: 'a' | 'b' | null,
            // }

            // Reference data loaded when edit mode is first entered
            this.unpositionedSites = [];
            this.providers         = [];
            this.circuitTypes      = [];

            // API/save state
            this.isSaving  = false;
            this.saveError = null;
        }

        // -------------------------------------------------------------------------
        // Core transition
        // -------------------------------------------------------------------------

        /**
         * Attempt a transition to `toState`, optionally merging `payload` into
         * the matching pending* slot.  Throws if the transition is not valid.
         *
         * @param {string} toState
         * @param {object} [payload]
         */
        transitionTo(toState, payload) {
            const allowed = VALID_TRANSITIONS[this.state];
            if (!allowed || !allowed.has(toState)) {
                throw new Error(
                    `EditModeStateMachine: invalid transition ${this.state} → ${toState}`
                );
            }

            const prevState = this.state;
            this.state = toState;
            this.saveError = null;

            // Apply payload and clear stale payload when leaving a context
            this._applyPayload(toState, payload || {});

            this._events.emit('editModeStateChanged', {
                prev:    prevState,
                state:   toState,
                machine: this,
            });
        }

        // -------------------------------------------------------------------------
        // Named actions — thin wrappers over transitionTo that validate payload
        // -------------------------------------------------------------------------

        /** Toggle edit mode ON — fetched reference data supplied by caller. */
        enterEditMode(refData) {
            refData = refData || {};
            if (refData.unpositionedSites) this.unpositionedSites = refData.unpositionedSites;
            if (refData.providers)         this.providers         = refData.providers;
            if (refData.circuitTypes)      this.circuitTypes      = refData.circuitTypes;
            this.transitionTo(STATES.EDIT_IDLE);
        }

        /** Toggle edit mode OFF from any state. */
        exitEditMode() {
            // Allow exit from any state by forcing a direct reset
            const prevState = this.state;
            this.state             = STATES.VIEW;
            this.pendingSite       = null;
            this.pendingConnection = null;
            this.isSaving          = false;
            this.saveError         = null;
            this._events.emit('editModeStateChanged', {
                prev:    prevState,
                state:   STATES.VIEW,
                machine: this,
            });
        }

        /** Cancel current in-progress operation via Escape (or Cancel button). */
        escape() {
            if (this.state === STATES.VIEW)      return;   // nothing to do
            if (this.state === STATES.EDIT_IDLE) return;   // nothing to do
            if (!ESCAPABLE.has(this.state))      return;
            this.transitionTo(STATES.EDIT_IDLE);
        }

        /** User clicked an existing positioned site marker. */
        selectSite(site) {
            this.transitionTo(STATES.SITE_SELECTED, { site });
        }

        /** Dragging a site marker updated the live position. */
        updateSitePosition(lat, lng) {
            if (this.state !== STATES.SITE_SELECTED && this.state !== STATES.NEW_SITE_FORM) return;
            if (!this.pendingSite) return;
            this.pendingSite.currentLat = lat;
            this.pendingSite.currentLng = lng;
            this._events.emit('editModeSitePositionUpdated', { lat, lng, machine: this });
        }

        /** User picked a site from the unpositioned list. */
        beginPlacingUnpositioned(site) {
            this.transitionTo(STATES.PLACING_UNPOSITIONED, { site });
        }

        /** User clicked the map while in placing_unpositioned — drop a marker. */
        placeUnpositionedSite(lat, lng) {
            if (!this.pendingSite) return;
            this.pendingSite.currentLat = lat;
            this.pendingSite.currentLng = lng;
            this.transitionTo(STATES.SITE_SELECTED);
        }

        /** User clicked "Add new site" action button. */
        beginPlacingNewSite() {
            this.transitionTo(STATES.PLACING_NEW_SITE);
        }

        /** User clicked the map while in placing_new_site — open form. */
        placeNewSite(lat, lng) {
            this.transitionTo(STATES.NEW_SITE_FORM, { lat, lng });
        }

        /** User clicked "New segment" button. */
        beginNewSegment() {
            this.transitionTo(STATES.PICKING_SEGMENT_START, {
                connection: { objectType: 'segment', mode: 'create', existingId: null,
                              siteA: null, siteB: null, endToChange: null },
            });
        }

        /** User clicked site A while picking segment endpoints. */
        pickSegmentSiteA(site) {
            this.transitionTo(STATES.PICKING_SEGMENT_END, { siteA: site });
        }

        /** User clicked site B while picking segment endpoints — open form. */
        pickSegmentSiteB(site) {
            this.transitionTo(STATES.NEW_SEGMENT_FORM, { siteB: site });
        }

        /** User clicked "New circuit" button. */
        beginNewCircuit() {
            this.transitionTo(STATES.PICKING_CIRCUIT_START, {
                connection: { objectType: 'circuit', mode: 'create', existingId: null,
                              siteA: null, siteB: null, endToChange: null },
            });
        }

        /** User clicked site A while picking circuit endpoints. */
        pickCircuitSiteA(site) {
            this.transitionTo(STATES.PICKING_CIRCUIT_END, { siteA: site });
        }

        /** User clicked site B while picking circuit endpoints — open form. */
        pickCircuitSiteB(site) {
            this.transitionTo(STATES.NEW_CIRCUIT_FORM, { siteB: site });
        }

        /** User clicked an existing editable segment or circuit line. */
        selectConnection(objectType, id, siteA, siteB, termA, termZ) {
            this.transitionTo(STATES.EDITING_CONNECTION, {
                connection: { objectType, mode: 'edit', existingId: id,
                              siteA, siteB, endToChange: null,
                              termA: termA || null, termZ: termZ || null },
            });
        }

        /** User clicked "Change site A" or "Change site B". */
        beginChangingEnd(end) {
            if (end !== 'a' && end !== 'b') {
                throw new Error('EditModeStateMachine: end must be "a" or "b"');
            }
            this.transitionTo(STATES.PICKING_REPLACEMENT_SITE, { endToChange: end });
        }

        /** User clicked a site marker as the replacement — save happens externally. */
        pickReplacementSite(site) {
            if (!this.pendingConnection) return;
            if (this.pendingConnection.endToChange === 'a') {
                this.pendingConnection.siteA = site;
            } else {
                this.pendingConnection.siteB = site;
            }
            // Return to editing_connection so the UI can show updated endpoints
            // and the caller can trigger the API save.
            this.transitionTo(STATES.EDITING_CONNECTION);
        }

        /** Mark a save as in-progress (called by editModeApi before the fetch). */
        beginSave() {
            this.isSaving  = true;
            this.saveError = null;
            this._events.emit('editModeSaveStarted', { machine: this });
        }

        /** Called by editModeApi on success. Transitions back to edit_idle. */
        completeSave() {
            this.isSaving          = false;
            this.saveError         = null;
            this.pendingSite       = null;
            this.pendingConnection = null;
            this.transitionTo(STATES.EDIT_IDLE);
        }

        /** Called by editModeApi on failure. Stays in current state, sets error. */
        failSave(message) {
            this.isSaving  = false;
            this.saveError = message || 'Save failed.';
            this._events.emit('editModeSaveFailed', { message: this.saveError, machine: this });
        }

        /** Called after a new object is added to the dataset post-save. */
        setReferenceData(refData) {
            if (refData.unpositionedSites !== undefined) this.unpositionedSites = refData.unpositionedSites;
            if (refData.providers !== undefined)         this.providers         = refData.providers;
            if (refData.circuitTypes !== undefined)      this.circuitTypes      = refData.circuitTypes;
        }

        // -------------------------------------------------------------------------
        // Internal helpers
        // -------------------------------------------------------------------------

        _applyPayload(toState, payload) {
            // Site payload
            if (payload.site) {
                const s = payload.site;
                this.pendingSite = {
                    id:             s.id   !== undefined ? s.id   : null,
                    name:           s.name || '',
                    isNew:          !!s.isNew,
                    isUnpositioned: !!s.isUnpositioned,
                    originalLat:    s.lat  !== undefined ? s.lat  : null,
                    originalLng:    s.lng  !== undefined ? s.lng  : null,
                    currentLat:     s.lat  !== undefined ? s.lat  : null,
                    currentLng:     s.lng  !== undefined ? s.lng  : null,
                };
            }

            // Coordinate update for placing states
            if (payload.lat !== undefined && payload.lng !== undefined) {
                if (toState === STATES.NEW_SITE_FORM) {
                    this.pendingSite = {
                        id: null, name: '', isNew: true, isUnpositioned: false,
                        originalLat: null, originalLng: null,
                        currentLat: payload.lat, currentLng: payload.lng,
                    };
                }
            }

            // Carry forward currentLat/Lng when transitioning from placing_unpositioned
            // to site_selected (the click position is already on pendingSite)
            // Nothing to do — pendingSite was set in beginPlacingUnpositioned and
            // currentLat/Lng updated in placeUnpositionedSite before this runs.

            // Connection payload
            if (payload.connection) {
                this.pendingConnection = { ...payload.connection };
            }

            if (payload.siteA !== undefined && this.pendingConnection) {
                this.pendingConnection.siteA = payload.siteA;
            }
            if (payload.siteB !== undefined && this.pendingConnection) {
                this.pendingConnection.siteB = payload.siteB;
            }
            if (payload.endToChange !== undefined && this.pendingConnection) {
                this.pendingConnection.endToChange = payload.endToChange;
            }

            // Clear stale payload when returning to idle
            if (toState === STATES.EDIT_IDLE) {
                this.pendingSite       = null;
                this.pendingConnection = null;
                this.isSaving          = false;
            }
        }
    }

    // -------------------------------------------------------------------------
    // Expose STATES so callers can reference state names without magic strings
    // -------------------------------------------------------------------------
    EditModeStateMachine.STATES = STATES;

    return { EditModeStateMachine };
}));
