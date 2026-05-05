'use strict';

const { EditModeStateMachine } = require(
    '../cesnet_service_path_plugin/static/cesnet_service_path_plugin/js/edit_mode_state_machine'
);

const S = EditModeStateMachine.STATES;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeSM() {
    const events = [];
    const emitter = { emit: (name, data) => events.push({ name, data }) };
    const sm = new EditModeStateMachine(emitter);
    return { sm, events };
}

function lastEvent(events) {
    return events[events.length - 1];
}

const SITE_A = { id: 1, name: 'Site A', lat: 50.0, lng: 14.0 };
const SITE_B = { id: 2, name: 'Site B', lat: 51.0, lng: 15.0 };
const SITE_UNPOS = { id: 3, name: 'Unpositioned', isUnpositioned: true };

// ---------------------------------------------------------------------------
// Initial state
// ---------------------------------------------------------------------------

describe('initial state', () => {
    test('starts in view', () => {
        const { sm } = makeSM();
        expect(sm.state).toBe(S.VIEW);
    });

    test('all payload slots are null', () => {
        const { sm } = makeSM();
        expect(sm.pendingSite).toBeNull();
        expect(sm.pendingConnection).toBeNull();
    });

    test('reference data arrays are empty', () => {
        const { sm } = makeSM();
        expect(sm.unpositionedSites).toEqual([]);
        expect(sm.providers).toEqual([]);
        expect(sm.circuitTypes).toEqual([]);
    });

    test('isSaving is false, saveError is null', () => {
        const { sm } = makeSM();
        expect(sm.isSaving).toBe(false);
        expect(sm.saveError).toBeNull();
    });
});

// ---------------------------------------------------------------------------
// Edit mode on / off
// ---------------------------------------------------------------------------

describe('entering and exiting edit mode', () => {
    test('enterEditMode transitions view → edit_idle', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        expect(sm.state).toBe(S.EDIT_IDLE);
    });

    test('enterEditMode stores reference data', () => {
        const { sm } = makeSM();
        const providers = [{ id: 1, name: 'Provider X' }];
        sm.enterEditMode({ providers });
        expect(sm.providers).toEqual(providers);
    });

    test('enterEditMode emits editModeStateChanged', () => {
        const { sm, events } = makeSM();
        sm.enterEditMode();
        const ev = lastEvent(events);
        expect(ev.name).toBe('editModeStateChanged');
        expect(ev.data.prev).toBe(S.VIEW);
        expect(ev.data.state).toBe(S.EDIT_IDLE);
    });

    test('exitEditMode from edit_idle returns to view', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.exitEditMode();
        expect(sm.state).toBe(S.VIEW);
    });

    test('exitEditMode from any in-progress state returns to view', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginNewSegment();
        sm.exitEditMode();
        expect(sm.state).toBe(S.VIEW);
    });

    test('exitEditMode clears pending payload', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        sm.exitEditMode();
        expect(sm.pendingSite).toBeNull();
        expect(sm.pendingConnection).toBeNull();
    });
});

// ---------------------------------------------------------------------------
// Escape key
// ---------------------------------------------------------------------------

