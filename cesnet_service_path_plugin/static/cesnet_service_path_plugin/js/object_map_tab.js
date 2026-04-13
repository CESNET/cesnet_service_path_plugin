/**
 * object_map_tab.js — Network Map embedded in a Site / Region tab
 *
 * Reads data from the JSON blob injected by network_map_tab_card.html.
 * Applies an initial filter from data-prefilter on the map div (server-set),
 * then lets the user toggle layers and change colour schemes — no filter panel.
 *
 * Globals expected from the template before this script loads:
 *   map          — L.Map instance (created inline in the template, id "tab-map")
 *   initializeLayerSwitching(map)  — from map_layers_config.html
 */

(function () {
    'use strict';

    // -------------------------------------------------------------------------
    // Data
    // -------------------------------------------------------------------------
    const _mapData        = JSON.parse(document.getElementById('tab-map-data').textContent);
    const allSites        = _mapData.sites;
    const allSegments     = _mapData.segments;
    const allCircuits     = _mapData.circuits;
    const regionAncestors = _mapData.regionAncestors;
    const mapBounds       = _mapData.mapBounds;
    const apiUrl          = _mapData.apiUrl;

    // Pre-filter seeded by the server (e.g. {"at_any_site": [42]} or {"region_id": [7]})
    const _prefilterEl = document.getElementById('tab-map-prefilter');
    const prefilter    = _prefilterEl ? JSON.parse(_prefilterEl.textContent) : {};

    // Retrieve the L.Map instance stored on the element by the inline template script
    const _mapEl = document.getElementById('tab-map');
    const map = _mapEl._leaflet_map;

    // -------------------------------------------------------------------------
    // Region descendant index
    // -------------------------------------------------------------------------
    const regionDescendants = {};
    Object.entries(regionAncestors).forEach(([ridStr, ancestors]) => {
        const rid = Number(ridStr);
        ancestors.forEach(aid => {
            if (!regionDescendants[aid]) regionDescendants[aid] = new Set();
            regionDescendants[aid].add(rid);
        });
    });

    // -------------------------------------------------------------------------
    // Color constants — Segments
    // -------------------------------------------------------------------------
    const segmentStatusColors = {
        'Active':          '#198754',
        'Planned':         '#ff8c00',
        'Offline':         '#dc3545',
        'Decommissioned':  '#6c757d',
        'Surveyed':        '#3b82f6',
    };
    const segmentStatusBadge = {
        'Active':          'success',
        'Planned':         'warning',
        'Offline':         'danger',
        'Decommissioned':  'secondary',
        'Surveyed':        'info',
    };
    const segmentTypeColors = {
        'Dark Fiber':       '#9c27b0',
        'Optical Spectrum': '#ff9800',
        'Ethernet Service': '#4caf50',
    };
    const ownershipTypeColors = {
        'Owned':   '#198754',
        'Leased':  '#0d6efd',
        'Shared':  '#fd7e14',
        'Foreign': '#dc3545',
    };

    // -------------------------------------------------------------------------
    // Color constants — Circuits
    // -------------------------------------------------------------------------
    const circuitStatusColors = {
        'Active':          '#198754',
        'Planned':         '#ff8c00',
        'Provisioning':    '#3b82f6',
        'Offline':         '#dc3545',
        'Deprovisioning':  '#fd7e14',
        'Decommissioned':  '#6c757d',
    };
    const circuitStatusBadge = {
        'Active':          'success',
        'Planned':         'warning',
        'Provisioning':    'info',
        'Offline':         'danger',
        'Deprovisioning':  'warning',
        'Decommissioned':  'secondary',
    };

    // -------------------------------------------------------------------------
    // Color constants — Sites
    // -------------------------------------------------------------------------
    const siteStatusColors = {
        'Active':          '#198754',
        'Planned':         '#ff8c00',
        'Staging':         '#3b82f6',
        'Decommissioning': '#fd7e14',
        'Retired':         '#6c757d',
    };
    const siteStatusBadge = {
        'Active':          'success',
        'Planned':         'warning',
        'Staging':         'info',
        'Decommissioning': 'warning',
        'Retired':         'secondary',
    };

    const colorPalette = [
        '#d32f2f','#1976d2','#512da8','#f57c00','#7b1fa2','#c2185b','#303f9f',
        '#00796b','#455a64','#ff1744','#00bcd4','#e64a19','#5d4037','#3f51b5',
        '#9c27b0','#ff5722','#b71c1c','#0d47a1','#ad1457','#4a148c',
    ];

    // -------------------------------------------------------------------------
    // State
    // -------------------------------------------------------------------------
    const providerColors        = {};
    const tenantColors          = {};
    const regionColors          = {};
    const circuitProviderColors = {};
    const circuitTypeColors     = {};

    let segmentScheme = 'status';
    let siteScheme    = 'status';
    let circuitScheme = 'status';
    const visibility  = { segments: true, sites: true, circuits: false };

    function buildPalette(items, store) {
        const unique = [...new Set(items.filter(Boolean))];
        unique.forEach((v, i) => { if (!store[v]) store[v] = colorPalette[i % colorPalette.length]; });
    }
    buildPalette(allSegments.map(s => s.provider), providerColors);
    buildPalette(allSites.map(s => s.tenant),       tenantColors);
    buildPalette(allSites.map(s => s.region),        regionColors);
    buildPalette(allCircuits.map(c => c.provider),   circuitProviderColors);
    buildPalette(allCircuits.map(c => c.type),        circuitTypeColors);

    // -------------------------------------------------------------------------
    // Color resolvers
    // -------------------------------------------------------------------------
    function getSegmentColor(seg) {
        switch (segmentScheme) {
            case 'status':         return segmentStatusColors[seg.status]         || '#6c757d';
            case 'provider':       return providerColors[seg.provider]            || '#6c757d';
            case 'segment_type':   return segmentTypeColors[seg.segment_type]     || '#6c757d';
            case 'ownership_type': return ownershipTypeColors[seg.ownership_type] || '#6c757d';
            default:               return '#6c757d';
        }
    }
    function getSiteColor(site) {
        switch (siteScheme) {
            case 'status': return siteStatusColors[site.status] || '#6c757d';
            case 'tenant': return tenantColors[site.tenant]     || '#6c757d';
            case 'region': return regionColors[site.region]     || '#6c757d';
            default:       return '#6c757d';
        }
    }
    function getCircuitColor(circ) {
        switch (circuitScheme) {
            case 'status':   return circuitStatusColors[circ.status]     || '#6c757d';
            case 'provider': return circuitProviderColors[circ.provider] || '#6c757d';
            case 'type':     return circuitTypeColors[circ.type]         || '#6c757d';
            default:         return '#6c757d';
        }
    }

    // -------------------------------------------------------------------------
    // Legend
    // -------------------------------------------------------------------------
    function buildLegendSection(title, colorMap) {
        const items = Object.entries(colorMap).map(([label, color]) =>
            `<li><span class="dropdown-item-text small">` +
            `<span style="display:inline-block;width:16px;height:3px;background:${color};margin-right:6px;vertical-align:middle;border-radius:1px;"></span>${label}` +
            `</span></li>`
        ).join('');
        return `<li><h6 class="dropdown-header">${title}</h6></li>${items}`;
    }

    function updateLegend() {
        const el = document.getElementById('tab-legendDropdown');
        if (!el) return;
        const segColors = segmentScheme === 'status' ? segmentStatusColors :
                          segmentScheme === 'provider' ? providerColors :
                          segmentScheme === 'segment_type' ? segmentTypeColors :
                          segmentScheme === 'ownership_type' ? ownershipTypeColors : {};
        const siteColors = siteScheme === 'status' ? siteStatusColors :
                           siteScheme === 'tenant' ? tenantColors :
                           siteScheme === 'region' ? regionColors : {};
        const circColors = circuitScheme === 'status' ? circuitStatusColors :
                           circuitScheme === 'provider' ? circuitProviderColors :
                           circuitScheme === 'type' ? circuitTypeColors : {};
        let html = '';
        if (visibility.segments) {
            const label = { status: 'Status', provider: 'Provider', segment_type: 'Segment Type', ownership_type: 'Ownership' }[segmentScheme];
            html += buildLegendSection(`Segments — ${label}`, segColors);
        }
        if (visibility.circuits) {
            if (html) html += '<li><hr class="dropdown-divider"></li>';
            const label = { status: 'Status', provider: 'Provider', type: 'Type' }[circuitScheme];
            html += buildLegendSection(`Circuits — ${label}`, circColors);
        }
        if (visibility.sites) {
            if (html) html += '<li><hr class="dropdown-divider"></li>';
            const label = { status: 'Status', tenant: 'Tenant', region: 'Region' }[siteScheme];
            html += buildLegendSection(`Sites — ${label}`, siteColors);
        }
        if (!html) html = '<li><span class="dropdown-item-text small text-muted">No layers visible</span></li>';
        html += `<li><hr class="dropdown-divider"></li>
                 <li><span class="dropdown-item-text small"><strong>Solid:</strong> actual path &nbsp;<strong>Dashed:</strong> no path data / circuit</span></li>`;
        el.innerHTML = html;
    }

    // -------------------------------------------------------------------------
    // Colour scheme switching
    // -------------------------------------------------------------------------
    function switchSegmentScheme(scheme) {
        segmentScheme = scheme;
        const labels = { status: 'Status', provider: 'Provider', segment_type: 'Segment Type', ownership_type: 'Ownership' };
        const el = document.getElementById('tab-segmentSchemeName');
        if (el) el.textContent = labels[scheme] || scheme;
        segmentLayers.forEach((layer, sid) => {
            const seg = allSegments.find(s => s.id.toString() === sid);
            if (!seg) return;
            const color = getSegmentColor(seg);
            if (layer instanceof L.Polyline) { layer.setStyle({ color }); }
            else if (layer.eachLayer) { layer.eachLayer(sub => { if (sub.setStyle) sub.setStyle({ color }); }); }
        });
        updateLegend();
    }
    function switchSiteScheme(scheme) {
        siteScheme = scheme;
        const labels = { status: 'Status', tenant: 'Tenant', region: 'Region' };
        const el = document.getElementById('tab-siteSchemeName');
        if (el) el.textContent = labels[scheme] || scheme;
        siteLayers.forEach((marker, sid) => {
            const site = allSites.find(s => s.id.toString() === sid);
            if (!site) return;
            marker.setStyle({ fillColor: getSiteColor(site) });
        });
        updateLegend();
    }
    function switchCircuitScheme(scheme) {
        circuitScheme = scheme;
        circuitLayers.forEach((layer, cid) => {
            const circ = allCircuits.find(c => c.id.toString() === cid);
            if (!circ) return;
            if (layer instanceof L.Polyline) layer.setStyle({ color: getCircuitColor(circ) });
        });
        updateLegend();
    }

    // -------------------------------------------------------------------------
    // Layer visibility toggle
    // -------------------------------------------------------------------------
    const toggleStyles = {
        segments: ['btn-success',  'btn-outline-success'],
        sites:    ['btn-primary',  'btn-outline-primary'],
        circuits: ['btn-warning',  'btn-outline-warning'],
    };
    function toggleLayer(type, btn) {
        visibility[type] = !visibility[type];
        const group = type === 'segments' ? segmentPathGroup : type === 'circuits' ? circuitGroup : siteGroup;
        const [onCls, offCls] = toggleStyles[type];
        if (visibility[type]) {
            group.addTo(map);
            btn.classList.replace(offCls, onCls);
            btn.title = `Hide ${type}`;
        } else {
            map.removeLayer(group);
            btn.classList.replace(onCls, offCls);
            btn.title = `Show ${type}`;
        }
        if (type === 'segments' || type === 'circuits') renderSites();
        updateLegend();
    }

    // -------------------------------------------------------------------------
    // Filtering helpers
    // -------------------------------------------------------------------------
    function siteInRegions(siteRegionId, filterRegionIds) {
        if (!siteRegionId) return false;
        return filterRegionIds.some(fid => {
            const desc = regionDescendants[fid];
            return desc && desc.has(siteRegionId);
        });
    }

    // -------------------------------------------------------------------------
    // Prefilter application
    // prefilter keys: "at_any_site" → array of site PKs
    //                 "region_id"   → array of region PKs
    // -------------------------------------------------------------------------
    function applyPrefilter() {
        const atSites   = (prefilter.at_any_site || []).map(Number);
        const atRegions = (prefilter.region_id   || []).map(Number);

        if (!atSites.length && !atRegions.length) return; // no pre-filter — show all

        // Filter sites
        activeSites = allSites.filter(site => {
            if (atSites.length   && (atSites.includes(site.id))) return true;
            if (atRegions.length && siteInRegions(site.region_id, atRegions)) return true;
            return false;
        });

        const activeSiteIds = new Set(activeSites.map(s => s.id));

        // Filter segments: at least one endpoint in active sites
        activeSegments = allSegments.filter(seg => {
            const siteAIn = seg.site_a && activeSiteIds.has(seg.site_a.id);
            const siteBIn = seg.site_b && activeSiteIds.has(seg.site_b.id);
            return siteAIn || siteBIn;
        });

        // Filter circuits: at least one endpoint in active sites
        activeCircuits = allCircuits.filter(circ => {
            const siteAIn = circ.site_a && activeSiteIds.has(circ.site_a.id);
            const siteBIn = circ.site_b && activeSiteIds.has(circ.site_b.id);
            return siteAIn || siteBIn;
        });
    }

    // -------------------------------------------------------------------------
    // Active subsets
    // -------------------------------------------------------------------------
    let activeSites    = allSites.slice();
    let activeSegments = allSegments.slice();
    let activeCircuits = allCircuits.slice();

    // Apply server-supplied prefilter before first render
    applyPrefilter();

    // -------------------------------------------------------------------------
    // Leaflet layer groups
    // -------------------------------------------------------------------------
    const segmentPathGroup = L.layerGroup().addTo(map);
    const circuitGroup     = L.layerGroup();   // hidden by default
    const siteGroup        = L.layerGroup().addTo(map);

    const segmentLayers = new Map();
    const siteLayers    = new Map();
    const circuitLayers = new Map();

    // -------------------------------------------------------------------------
    // Site rendering
    // -------------------------------------------------------------------------
    function buildSiteSegmentIndex() {
        const index = {};
        activeSegments.forEach(seg => {
            [seg.site_a, seg.site_b].forEach(s => {
                if (!s) return;
                if (!index[s.id]) index[s.id] = [];
                index[s.id].push({ name: seg.name, url: seg.url });
            });
        });
        return index;
    }
    function buildSiteCircuitIndex() {
        const index = {};
        activeCircuits.forEach(circ => {
            [circ.site_a, circ.site_b].forEach(s => {
                if (!s) return;
                if (!index[s.id]) index[s.id] = [];
                index[s.id].push({ name: circ.cid, url: circ.url });
            });
        });
        return index;
    }

    function renderSites() {
        siteGroup.clearLayers();
        siteLayers.clear();
        const siteSegmentIndex = buildSiteSegmentIndex();
        const siteCircuitIndex = buildSiteCircuitIndex();
        const renderedIds = new Set();

        function addSiteMarker(id, name, lat, lng, siteObj) {
            if (renderedIds.has(id)) return;
            renderedIds.add(id);
            const color  = siteObj ? getSiteColor(siteObj) : '#6c757d';
            const marker = L.circleMarker([lat, lng], {
                radius: 7, fillColor: color, color: '#fff',
                weight: 2, opacity: 1, fillOpacity: 0.9,
            });
            let html = `<strong>Site: ${name}</strong>`;
            if (siteObj) {
                const badge = siteStatusBadge[siteObj.status] || 'secondary';
                html += `<br><span class="badge text-bg-${badge}">${siteObj.status}</span>`;
                if (siteObj.region) html += `<br><small>Region: ${siteObj.region}</small>`;
                if (siteObj.tenant) html += `<br><small>Tenant: ${siteObj.tenant}</small>`;
                html += `<br><a href="${siteObj.url}" class="small">View site</a>`;
            }
            const relatedSegs = siteSegmentIndex[id] || [];
            if (relatedSegs.length) {
                html += `<hr class="my-1"><small><strong>Segments (${relatedSegs.length}):</strong><br>`;
                html += relatedSegs.slice(0, 10).map(s => `<a href="${s.url}">${s.name}</a>`).join('<br>');
                if (relatedSegs.length > 10) html += `<br>… and ${relatedSegs.length - 10} more`;
                html += `</small>`;
            }
            const relatedCircs = siteCircuitIndex[id] || [];
            if (relatedCircs.length) {
                html += `<hr class="my-1"><small><strong>Circuits (${relatedCircs.length}):</strong><br>`;
                html += relatedCircs.slice(0, 10).map(c => `<a href="${c.url}">${c.name}</a>`).join('<br>');
                if (relatedCircs.length > 10) html += `<br>… and ${relatedCircs.length - 10} more`;
                html += `</small>`;
            }
            marker.bindPopup(html, { maxWidth: 280 });
            siteGroup.addLayer(marker);
            siteLayers.set(id.toString(), marker);
        }

        const siteById = {};
        activeSites.forEach(s => {
            siteById[s.id] = s;
            addSiteMarker(s.id, s.name, s.lat, s.lng, s);
        });
        if (visibility.segments) {
            activeSegments.forEach(seg => {
                [seg.site_a, seg.site_b].forEach(s => {
                    if (s && !renderedIds.has(s.id)) addSiteMarker(s.id, s.name, s.lat, s.lng, siteById[s.id] || null);
                });
            });
        }
        if (visibility.circuits) {
            activeCircuits.forEach(circ => {
                [circ.site_a, circ.site_b].forEach(s => {
                    if (s && !renderedIds.has(s.id)) addSiteMarker(s.id, s.name, s.lat, s.lng, siteById[s.id] || null);
                });
            });
        }
    }

    // -------------------------------------------------------------------------
    // Segment rendering
    // -------------------------------------------------------------------------
    function distanceToSegmentScreen(p, a, b) {
        const ax = b.x - a.x, ay = b.y - a.y;
        const t  = Math.max(0, Math.min(1, ((p.x - a.x) * ax + (p.y - a.y) * ay) / (ax * ax + ay * ay || 1)));
        const dx = p.x - (a.x + t * ax), dy = p.y - (a.y + t * ay);
        return Math.sqrt(dx * dx + dy * dy);
    }
    function polylineNearPoint(polyline, screenPt, tol) {
        const lls  = polyline.getLatLngs();
        const flat = Array.isArray(lls[0]) ? lls.flat() : lls;
        for (let i = 0; i < flat.length - 1; i++) {
            const a = map.latLngToContainerPoint(flat[i]);
            const b = map.latLngToContainerPoint(flat[i + 1]);
            if (distanceToSegmentScreen(screenPt, a, b) <= tol) return true;
        }
        return false;
    }
    function findNearbySegments(e) {
        const screenPt = map.latLngToContainerPoint(e.latlng);
        const nearby = [];
        segmentLayers.forEach((layer, sid) => {
            const seg = activeSegments.find(s => s.id.toString() === sid);
            if (!seg) return;
            let near = false;
            if (layer instanceof L.Polyline) near = polylineNearPoint(layer, screenPt, 10);
            else if (layer.eachLayer) layer.eachLayer(sub => { if (sub instanceof L.Polyline) near = near || polylineNearPoint(sub, screenPt, 10); });
            if (near) nearby.push({ layer, seg });
        });
        return nearby;
    }
    function showSegmentPopup(seg, latlng) {
        const sc = segmentStatusBadge[seg.status] || 'secondary';
        const len = seg.path_length_km ? seg.path_length_km + ' km' : 'unknown';
        L.popup({ maxWidth: 320 }).setLatLng(latlng).setContent(
            `<strong>Segment: ${seg.name}</strong><br>` +
            `<span class="badge text-bg-${sc}">${seg.status}</span><br>` +
            `<small>${seg.site_a ? seg.site_a.name : 'N/A'} ↔ ${seg.site_b ? seg.site_b.name : 'N/A'}</small><br>` +
            `<small>Provider: ${seg.provider || 'N/A'} · Length: ${len}</small><br>` +
            `<a href="${seg.url}" class="small">View segment</a> ` +
            `<a href="${seg.map_url}" class="small">Individual map</a>`
        ).openOn(map);
    }
    function handleLineClick(e) {
        e.originalEvent.preventDefault();
        const nearby = findNearbySegments(e);
        if (!nearby.length) return;
        if (nearby.length === 1) {
            showSegmentPopup(nearby[0].seg, e.latlng);
        } else {
            let html = `<div><strong>${nearby.length} segments here</strong>`;
            nearby.forEach(({ seg }) => {
                const sc = segmentStatusBadge[seg.status] || 'secondary';
                html += `<div class="border-top pt-1 mt-1"><a href="${seg.url}">${seg.name}</a><br>
                    <span class="badge text-bg-${sc} small">${seg.status}</span>
                    <small>${seg.site_a ? seg.site_a.name : ''} ↔ ${seg.site_b ? seg.site_b.name : ''}</small></div>`;
            });
            html += '</div>';
            L.popup({ maxWidth: 340 }).setLatLng(e.latlng).setContent(html).openOn(map);
        }
    }

    let cachedGeoFeatures = null;
    function renderSegments() {
        segmentPathGroup.clearLayers();
        segmentLayers.clear();
        const visibleIds = new Set(activeSegments.map(s => s.id));

        activeSegments.forEach(seg => {
            if (!seg.has_path_data && seg.site_a && seg.site_b) {
                const line = L.polyline(
                    [[seg.site_a.lat, seg.site_a.lng], [seg.site_b.lat, seg.site_b.lng]],
                    { color: getSegmentColor(seg), weight: 3, opacity: 0.7, dashArray: '6, 10' }
                );
                line.on('click', handleLineClick);
                segmentPathGroup.addLayer(line);
                segmentLayers.set(seg.id.toString(), line);
            }
        });

        function applyGeoFeatures(features) {
            features.forEach(feature => {
                if (feature.properties.type !== 'path') return;
                if (!visibleIds.has(feature.properties.id)) return;
                const existing = segmentLayers.get(feature.properties.id.toString());
                if (existing) segmentPathGroup.removeLayer(existing);
                const seg   = activeSegments.find(s => s.id === feature.properties.id);
                const color = seg ? getSegmentColor(seg) : '#6c757d';
                const layer = L.geoJSON(feature, { style: { color, weight: 4, opacity: 0.85 } });
                layer.on('click', handleLineClick);
                segmentPathGroup.addLayer(layer);
                segmentLayers.set(feature.properties.id.toString(), layer);
            });
            fitMap();
        }

        if (cachedGeoFeatures) {
            applyGeoFeatures(cachedGeoFeatures);
        } else {
            // Build API URL scoped to the prefilter
            let scopedApiUrl = apiUrl;
            if (prefilter.at_any_site && prefilter.at_any_site.length) {
                scopedApiUrl += (scopedApiUrl.includes('?') ? '&' : '?') +
                    prefilter.at_any_site.map(id => `at_any_site=${id}`).join('&');
            }
            fetch(scopedApiUrl)
                .then(r => r.json())
                .then(data => {
                    if (!data.features) return;
                    cachedGeoFeatures = data.features;
                    applyGeoFeatures(cachedGeoFeatures);
                })
                .catch(() => fitMap());
        }
    }

    // -------------------------------------------------------------------------
    // Circuit rendering
    // -------------------------------------------------------------------------
    function renderCircuits() {
        circuitGroup.clearLayers();
        circuitLayers.clear();
        activeCircuits.forEach(circ => {
            if (!circ.site_a || !circ.site_b) return;
            const color = getCircuitColor(circ);
            const line = L.polyline(
                [[circ.site_a.lat, circ.site_a.lng], [circ.site_b.lat, circ.site_b.lng]],
                { color, weight: 3, opacity: 0.7, dashArray: '8, 5, 2, 5' }
            );
            const sc = circuitStatusBadge[circ.status] || 'secondary';
            line.bindPopup(
                `<strong>Circuit: ${circ.cid}</strong><br>` +
                `<span class="badge text-bg-${sc}">${circ.status}</span><br>` +
                `<small>${circ.site_a.name} ↔ ${circ.site_b.name}</small><br>` +
                `<small>Provider: ${circ.provider || 'N/A'} · Type: ${circ.type || 'N/A'}</small><br>` +
                `<a href="${circ.url}" class="small">View circuit</a>`,
                { maxWidth: 300 }
            );
            circuitGroup.addLayer(line);
            circuitLayers.set(circ.id.toString(), line);
        });
    }

    // -------------------------------------------------------------------------
    // Fit bounds
    // -------------------------------------------------------------------------
    function fitMap() {
        if (mapBounds.minLat === null) return;
        map.fitBounds(
            [[mapBounds.minLat, mapBounds.minLng], [mapBounds.maxLat, mapBounds.maxLng]],
            { padding: [20, 20] }
        );
    }

    // -------------------------------------------------------------------------
    // Initial render
    // -------------------------------------------------------------------------
    renderSites();
    renderSegments();
    renderCircuits();
    updateLegend();

    // -------------------------------------------------------------------------
    // Wire controls
    // -------------------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('[data-segment-scheme]').forEach(el => {
            el.addEventListener('click', e => { e.preventDefault(); switchSegmentScheme(el.getAttribute('data-segment-scheme')); });
        });
        document.querySelectorAll('[data-circuit-scheme]').forEach(el => {
            el.addEventListener('click', e => { e.preventDefault(); switchCircuitScheme(el.getAttribute('data-circuit-scheme')); });
        });
        document.querySelectorAll('[data-site-scheme]').forEach(el => {
            el.addEventListener('click', e => { e.preventDefault(); switchSiteScheme(el.getAttribute('data-site-scheme')); });
        });

        const toggleSegBtn  = document.getElementById('tab-toggleSegments');
        const toggleSiteBtn = document.getElementById('tab-toggleSites');
        const toggleCircBtn = document.getElementById('tab-toggleCircuits');
        if (toggleSegBtn)  toggleSegBtn.addEventListener('click',  () => toggleLayer('segments', toggleSegBtn));
        if (toggleSiteBtn) toggleSiteBtn.addEventListener('click', () => toggleLayer('sites',    toggleSiteBtn));
        if (toggleCircBtn) toggleCircBtn.addEventListener('click', () => toggleLayer('circuits', toggleCircBtn));

        const fitBtn = document.getElementById('tab-fitBounds');
        if (fitBtn) fitBtn.addEventListener('click', fitMap);

        initializeLayerSwitching(map);
    });

})();
