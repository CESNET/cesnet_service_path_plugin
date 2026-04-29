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
 *   object_map.js globals:
 *     map, allSites, allSegments, allCircuits,
 *     allSitesById, allSegmentsById, allCircuitsById,
 *     renderSites, renderSegments, renderCircuits,
 *     buildSiteInfoCard, buildSegmentInfoCard, buildCircuitInfoCard,
 *     showInfoCard, hideInfoCard, siteLayers, segmentLayers, circuitLayers
 *
 * Instantiated at the bottom of object_map.js when _mapData.canEdit === true.
 */

(function (root) {
    'use strict';

    const S = EditModeStateMachine.STATES;

    // -------------------------------------------------------------------------
    // Slug auto-generation (mirrors NetBox behaviour)
    // NetBox DecimalField for lat/lng allows max 8 significant digits.
    // 6 decimal places (~11 cm precision) fits comfortably within that limit.
    function _roundCoord(v) { return Math.round(v * 1e6) / 1e6; }

    // -------------------------------------------------------------------------
    function slugify(str) {
        return str
            .toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .trim()
            .replace(/[\s_]+/g, '-')
            .replace(/-+/g, '-');
    }

    // -------------------------------------------------------------------------
    // Simple event bus used to communicate between object_map and this module
    // -------------------------------------------------------------------------
    const _editEvents = { _handlers: {} };
    _editEvents.on = function (name, fn) {
        if (!this._handlers[name]) this._handlers[name] = [];
        this._handlers[name].push(fn);
    };
    _editEvents.emit = function (name, data) {
        (_editEvents._handlers[name] || []).forEach(fn => fn(data));
    };

    // -------------------------------------------------------------------------
    // Module init — called once from object_map.js
    // -------------------------------------------------------------------------
    class EditModeUI {
        constructor(map, allSitesArr, allSegmentsArr, allCircuitsArr,
                    allSitesByIdMap, renderSitesFn, renderSegmentsFn, renderCircuitsFn,
                    buildSiteInfoCardFn, buildSegmentInfoCardFn, buildCircuitInfoCardFn,
                    showInfoCardFn, hideInfoCardFn, siteLayersMap, segmentLayersMap,
                    applyFiltersFn, circuitLayersMap, handleLineClickFn, findNearbySegmentsFn) {

            this._map            = map;
            this._allSites       = allSitesArr;
            this._allSegments    = allSegmentsArr;
            this._allCircuits    = allCircuitsArr;
            this._allSitesById   = allSitesByIdMap;
            this._renderSites    = renderSitesFn;
            this._renderSegments = renderSegmentsFn;
            this._renderCircuits = renderCircuitsFn;
            this._applyFilters   = applyFiltersFn || renderSitesFn;
            this._buildSiteCard  = buildSiteInfoCardFn;
            this._buildSegCard   = buildSegmentInfoCardFn;
            this._buildCircCard  = buildCircuitInfoCardFn;
            this._showInfoCard   = showInfoCardFn;
            this._hideInfoCard   = hideInfoCardFn;
            this._siteLayers     = siteLayersMap;
            this._segmentLayers  = segmentLayersMap;
            this._circuitLayers      = circuitLayersMap || new Map();
            this._handleLineClick    = handleLineClickFn || null;
            this._findNearbySegments = findNearbySegmentsFn || null;
            this._editSegMapHandler  = null;   // map-level click handler for segment selection

            this._sm      = new EditModeStateMachine(_editEvents);
            this._api     = new EditModeApi();
            this._marker  = new EditModeMarker(map);
            this._preview = null;   // dashed Leaflet Polyline for connection preview

            // Edit-mode highlight tracking — distinct from read-mode highlight
            this._editHL = null;    // { layer, style } — currently highlighted layer

            this._init();
        }

        // -------------------------------------------------------------------------
        // Initialisation
        // -------------------------------------------------------------------------
        _init() {
            // Listen for state changes and re-render the right panel accordingly
            _editEvents.on('editModeStateChanged', ev => {
                this._onStateChanged(ev.state, ev.prev);
            });
            _editEvents.on('editModeSitePositionUpdated', ev => {
                this._onPositionUpdated(ev.lat, ev.lng);
            });
            _editEvents.on('editModeSaveFailed', ev => {
                this._showError(ev.message);
            });

            // Escape key — global
            document.addEventListener('keydown', e => {
                if (e.key === 'Escape') this._sm.escape();
            });

            // Wire the toolbar toggle button
            const toggleBtn = document.getElementById('editModeToggle');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', () => {
                    if (this._sm.state === S.VIEW) {
                        this._enterEditMode();
                    } else {
                        this._sm.exitEditMode();
                    }
                });
            }

            // Map click — context-sensitive
            this._map.on('click', e => {
                this._onMapClick(e.latlng.lat, e.latlng.lng);
            });
        }

        // -------------------------------------------------------------------------
        // Enter edit mode — load reference data first
        // -------------------------------------------------------------------------
        _enterEditMode() {
            const toggleBtn = document.getElementById('editModeToggle');
            if (toggleBtn) {
                toggleBtn.disabled = true;
                toggleBtn.innerHTML = '<i class="mdi mdi-loading mdi-spin"></i> Loading…';
            }
            this._api.loadReferenceData().then(refData => {
                this._sm.enterEditMode(refData);
                // Pre-select the object that was showing in the info card before edit mode was entered
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
        // State change handler — drives all panel and cursor changes
        // -------------------------------------------------------------------------
        _onStateChanged(state, prev) {
            // Toolbar button label
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

            // Cursor on the map container
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

            // Show/hide filter sidebar vs edit panel
            const filterSidebar = document.getElementById('filterSidebar');
            const editPanel     = document.getElementById('editModePanel');
            if (state === S.VIEW) {
                if (filterSidebar) filterSidebar.style.display = '';
                if (editPanel)     editPanel.style.display     = 'none';
                this._marker.remove();
                this._removePreview();
                this._makeAllSitesNonDraggable();
                this._clearEditHighlight();
            } else {
                if (filterSidebar) filterSidebar.style.display = 'none';
                if (editPanel)     editPanel.style.display     = '';
                if (state === S.EDIT_IDLE) this._clearEditHighlight();
                this._renderEditPanel(state);
            }

            // Re-wire site click listeners for edit mode site selection
            if (state !== S.VIEW) {
                this._wireSiteClicksForEditMode();
            } else {
                this._wireSiteClicksForReadMode();
            }

            // Re-wire segment/circuit clicks
            if (state !== S.VIEW) {
                this._wireConnectionClicksForEditMode();
            } else {
                this._wireConnectionClicksForReadMode();
            }
        }

        // -------------------------------------------------------------------------
        // Render the edit panel content based on state
        // -------------------------------------------------------------------------
        _renderEditPanel(state) {
            const sm    = this._sm;
            const panel = document.getElementById('editModePanel');
            if (!panel) return;

            let html = '';

            switch (state) {

            case S.EDIT_IDLE:
                html = this._renderIdlePanel();
                break;

            case S.SITE_SELECTED:
                html = this._renderSiteSelectedPanel();
                break;

            case S.PLACING_UNPOSITIONED: {
                const name = sm.pendingSite ? sm.pendingSite.name : '';
                html = _instruction('mdi-map-marker-plus', `Click on the map to place <strong>${_esc(name)}</strong>`);
                break;
            }

            case S.PLACING_NEW_SITE:
                html = _instruction('mdi-map-marker-plus', 'Click on the map to place a new site marker');
                break;

            case S.NEW_SITE_FORM:
                html = this._renderNewSiteForm();
                break;

            case S.PICKING_SEGMENT_START:
                html = _instruction('mdi-vector-polyline', 'Click <strong>site A</strong> on the map to start a new segment');
                break;

            case S.PICKING_SEGMENT_END: {
                const aName = sm.pendingConnection && sm.pendingConnection.siteA ? sm.pendingConnection.siteA.name : '?';
                html = _instruction('mdi-vector-polyline',
                    `Site A: <strong>${_esc(aName)}</strong><br>Now click <strong>site B</strong> on the map`);
                break;
            }

            case S.NEW_SEGMENT_FORM:
                html = this._renderNewSegmentForm();
                break;

            case S.PICKING_CIRCUIT_START:
                html = _instruction('mdi-transit-connection-variant', 'Click <strong>site A</strong> on the map to start a new circuit');
                break;

            case S.PICKING_CIRCUIT_END: {
                const caName = sm.pendingConnection && sm.pendingConnection.siteA ? sm.pendingConnection.siteA.name : '?';
                html = _instruction('mdi-transit-connection-variant',
                    `Site A: <strong>${_esc(caName)}</strong><br>Now click <strong>site B</strong> on the map`);
                break;
            }

            case S.NEW_CIRCUIT_FORM:
                html = this._renderNewCircuitForm();
                break;

            case S.EDITING_CONNECTION:
                html = this._renderEditConnectionPanel();
                break;

            case S.PICKING_REPLACEMENT_SITE: {
                const endLabel = sm.pendingConnection && sm.pendingConnection.endToChange === 'a' ? 'A' : 'B';
                html = _instruction('mdi-cursor-pointer', `Click the new <strong>site ${endLabel}</strong> on the map`);
                break;
            }
            }

            panel.innerHTML = html;
            this._bindEditPanelEvents(state);
        }

        // -------------------------------------------------------------------------
        // Panel HTML builders
        // -------------------------------------------------------------------------

        _renderIdlePanel() {
            const sm    = this._sm;
            const sites = sm.unpositionedSites;
            let listHtml;

            if (sites.length === 0) {
                listHtml = '<div class="text-muted small">All sites have GPS coordinates.</div>';
            } else {
                listHtml =
                    '<input type="search" id="unposSearch" class="form-control form-control-sm mb-1" placeholder="Search…" autocomplete="off">' +
                    '<div id="unpositionedList" style="overflow-y:auto; max-height:320px;">' +
                    sites.map(s =>
                        `<div class="list-row py-1 px-1 border-bottom" data-site-id="${s.id}" ` +
                        `style="cursor:pointer; font-size:0.78rem;" title="Click to place on map">` +
                        `<i class="mdi mdi-map-marker-off text-muted me-1"></i>${_esc(s.name)}` +
                        `</div>`
                    ).join('') +
                    '</div>';
            }

            return _card(
                '<i class="mdi mdi-pencil"></i> Edit Mode',
                '<div class="mb-2">' +
                '<div class="text-muted small mb-1 fw-bold text-uppercase" style="font-size:0.68rem;">Actions</div>' +
                '<div class="d-grid gap-1">' +
                '<button id="btnAddNewSite"     class="btn btn-outline-primary  btn-sm"><i class="mdi mdi-map-marker-plus"></i> Add new site</button>' +
                '<button id="btnNewSegment"     class="btn btn-outline-success  btn-sm"><i class="mdi mdi-vector-polyline-plus"></i> New segment</button>' +
                '<button id="btnNewCircuit"     class="btn btn-outline-warning  btn-sm"><i class="mdi mdi-transit-connection-variant"></i> New circuit</button>' +
                '</div></div>' +
                '<hr class="my-1">' +
                `<div class="text-muted small mb-1 fw-bold text-uppercase" style="font-size:0.68rem;">` +
                `<i class="mdi mdi-map-marker-off"></i> Sites without GPS (${sites.length})` +
                '</div>' +
                listHtml
            );
        }

        _renderSiteSelectedPanel() {
            const sm  = this._sm;
            const ps  = sm.pendingSite;
            if (!ps) return '';
            const isNew     = ps.isNew;
            const title     = isNew ? 'New site' : _esc(ps.name);
            const saveLabel = isNew ? 'Save &amp; open full form' : 'Save coordinates';

            return _card(
                `<i class="mdi mdi-map-marker-check"></i> ${title}`,
                '<div class="mb-2">' +
                '<div class="mb-1"><label class="form-label mb-0 small">Latitude</label>' +
                `<input type="number" id="editLat" class="form-control form-control-sm" step="0.000001" value="${ps.currentLat || ''}"></div>` +
                '<div class="mb-2"><label class="form-label mb-0 small">Longitude</label>' +
                `<input type="number" id="editLng" class="form-control form-control-sm" step="0.000001" value="${ps.currentLng || ''}"></div>` +
                (sm.saveError ? `<div class="alert alert-danger py-1 small mb-2">${_esc(sm.saveError)}</div>` : '') +
                '<div class="d-flex gap-1">' +
                `<button id="btnSaveSite" class="btn btn-primary btn-sm flex-fill"${sm.isSaving ? ' disabled' : ''}>` +
                (sm.isSaving ? '<i class="mdi mdi-loading mdi-spin"></i> Saving…' : `<i class="mdi mdi-content-save"></i> ${saveLabel}`) +
                '</button>' +
                '<button id="btnCancelSite" class="btn btn-outline-secondary btn-sm">Cancel</button>' +
                '</div></div>'
            );
        }

        _renderNewSiteForm() {
            const sm  = this._sm;
            const ps  = sm.pendingSite;
            const lat = ps ? ps.currentLat : '';
            const lng = ps ? ps.currentLng : '';

            return _card(
                '<i class="mdi mdi-map-marker-plus"></i> New Site',
                '<form id="newSiteForm" autocomplete="off">' +
                _formField('Name', 'newSiteName', 'text', '', true) +
                _formField('Slug', 'newSiteSlug', 'text', '', true) +
                _formField('Latitude',  'newSiteLat', 'number', lat) +
                _formField('Longitude', 'newSiteLng', 'number', lng) +
                (sm.saveError ? `<div class="alert alert-danger py-1 small mb-2">${_esc(sm.saveError)}</div>` : '') +
                '<div class="d-flex gap-1 mb-1">' +
                `<button type="submit" class="btn btn-primary btn-sm flex-fill"${sm.isSaving ? ' disabled' : ''}>` +
                (sm.isSaving ? '<i class="mdi mdi-loading mdi-spin"></i> Saving…' : '<i class="mdi mdi-content-save"></i> Create site') +
                '</button>' +
                '<button type="button" id="btnCancelNewSite" class="btn btn-outline-secondary btn-sm">Cancel</button>' +
                '</div>' +
                '<a href="/dcim/sites/add/" target="_blank" class="btn btn-outline-secondary btn-sm w-100">' +
                '<i class="mdi mdi-open-in-new"></i> Open full form</a>' +
                '</form>'
            );
        }

        _renderNewSegmentForm() {
            const sm        = this._sm;
            const conn      = sm.pendingConnection;
            const siteAName = conn && conn.siteA ? _esc(conn.siteA.name) : '—';
            const siteBName = conn && conn.siteB ? _esc(conn.siteB.name) : '—';

            const providerOptions = sm.providers.map(p =>
                `<option value="${p.id}">${_esc(p.name)}</option>`
            ).join('');

            return _card(
                '<i class="mdi mdi-vector-polyline-plus"></i> New Segment',
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
                '<option value="leased" selected>Leased</option>' +
                '<option value="owned">Owned</option>' +
                '<option value="shared">Shared</option>' +
                '<option value="foreign">Foreign</option>' +
                '</select></div>' +
                '<div class="mb-2"><label class="form-label mb-0 small">Status</label>' +
                '<select id="newSegStatus" class="form-select form-select-sm">' +
                '<option value="active" selected>Active</option>' +
                '<option value="planned">Planned</option>' +
                '<option value="offline">Offline</option>' +
                '<option value="decommissioned">Decommissioned</option>' +
                '<option value="surveyed">Surveyed</option>' +
                '</select></div>' +
                `<div class="mb-1 small"><strong>Site A:</strong> ${siteAName}</div>` +
                `<div class="mb-2 small"><strong>Site B:</strong> ${siteBName}</div>` +
                (sm.saveError ? `<div class="alert alert-danger py-1 small mb-2">${_esc(sm.saveError)}</div>` : '') +
                '<div class="d-flex gap-1 mb-1">' +
                `<button type="submit" class="btn btn-primary btn-sm flex-fill"${sm.isSaving ? ' disabled' : ''}>` +
                (sm.isSaving ? '<i class="mdi mdi-loading mdi-spin"></i> Saving…' : '<i class="mdi mdi-content-save"></i> Create segment') +
                '</button>' +
                '<button type="button" id="btnCancelNewSeg" class="btn btn-outline-secondary btn-sm">Cancel</button>' +
                '</div>' +
                '<a href="/plugins/cesnet-service-path-plugin/segments/add/" target="_blank" class="btn btn-outline-secondary btn-sm w-100">' +
                '<i class="mdi mdi-open-in-new"></i> Open full form</a>' +
                '</form>'
            );
        }

        _renderNewCircuitForm() {
            const sm        = this._sm;
            const conn      = sm.pendingConnection;
            const siteAName = conn && conn.siteA ? _esc(conn.siteA.name) : '—';
            const siteBName = conn && conn.siteB ? _esc(conn.siteB.name) : '—';

            const providerOptions = sm.providers.map(p =>
                `<option value="${p.id}">${_esc(p.name)}</option>`
            ).join('');
            const typeOptions = sm.circuitTypes.map(t =>
                `<option value="${t.id}">${_esc(t.name)}</option>`
            ).join('');

            return _card(
                '<i class="mdi mdi-transit-connection-variant"></i> New Circuit',
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
                '</button>' +
                '<button type="button" id="btnCancelNewCirc" class="btn btn-outline-secondary btn-sm">Cancel</button>' +
                '</div>' +
                '<a href="/circuits/circuits/add/" target="_blank" class="btn btn-outline-secondary btn-sm w-100">' +
                '<i class="mdi mdi-open-in-new"></i> Open full form</a>' +
                '</form>'
            );
        }

        _renderEditConnectionPanel() {
            const sm      = this._sm;
            const conn    = sm.pendingConnection;
            if (!conn) return '';
            const isSegment = conn.objectType === 'segment';
            const icon      = isSegment ? 'mdi-vector-polyline' : 'mdi-transit-connection-variant';
            const siteAName = conn.siteA ? _esc(conn.siteA.name) : '—';
            const siteBName = conn.siteB ? _esc(conn.siteB.name) : '—';

            return _card(
                `<i class="mdi ${icon}"></i> Edit endpoints`,
                '<div class="mb-2 small">' +
                '<div class="mb-1 d-flex align-items-center justify-content-between">' +
                `<span><strong>Site A:</strong> ${siteAName}</span>` +
                '<button id="btnChangeEndA" class="btn btn-outline-primary btn-sm py-0">Change</button>' +
                '</div>' +
                '<div class="d-flex align-items-center justify-content-between">' +
                `<span><strong>Site B:</strong> ${siteBName}</span>` +
                '<button id="btnChangeEndB" class="btn btn-outline-primary btn-sm py-0">Change</button>' +
                '</div></div>' +
                (sm.saveError ? `<div class="alert alert-danger py-1 small mb-2">${_esc(sm.saveError)}</div>` : '') +
                '<button id="btnCancelEditConn" class="btn btn-outline-secondary btn-sm w-100">Cancel</button>'
            );
        }

        // -------------------------------------------------------------------------
        // Bind panel event handlers after innerHTML is set
        // -------------------------------------------------------------------------
        _bindEditPanelEvents(state) {
            const sm = this._sm;

            const on = (id, event, fn) => {
                const el = document.getElementById(id);
                if (el) el.addEventListener(event, fn);
            };

            switch (state) {

            case S.EDIT_IDLE:
                on('btnAddNewSite', 'click', () => sm.beginPlacingNewSite());
                on('btnNewSegment', 'click', () => sm.beginNewSegment());
                on('btnNewCircuit', 'click', () => sm.beginNewCircuit());

                // Unpositioned site list click
                {
                    const list = document.getElementById('unpositionedList');
                    if (list) {
                        list.addEventListener('click', e => {
                            const row = e.target.closest('.list-row');
                            if (!row) return;
                            const siteId = Number(row.dataset.siteId);
                            const site   = sm.unpositionedSites.find(s => s.id === siteId);
                            if (site) sm.beginPlacingUnpositioned(site);
                        });
                    }

                    // Unpositioned site search
                    const search = document.getElementById('unposSearch');
                    if (search) {
                        search.addEventListener('input', function () {
                            const q = this.value.toLowerCase();
                            document.querySelectorAll('#unpositionedList .list-row').forEach(row => {
                                row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
                            });
                        });
                    }
                }
                break;

            case S.SITE_SELECTED:
                // Live lat/lng inputs update both the marker position and state machine
                on('editLat', 'input', e => {
                    const lat = parseFloat(e.target.value);
                    const lng = parseFloat(document.getElementById('editLng').value);
                    if (!isNaN(lat) && !isNaN(lng)) {
                        this._marker.moveTo(lat, lng);
                        sm.updateSitePosition(lat, lng);
                    }
                });
                on('editLng', 'input', e => {
                    const lat = parseFloat(document.getElementById('editLat').value);
                    const lng = parseFloat(e.target.value);
                    if (!isNaN(lat) && !isNaN(lng)) {
                        this._marker.moveTo(lat, lng);
                        sm.updateSitePosition(lat, lng);
                    }
                });
                on('btnSaveSite',   'click', () => this._saveSiteCoordinates());
                on('btnCancelSite', 'click', () => {
                    this._marker.remove();
                    sm.escape();
                });
                break;

            case S.NEW_SITE_FORM: {
                // Slug auto-generation
                on('newSiteName', 'input', function () {
                    const slugEl = document.getElementById('newSiteSlug');
                    if (slugEl && !slugEl.dataset.userEdited) {
                        slugEl.value = slugify(this.value);
                    }
                });
                on('newSiteSlug', 'input', function () {
                    this.dataset.userEdited = '1';
                });
                // Marker drag updates lat/lng inputs
                const latInput = document.getElementById('newSiteLat');
                const lngInput = document.getElementById('newSiteLng');
                this._marker.remove();
                const ps = sm.pendingSite;
                if (ps) {
                    this._marker.place(ps.currentLat, ps.currentLng, (lat, lng) => {
                        lat = _roundCoord(lat);
                        lng = _roundCoord(lng);
                        if (latInput) latInput.value = lat.toFixed(6);
                        if (lngInput) lngInput.value = lng.toFixed(6);
                        sm.updateSitePosition(lat, lng);
                    });
                }
                on('newSiteLat', 'input', function () {
                    const lat = parseFloat(this.value);
                    const lng = parseFloat(document.getElementById('newSiteLng').value);
                    if (!isNaN(lat) && !isNaN(lng)) this._marker.moveTo(lat, lng);
                }.bind(this));
                on('newSiteLng', 'input', function () {
                    const lat = parseFloat(document.getElementById('newSiteLat').value);
                    const lng = parseFloat(this.value);
                    if (!isNaN(lat) && !isNaN(lng)) this._marker.moveTo(lat, lng);
                }.bind(this));
                const newSiteForm = document.getElementById('newSiteForm');
                if (newSiteForm) {
                    newSiteForm.addEventListener('submit', e => {
                        e.preventDefault();
                        this._submitNewSiteForm();
                    });
                }
                on('btnCancelNewSite', 'click', () => {
                    this._marker.remove();
                    sm.escape();
                });
                break;
            }

            case S.NEW_SEGMENT_FORM: {
                const newSegForm = document.getElementById('newSegmentForm');
                if (newSegForm) {
                    newSegForm.addEventListener('submit', e => {
                        e.preventDefault();
                        this._submitNewSegmentForm();
                    });
                }
                on('btnCancelNewSeg', 'click', () => {
                    this._removePreview();
                    sm.escape();
                });
                break;
            }

            case S.NEW_CIRCUIT_FORM: {
                const newCircForm = document.getElementById('newCircuitForm');
                if (newCircForm) {
                    newCircForm.addEventListener('submit', e => {
                        e.preventDefault();
                        this._submitNewCircuitForm();
                    });
                }
                on('btnCancelNewCirc', 'click', () => {
                    this._removePreview();
                    sm.escape();
                });
                break;
            }

            case S.EDITING_CONNECTION:
                on('btnChangeEndA',     'click', () => sm.beginChangingEnd('a'));
                on('btnChangeEndB',     'click', () => sm.beginChangingEnd('b'));
                on('btnCancelEditConn', 'click', () => sm.escape());
                break;
            }
        }

        // -------------------------------------------------------------------------
        // Position update — called when marker is dragged in site_selected
        // -------------------------------------------------------------------------
        _onPositionUpdated(lat, lng) {
            const latEl = document.getElementById('editLat');
            const lngEl = document.getElementById('editLng');
            if (latEl) latEl.value = lat.toFixed(6);
            if (lngEl) lngEl.value = lng.toFixed(6);
        }

        // -------------------------------------------------------------------------
        // Map click handler
        // -------------------------------------------------------------------------
        _onMapClick(lat, lng) {
            const sm    = this._sm;
            const state = sm.state;
            lat = _roundCoord(lat);
            lng = _roundCoord(lng);

            if (state === S.PLACING_UNPOSITIONED) {
                this._marker.place(lat, lng, (dlat, dlng) => {
                    sm.updateSitePosition(_roundCoord(dlat), _roundCoord(dlng));
                });
                sm.placeUnpositionedSite(lat, lng);
                // Now in site_selected — place draggable marker
                this._marker.place(lat, lng, (dlat, dlng) => {
                    sm.updateSitePosition(_roundCoord(dlat), _roundCoord(dlng));
                });
            } else if (state === S.PLACING_NEW_SITE) {
                sm.placeNewSite(lat, lng);
                // new_site_form state — marker placed by _bindEditPanelEvents
            }
            // PICKING_* states are handled by site/connection click wiring
        }

        // -------------------------------------------------------------------------
        // Site click wiring
        // -------------------------------------------------------------------------
        // -------------------------------------------------------------------------
        // Edit-mode layer highlight — vivid green, distinct from read-mode orange
        // -------------------------------------------------------------------------
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
            } else if (type === 'segment') {
                layer = this._segmentLayers.get(id.toString());
                if (layer) {
                    const first = (layer instanceof L.Polyline) ? layer : (() => { let f; layer.eachLayer(l => { if (!f) f = l; }); return f; })();
                    const o = first ? first.options : {};
                    restoreStyle = { color: o.color, weight: o.weight, opacity: o.opacity };
                    hlStyle      = { color: '#ffff00', weight: 7, opacity: 1 };
                }
            } else if (type === 'circuit') {
                layer = this._circuitLayers.get(id.toString());
                if (layer) {
                    const o = layer.options;
                    restoreStyle = { color: o.color, weight: o.weight, opacity: o.opacity };
                    hlStyle      = { color: '#ffff00', weight: 6, opacity: 1 };
                }
            }
            if (!layer || !hlStyle) return;
            this._editHL = { layer, restoreStyle };
            if (layer instanceof L.CircleMarker || layer instanceof L.Polyline) {
                layer.setStyle(hlStyle);
            } else if (layer.eachLayer) {
                layer.eachLayer(sub => { if (sub.setStyle) sub.setStyle(hlStyle); });
            }
        }

        _clearEditHighlight() {
            if (!this._editHL) return;
            const { layer, restoreStyle } = this._editHL;
            this._editHL = null;
            if (layer instanceof L.CircleMarker || layer instanceof L.Polyline) {
                layer.setStyle(restoreStyle);
            } else if (layer.eachLayer) {
                layer.eachLayer(sub => { if (sub.setStyle) sub.setStyle(restoreStyle); });
            }
        }

        _wireSiteClicksForEditMode() {
            const sm = this._sm;
            this._siteLayers.forEach((marker, idStr) => {
                marker.off('click');
                marker.on('click', e => {
                    L.DomEvent.stopPropagation(e);
                    const site  = this._allSitesById.get(idStr);
                    const state = sm.state;

                    if (state === S.EDIT_IDLE || state === S.SITE_SELECTED) {
                        // Select site for coordinate editing
                        if (!site) return;
                        if (state === S.SITE_SELECTED) sm.escape(); // back to EDIT_IDLE first
                        this._marker.place(site.lat, site.lng, (lat, lng) => {
                            sm.updateSitePosition(_roundCoord(lat), _roundCoord(lng));
                        });
                        sm.selectSite(site);
                        this._buildSiteCard(site);
                        this._applyEditHighlight('site', site.id);

                    } else if (state === S.PICKING_SEGMENT_START) {
                        if (!site) return;
                        sm.pickSegmentSiteA(site);

                    } else if (state === S.PICKING_SEGMENT_END) {
                        if (!site) return;
                        sm.pickSegmentSiteB(site);
                        this._drawPreview(sm.pendingConnection.siteA, site);

                    } else if (state === S.PICKING_CIRCUIT_START) {
                        if (!site) return;
                        sm.pickCircuitSiteA(site);

                    } else if (state === S.PICKING_CIRCUIT_END) {
                        if (!site) return;
                        sm.pickCircuitSiteB(site);
                        this._drawPreview(sm.pendingConnection.siteA, site);

                    } else if (state === S.PICKING_REPLACEMENT_SITE) {
                        if (!site) return;
                        this._saveReplacementSite(site);
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
        // Segment / circuit click wiring
        // -------------------------------------------------------------------------
        _wireConnectionClicksForEditMode() {
            const sm = this._sm;

            // Remove per-layer segment handlers — selection is handled by the map-level handler below
            this._segmentLayers.forEach(layer => layer.off('click'));

            // Map-level segment click: use proximity scan so overlapping segments show a pick popup
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
                    // Show a compact pick popup identical in style to read-mode overlap popup
                    const segById = new Map(nearby.map(({ seg }) => [seg.id, seg]));
                    let html = `<div><strong>${nearby.length} segments here</strong>
                        <div style="font-size:0.78rem;color:#555;">Click a name to select for editing</div>`;
                    nearby.forEach(({ seg }) => {
                        html += `<hr style="margin:4px 0;">
                        <div>
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
                        const el = popup.getElement();
                        if (!el) return;
                        el.querySelectorAll('.seg-edit-pick').forEach(span => {
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

            // Circuits — per-layer is fine, circuits don't overlap like path segments
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
            // Remove the edit-mode map-level segment handler
            if (this._editSegMapHandler) {
                this._map.off('click', this._editSegMapHandler);
                this._editSegMapHandler = null;
            }
            // Restore original segment click behaviour — proximity scan + overlap popup
            this._segmentLayers.forEach(layer => {
                layer.off('click');
                if (this._handleLineClick) layer.on('click', this._handleLineClick);
            });
            // Restore circuit click behaviour
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
            if (this._preview) {
                this._preview.remove();
                this._preview = null;
            }
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
            if (isNaN(lat) || isNaN(lng)) {
                this._showError('Invalid coordinates.');
                return;
            }

            sm.beginSave();
            this._renderEditPanel(sm.state);   // re-render to show spinner

            const idStr    = ps.id.toString();
            const existing = this._allSitesById.get(idStr);

            this._api.updateSiteCoordinates(ps.id, lat, lng)
                .then(updated => {
                    if (existing) {
                        // Existing positioned site — update coordinates in place
                        existing.lat = lat;
                        existing.lng = lng;
                        // Update nested site coords in all segments and circuits that reference this site
                        this._allSegments.forEach(seg => {
                            if (seg.site_a && seg.site_a.id === ps.id) { seg.site_a.lat = lat; seg.site_a.lng = lng; }
                            if (seg.site_b && seg.site_b.id === ps.id) { seg.site_b.lat = lat; seg.site_b.lng = lng; }
                        });
                        this._allCircuits.forEach(circ => {
                            if (circ.site_a && circ.site_a.id === ps.id) { circ.site_a.lat = lat; circ.site_a.lng = lng; }
                            if (circ.site_b && circ.site_b.id === ps.id) { circ.site_b.lat = lat; circ.site_b.lng = lng; }
                        });
                        this._marker.remove();
                        sm.completeSave();
                        this._applyFilters();
                        this._wireSiteClicksForEditMode();
                        this._renderEditPanel(sm.state);
                    } else {
                        // Unpositioned site — fetch full data then promote into dataset
                        return this._api.fetchSite(ps.id).then(site => {
                            const mapSite = {
                                id:     site.id,
                                name:   site.name,
                                slug:   site.slug || '',
                                status: site.status ? (site.status.value || site.status) : 'active',
                                lat,
                                lng,
                                url:    site.url || '',
                                region: site.region || null,
                                tenant: site.tenant || null,
                                tags:   site.tags   || [],
                            };
                            this._allSites.push(mapSite);
                            this._allSitesById.set(idStr, mapSite);
                            // Remove from unpositioned list so the panel count is correct
                            sm.unpositionedSites = sm.unpositionedSites.filter(s => s.id !== ps.id);
                            this._marker.remove();
                            sm.completeSave();
                            // applyFilters re-reads allSites, so the new site is included
                            this._applyFilters();
                            this._wireSiteClicksForEditMode();
                            this._renderEditPanel(sm.state);
                            this._map.setView([lat, lng], this._map.getZoom());
                        });
                    }
                })
                .catch(err => {
                    sm.failSave(err.message);
                    this._renderEditPanel(sm.state);
                });
        }

        _submitNewSiteForm() {
            const sm = this._sm;

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
                    // Add to in-memory dataset in the shape the map expects
                    const mapSite = {
                        id:     site.id,
                        name:   site.name,
                        slug:   site.slug,
                        status: site.status ? site.status.value || site.status : 'active',
                        lat:    parseFloat(site.latitude),
                        lng:    parseFloat(site.longitude),
                        url:    site.url,
                        region: null,
                        tenant: null,
                        tags:   [],
                    };
                    this._allSites.push(mapSite);
                    this._allSitesById.set(site.id.toString(), mapSite);
                    this._marker.remove();
                    sm.completeSave();
                    this._applyFilters();
                    this._wireSiteClicksForEditMode();
                    this._map.setView([mapSite.lat, mapSite.lng], this._map.getZoom());
                })
                .catch(err => {
                    sm.failSave(err.message);
                    this._renderEditPanel(sm.state);
                });
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

            this._api.createSegment({
                name,
                segment_type:   segType,
                provider,
                ownership_type: ownership,
                status,
                site_a:         conn.siteA.id,
                site_b:         conn.siteB.id,
            }).then(seg => this._api.fetchSegment(seg.id))
              .then(seg => {
                const mapSeg = _segmentToMapShape(seg);
                // Brief site serializer has no lat/lng — look up from local site index
                const sa = mapSeg.site_a && this._allSitesById.get(mapSeg.site_a.id.toString());
                const sb = mapSeg.site_b && this._allSitesById.get(mapSeg.site_b.id.toString());
                if (sa) { mapSeg.site_a.lat = sa.lat; mapSeg.site_a.lng = sa.lng; }
                if (sb) { mapSeg.site_b.lat = sb.lat; mapSeg.site_b.lng = sb.lng; }
                this._allSegments.push(mapSeg);
                this._removePreview();
                sm.completeSave();
                this._applyFilters();
                this._wireConnectionClicksForEditMode();
                if (conn.siteA && conn.siteB) {
                    const midLat = (conn.siteA.lat + conn.siteB.lat) / 2;
                    const midLng = (conn.siteA.lng + conn.siteB.lng) / 2;
                    this._map.setView([midLat, midLng], this._map.getZoom());
                }
            }).catch(err => {
                sm.failSave(err.message);
                this._renderEditPanel(sm.state);
            });
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

            this._api.createCircuit({
                cid, provider, type,
                siteA: conn.siteA.id,
                siteB: conn.siteB.id,
            }).then(circ => this._api.fetchCircuit(circ.id))
              .then(circ => {
                const mapCirc = _circuitToMapShape(circ);
                // Brief site serializer has no lat/lng — look up from local site index
                const sa = mapCirc.site_a && this._allSitesById.get(mapCirc.site_a.id.toString());
                const sb = mapCirc.site_b && this._allSitesById.get(mapCirc.site_b.id.toString());
                if (sa) { mapCirc.site_a.lat = sa.lat; mapCirc.site_a.lng = sa.lng; }
                if (sb) { mapCirc.site_b.lat = sb.lat; mapCirc.site_b.lng = sb.lng; }
                this._allCircuits.push(mapCirc);
                this._removePreview();
                sm.completeSave();
                this._applyFilters();
                this._wireConnectionClicksForEditMode();
                if (conn.siteA && conn.siteB) {
                    const midLat = (conn.siteA.lat + conn.siteB.lat) / 2;
                    const midLng = (conn.siteA.lng + conn.siteB.lng) / 2;
                    this._map.setView([midLat, midLng], this._map.getZoom());
                }
            }).catch(err => {
                sm.failSave(err.message);
                this._renderEditPanel(sm.state);
            });
        }

        _saveReplacementSite(site) {
            const sm   = this._sm;
            const conn = sm.pendingConnection;
            if (!conn) return;

            const end = conn.endToChange;
            sm.pickReplacementSite(site);   // updates conn.siteA/B, returns to editing_connection

            sm.beginSave();

            let promise;
            if (conn.objectType === 'segment') {
                promise = this._api.updateSegmentEndpoint(conn.existingId, end, site.id);
            } else {
                const termPk = end === 'a'
                    ? (conn.termA && conn.termA.termination_pk)
                    : (conn.termZ && conn.termZ.termination_pk);
                promise = this._api.updateCircuitTerminationSite(termPk, site.id);
            }

            promise.then(() => {
                // Update in-memory dataset
                let updatedObj = null;
                if (conn.objectType === 'segment') {
                    const seg = this._allSegments.find(s => s.id === conn.existingId);
                    if (seg) {
                        if (end === 'a') seg.site_a = site;
                        else             seg.site_b = site;
                        updatedObj = seg;
                    }
                } else {
                    const circ = this._allCircuits.find(c => c.id === conn.existingId);
                    if (circ) {
                        if (end === 'a') {
                            circ.site_a = site;
                            if (circ.term_a) circ.term_a.site = site.name;
                        } else {
                            circ.site_b = site;
                            if (circ.term_z) circ.term_z.site = site.name;
                        }
                        updatedObj = circ;
                    }
                }
                sm.completeSave();
                this._applyFilters();
                this._wireSiteClicksForEditMode();
                this._wireConnectionClicksForEditMode();
                // Refresh the info card to show the updated endpoint
                if (updatedObj) {
                    if (conn.objectType === 'segment') this._buildSegCard(updatedObj);
                    else                               this._buildCircCard(updatedObj);
                }
            }).catch(err => {
                sm.failSave(err.message);
                this._renderEditPanel(sm.state);
            });
        }

        // -------------------------------------------------------------------------
        // Helpers
        // -------------------------------------------------------------------------

        _showError(msg) {
            const panel = document.getElementById('editModePanel');
            if (!panel) return;
            const existing = panel.querySelector('.edit-mode-error');
            if (existing) existing.remove();
            const el = document.createElement('div');
            el.className = 'alert alert-danger py-1 small mt-2 edit-mode-error';
            el.textContent = msg;
            panel.appendChild(el);
        }

        _makeAllSitesNonDraggable() {
            // CircleMarkers are never draggable — nothing to do.
            // The draggable marker (EditModeMarker) is removed separately.
        }
    }

    // -------------------------------------------------------------------------
    // Module-level helpers (not on the class — no `this` needed)
    // -------------------------------------------------------------------------

    function _esc(str) {
        return String(str || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
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

    // Convert DRF segment response to the shape object_map.js expects
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
            url:                 seg.url || '',
            map_url:             seg.url ? seg.url.replace('/api/plugins/', '/plugins/').replace(/\/$/, '/map/') : '',
            type_data:           null,
        };
    }

    // Convert DRF circuit response to the shape object_map.js expects
    function _circuitToMapShape(circ) {
        const termA = circ.termination_a || null;
        const termZ = circ.termination_z || null;
        // NetBox >= 4.x uses termination (GFK) instead of the old site field
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
            url:              circ.url || '',
        };
    }

    root.EditModeUI = EditModeUI;

}(typeof globalThis !== 'undefined' ? globalThis : window));