describe('escape', () => {
    test('escape from view is a no-op', () => {
        const { sm } = makeSM();
        sm.escape();
        expect(sm.state).toBe(S.VIEW);
    });

    test('escape from edit_idle is a no-op', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.escape();
        expect(sm.state).toBe(S.EDIT_IDLE);
    });

    test.each([
        ['site_selected',            sm => sm.selectSite(SITE_A)],
        ['placing_unpositioned',     sm => sm.beginPlacingUnpositioned(SITE_UNPOS)],
        ['placing_new_site',         sm => sm.beginPlacingNewSite()],
        ['new_site_form',            sm => { sm.beginPlacingNewSite(); sm.placeNewSite(50, 14); }],
        ['picking_segment_start',    sm => sm.beginNewSegment()],
        ['picking_segment_end',      sm => { sm.beginNewSegment(); sm.pickSegmentSiteA(SITE_A); }],
        ['new_segment_form',         sm => { sm.beginNewSegment(); sm.pickSegmentSiteA(SITE_A); sm.pickSegmentSiteB(SITE_B); }],
        ['picking_circuit_start',    sm => sm.beginNewCircuit()],
        ['picking_circuit_end',      sm => { sm.beginNewCircuit(); sm.pickCircuitSiteA(SITE_A); }],
        ['new_circuit_form',         sm => { sm.beginNewCircuit(); sm.pickCircuitSiteA(SITE_A); sm.pickCircuitSiteB(SITE_B); }],
        ['editing_connection',       sm => sm.selectConnection('segment', 99, SITE_A, SITE_B)],
        ['picking_replacement_site', sm => { sm.selectConnection('segment', 99, SITE_A, SITE_B); sm.beginChangingEnd('a'); }],
    ])('escape from %s returns to edit_idle', (label, setup) => {
        const { sm } = makeSM();
        sm.enterEditMode();
        setup(sm);
        sm.escape();
        expect(sm.state).toBe(S.EDIT_IDLE);
    });

    test('escape clears pending payload', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        sm.escape();
        expect(sm.pendingSite).toBeNull();
    });
});

// ---------------------------------------------------------------------------
// Invalid transitions
// ---------------------------------------------------------------------------

describe('invalid transitions throw', () => {
    test('cannot transition from view directly to site_selected', () => {
        const { sm } = makeSM();
        expect(() => sm.transitionTo(S.SITE_SELECTED)).toThrow();
    });

    test('cannot transition from view to picking_segment_start', () => {
        const { sm } = makeSM();
        expect(() => sm.transitionTo(S.PICKING_SEGMENT_START)).toThrow();
    });

    test('cannot transition from edit_idle to new_site_form (must go via placing)', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        expect(() => sm.transitionTo(S.NEW_SITE_FORM)).toThrow();
    });

    test('cannot transition from site_selected to picking_segment_start', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        expect(() => sm.transitionTo(S.PICKING_SEGMENT_START)).toThrow();
    });

    test('cannot transition from picking_segment_end to new_circuit_form', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginNewSegment();
        sm.pickSegmentSiteA(SITE_A);
        expect(() => sm.transitionTo(S.NEW_CIRCUIT_FORM)).toThrow();
    });
});

// ---------------------------------------------------------------------------
// Site drag flow
// ---------------------------------------------------------------------------

describe('site drag flow', () => {
    test('selectSite sets pendingSite from site data', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        expect(sm.pendingSite.id).toBe(1);
        expect(sm.pendingSite.name).toBe('Site A');
        expect(sm.pendingSite.originalLat).toBe(50.0);
        expect(sm.pendingSite.currentLat).toBe(50.0);
    });

    test('updateSitePosition updates currentLat/Lng', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        sm.updateSitePosition(52.0, 16.0);
        expect(sm.pendingSite.currentLat).toBe(52.0);
        expect(sm.pendingSite.currentLng).toBe(16.0);
    });

    test('updateSitePosition does not change originalLat', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        sm.updateSitePosition(52.0, 16.0);
        expect(sm.pendingSite.originalLat).toBe(50.0);
    });

    test('updateSitePosition emits editModeSitePositionUpdated', () => {
        const { sm, events } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        sm.updateSitePosition(52.0, 16.0);
        const ev = lastEvent(events);
        expect(ev.name).toBe('editModeSitePositionUpdated');
        expect(ev.data.lat).toBe(52.0);
    });

    test('updateSitePosition is ignored in wrong state', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        // not in site_selected — should not throw, just no-op
        expect(() => sm.updateSitePosition(52.0, 16.0)).not.toThrow();
    });

    test('completeSave returns to edit_idle and clears pendingSite', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        sm.beginSave();
        sm.completeSave();
        expect(sm.state).toBe(S.EDIT_IDLE);
        expect(sm.pendingSite).toBeNull();
        expect(sm.isSaving).toBe(false);
    });

    test('failSave keeps current state and sets saveError', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        sm.beginSave();
        sm.failSave('Network error');
        expect(sm.state).toBe(S.SITE_SELECTED);
        expect(sm.saveError).toBe('Network error');
        expect(sm.isSaving).toBe(false);
    });
});

