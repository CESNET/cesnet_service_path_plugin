/**
 * edit_mode_ui.js — DOM orchestration for Network Map edit mode.
 *
 * Wires EditModeStateMachine events → DOM changes, and DOM events → state
 * machine actions.  Calls EditModeApi for all network operations.
 *
 * Depends on (loaded before this script):
 *   edit_mode_state_machine.js  → window.EditModeStateMachine
 *   edit_mode_api.js            → window.EditModeApi
 *   edit_mode_marker.js         → window.EditModeMarker
 *
 * Instantiated at the bottom of object_map.js when _mapData.canEdit === true.
 */

(function (root) {
    'use strict';

    const S = EditModeStateMachine.STATES;

    function _roundCoord(v) { return Math.round(v * 1e6) / 1e6; }

    function slugify(str) {
        return str.toLowerCase()
            .replace(/[^\w\s-]/g, '').trim()
            .replace(/[\s_]+/g, '-').replace(/-+/g, '-');
    }

    // -------------------------------------------------------------------------
    // Minimal event bus
    // -------------------------------------------------------------------------
    class EventBus {
        constructor() { this._h = {}; }
        on(name, fn)  { (this._h[name] ??= []).push(fn); }
        emit(name, d) { (this._h[name] || []).forEach(fn => fn(d)); }
    }

    // -------------------------------------------------------------------------
    // EditModeUI
    // -------------------------------------------------------------------------
    class EditModeUI {
        /**
         * @param {object} opts  All dependencies passed as a single named-arg object.
         */
        constructor(opts) {
            this._map            = opts.map;
            this._allSites       = opts.allSites;
            this._allSegments    = opts.allSegments;
            this._allCircuits    = opts.allCircuits;
            this._allSitesById   = opts.allSitesById;
            this._renderSites    = opts.renderSites;
            this._renderSegments = opts.renderSegments;
            this._renderCircuits = opts.renderCircuits;
            this._applyFilters   = opts.applyFilters || opts.renderSites;
            this._buildSiteCard  = opts.buildSiteInfoCard;
            this._buildSegCard   = opts.buildSegmentInfoCard;
            this._buildCircCard  = opts.buildCircuitInfoCard;
            this._showInfoCard   = opts.showInfoCard;
            this._hideInfoCard   = opts.hideInfoCard;
            this._siteLayers     = opts.siteLayers;
            this._segmentLayers  = opts.segmentLayers;
            this._circuitLayers  = opts.circuitLayers || new Map();
            this._handleLineClick    = opts.handleLineClick    || null;
            this._findNearbySegments = opts.findNearbySegments || null;
            this._editSegMapHandler  = null;

            this._events  = new EventBus();
            this._sm      = new EditModeStateMachine(this._events);
            this._api     = new EditModeApi();
            this._marker  = new EditModeMarker(opts.map);
            this._preview = null;
            this._editHL  = null;   // { layer, restoreStyle } — current edit highlight

            this._init();
        }

        // -------------------------------------------------------------------------
        // Initialisation
        // -------------------------------------------------------------------------
        _init() {
            this._events.on('editModeStateChanged',    ev => this._onStateChanged(ev.state, ev.prev));
            this._events.on('editModeSitePositionUpdated', ev => this._onPositionUpdated(ev.lat, ev.lng));
            this._events.on('editModeSaveFailed',      ev => this._showError(ev.message));

            document.addEventListener('keydown', e => {
                if (e.key === 'Escape') this._sm.escape();
            });

            const toggleBtn = document.getElementById('editModeToggle');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', () => {
                    if (this._sm.state === S.VIEW) this._enterEditMode();
                    else                           this._sm.exitEditMode();
                });
            }

            this._map.on('click', e => this._onMapClick(e.latlng.lat, e.latlng.lng));
        }

        // -------------------------------------------------------------------------
        // Enter edit mode
        // -------------------------------------------------------------------------
        _enterEditMode() {
            const toggleBtn = document.getElementById('editModeToggle');
            if (toggleBtn) {
                toggleBtn.disabled = true;
                toggleBtn.innerHTML = '<i class="mdi mdi-loading mdi-spin"></i> Loading…';
            }
            this._api.loadReferenceData().then(refData => {
                this._sm.enterEditMode(refData);
                const presite = window._editModeLastSite || null;
                const preconn = window._editModeLastConnection || null;
                if (presite && presite.lat != null && presite.lng != null) {
                    this._marker.place(presite.lat, presite.lng, (lat, lng) => {
                        this._sm.updateSitePosition(_roundCoord(lat), _roundCoord(lng));
                    });
                    this._sm.selectSite(presite);
                    this._applyEditHighlight('site', presite.id);
                } else if (preconn) {
                    const obj = preconn.obj;
                    this._sm.selectConnection(preconn.objectType, obj.id, obj.site_a, obj.site_b, obj.term_a, obj.term_z);
                    this._applyEditHighlight(preconn.objectType, obj.id);
                }
            }).catch(err => {
                if (toggleBtn) {
                    toggleBtn.disabled = false;
                    toggleBtn.innerHTML = '<i class="mdi mdi-pencil"></i> Edit';
                }
                this._showError(`Could not load edit mode data: ${err.message}`);
            });
        }

        // -------------------------------------------------------------------------
        // State change handler
        // -------------------------------------------------------------------------
        _onStateChanged(state) {
            const toggleBtn = document.getElementById('editModeToggle');
            if (toggleBtn) {
                toggleBtn.disabled = false;
                if (state === S.VIEW) {
                    toggleBtn.className = 'btn btn-outline-warning btn-sm';
                    toggleBtn.innerHTML = '<i class="mdi mdi-pencil"></i> Edit';
                } else {
                    toggleBtn.className = 'btn btn-warning btn-sm';
                    toggleBtn.innerHTML = '<i class="mdi mdi-pencil-off"></i> Exit Edit';
                }
            }

            const mapEl = document.getElementById('map');
            if (mapEl) {
                mapEl.classList.remove('edit-cursor-crosshair', 'edit-cursor-pointer');
                if (state === S.PLACING_UNPOSITIONED || state === S.PLACING_NEW_SITE) {
                    mapEl.classList.add('edit-cursor-crosshair');
                } else if (state === S.PICKING_SEGMENT_START || state === S.PICKING_SEGMENT_END ||
                           state === S.PICKING_CIRCUIT_START  || state === S.PICKING_CIRCUIT_END ||
                           state === S.PICKING_REPLACEMENT_SITE) {
                    mapEl.classList.add('edit-cursor-pointer');
                }
            }

            const filterSidebar = document.getElementById('filterSidebar');
            const editPanel     = document.getElementById('editModePanel');
            if (state === S.VIEW) {
                if (filterSidebar) filterSidebar.style.display = '';
                if (editPanel)     editPanel.style.display     = 'none';
                this._marker.remove();
                this._removePreview();
                this._clearEditHighlight();
            } else {
                if (filterSidebar) filterSidebar.style.display = 'none';
                if (editPanel)     editPanel.style.display     = '';
                if (state === S.EDIT_IDLE) this._clearEditHighlight();
                this._renderEditPanel(state);
            }

            if (state !== S.VIEW) {
                this._wireSiteClicksForEditMode();
                this._wireConnectionClicksForEditMode();
            } else {
                this._wireSiteClicksForReadMode();
                this._wireConnectionClicksForReadMode();
            }
        }

        // -------------------------------------------------------------------------
        // Edit panel rendering
        // -------------------------------------------------------------------------
        _renderEditPanel(state) {
            const sm    = this._sm;
            const panel = document.getElementById('editModePanel');
            if (!panel) return;

            const pendingA = sm.pendingConnection && sm.pendingConnection.siteA;
            const pendingB = sm.pendingConnection && sm.pendingConnection.siteB;

            const html = (() => { switch (state) {
                case S.EDIT_IDLE:
                    return this._renderIdlePanel();
                case S.SITE_SELECTED:
                    return this._renderSiteSelectedPanel();
                case S.PLACING_UNPOSITIONED:
                    return _instruction('mdi-map-marker-plus',
                        `Click on the map to place <strong>${_esc(sm.pendingSite ? sm.pendingSite.name : '')}</strong>`);
                case S.PLACING_NEW_SITE:
                    return _instruction('mdi-map-marker-plus', 'Click on the map to place a new site marker');
                case S.NEW_SITE_FORM:
                    return this._renderNewSiteForm();
                case S.PICKING_SEGMENT_START:
                    return _instruction('mdi-vector-polyline', 'Click <strong>site A</strong> on the map to start a new segment');
                case S.PICKING_SEGMENT_END:
                    return _instruction('mdi-vector-polyline',
                        `Site A: <strong>${_esc(pendingA ? pendingA.name : '?')}</strong><br>Now click <strong>site B</strong> on the map`);
                case S.NEW_SEGMENT_FORM:
                    return this._renderNewSegmentForm();
                case S.PICKING_CIRCUIT_START:
                    return _instruction('mdi-transit-connection-variant', 'Click <strong>site A</strong> on the map to start a new circuit');
                case S.PICKING_CIRCUIT_END:
                    return _instruction('mdi-transit-connection-variant',
                        `Site A: <strong>${_esc(pendingA ? pendingA.name : '?')}</strong><br>Now click <strong>site B</strong> on the map`);
                case S.NEW_CIRCUIT_FORM:
                    return this._renderNewCircuitForm();
                case S.EDITING_CONNECTION:
                    return this._renderEditConnectionPanel();
                case S.PICKING_REPLACEMENT_SITE: {
                    const endLabel = sm.pendingConnection && sm.pendingConnection.endToChange === 'a' ? 'A' : 'B';
                    return _instruction('mdi-cursor-pointer', `Click the new <strong>site ${endLabel}</strong> on the map`);
                }
                case S.CONFIRMING_REPLACEMENT:
                    return this._renderConfirmReplacementPanel();
                default: return '';
            }})();

            panel.innerHTML = html;
            this._bindEditPanelEvents(state);
        }

        // -------------------------------------------------------------------------
        // Panel HTML builders
        // -------------------------------------------------------------------------
        _renderIdlePanel() {
            const sites = this._sm.unpositionedSites;
            const listHtml = sites.length === 0
                ? '<div class="text-muted small">All sites have GPS coordinates.</div>'
                : '<input type="search" id="unposSearch" class="form-control form-control-sm mb-1" placeholder="Search…" autocomplete="off">' +
                  '<div id="unpositionedList" style="overflow-y:auto; max-height:320px;">' +
                  sites.map(s =>
                      `<div class="list-row py-1 px-1 border-bottom" data-site-id="${s.id}" ` +
                      `style="cursor:pointer; font-size:0.78rem;" title="Click to place on map">` +
                      `<i class="mdi mdi-map-marker-off text-muted me-1"></i>${_esc(s.name)}</div>`
                  ).join('') +
                  '</div>';

            return _card('<i class="mdi mdi-pencil"></i> Edit Mode',
                '<div class="mb-2">' +
                '<div class="text-muted small mb-1 fw-bold text-uppercase" style="font-size:0.68rem;">Actions</div>' +
                '<div class="d-grid gap-1">' +
                '<button id="btnAddNewSite" class="btn btn-outline-primary btn-sm"><i class="mdi mdi-map-marker-plus"></i> Add new site</button>' +
                '<button id="btnNewSegment" class="btn btn-outline-success btn-sm"><i class="mdi mdi-vector-polyline-plus"></i> New segment</button>' +
                '<button id="btnNewCircuit" class="btn btn-outline-warning btn-sm"><i class="mdi mdi-transit-connection-variant"></i> New circuit</button>' +
                '</div></div><hr class="my-1">' +
                `<div class="text-muted small mb-1 fw-bold text-uppercase" style="font-size:0.68rem;">` +
                `<i class="mdi mdi-map-marker-off"></i> Sites without GPS (${sites.length})</div>` +
                listHtml
            );
        }

        _renderSiteSelectedPanel() {
            const sm = this._sm;
            const ps = sm.pendingSite;
            if (!ps) return '';
            const saveLabel = ps.isNew ? 'Save &amp; open full form' : 'Save coordinates';
            return _card(
                `<i class="mdi mdi-map-marker-check"></i> ${ps.isNew ? 'New site' : _esc(ps.name)}`,
                '<div class="mb-2">' +
                '<div class="mb-1"><label class="form-label mb-0 small">Latitude</label>' +
                `<input type="number" id="editLat" class="form-control form-control-sm" step="0.000001" value="${ps.currentLat || ''}"></div>` +
                '<div class="mb-2"><label class="form-label mb-0 small">Longitude</label>' +
                `<input type="number" id="editLng" class="form-control form-control-sm" step="0.000001" value="${ps.currentLng || ''}"></div>` +
                (sm.saveError ? `<div class="alert alert-danger py-1 small mb-2">${_esc(sm.saveError)}</div>` : '') +
                '<div class="d-flex gap-1">' +
                `<button id="btnSaveSite" class="btn btn-primary btn-sm flex-fill"${sm.isSaving ? ' disabled' : ''}>` +
                (sm.isSaving ? '<i class="mdi mdi-loading mdi-spin"></i> Saving…' : `<i class="mdi mdi-content-save"></i> ${saveLabel}`) +
                '</button><button id="btnCancelSite" class="btn btn-outline-secondary btn-sm">Cancel</button>' +
                '</div></div>'
            );
        }

        _renderNewSiteForm() {
            const sm = this._sm;
            const ps = sm.pendingSite;
            return _card('<i class="mdi mdi-map-marker-plus"></i> New Site',
                '<form id="newSiteForm" autocomplete="off">' +
                _formField('Name', 'newSiteName', 'text', '', true) +
                _formField('Slug', 'newSiteSlug', 'text', '', true) +
                _formField('Latitude',  'newSiteLat', 'number', ps ? ps.currentLat : '') +
                _formField('Longitude', 'newSiteLng', 'number', ps ? ps.currentLng : '') +
                (sm.saveError ? `<div class="alert alert-danger py-1 small mb-2">${_esc(sm.saveError)}</div>` : '') +
                '<div class="d-flex gap-1 mb-1">' +
                `<button type="submit" class="btn btn-primary btn-sm flex-fill"${sm.isSaving ? ' disabled' : ''}>` +
                (sm.isSaving ? '<i class="mdi mdi-loading mdi-spin"></i> Saving…' : '<i class="mdi mdi-content-save"></i> Create site') +
                '</button><button type="button" id="btnCancelNewSite" class="btn btn-outline-secondary btn-sm">Cancel</button>' +
                '</div>' +
                '</form>'
            );
        }

        _renderNewSegmentForm() {
            const sm        = this._sm;
            const conn      = sm.pendingConnection;
            const siteAName = conn && conn.siteA ? _esc(conn.siteA.name) : '—';
            const siteBName = conn && conn.siteB ? _esc(conn.siteB.name) : '—';
            const providerOptions = sm.providers.map(p => `<option value="${p.id}">${_esc(p.name)}</option>`).join('');
            return _card('<i class="mdi mdi-vector-polyline-plus"></i> New Segment',
                '<form id="newSegmentForm" autocomplete="off">' +
                _formField('Name', 'newSegName', 'text', '', true) +
                '<div class="mb-1"><label class="form-label mb-0 small">Segment type <span class="text-danger">*</span></label>' +
                '<select id="newSegType" class="form-select form-select-sm">' +
                '<option value="dark_fiber" selected>Dark Fiber</option>' +
                '<option value="optical_spectrum">Optical Spectrum</option>' +
                '<option value="ethernet_service">Ethernet Service</option>' +
                '</select></div>' +
                '<div class="mb-1"><label class="form-label mb-0 small">Provider <span class="text-danger">*</span></label>' +
                `<select id="newSegProvider" class="form-select form-select-sm"><option value="">— select —</option>${providerOptions}</select></div>` +
                '<div class="mb-1"><label class="form-label mb-0 small">Ownership type</label>' +
                '<select id="newSegOwnership" class="form-select form-select-sm">' +
                '<option value="leased" selected>Leased</option><option value="owned">Owned</option>' +
                '<option value="shared">Shared</option><option value="foreign">Foreign</option>' +
                '</select></div>' +
                '<div class="mb-2"><label class="form-label mb-0 small">Status</label>' +
                '<select id="newSegStatus" class="form-select form-select-sm">' +
                '<option value="active" selected>Active</option><option value="planned">Planned</option>' +
                '<option value="offline">Offline</option><option value="decommissioned">Decommissioned</option>' +
                '<option value="surveyed">Surveyed</option>' +
                '</select></div>' +
                `<div class="mb-1 small"><strong>Site A:</strong> ${siteAName}</div>` +
                `<div class="mb-2 small"><strong>Site B:</strong> ${siteBName}</div>` +
                (sm.saveError ? `<div class="alert alert-danger py-1 small mb-2">${_esc(sm.saveError)}</div>` : '') +
                '<div class="d-flex gap-1 mb-1">' +
                `<button type="submit" class="btn btn-primary btn-sm flex-fill"${sm.isSaving ? ' disabled' : ''}>` +
                (sm.isSaving ? '<i class="mdi mdi-loading mdi-spin"></i> Saving…' : '<i class="mdi mdi-content-save"></i> Create segment') +
                '</button><button type="button" id="btnCancelNewSeg" class="btn btn-outline-secondary btn-sm">Cancel</button>' +
                '</div>' +
                '</form>'
            );
        }

        _renderNewCircuitForm() {
            const sm        = this._sm;
            const conn      = sm.pendingConnection;
            const siteAName = conn && conn.siteA ? _esc(conn.siteA.name) : '—';
            const siteBName = conn && conn.siteB ? _esc(conn.siteB.name) : '—';
            const providerOptions = sm.providers.map(p => `<option value="${p.id}">${_esc(p.name)}</option>`).join('');
            const typeOptions     = sm.circuitTypes.map(t => `<option value="${t.id}">${_esc(t.name)}</option>`).join('');
            return _card('<i class="mdi mdi-transit-connection-variant"></i> New Circuit',
                '<form id="newCircuitForm" autocomplete="off">' +
                _formField('Circuit ID', 'newCircCid', 'text', '', true) +
                '<div class="mb-1"><label class="form-label mb-0 small">Provider <span class="text-danger">*</span></label>' +
                `<select id="newCircProvider" class="form-select form-select-sm"><option value="">— select —</option>${providerOptions}</select></div>` +
                '<div class="mb-2"><label class="form-label mb-0 small">Type <span class="text-danger">*</span></label>' +
                `<select id="newCircType" class="form-select form-select-sm"><option value="">— select —</option>${typeOptions}</select></div>` +
                `<div class="mb-1 small"><strong>Site A:</strong> ${siteAName}</div>` +
                `<div class="mb-2 small"><strong>Site B:</strong> ${siteBName}</div>` +
                (sm.saveError ? `<div class="alert alert-danger py-1 small mb-2">${_esc(sm.saveError)}</div>` : '') +
                '<div class="d-flex gap-1 mb-1">' +
                `<button type="submit" class="btn btn-primary btn-sm flex-fill"${sm.isSaving ? ' disabled' : ''}>` +
                (sm.isSaving ? '<i class="mdi mdi-loading mdi-spin"></i> Saving…' : '<i class="mdi mdi-content-save"></i> Create circuit') +
                '</button><button type="button" id="btnCancelNewCirc" class="btn btn-outline-secondary btn-sm">Cancel</button>' +
                '</div>' +
                '</form>'
            );
        }

        _renderEditConnectionPanel() {
            const sm   = this._sm;
            const conn = sm.pendingConnection;
            if (!conn) return '';
            const icon      = conn.objectType === 'segment' ? 'mdi-vector-polyline' : 'mdi-transit-connection-variant';
            const siteAName = conn.siteA ? _esc(conn.siteA.name) : '—';
            const siteBName = conn.siteB ? _esc(conn.siteB.name) : '—';
            return _card(`<i class="mdi ${icon}"></i> Edit endpoints`,
                '<div class="mb-2 small">' +
                '<div class="mb-1 d-flex align-items-center justify-content-between">' +
                `<span><strong>Site A:</strong> ${siteAName}</span>` +
                '<button id="btnChangeEndA" class="btn btn-outline-primary btn-sm py-0">Change</button></div>' +
                '<div class="d-flex align-items-center justify-content-between">' +
                `<span><strong>Site B:</strong> ${siteBName}</span>` +
                '<button id="btnChangeEndB" class="btn btn-outline-primary btn-sm py-0">Change</button>' +
                '</div></div>' +
                (sm.saveError ? `<div class="alert alert-danger py-1 small mb-2">${_esc(sm.saveError)}</div>` : '') +
                '<button id="btnCancelEditConn" class="btn btn-outline-secondary btn-sm w-100">Cancel</button>'
            );
        }

        _renderConfirmReplacementPanel() {
            const sm   = this._sm;
            const conn = sm.pendingConnection;
            if (!conn) return '';
            const end       = conn.endToChange === 'a' ? 'A' : 'B';
            const oldSite   = conn.endToChange === 'a' ? conn.siteA : conn.siteB;
            const newSite   = conn.pendingReplacementSite;
            const icon      = conn.objectType === 'segment' ? 'mdi-vector-polyline' : 'mdi-transit-connection-variant';
            const oldName   = oldSite ? _esc(oldSite.name) : '—';
            const newName   = newSite ? _esc(newSite.name) : '—';
            return _card(`<i class="mdi ${icon}"></i> Confirm change`,
                `<div class="mb-2 small">` +
                `<div class="mb-1">Change <strong>Site ${end}</strong>:</div>` +
                `<div class="mb-1"><span class="text-muted">From:</span> <strong>${oldName}</strong></div>` +
                `<div class="mb-2"><span class="text-muted">To:</span> <strong class="text-primary">${newName}</strong></div>` +
                `</div>` +
                (sm.saveError ? `<div class="alert alert-danger py-1 small mb-2">${_esc(sm.saveError)}</div>` : '') +
                `<div class="d-flex gap-1">` +
                `<button id="btnConfirmReplacement" class="btn btn-primary btn-sm flex-fill"${sm.isSaving ? ' disabled' : ''}>` +
                (sm.isSaving ? '<i class="mdi mdi-loading mdi-spin"></i> Saving…' : '<i class="mdi mdi-check"></i> Confirm') +
                `</button>` +
                `<button id="btnCancelReplacement" class="btn btn-outline-secondary btn-sm">Cancel</button>` +
                `</div>`
            );
        }

        // -------------------------------------------------------------------------
        // Panel event binding
        // -------------------------------------------------------------------------
        _bindEditPanelEvents(state) {
            const sm = this._sm;
            const on = (id, event, fn) => document.getElementById(id)?.addEventListener(event, fn);

            switch (state) {
            case S.EDIT_IDLE:
                on('btnAddNewSite', 'click', () => sm.beginPlacingNewSite());
                on('btnNewSegment', 'click', () => sm.beginNewSegment());
                on('btnNewCircuit', 'click', () => sm.beginNewCircuit());
                document.getElementById('unpositionedList')?.addEventListener('click', e => {
                    const row = e.target.closest('.list-row');
                    if (!row) return;
                    const site = sm.unpositionedSites.find(s => s.id === Number(row.dataset.siteId));
                    if (site) sm.beginPlacingUnpositioned(site);
                });
                document.getElementById('unposSearch')?.addEventListener('input', function () {
                    const q = this.value.toLowerCase();
                    document.querySelectorAll('#unpositionedList .list-row').forEach(row => {
                        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
                    });
                });
                break;

            case S.SITE_SELECTED:
                on('editLat', 'input', () => {
                    const lat = parseFloat(document.getElementById('editLat').value);
                    const lng = parseFloat(document.getElementById('editLng').value);
                    if (!isNaN(lat) && !isNaN(lng)) { this._marker.moveTo(lat, lng); sm.updateSitePosition(lat, lng); }
                });
                on('editLng', 'input', () => {
                    const lat = parseFloat(document.getElementById('editLat').value);
                    const lng = parseFloat(document.getElementById('editLng').value);
                    if (!isNaN(lat) && !isNaN(lng)) { this._marker.moveTo(lat, lng); sm.updateSitePosition(lat, lng); }
                });
                on('btnSaveSite',   'click', () => this._saveSiteCoordinates());
                on('btnCancelSite', 'click', () => { this._marker.remove(); sm.escape(); });
                break;

            case S.NEW_SITE_FORM: {
                on('newSiteName', 'input', function () {
                    const slugEl = document.getElementById('newSiteSlug');
                    if (slugEl && !slugEl.dataset.userEdited) slugEl.value = slugify(this.value);
                });
                on('newSiteSlug', 'input', function () { this.dataset.userEdited = '1'; });
                const ps = sm.pendingSite;
                if (ps) {
                    this._marker.remove();
                    this._marker.place(ps.currentLat, ps.currentLng, (lat, lng) => {
                        lat = _roundCoord(lat); lng = _roundCoord(lng);
                        const latEl = document.getElementById('newSiteLat');
                        const lngEl = document.getElementById('newSiteLng');
                        if (latEl) latEl.value = lat.toFixed(6);
                        if (lngEl) lngEl.value = lng.toFixed(6);
                        sm.updateSitePosition(lat, lng);
                    });
                }
                on('newSiteLat', 'input', () => {
                    const lat = parseFloat(document.getElementById('newSiteLat').value);
                    const lng = parseFloat(document.getElementById('newSiteLng').value);
                    if (!isNaN(lat) && !isNaN(lng)) this._marker.moveTo(lat, lng);
                });
                on('newSiteLng', 'input', () => {
                    const lat = parseFloat(document.getElementById('newSiteLat').value);
                    const lng = parseFloat(document.getElementById('newSiteLng').value);
                    if (!isNaN(lat) && !isNaN(lng)) this._marker.moveTo(lat, lng);
                });
                document.getElementById('newSiteForm')?.addEventListener('submit', e => {
                    e.preventDefault(); this._submitNewSiteForm();
                });
                on('btnCancelNewSite', 'click', () => { this._marker.remove(); sm.escape(); });
                break;
            }

            case S.NEW_SEGMENT_FORM:
                document.getElementById('newSegmentForm')?.addEventListener('submit', e => {
                    e.preventDefault(); this._submitNewSegmentForm();
                });
                on('btnCancelNewSeg', 'click', () => { this._removePreview(); sm.escape(); });
                break;

            case S.NEW_CIRCUIT_FORM:
                document.getElementById('newCircuitForm')?.addEventListener('submit', e => {
                    e.preventDefault(); this._submitNewCircuitForm();
                });
                on('btnCancelNewCirc', 'click', () => { this._removePreview(); sm.escape(); });
                break;

            case S.EDITING_CONNECTION:
                on('btnChangeEndA',     'click', () => sm.beginChangingEnd('a'));
                on('btnChangeEndB',     'click', () => sm.beginChangingEnd('b'));
                on('btnCancelEditConn', 'click', () => sm.escape());
                break;

            case S.CONFIRMING_REPLACEMENT:
                on('btnConfirmReplacement', 'click', () => this._saveReplacementSite());
                on('btnCancelReplacement',  'click', () => sm.escape());
                break;
            }
        }

        // -------------------------------------------------------------------------
        // Position update — marker dragged in site_selected / new_site_form
        // -------------------------------------------------------------------------
        _onPositionUpdated(lat, lng) {
            document.getElementById('editLat')?.setAttribute('value', lat.toFixed(6));
            document.getElementById('editLng')?.setAttribute('value', lng.toFixed(6));
            const latEl = document.getElementById('editLat');
            const lngEl = document.getElementById('editLng');
            if (latEl) latEl.value = lat.toFixed(6);
            if (lngEl) lngEl.value = lng.toFixed(6);
        }

        // -------------------------------------------------------------------------
        // Map click
        // -------------------------------------------------------------------------
        _onMapClick(lat, lng) {
            const state = this._sm.state;
            lat = _roundCoord(lat);
            lng = _roundCoord(lng);
            if (state === S.PLACING_UNPOSITIONED) {
                const cb = (dlat, dlng) => this._sm.updateSitePosition(_roundCoord(dlat), _roundCoord(dlng));
                this._marker.place(lat, lng, cb);
                this._sm.placeUnpositionedSite(lat, lng);
            } else if (state === S.PLACING_NEW_SITE) {
                this._sm.placeNewSite(lat, lng);
            }
        }

        // -------------------------------------------------------------------------
        // Layer highlight
        // -------------------------------------------------------------------------
        _setLayerStyle(layer, style) {
            if (layer instanceof L.CircleMarker || layer instanceof L.Polyline) {
                layer.setStyle(style);
            } else if (layer.eachLayer) {
                layer.eachLayer(sub => { if (sub.setStyle) sub.setStyle(style); });
            }
        }

        _applyEditHighlight(type, id) {
            this._clearEditHighlight();
            let layer, hlStyle, restoreStyle;

            if (type === 'site') {
                layer = this._siteLayers.get(id.toString());
                if (layer) {
                    const o = layer.options;
                    restoreStyle = { fillColor: o.fillColor, radius: o.radius, weight: o.weight, color: o.color };
                    hlStyle      = { fillColor: '#ffff00', radius: 11, weight: 3, color: '#e65100' };
                }
            } else {
                layer = (type === 'segment' ? this._segmentLayers : this._circuitLayers).get(id.toString());
                if (layer) {
                    let ref = layer;
                    if (!(layer instanceof L.Polyline)) layer.eachLayer(l => { if (ref === layer) ref = l; });
                    const o = ref.options || {};
                    restoreStyle = { color: o.color, weight: o.weight, opacity: o.opacity };
                    hlStyle      = { color: '#ffff00', weight: type === 'segment' ? 7 : 6, opacity: 1 };
                }
            }

            if (!layer || !hlStyle) return;
            this._editHL = { layer, restoreStyle };
            this._setLayerStyle(layer, hlStyle);
        }

        _clearEditHighlight() {
            if (!this._editHL) return;
            const { layer, restoreStyle } = this._editHL;
            this._editHL = null;
            this._setLayerStyle(layer, restoreStyle);
        }

        // -------------------------------------------------------------------------
        // Site click wiring
        // -------------------------------------------------------------------------
        _wireSiteClicksForEditMode() {
            const sm = this._sm;
            this._siteLayers.forEach((marker, idStr) => {
                marker.off('click');
                marker.on('click', e => {
                    L.DomEvent.stopPropagation(e);
                    const site  = this._allSitesById.get(idStr);
                    const state = sm.state;
                    if (state === S.EDIT_IDLE || state === S.SITE_SELECTED) {
                        if (!site) return;
                        if (state === S.SITE_SELECTED) sm.escape();
                        this._marker.place(site.lat, site.lng, (lat, lng) => {
                            sm.updateSitePosition(_roundCoord(lat), _roundCoord(lng));
                        });
                        sm.selectSite(site);
                        this._buildSiteCard(site);
                        this._applyEditHighlight('site', site.id);
                    } else if (state === S.PICKING_SEGMENT_START) {
                        if (site) sm.pickSegmentSiteA(site);
                    } else if (state === S.PICKING_SEGMENT_END) {
                        if (site) { sm.pickSegmentSiteB(site); this._drawPreview(sm.pendingConnection.siteA, site); }
                    } else if (state === S.PICKING_CIRCUIT_START) {
                        if (site) sm.pickCircuitSiteA(site);
                    } else if (state === S.PICKING_CIRCUIT_END) {
                        if (site) { sm.pickCircuitSiteB(site); this._drawPreview(sm.pendingConnection.siteA, site); }
                    } else if (state === S.PICKING_REPLACEMENT_SITE) {
                        if (site) sm.pickReplacementSite(site);
                    }
                });
            });
        }

        _wireSiteClicksForReadMode() {
            this._siteLayers.forEach((marker, idStr) => {
                marker.off('click');
                marker.on('click', () => {
                    const site = this._allSitesById.get(idStr);
                    if (site) this._buildSiteCard(site);
                });
            });
        }

        // -------------------------------------------------------------------------
        // Connection click wiring
        // -------------------------------------------------------------------------
        _wireConnectionClicksForEditMode() {
            const sm = this._sm;

            this._segmentLayers.forEach(layer => layer.off('click'));

            if (this._editSegMapHandler) this._map.off('click', this._editSegMapHandler);
            this._editSegMapHandler = e => {
                if (sm.state !== S.EDIT_IDLE && sm.state !== S.EDITING_CONNECTION) return;
                if (!this._findNearbySegments) return;
                const nearby = this._findNearbySegments(e);
                if (!nearby.length) return;
                L.DomEvent.stopPropagation(e);

                const selectSeg = seg => {
                    if (sm.state === S.EDITING_CONNECTION) sm.escape();
                    sm.selectConnection('segment', seg.id, seg.site_a, seg.site_b);
                    this._buildSegCard(seg);
                    this._applyEditHighlight('segment', seg.id);
                };

                if (nearby.length === 1) {
                    selectSeg(nearby[0].seg);
                } else {
                    const segById = new Map(nearby.map(({ seg }) => [seg.id, seg]));
                    let html = `<div><strong>${nearby.length} segments here</strong>
                        <div style="font-size:0.78rem;color:#555;">Click a name to select for editing</div>`;
                    nearby.forEach(({ seg }) => {
                        html += `<hr style="margin:4px 0;"><div>
                            <span class="seg-edit-pick" data-seg-id="${seg.id}"
                                  style="cursor:pointer;font-weight:500;color:#0d6efd;"
                                  onmouseover="this.style.textDecoration='underline'"
                                  onmouseout="this.style.textDecoration='none'">${_esc(seg.name)}</span><br>
                            <small>${seg.site_a ? seg.site_a.name : ''} ↔ ${seg.site_b ? seg.site_b.name : ''}</small>
                        </div>`;
                    });
                    html += '</div>';
                    const popup = L.popup({ maxWidth: 340 }).setLatLng(e.latlng).setContent(html);
                    popup.on('add', () => {
                        popup.getElement()?.querySelectorAll('.seg-edit-pick').forEach(span => {
                            span.addEventListener('click', () => {
                                const seg = segById.get(Number(span.dataset.segId));
                                if (seg) { this._map.closePopup(); selectSeg(seg); }
                            });
                        });
                    });
                    popup.openOn(this._map);
                }
            };
            this._map.on('click', this._editSegMapHandler);

            this._circuitLayers.forEach((layer, idStr) => {
                layer.off('click');
                layer.on('click', e => {
                    L.DomEvent.stopPropagation(e);
                    const circ = this._allCircuits.find(c => c.id.toString() === idStr);
                    if (!circ) return;
                    if (sm.state !== S.EDIT_IDLE && sm.state !== S.EDITING_CONNECTION) return;
                    if (sm.state === S.EDITING_CONNECTION) sm.escape();
                    sm.selectConnection('circuit', circ.id, circ.site_a, circ.site_b, circ.term_a, circ.term_z);
                    this._buildCircCard(circ);
                    this._applyEditHighlight('circuit', circ.id);
                });
            });
        }

        _wireConnectionClicksForReadMode() {
            if (this._editSegMapHandler) {
                this._map.off('click', this._editSegMapHandler);
                this._editSegMapHandler = null;
            }
            this._segmentLayers.forEach(layer => {
                layer.off('click');
                if (this._handleLineClick) layer.on('click', this._handleLineClick);
            });
            this._circuitLayers.forEach((layer, idStr) => {
                layer.off('click');
                layer.on('click', () => {
                    const circ = this._allCircuits.find(c => c.id.toString() === idStr);
                    if (circ) this._buildCircCard(circ);
                });
            });
        }

        // -------------------------------------------------------------------------
        // Preview line
        // -------------------------------------------------------------------------
        _drawPreview(siteA, siteB) {
            this._removePreview();
            if (!siteA || !siteB) return;
            this._preview = L.polyline(
                [[siteA.lat, siteA.lng], [siteB.lat, siteB.lng]],
                { color: '#e65100', weight: 3, dashArray: '8 6', opacity: 0.8 }
            ).addTo(this._map);
        }

        _removePreview() {
            if (this._preview) { this._preview.remove(); this._preview = null; }
        }

        // -------------------------------------------------------------------------
        // Save helpers
        // -------------------------------------------------------------------------
        _patchSiteCoords(mapObj) {
            const sa = mapObj.site_a && this._allSitesById.get(mapObj.site_a.id.toString());
            const sb = mapObj.site_b && this._allSitesById.get(mapObj.site_b.id.toString());
            if (sa) { mapObj.site_a.lat = sa.lat; mapObj.site_a.lng = sa.lng; }
            if (sb) { mapObj.site_b.lat = sb.lat; mapObj.site_b.lng = sb.lng; }
        }

        _zoomToMidpoint(siteA, siteB) {
            if (siteA && siteB) {
                this._map.setView(
                    [(siteA.lat + siteB.lat) / 2, (siteA.lng + siteB.lng) / 2],
                    this._map.getZoom()
                );
            }
        }

        _afterSiteSave(lat, lng) {
            this._marker.remove();
            this._sm.completeSave();
            this._applyFilters();
            this._wireSiteClicksForEditMode();
            this._renderEditPanel(this._sm.state);
            if (lat != null) this._map.setView([lat, lng], this._map.getZoom());
        }

        // -------------------------------------------------------------------------
        // Save operations
        // -------------------------------------------------------------------------
        _saveSiteCoordinates() {
            const sm = this._sm;
            const ps = sm.pendingSite;
            if (!ps) return;

            const lat = _roundCoord(parseFloat(document.getElementById('editLat').value));
            const lng = _roundCoord(parseFloat(document.getElementById('editLng').value));
            if (isNaN(lat) || isNaN(lng)) { this._showError('Invalid coordinates.'); return; }

            sm.beginSave();
            this._renderEditPanel(sm.state);

            const idStr    = ps.id.toString();
            const existing = this._allSitesById.get(idStr);

            this._api.updateSiteCoordinates(ps.id, lat, lng)
                .then(() => {
                    if (existing) {
                        existing.lat = lat;
                        existing.lng = lng;
                        this._allSegments.forEach(seg => {
                            if (seg.site_a && seg.site_a.id === ps.id) { seg.site_a.lat = lat; seg.site_a.lng = lng; }
                            if (seg.site_b && seg.site_b.id === ps.id) { seg.site_b.lat = lat; seg.site_b.lng = lng; }
                        });
                        this._allCircuits.forEach(circ => {
                            if (circ.site_a && circ.site_a.id === ps.id) { circ.site_a.lat = lat; circ.site_a.lng = lng; }
                            if (circ.site_b && circ.site_b.id === ps.id) { circ.site_b.lat = lat; circ.site_b.lng = lng; }
                        });
                        this._afterSiteSave(lat, lng);
                    } else {
                        return this._api.fetchSite(ps.id).then(site => {
                            const mapSite = {
                                id:     site.id,   name: site.name,   slug: site.slug || '',
                                status: site.status ? (site.status.value || site.status) : 'active',
                                lat, lng,
                                url:    site.url || '',
                                region: site.region || null,   tenant: site.tenant || null,
                                tags:   site.tags   || [],
                            };
                            this._allSites.push(mapSite);
                            this._allSitesById.set(idStr, mapSite);
                            sm.unpositionedSites = sm.unpositionedSites.filter(s => s.id !== ps.id);
                            this._afterSiteSave(lat, lng);
                        });
                    }
                })
                .catch(err => { sm.failSave(err.message); this._renderEditPanel(sm.state); });
        }

        _submitNewSiteForm() {
            const sm  = this._sm;
            const name = (document.getElementById('newSiteName').value || '').trim();
            const slug = (document.getElementById('newSiteSlug').value || '').trim();
            const lat  = _roundCoord(parseFloat(document.getElementById('newSiteLat').value));
            const lng  = _roundCoord(parseFloat(document.getElementById('newSiteLng').value));

            if (!name || !slug) { this._showError('Name and slug are required.'); return; }
            if (isNaN(lat) || isNaN(lng)) { this._showError('Invalid coordinates.'); return; }

            sm.beginSave();
            this._renderEditPanel(sm.state);

            this._api.createSite(name, slug, lat, lng)
                .then(site => {
                    const mapSite = {
                        id: site.id, name: site.name, slug: site.slug,
                        status: site.status ? site.status.value || site.status : 'active',
                        lat: parseFloat(site.latitude), lng: parseFloat(site.longitude),
                        url: `/dcim/sites/${site.id}/`, region: null, tenant: null, tags: [],
                    };
                    this._allSites.push(mapSite);
                    this._allSitesById.set(site.id.toString(), mapSite);
                    this._afterSiteSave(mapSite.lat, mapSite.lng);
                })
                .catch(err => { sm.failSave(err.message); this._renderEditPanel(sm.state); });
        }

        _submitNewSegmentForm() {
            const sm   = this._sm;
            const conn = sm.pendingConnection;
            const name      = (document.getElementById('newSegName').value || '').trim();
            const segType   = document.getElementById('newSegType').value;
            const provider  = Number(document.getElementById('newSegProvider').value);
            const ownership = document.getElementById('newSegOwnership').value;
            const status    = document.getElementById('newSegStatus').value;

            if (!name)     { this._showError('Name is required.'); return; }
            if (!provider) { this._showError('Provider is required.'); return; }
            if (!conn || !conn.siteA || !conn.siteB) { this._showError('Both sites must be selected.'); return; }

            sm.beginSave();
            this._renderEditPanel(sm.state);

            this._api.createSegment({ name, segment_type: segType, provider, ownership_type: ownership, status,
                                      site_a: conn.siteA.id, site_b: conn.siteB.id })
                .then(seg => this._api.fetchSegment(seg.id))
                .then(seg => {
                    const mapSeg = _segmentToMapShape(seg);
                    this._patchSiteCoords(mapSeg);
                    this._allSegments.push(mapSeg);
                    this._removePreview();
                    sm.completeSave();
                    this._applyFilters();
                    this._wireConnectionClicksForEditMode();
                    this._zoomToMidpoint(conn.siteA, conn.siteB);
                })
                .catch(err => { sm.failSave(err.message); this._renderEditPanel(sm.state); });
        }

        _submitNewCircuitForm() {
            const sm   = this._sm;
            const conn = sm.pendingConnection;
            const cid      = (document.getElementById('newCircCid').value || '').trim();
            const provider = Number(document.getElementById('newCircProvider').value);
            const type     = Number(document.getElementById('newCircType').value);

            if (!cid)      { this._showError('Circuit ID is required.'); return; }
            if (!provider) { this._showError('Provider is required.'); return; }
            if (!type)     { this._showError('Circuit type is required.'); return; }
            if (!conn || !conn.siteA || !conn.siteB) { this._showError('Both sites must be selected.'); return; }

            sm.beginSave();
            this._renderEditPanel(sm.state);

            this._api.createCircuit({ cid, provider, type, siteA: conn.siteA.id, siteB: conn.siteB.id })
                .then(circ => this._api.fetchCircuit(circ.id))
                .then(circ => {
                    const mapCirc = _circuitToMapShape(circ);
                    this._patchSiteCoords(mapCirc);
                    this._allCircuits.push(mapCirc);
                    this._removePreview();
                    sm.completeSave();
                    this._applyFilters();
                    this._wireConnectionClicksForEditMode();
                    this._zoomToMidpoint(conn.siteA, conn.siteB);
                })
                .catch(err => { sm.failSave(err.message); this._renderEditPanel(sm.state); });
        }

        _saveReplacementSite() {
            const sm   = this._sm;
            const conn = sm.pendingConnection;
            if (!conn || !conn.pendingReplacementSite) return;

            const site = conn.pendingReplacementSite;
            const end  = conn.endToChange;
            sm.confirmReplacement();
            sm.beginSave();

            const promise = conn.objectType === 'segment'
                ? this._api.updateSegmentEndpoint(conn.existingId, end, site.id)
                : this._api.updateCircuitTerminationSite(
                    end === 'a' ? conn.termA?.termination_pk : conn.termZ?.termination_pk,
                    site.id
                  );

            promise.then(() => {
                let updatedObj = null;
                if (conn.objectType === 'segment') {
                    const seg = this._allSegments.find(s => s.id === conn.existingId);
                    if (seg) {
                        if (end === 'a') seg.site_a = site; else seg.site_b = site;
                        updatedObj = seg;
                    }
                } else {
                    const circ = this._allCircuits.find(c => c.id === conn.existingId);
                    if (circ) {
                        if (end === 'a') { circ.site_a = site; if (circ.term_a) circ.term_a.site = site.name; }
                        else             { circ.site_b = site; if (circ.term_z) circ.term_z.site = site.name; }
                        updatedObj = circ;
                    }
                }
                sm.completeSave();
                this._applyFilters();
                this._wireSiteClicksForEditMode();
                this._wireConnectionClicksForEditMode();
                if (updatedObj) {
                    if (conn.objectType === 'segment') this._buildSegCard(updatedObj);
                    else                               this._buildCircCard(updatedObj);
                }
            }).catch(err => { sm.failSave(err.message); this._renderEditPanel(sm.state); });
        }

        // -------------------------------------------------------------------------
        // Misc helpers
        // -------------------------------------------------------------------------
        _showError(msg) {
            const panel = document.getElementById('editModePanel');
            if (!panel) return;
            panel.querySelector('.edit-mode-error')?.remove();
            const el = document.createElement('div');
            el.className = 'alert alert-danger py-1 small mt-2 edit-mode-error';
            el.textContent = msg;
            panel.appendChild(el);
        }
    }

    // -------------------------------------------------------------------------
    // Module-level pure helpers
    // -------------------------------------------------------------------------
    function _esc(str) {
        return String(str || '')
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function _card(title, body) {
        return `<div class="card">` +
               `<div class="card-header py-2 fw-bold small">${title}</div>` +
               `<div class="card-body p-2" style="font-size:0.8rem;">${body}</div>` +
               `</div>`;
    }

    function _instruction(icon, text) {
        return _card(
            `<i class="mdi ${icon}"></i> Edit Mode`,
            `<div class="text-center py-3 small text-muted">` +
            `<i class="mdi ${icon} mdi-48px d-block mb-2"></i>${text}` +
            `<div class="mt-2"><kbd>Esc</kbd> to cancel</div></div>`
        );
    }

    function _formField(label, id, type, value, required) {
        const req = required ? ' <span class="text-danger">*</span>' : '';
        return `<div class="mb-1"><label class="form-label mb-0 small" for="${id}">${label}${req}</label>` +
               `<input type="${type}" id="${id}" class="form-control form-control-sm"` +
               (value !== undefined && value !== '' ? ` value="${_esc(String(value))}"` : '') + `></div>`;
    }

    function _segmentToMapShape(seg) {
        return {
            id:                  seg.id,
            name:                seg.name,
            segment_type:        seg.segment_type,
            status:              (seg.status && seg.status.value) || seg.status || 'active',
            ownership_type:      (seg.ownership_type && seg.ownership_type.value) || seg.ownership_type || '',
            has_path_data:       !!(seg.path_geometry),
            provider:            seg.provider ? (seg.provider.name || seg.provider) : null,
            provider_id:         seg.provider ? (seg.provider.id || null) : null,
            provider_segment_id: seg.provider_segment_id || null,
            path_length_km:      seg.path_length_km || null,
            site_a:              seg.site_a ? { id: seg.site_a.id, name: seg.site_a.name,
                                                lat: parseFloat(seg.site_a.latitude),
                                                lng: parseFloat(seg.site_a.longitude) } : null,
            site_b:              seg.site_b ? { id: seg.site_b.id, name: seg.site_b.name,
                                                lat: parseFloat(seg.site_b.latitude),
                                                lng: parseFloat(seg.site_b.longitude) } : null,
            tags:                seg.tags || [],
            url:                 `/plugins/cesnet-service-path-plugin/segments/${seg.id}/`,
            map_url:             `/plugins/cesnet-service-path-plugin/segments/${seg.id}/map/`,
            type_data:           null,
        };
    }

    function _circuitToMapShape(circ) {
        const termA = circ.termination_a || null;
        const termZ = circ.termination_z || null;
        const siteA = termA ? (termA.termination || termA.site || null) : null;
        const siteZ = termZ ? (termZ.termination || termZ.site || null) : null;
        return {
            id:               circ.id,
            cid:              circ.cid,
            provider:         circ.provider ? (circ.provider.name || circ.provider) : null,
            provider_id:      circ.provider ? (circ.provider.id || null) : null,
            status:           (circ.status && circ.status.value) || circ.status || 'active',
            type:             circ.type ? (circ.type.name || circ.type) : null,
            type_id:          circ.type ? (circ.type.id || null) : null,
            tenant:           circ.tenant ? (circ.tenant.name || circ.tenant) : null,
            install_date:     circ.install_date || null,
            termination_date: circ.termination_date || null,
            tags:             circ.tags || [],
            term_a:           termA ? { termination_pk: termA.id, site: siteA ? siteA.name : null } : null,
            term_z:           termZ ? { termination_pk: termZ.id, site: siteZ ? siteZ.name : null } : null,
            site_a:           siteA ? { id: siteA.id, name: siteA.name,
                                        lat: parseFloat(siteA.latitude),
                                        lng: parseFloat(siteA.longitude) } : null,
            site_b:           siteZ ? { id: siteZ.id, name: siteZ.name,
                                        lat: parseFloat(siteZ.latitude),
                                        lng: parseFloat(siteZ.longitude) } : null,
            url:              `/circuits/circuits/${circ.id}/`,
        };
    }

    root.EditModeUI = EditModeUI;

}(typeof globalThis !== 'undefined' ? globalThis : window));