// ---------------------------------------------------------------------------
// Placing unpositioned site
// ---------------------------------------------------------------------------

describe('placing unpositioned site', () => {
    test('beginPlacingUnpositioned stores site and transitions', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginPlacingUnpositioned(SITE_UNPOS);
        expect(sm.state).toBe(S.PLACING_UNPOSITIONED);
        expect(sm.pendingSite.id).toBe(3);
        expect(sm.pendingSite.isUnpositioned).toBe(true);
    });

    test('placeUnpositionedSite sets coordinates and moves to site_selected', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginPlacingUnpositioned(SITE_UNPOS);
        sm.placeUnpositionedSite(49.5, 13.5);
        expect(sm.state).toBe(S.SITE_SELECTED);
        expect(sm.pendingSite.currentLat).toBe(49.5);
        expect(sm.pendingSite.currentLng).toBe(13.5);
    });

    test('site is still unpositioned until save completes', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginPlacingUnpositioned(SITE_UNPOS);
        sm.placeUnpositionedSite(49.5, 13.5);
        expect(sm.pendingSite.isUnpositioned).toBe(true);
    });
});

// ---------------------------------------------------------------------------
// New site flow
// ---------------------------------------------------------------------------

describe('new site flow', () => {
    test('beginPlacingNewSite transitions to placing_new_site', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginPlacingNewSite();
        expect(sm.state).toBe(S.PLACING_NEW_SITE);
    });

    test('placeNewSite transitions to new_site_form with coordinates', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginPlacingNewSite();
        sm.placeNewSite(50.1, 14.4);
        expect(sm.state).toBe(S.NEW_SITE_FORM);
        expect(sm.pendingSite.currentLat).toBe(50.1);
        expect(sm.pendingSite.currentLng).toBe(14.4);
        expect(sm.pendingSite.isNew).toBe(true);
        expect(sm.pendingSite.id).toBeNull();
    });

    test('drag in new_site_form updates coordinates', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginPlacingNewSite();
        sm.placeNewSite(50.1, 14.4);
        sm.updateSitePosition(51.0, 15.0);
        expect(sm.pendingSite.currentLat).toBe(51.0);
    });
});

// ---------------------------------------------------------------------------
// New segment flow
// ---------------------------------------------------------------------------

describe('new segment flow', () => {
    test('beginNewSegment transitions to picking_segment_start', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginNewSegment();
        expect(sm.state).toBe(S.PICKING_SEGMENT_START);
    });

    test('beginNewSegment initialises pendingConnection', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginNewSegment();
        expect(sm.pendingConnection.objectType).toBe('segment');
        expect(sm.pendingConnection.mode).toBe('create');
        expect(sm.pendingConnection.siteA).toBeNull();
        expect(sm.pendingConnection.siteB).toBeNull();
    });

    test('pickSegmentSiteA stores siteA and transitions to picking_segment_end', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginNewSegment();
        sm.pickSegmentSiteA(SITE_A);
        expect(sm.state).toBe(S.PICKING_SEGMENT_END);
        expect(sm.pendingConnection.siteA.id).toBe(1);
    });

    test('pickSegmentSiteB stores siteB and transitions to new_segment_form', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginNewSegment();
        sm.pickSegmentSiteA(SITE_A);
        sm.pickSegmentSiteB(SITE_B);
        expect(sm.state).toBe(S.NEW_SEGMENT_FORM);
        expect(sm.pendingConnection.siteB.id).toBe(2);
    });

    test('both sites preserved on the connection at new_segment_form', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginNewSegment();
        sm.pickSegmentSiteA(SITE_A);
        sm.pickSegmentSiteB(SITE_B);
        expect(sm.pendingConnection.siteA.id).toBe(1);
        expect(sm.pendingConnection.siteB.id).toBe(2);
    });

    test('completeSave after segment form returns to edit_idle', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginNewSegment();
        sm.pickSegmentSiteA(SITE_A);
        sm.pickSegmentSiteB(SITE_B);
        sm.beginSave();
        sm.completeSave();
        expect(sm.state).toBe(S.EDIT_IDLE);
        expect(sm.pendingConnection).toBeNull();
    });
});

// ---------------------------------------------------------------------------
// New circuit flow (mirrors segment)
// ---------------------------------------------------------------------------

describe('new circuit flow', () => {
    test('full circuit creation flow ends at new_circuit_form with both sites', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginNewCircuit();
        expect(sm.state).toBe(S.PICKING_CIRCUIT_START);
        expect(sm.pendingConnection.objectType).toBe('circuit');
        sm.pickCircuitSiteA(SITE_A);
        expect(sm.state).toBe(S.PICKING_CIRCUIT_END);
        sm.pickCircuitSiteB(SITE_B);
        expect(sm.state).toBe(S.NEW_CIRCUIT_FORM);
        expect(sm.pendingConnection.siteA.id).toBe(1);
        expect(sm.pendingConnection.siteB.id).toBe(2);
    });
});

// ---------------------------------------------------------------------------
// Editing existing connection
// ---------------------------------------------------------------------------

describe('editing existing connection', () => {
    test('selectConnection transitions to editing_connection', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectConnection('segment', 42, SITE_A, SITE_B);
        expect(sm.state).toBe(S.EDITING_CONNECTION);
    });

    test('selectConnection stores existing id and sites', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectConnection('circuit', 77, SITE_A, SITE_B);
        expect(sm.pendingConnection.existingId).toBe(77);
        expect(sm.pendingConnection.objectType).toBe('circuit');
        expect(sm.pendingConnection.mode).toBe('edit');
        expect(sm.pendingConnection.siteA.id).toBe(1);
        expect(sm.pendingConnection.siteB.id).toBe(2);
    });

    test('beginChangingEnd("a") transitions to picking_replacement_site', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectConnection('segment', 42, SITE_A, SITE_B);
        sm.beginChangingEnd('a');
        expect(sm.state).toBe(S.PICKING_REPLACEMENT_SITE);
        expect(sm.pendingConnection.endToChange).toBe('a');
    });

    test('beginChangingEnd("b") sets endToChange to b', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectConnection('segment', 42, SITE_A, SITE_B);
        sm.beginChangingEnd('b');
        expect(sm.pendingConnection.endToChange).toBe('b');
    });

    test('beginChangingEnd with invalid end throws', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectConnection('segment', 42, SITE_A, SITE_B);
        expect(() => sm.beginChangingEnd('x')).toThrow();
    });

    test('pickReplacementSite transitions to confirming_replacement', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectConnection('segment', 42, SITE_A, SITE_B);
        sm.beginChangingEnd('a');
        const SITE_NEW = { id: 99, name: 'New Site', lat: 48.0, lng: 17.0 };
        sm.pickReplacementSite(SITE_NEW);
        expect(sm.state).toBe(S.CONFIRMING_REPLACEMENT);
    });

    test('pickReplacementSite stores site as pendingReplacementSite', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectConnection('segment', 42, SITE_A, SITE_B);
        sm.beginChangingEnd('a');
        const SITE_NEW = { id: 99, name: 'New Site', lat: 48.0, lng: 17.0 };
        sm.pickReplacementSite(SITE_NEW);
        expect(sm.pendingConnection.pendingReplacementSite.id).toBe(99);
        expect(sm.pendingConnection.siteA.id).toBe(1);  // not yet updated
    });

    test('confirmReplacement updates siteA and returns to editing_connection', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectConnection('segment', 42, SITE_A, SITE_B);
        sm.beginChangingEnd('a');
        const SITE_NEW = { id: 99, name: 'New Site', lat: 48.0, lng: 17.0 };
        sm.pickReplacementSite(SITE_NEW);
        sm.confirmReplacement();
        expect(sm.state).toBe(S.EDITING_CONNECTION);
        expect(sm.pendingConnection.siteA.id).toBe(99);
        expect(sm.pendingConnection.siteB.id).toBe(2);  // unchanged
        expect(sm.pendingConnection.pendingReplacementSite).toBeNull();
    });

    test('confirmReplacement updates siteB when endToChange is b', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectConnection('circuit', 77, SITE_A, SITE_B);
        sm.beginChangingEnd('b');
        const SITE_NEW = { id: 55, name: 'Another Site', lat: 47.0, lng: 18.0 };
        sm.pickReplacementSite(SITE_NEW);
        sm.confirmReplacement();
        expect(sm.pendingConnection.siteB.id).toBe(55);
        expect(sm.pendingConnection.siteA.id).toBe(1);  // unchanged
    });

    test('escape from picking_replacement_site returns to edit_idle', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectConnection('segment', 42, SITE_A, SITE_B);
        sm.beginChangingEnd('a');
        sm.escape();
        expect(sm.state).toBe(S.EDIT_IDLE);
    });

    test('escape from confirming_replacement returns to editing_connection', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectConnection('segment', 42, SITE_A, SITE_B);
        sm.beginChangingEnd('a');
        sm.pickReplacementSite({ id: 99, name: 'New Site', lat: 48.0, lng: 17.0 });
        sm.escape();
        expect(sm.state).toBe(S.EDITING_CONNECTION);
        expect(sm.pendingConnection.siteA.id).toBe(1);  // original site preserved
    });
});

// ---------------------------------------------------------------------------
// Save lifecycle
// ---------------------------------------------------------------------------

describe('save lifecycle', () => {
    test('beginSave sets isSaving true and clears error', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        sm.failSave('old error');
        sm.beginSave();
        expect(sm.isSaving).toBe(true);
        expect(sm.saveError).toBeNull();
    });

    test('completeSave clears isSaving and moves to edit_idle', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        sm.beginSave();
        sm.completeSave();
        expect(sm.isSaving).toBe(false);
        expect(sm.state).toBe(S.EDIT_IDLE);
    });

    test('failSave keeps current state', () => {
        const { sm } = makeSM();
        sm.enterEditMode();
        sm.beginNewSegment();
        sm.pickSegmentSiteA(SITE_A);
        sm.pickSegmentSiteB(SITE_B);
        sm.beginSave();
        sm.failSave('Timeout');
        expect(sm.state).toBe(S.NEW_SEGMENT_FORM);
        expect(sm.saveError).toBe('Timeout');
    });

    test('failSave emits editModeSaveFailed event', () => {
        const { sm, events } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        sm.beginSave();
        sm.failSave('Bad request');
        const ev = lastEvent(events);
        expect(ev.name).toBe('editModeSaveFailed');
        expect(ev.data.message).toBe('Bad request');
    });
});

// ---------------------------------------------------------------------------
// Event emission
// ---------------------------------------------------------------------------

describe('event emission', () => {
    test('every valid transition emits editModeStateChanged', () => {
        const { sm, events } = makeSM();
        sm.enterEditMode();
        sm.beginNewSegment();
        sm.pickSegmentSiteA(SITE_A);

        const stateChanges = events.filter(e => e.name === 'editModeStateChanged');
        // enterEditMode + beginNewSegment + pickSegmentSiteA = 3 transitions
        expect(stateChanges.length).toBe(3);
    });

    test('editModeStateChanged carries prev and state', () => {
        const { sm, events } = makeSM();
        sm.enterEditMode();
        sm.selectSite(SITE_A);
        const ev = lastEvent(events);
        expect(ev.data.prev).toBe(S.EDIT_IDLE);
        expect(ev.data.state).toBe(S.SITE_SELECTED);
    });

    test('machine reference is on every event', () => {
        const { sm, events } = makeSM();
        sm.enterEditMode();
        const ev = lastEvent(events);
        expect(ev.data.machine).toBe(sm);
    });
});

// ---------------------------------------------------------------------------
// setReferenceData
// ---------------------------------------------------------------------------

describe('setReferenceData', () => {
    test('updates only the supplied keys', () => {
        const { sm } = makeSM();
        sm.enterEditMode({ providers: [{ id: 1, name: 'P1' }] });
        sm.setReferenceData({ circuitTypes: [{ id: 5, name: 'CT' }] });
        expect(sm.providers).toEqual([{ id: 1, name: 'P1' }]);   // unchanged
        expect(sm.circuitTypes).toEqual([{ id: 5, name: 'CT' }]);
    });
});
