/**
 * object_map.js — Network Map (Sites + Segments + Circuits)
 *
 * Reads _mapData from the JSON blob injected by object_map.html.
 * All filtering is done client-side — no page reloads.
 * Filters are applied immediately on any change to the filter panel.
 *
 * Globals expected from the template before this script loads:
 *   map          — L.Map instance
 *   _mapData     — { sites, segments, circuits, mapBounds, mapCenter, apiUrl }
 *   initializeLayerSwitching(map)  — from map_layers_config.html
 */

(function () {
    'use strict';

    // -------------------------------------------------------------------------
    // Data — the full dataset, never mutated
    // -------------------------------------------------------------------------
    const allSites        = _mapData.sites;
    const allSegments     = _mapData.segments;
    const allCircuits     = _mapData.circuits;
    const regionAncestors = _mapData.regionAncestors; // { regionId: [ancestorIds including self] }
    const mapBounds       = _mapData.mapBounds;
    const apiUrl          = _mapData.apiUrl;

    // Pre-build reverse index: regionId → Set of all descendant region IDs (including self)
    // so "filter by region R" can quickly find all descendant IDs.
    const regionDescendants = {};  // { ancestorId: Set<descendantId> }
    Object.entries(regionAncestors).forEach(([ridStr, ancestors]) => {
        const rid = Number(ridStr);
        ancestors.forEach(aid => {
            if (!regionDescendants[aid]) regionDescendants[aid] = new Set();
            regionDescendants[aid].add(rid);
        });
    });

    // -------------------------------------------------------------------------
    // Color constants — Segments
    // No greens. Status values span maximally separated hues.
    // -------------------------------------------------------------------------
    const segmentStatusColors = {
        'Active':          '#1565c0',   // strong blue
        'Planned':         '#e65100',   // deep orange
        'Offline':         '#c62828',   // deep red
        'Decommissioned':  '#455a64',   // dark blue-grey
        'Surveyed':        '#6a1b9a',   // deep purple
    };
    const segmentStatusBadge = {
        'Active':          'success',
        'Planned':         'warning',
        'Offline':         'danger',
        'Decommissioned':  'secondary',
        'Surveyed':        'info',
    };
    const segmentTypeColors = {
        'Dark Fiber':       '#6a1b9a',   // deep purple
        'Optical Spectrum': '#e65100',   // deep orange
        'Ethernet Service': '#1565c0',   // strong blue
    };
    const ownershipTypeColors = {
        'Owned':   '#1565c0',   // strong blue
        'Leased':  '#6a1b9a',   // deep purple
        'Shared':  '#e65100',   // deep orange
        'Foreign': '#c62828',   // deep red
    };

    // -------------------------------------------------------------------------
    // Color constants — Circuits
    // Hue anchor: magenta/pink — instantly distinct from segments (blue/orange)
    // and from OSM background. No greens anywhere.
    // -------------------------------------------------------------------------
    const circuitStatusColors = {
        'Active':          '#ad1457',   // deep pink / magenta
        'Planned':         '#f9a825',   // amber
        'Provisioning':    '#0277bd',   // cerulean blue
        'Offline':         '#c62828',   // deep red
        'Deprovisioning':  '#ef6c00',   // orange
        'Decommissioned':  '#455a64',   // dark blue-grey
    };
    const circuitStatusBadge = {
        'Active':          'success',
        'Planned':         'warning',
        'Provisioning':    'info',
        'Offline':         'danger',
        'Deprovisioning':  'warning',
        'Decommissioned':  'secondary',
    };

    // Dynamic palette — provider / type / region colour-by schemes.
    // Rules: no greens, no yellows, no light colours. Maximum hue separation
    // between adjacent entries so the first ~6 picks are already very distinct.
    const colorPalette = [
        '#1565c0',   // 1  strong blue
        '#c62828',   // 2  deep red
        '#ad1457',   // 3  deep pink / magenta
        '#e65100',   // 4  deep orange
        '#4527a0',   // 5  deep purple
        '#0277bd',   // 6  cerulean
        '#880e4f',   // 7  dark magenta
        '#d84315',   // 8  burnt orange
        '#283593',   // 9  indigo
        '#b71c1c',   // 10 crimson
        '#4a148c',   // 11 violet
        '#e64a19',   // 12 vermillion
        '#0d47a1',   // 13 navy blue
        '#f57f17',   // 14 dark amber
        '#6a1b9a',   // 15 purple
        '#bf360c',   // 16 deep burnt orange
        '#1a237e',   // 17 deep indigo
        '#c2185b',   // 18 pink
        '#37474f',   // 19 slate (neutral separator)
        '#4e342e',   // 20 dark brown
    ];

    // -------------------------------------------------------------------------
    // Color constants — Sites
    // Sites are point markers — vivid, no greens.
    // -------------------------------------------------------------------------
    const siteStatusColors = {
        'Active':          '#1565c0',   // strong blue
        'Planned':         '#e65100',   // deep orange
        'Staging':         '#6a1b9a',   // deep purple
        'Decommissioning': '#ef6c00',   // orange
        'Retired':         '#455a64',   // dark blue-grey
    };
    const siteStatusBadge = {
        'Active':          'success',
        'Planned':         'warning',
        'Staging':         'info',
        'Decommissioning': 'warning',
        'Retired':         'secondary',
    };

    // -------------------------------------------------------------------------
    // State
    // -------------------------------------------------------------------------
    const providerColors      = {};
    const tenantColors        = {};
    const regionColors        = {};
    const circuitProviderColors = {};
    const circuitTypeColors     = {};

    let segmentScheme = 'status';
    let siteScheme    = 'status';
    let circuitScheme = 'status';
    const visibility  = { segments: true, sites: true, circuits: false };

    // Currently rendered (filtered) subsets
    let activeSites    = allSites.slice();
    let activeSegments = allSegments.slice();
    let activeCircuits = allCircuits.slice();

    // -------------------------------------------------------------------------
    // Leaflet layer groups
    // -------------------------------------------------------------------------
    const segmentPathGroup = L.layerGroup().addTo(map);
    const circuitGroup     = L.layerGroup();   // not added to map initially — circuits hidden by default
    const siteGroup        = L.layerGroup().addTo(map);

    // id → Leaflet layer, for re-styling without full redraw
    const segmentLayers = new Map();
    const siteLayers    = new Map();
    const circuitLayers = new Map();

    // -------------------------------------------------------------------------
    // Dynamic palette builders
    // -------------------------------------------------------------------------
    function buildPalette(items, store) {
        const unique = [...new Set(items.filter(Boolean))];
        unique.forEach((v, i) => {
            if (!store[v]) store[v] = colorPalette[i % colorPalette.length];
        });
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
            case 'status':   return circuitStatusColors[circ.status]        || '#6c757d';
            case 'provider': return circuitProviderColors[circ.provider]    || '#6c757d';
            case 'type':     return circuitTypeColors[circ.type]            || '#6c757d';
            default:         return '#6c757d';
        }
    }

    // -------------------------------------------------------------------------
    // Legend
    // -------------------------------------------------------------------------
    function buildLegendSection(title, colorMap) {
        const items = Object.entries(colorMap)
            .map(([label, color]) =>
                `<li><span class="dropdown-item-text small">` +
                `<span style="display:inline-block;width:16px;height:3px;background:${color};` +
                `margin-right:6px;vertical-align:middle;border-radius:1px;"></span>${label}` +
                `</span></li>`
            ).join('');
        return `<li><h6 class="dropdown-header">${title}</h6></li>${items}`;
    }

    function updateLegend() {
        const el = document.getElementById('legendDropdown');
        if (!el) return;

        const segColors =
            segmentScheme === 'status'         ? segmentStatusColors :
            segmentScheme === 'provider'       ? providerColors :
            segmentScheme === 'segment_type'   ? segmentTypeColors :
            segmentScheme === 'ownership_type' ? ownershipTypeColors : {};

        const siteColors =
            siteScheme === 'status' ? siteStatusColors :
            siteScheme === 'tenant' ? tenantColors :
            siteScheme === 'region' ? regionColors : {};

        const circColors =
            circuitScheme === 'status'   ? circuitStatusColors :
            circuitScheme === 'provider' ? circuitProviderColors :
            circuitScheme === 'type'     ? circuitTypeColors : {};

        let html = '';
        if (visibility.segments) {
            const label = { status: 'Status', provider: 'Provider',
                            segment_type: 'Segment Type', ownership_type: 'Ownership' }[segmentScheme];
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
                 <li><span class="dropdown-item-text small">
                   <strong>Solid:</strong> actual path &nbsp;
                   <strong>Dashed:</strong> no path data / circuit
                 </span></li>`;
        el.innerHTML = html;
    }

    // -------------------------------------------------------------------------
    // Colour scheme switching
    // -------------------------------------------------------------------------
    function switchSegmentScheme(scheme) {
        segmentScheme = scheme;
        const labels = { status: 'Status', provider: 'Provider',
                         segment_type: 'Segment Type', ownership_type: 'Ownership' };
        const el = document.getElementById('segmentSchemeName');
        if (el) el.textContent = labels[scheme] || scheme;

        segmentLayers.forEach((layer, sid) => {
            const seg = allSegments.find(s => s.id.toString() === sid);
            if (!seg) return;
            const color = getSegmentColor(seg);
            if (layer instanceof L.Polyline) {
                layer.setStyle({ color });
            } else if (layer.eachLayer) {
                layer.eachLayer(sub => { if (sub.setStyle) sub.setStyle({ color }); });
            }
        });
        updateLegend();
    }

    function switchSiteScheme(scheme) {
        siteScheme = scheme;
        const labels = { status: 'Status', tenant: 'Tenant', region: 'Region' };
        const el = document.getElementById('siteSchemeName');
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
        const labels = { status: 'Status', provider: 'Provider', type: 'Type' };
        const el = document.getElementById('circuitSchemeName');
        if (el) el.textContent = labels[scheme] || scheme;

        circuitLayers.forEach((layer, cid) => {
            const circ = allCircuits.find(c => c.id.toString() === cid);
            if (!circ) return;
            const color = getCircuitColor(circ);
            if (layer instanceof L.Polyline) {
                layer.setStyle({ color });
            }
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
        const group =
            type === 'segments' ? segmentPathGroup :
            type === 'circuits' ? circuitGroup :
            siteGroup;
        const filterSection = document.getElementById(
            type === 'segments' ? 'filterSectionSegments' :
            type === 'circuits' ? 'filterSectionCircuits' :
            'filterSectionSites'
        );
        const [onCls, offCls] = toggleStyles[type];

        if (visibility[type]) {
            group.addTo(map);
            btn.classList.replace(offCls, onCls);
            btn.title = `Hide ${type}`;
            if (filterSection) filterSection.classList.remove('d-none');
        } else {
            map.removeLayer(group);
            btn.classList.replace(onCls, offCls);
            btn.title = `Show ${type}`;
            if (filterSection) filterSection.classList.add('d-none');
        }

        // Toggling segments or circuits changes which grey anchor sites are shown,
        // so re-render the site layer to add/remove those anchors.
        if (type === 'segments' || type === 'circuits') {
            renderSites();
        }

        updateLegend();
        updateCounts();
    }

    // -------------------------------------------------------------------------
    // Client-side filtering
    // -------------------------------------------------------------------------

    /**
     * Read the current state of the filter widgets and return
     * { site, segment, circuit } filter objects with arrays of values.
     */
    function readFilters() {
        function selectValues(name) {
            const el = document.querySelector(`[name="${name}"]`);
            if (!el) return [];
            if (el.tagName === 'SELECT') {
                return Array.from(el.selectedOptions).map(o => o.value).filter(Boolean);
            }
            return [];
        }
        return {
            site: {
                region_ids:  selectValues('region_id').map(Number),
                group_ids:   selectValues('site_group_id').map(Number),
                tenant_ids:  selectValues('site_tenant_id').map(Number),
                statuses:    selectValues('site_status'),
            },
            segment: {
                region_ids:   selectValues('region_id').map(Number),
                at_any_sites: selectValues('at_any_site').map(Number),
                provider_ids: selectValues('segment_provider_id').map(Number),
                statuses:     selectValues('segment_status'),
                types:        selectValues('segment_type'),
            },
            circuit: {
                region_ids:   selectValues('region_id').map(Number),
                at_any_sites: selectValues('at_any_site').map(Number),
                provider_ids: selectValues('circuit_provider_id').map(Number),
                type_ids:     selectValues('circuit_type_id').map(Number),
                statuses:     selectValues('circuit_status'),
            },
        };
    }

    /**
     * Returns true if siteRegionId is a descendant-or-self of any of the
     * selected filterRegionIds (tree-aware, mirrors TreeNodeMultipleChoiceFilter).
     */
    function siteInRegions(siteRegionId, filterRegionIds) {
        if (!siteRegionId) return false;
        return filterRegionIds.some(fid => {
            const desc = regionDescendants[fid];
            return desc && desc.has(siteRegionId);
        });
    }

    function filterSites(filters) {
        return allSites.filter(site => {
            if (filters.region_ids.length && !siteInRegions(site.region_id, filters.region_ids)) return false;
            if (filters.group_ids.length  && !filters.group_ids.includes(site.group_id))         return false;
            if (filters.tenant_ids.length && !filters.tenant_ids.includes(site.tenant_id))       return false;
            if (filters.statuses.length) {
                const key = site.status ? site.status.toLowerCase().replace(/\s+/g, '_') : '';
                if (!filters.statuses.some(s => key === s || site.status === s)) return false;
            }
            return true;
        });
    }

    function filterSegments(filters, activeSiteIds) {
        return allSegments.filter(seg => {
            if (filters.statuses.length) {
                const key = seg.status ? seg.status.toLowerCase().replace(/\s+/g, '_') : '';
                if (!filters.statuses.some(s => key === s || seg.status === s)) return false;
            }
            if (filters.types.length) {
                const typeMap = { 'dark_fiber': 'Dark Fiber', 'optical_spectrum': 'Optical Spectrum', 'ethernet_service': 'Ethernet Service' };
                if (!filters.types.some(t => seg.segment_type === (typeMap[t] || t))) return false;
            }
            if (filters.provider_ids.length && !filters.provider_ids.includes(seg.provider_id)) return false;
            if (filters.at_any_sites.length) {
                const siteAId = seg.site_a ? seg.site_a.id : null;
                const siteBId = seg.site_b ? seg.site_b.id : null;
                if (!filters.at_any_sites.includes(siteAId) && !filters.at_any_sites.includes(siteBId)) return false;
            }
            // Region filter: segment passes if at least one endpoint site passed the site region filter
            if (filters.region_ids.length) {
                const siteAInRegion = seg.site_a && activeSiteIds.has(seg.site_a.id);
                const siteBInRegion = seg.site_b && activeSiteIds.has(seg.site_b.id);
                if (!siteAInRegion && !siteBInRegion) return false;
            }
            return true;
        });
    }

    function filterCircuits(filters, activeSiteIds) {
        return allCircuits.filter(circ => {
            if (filters.statuses.length) {
                const key = circ.status ? circ.status.toLowerCase().replace(/\s+/g, '_') : '';
                if (!filters.statuses.some(s => key === s || circ.status === s)) return false;
            }
            if (filters.provider_ids.length && !filters.provider_ids.includes(circ.provider_id)) return false;
            if (filters.type_ids.length     && !filters.type_ids.includes(circ.type_id))         return false;
            if (filters.at_any_sites.length) {
                const siteAId = circ.site_a ? circ.site_a.id : null;
                const siteBId = circ.site_b ? circ.site_b.id : null;
                if (!filters.at_any_sites.includes(siteAId) && !filters.at_any_sites.includes(siteBId)) return false;
            }
            // Region filter: circuit passes if at least one endpoint site passed the site region filter
            if (filters.region_ids.length) {
                const siteAInRegion = circ.site_a && activeSiteIds.has(circ.site_a.id);
                const siteBInRegion = circ.site_b && activeSiteIds.has(circ.site_b.id);
                if (!siteAInRegion && !siteBInRegion) return false;
            }
            return true;
        });
    }

    function applyFilters() {
        const f = readFilters();

        activeSites = filterSites(f.site);
        const activeSiteIds = new Set(activeSites.map(s => s.id));
        activeSegments = filterSegments(f.segment, activeSiteIds);
        activeCircuits = filterCircuits(f.circuit, activeSiteIds);

        renderSites();
        renderSegments();
        renderCircuits();
        updateLegend();
        updateCounts();
        updateFilterChips();
    }

    function updateCounts() {
        const cs = document.getElementById('countSites');
        const cg = document.getElementById('countSegments');
        const cc = document.getElementById('countCircuits');
        if (cs) cs.textContent = visibility.sites    ? activeSites.length    : 0;
        if (cg) cg.textContent = visibility.segments ? activeSegments.length : 0;
        if (cc) cc.textContent = visibility.circuits ? activeCircuits.length : 0;
    }

    // -------------------------------------------------------------------------
    // Active filter chips — shown below the toolbar when filters are active
    // -------------------------------------------------------------------------

    function collectActiveChips() {
        const chips = [];

        function selectedOptions(name) {
            const el = document.querySelector(`[name="${name}"]`);
            if (!el || el.tagName !== 'SELECT') return [];
            return Array.from(el.selectedOptions).map(o => ({ value: o.value, text: o.textContent.trim() }));
        }

        function deselectOption(name, value) {
            const el = document.querySelector(`[name="${name}"]`);
            if (!el) return;
            const opt = Array.from(el.options).find(o => o.value === value);
            if (opt) opt.selected = false;
            if (window.$ && $(el).data('select2')) {
                $(el).trigger('change');
            } else {
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }

        const selectFields = [
            { name: 'region_id',            prefix: 'Region' },
            { name: 'site_group_id',         prefix: 'Site Group' },
            { name: 'at_any_site',           prefix: 'Site' },
            { name: 'site_status',           prefix: 'Site status' },
            { name: 'site_tenant_id',        prefix: 'Tenant' },
            { name: 'segment_status',        prefix: 'Seg. status' },
            { name: 'segment_type',          prefix: 'Seg. type' },
            { name: 'segment_provider_id',   prefix: 'Seg. Provider' },
            { name: 'circuit_status',        prefix: 'Circ. status' },
            { name: 'circuit_provider_id',   prefix: 'Circ. Provider' },
            { name: 'circuit_type_id',       prefix: 'Circ. Type' },
        ];

        selectFields.forEach(({ name, prefix }) => {
            selectedOptions(name).forEach(({ value, text }) => {
                chips.push({
                    label: `${prefix}: ${text}`,
                    clear: () => deselectOption(name, value),
                });
            });
        });

        return chips;
    }

    function updateFilterChips() {
        const bar = document.getElementById('activeFilters');
        const countBadge = document.getElementById('filterCount');
        const clearHeaderBtn = document.getElementById('clearFiltersHeader');
        if (!bar) return;

        const chips = collectActiveChips();

        if (!chips.length) {
            bar.style.display = 'none';
            if (countBadge) countBadge.style.display = 'none';
            if (clearHeaderBtn) clearHeaderBtn.style.display = 'none';
            return;
        }

        bar.style.display = 'flex';
        if (countBadge) {
            countBadge.textContent = chips.length;
            countBadge.style.display = '';
        }
        if (clearHeaderBtn) clearHeaderBtn.style.display = '';

        bar.innerHTML = chips.map((c, i) =>
            `<span class="badge text-bg-secondary d-flex align-items-center gap-1" style="font-size:.8rem;font-weight:500;">
                ${c.label}
                <button type="button" class="btn-close btn-close-white" style="font-size:.6rem;" data-chip="${i}" aria-label="Remove filter"></button>
             </span>`
        ).join('');

        bar.querySelectorAll('[data-chip]').forEach(btn => {
            btn.addEventListener('click', () => {
                chips[Number(btn.dataset.chip)].clear();
            });
        });
    }

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
                radius:      7,
                fillColor:   color,
                color:       '#fff',
                weight:      2,
                opacity:     1,
                fillOpacity: 0.9,
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
                html += `<hr class="my-1">`;
                html += `<small><strong>Segments (${relatedSegs.length}):</strong><br>`;
                html += relatedSegs.slice(0, 10).map(s => `<a href="${s.url}">${s.name}</a>`).join('<br>');
                if (relatedSegs.length > 10) html += `<br>… and ${relatedSegs.length - 10} more`;
                html += `</small>`;
            }

            const relatedCircs = siteCircuitIndex[id] || [];
            if (relatedCircs.length) {
                html += `<hr class="my-1">`;
                html += `<small><strong>Circuits (${relatedCircs.length}):</strong><br>`;
                html += relatedCircs.slice(0, 10).map(c => `<a href="${c.url}">${c.name}</a>`).join('<br>');
                if (relatedCircs.length > 10) html += `<br>… and ${relatedCircs.length - 10} more`;
                html += `</small>`;
            }

            marker.bindPopup(html, { maxWidth: 280 });
            marker.on('click', function () {
                if (siteObj) buildSiteInfoCard(siteObj);
            });
            siteGroup.addLayer(marker);
            siteLayers.set(id.toString(), marker);
        }

        const siteById = {};
        activeSites.forEach(s => {
            siteById[s.id] = s;
            addSiteMarker(s.id, s.name, s.lat, s.lng, s);
        });

        // Segment endpoint sites not in the filtered site list — grey anchors.
        // Only rendered when segments are visible.
        if (visibility.segments) {
            activeSegments.forEach(seg => {
                [seg.site_a, seg.site_b].forEach(s => {
                    if (!s) return;
                    if (!renderedIds.has(s.id)) {
                        addSiteMarker(s.id, s.name, s.lat, s.lng, siteById[s.id] || null);
                    }
                });
            });
        }

        // Circuit endpoint sites not yet rendered — grey anchors when circuits visible.
        if (visibility.circuits) {
            activeCircuits.forEach(circ => {
                [circ.site_a, circ.site_b].forEach(s => {
                    if (!s) return;
                    if (!renderedIds.has(s.id)) {
                        addSiteMarker(s.id, s.name, s.lat, s.lng, siteById[s.id] || null);
                    }
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
        const tol = 10;
        const nearby = [];
        segmentLayers.forEach((layer, sid) => {
            const seg = activeSegments.find(s => s.id.toString() === sid);
            if (!seg) return;
            let near = false;
            if (layer instanceof L.Polyline) {
                near = polylineNearPoint(layer, screenPt, tol);
            } else if (layer.eachLayer) {
                layer.eachLayer(sub => {
                    if (sub instanceof L.Polyline) near = near || polylineNearPoint(sub, screenPt, tol);
                });
            }
            if (near) nearby.push({ layer, seg });
        });
        return nearby;
    }

    // -------------------------------------------------------------------------
    // Info card
    // -------------------------------------------------------------------------
    function showInfoCard(title, bodyHtml) {
        const card  = document.getElementById('infoCard');
        const titleEl = document.getElementById('infoCardTitle');
        const body  = document.getElementById('infoCardBody');
        if (!card) return;
        titleEl.innerHTML = title;
        body.innerHTML    = bodyHtml;
        card.style.display = '';
    }

    function hideInfoCard() {
        const card = document.getElementById('infoCard');
        if (card) card.style.display = 'none';
    }

    function _row(label, value) {
        if (value === null || value === undefined || value === '') return '';
        return `<tr><td class="text-muted pe-2" style="white-space:nowrap">${label}</td><td>${value}</td></tr>`;
    }

    function _tagTextColor(hex) {
        // Returns black or white depending on background luminance.
        const r = parseInt(hex.slice(0, 2), 16);
        const g = parseInt(hex.slice(2, 4), 16);
        const b = parseInt(hex.slice(4, 6), 16);
        // Perceived luminance (ITU-R BT.601)
        return (r * 0.299 + g * 0.587 + b * 0.114) > 150 ? '#000' : '#fff';
    }

    function _tags(tags) {
        if (!tags || !tags.length) return '';
        return tags.map(t => {
            if (typeof t === 'object' && t.color) {
                const fg = _tagTextColor(t.color);
                return `<span class="badge me-1" style="background:#${t.color};color:${fg};">${t.name}</span>`;
            }
            return `<span class="badge text-bg-secondary me-1">${typeof t === 'object' ? t.name : t}</span>`;
        }).join('');
    }

    function _table(rows) {
        const inner = rows.filter(Boolean).join('');
        if (!inner) return '';
        return `<table class="table table-sm table-borderless mb-0">${inner}</table>`;
    }

    function buildSiteInfoCard(site) {
        const badge = siteStatusBadge[site.status] || 'secondary';
        const rows = _table([
            _row('Region',    site.region  || '—'),
            _row('Status',    `<span class="badge text-bg-${badge}">${site.status}</span>`),
            _row('Tenant',    site.tenant  || '—'),
            _row('Address',   site.physical_address ? site.physical_address.replace(/\n/g, ', ') : '—'),
            _row('GPS',       `${site.lat}, ${site.lng}`),
            _row('Facility',  site.facility || '—'),
            _row('Tags',      site.tags && site.tags.length ? _tags(site.tags) : '—'),
        ]);
        const links = `<div class="mt-2"><a href="${site.url}" class="btn btn-outline-primary btn-sm w-100">
            <i class="mdi mdi-open-in-new"></i> View site</a></div>`;
        showInfoCard(
            `<i class="mdi mdi-map-marker text-primary"></i> ${site.name}`,
            rows + links
        );
    }

    function buildSegmentInfoCard(seg) {
        const sc = segmentStatusBadge[seg.status] || 'secondary';
        let rows = _table([
            _row('Provider',       seg.provider || '—'),
            _row('Provider ID',    seg.provider_segment_id || '—'),
            _row('Status',         `<span class="badge text-bg-${sc}">${seg.status}</span>`),
            _row('Type',           seg.segment_type || '—'),
            _row('Ownership',      seg.ownership_type || '—'),
            _row('Length',         seg.path_length_km ? seg.path_length_km + ' km' : '—'),
            _row('Site A',         seg.site_a ? seg.site_a.name : '—'),
            _row('Site B',         seg.site_b ? seg.site_b.name : '—'),
            _row('Tags',           seg.tags && seg.tags.length ? _tags(seg.tags) : '—'),
        ]);
        if (seg.type_data && Object.keys(seg.type_data).length) {
            rows += `<hr class="my-1"><div class="text-muted text-uppercase small fw-bold mb-1">${seg.segment_type} details</div>`;
            rows += _table(Object.entries(seg.type_data).map(([k, v]) => _row(k, v)));
        }
        const links = `<div class="mt-2 d-flex gap-1">
            <a href="${seg.url}" class="btn btn-outline-primary btn-sm flex-fill">
                <i class="mdi mdi-open-in-new"></i> View</a>
            <a href="${seg.map_url}" class="btn btn-outline-secondary btn-sm flex-fill">
                <i class="mdi mdi-map"></i> Map</a>
        </div>`;
        showInfoCard(
            `<i class="mdi mdi-vector-polyline text-primary"></i> ${seg.name}`,
            rows + links
        );
    }

    function _connectDropdown(termPk, returnUrl) {
        const base = `/dcim/cables/add/?a_terminations_type=circuits.circuittermination&a_terminations=${termPk}`;
        const ret  = `&return_url=${encodeURIComponent(returnUrl)}`;
        return `<div class="dropdown d-inline-block">
            <button type="button" class="btn btn-primary btn-sm dropdown-toggle" data-bs-toggle="dropdown">
                <i class="mdi mdi-ethernet-cable"></i> Connect
            </button>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="${base}&b_terminations_type=dcim.interface${ret}">Interface</a></li>
                <li><a class="dropdown-item" href="${base}&b_terminations_type=dcim.frontport${ret}">Front Port</a></li>
                <li><a class="dropdown-item" href="${base}&b_terminations_type=dcim.rearport${ret}">Rear Port</a></li>
                <li><a class="dropdown-item" href="${base}&b_terminations_type=circuits.circuittermination${ret}">Circuit Termination</a></li>
            </ul>
        </div>`;
    }

    function _termRows(label, term, circuitUrl) {
        if (!term) return _row(label + ' site', '—');
        let out = _row(label + ' site', term.site || '—');
        if (term.connection) {
            out += _row(label + ' cable', term.connection);
        } else if (term.termination_pk) {
            out += _row(label + ' cable', _connectDropdown(term.termination_pk, circuitUrl));
        }
        if (term.xconnect_id) out += _row(label + ' Xconnect', term.xconnect_id);
        if (term.pp_info)     out += _row(label + ' PP info',  term.pp_info);
        if (term.port_speed)  out += _row(label + ' speed',    term.port_speed);
        if (term.description) out += _row(label + ' note',     term.description);
        return out;
    }

    function buildCircuitInfoCard(circ) {
        const sc = circuitStatusBadge[circ.status] || 'secondary';
        const rows = _table([
            _row('Provider',     circ.provider || '—'),
            _row('Status',       `<span class="badge text-bg-${sc}">${circ.status}</span>`),
            _row('Type',         circ.type || '—'),
            _row('Tenant',       circ.tenant || '—'),
            _row('Install date', circ.install_date || '—'),
            _row('Terminate',    circ.termination_date || '—'),
            _row('Tags',         circ.tags && circ.tags.length ? _tags(circ.tags) : '—'),
            _termRows('Term A', circ.term_a, circ.url),
            _termRows('Term Z', circ.term_z, circ.url),
        ]);
        const links = `<div class="mt-2"><a href="${circ.url}" class="btn btn-outline-primary btn-sm w-100">
            <i class="mdi mdi-open-in-new"></i> View circuit</a></div>`;
        showInfoCard(
            `<i class="mdi mdi-transit-connection-variant" style="color:#ad1457"></i> ${circ.cid}`,
            rows + links
        );
    }

    function showSegmentPopup(seg, latlng) {
        const sc  = segmentStatusBadge[seg.status] || 'secondary';
        const siteA = seg.site_a ? seg.site_a.name : 'N/A';
        const siteB = seg.site_b ? seg.site_b.name : 'N/A';
        const len   = seg.path_length_km ? seg.path_length_km + ' km' : 'unknown';
        L.popup({ maxWidth: 320 })
            .setLatLng(latlng)
            .setContent(
                `<strong>Segment: ${seg.name}</strong><br>` +
                `<span class="badge text-bg-${sc}">${seg.status}</span><br>` +
                `<small>${siteA} ↔ ${siteB}</small><br>` +
                `<small>Provider: ${seg.provider || 'N/A'} · Length: ${len}</small><br>` +
                `<a href="${seg.url}" class="small">View segment</a> ` +
                `<a href="${seg.map_url}" class="small">Individual map</a>`
            )
            .openOn(map);
        buildSegmentInfoCard(seg);
    }

    // Segment lookup used by overlap popup click handlers
    const _overlapSegById = {};

    function showOverlapPopup(items, latlng) {
        let html = `<div><strong>${items.length} segments here</strong>`;
        items.forEach(({ seg }) => {
            const sc = segmentStatusBadge[seg.status] || 'secondary';
            _overlapSegById[seg.id] = seg;
            html += `<div class="border-top pt-1 mt-1">
                <span class="seg-overlap-name"
                      data-seg-id="${seg.id}"
                      style="cursor:pointer;font-weight:500;"
                      title="Show details in info card">${seg.name}</span><br>
                <span class="badge text-bg-${sc} small">${seg.status}</span>
                <small> ${seg.site_a ? seg.site_a.name : ''} ↔ ${seg.site_b ? seg.site_b.name : ''}</small>
                <small class="ms-1"><a href="${seg.url}">View</a></small>
            </div>`;
        });
        html += '</div>';

        const popup = L.popup({ maxWidth: 340 }).setLatLng(latlng).setContent(html);
        popup.on('add', function () {
            const el = popup.getElement();
            if (!el) return;
            el.querySelectorAll('.seg-overlap-name').forEach(span => {
                span.addEventListener('click', function () {
                    const seg = _overlapSegById[Number(this.dataset.segId)];
                    if (seg) buildSegmentInfoCard(seg);
                });
            });
        });
        popup.openOn(map);
    }

    function handleLineClick(e) {
        e.originalEvent.preventDefault();
        const nearby = findNearbySegments(e);
        if (!nearby.length) return;
        if (nearby.length === 1) {
            showSegmentPopup(nearby[0].seg, e.latlng);
        } else {
            showOverlapPopup(nearby, e.latlng);
        }
    }

    // GeoJSON features fetched once and cached
    let cachedGeoFeatures = null;

    function renderSegments() {
        segmentPathGroup.clearLayers();
        segmentLayers.clear();

        const visibleIds = new Set(activeSegments.map(s => s.id));

        // Dashed straight-line fallbacks for segments without GeoJSON
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
            fetch(apiUrl)
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
            line.on('click', (function(c) {
                return function() { buildCircuitInfoCard(c); };
            })(circ));

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
    updateCounts();

    // -------------------------------------------------------------------------
    // Wire controls (after DOM ready)
    // -------------------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', function () {

        // Segment colour scheme
        document.querySelectorAll('[data-segment-scheme]').forEach(el => {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                switchSegmentScheme(this.getAttribute('data-segment-scheme'));
            });
        });

        // Circuit colour scheme
        document.querySelectorAll('[data-circuit-scheme]').forEach(el => {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                switchCircuitScheme(this.getAttribute('data-circuit-scheme'));
            });
        });

        // Site colour scheme
        document.querySelectorAll('[data-site-scheme]').forEach(el => {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                switchSiteScheme(this.getAttribute('data-site-scheme'));
            });
        });

        // Visibility toggles
        const toggleSegBtn  = document.getElementById('toggleSegments');
        const toggleSiteBtn = document.getElementById('toggleSites');
        const toggleCircBtn = document.getElementById('toggleCircuits');
        if (toggleSegBtn)  toggleSegBtn.addEventListener('click',  () => toggleLayer('segments', toggleSegBtn));
        if (toggleSiteBtn) toggleSiteBtn.addEventListener('click', () => toggleLayer('sites',    toggleSiteBtn));
        if (toggleCircBtn) {
            // Circuits are hidden by default — sync button and filter section to off state
            toggleCircBtn.classList.replace('btn-warning', 'btn-outline-warning');
            toggleCircBtn.title = 'Show circuits';
            const circFilterSection = document.getElementById('filterSectionCircuits');
            if (circFilterSection) circFilterSection.classList.add('d-none');
            toggleCircBtn.addEventListener('click', () => toggleLayer('circuits', toggleCircBtn));
        }

        // Fit all
        const fitBtn = document.getElementById('fitBounds');
        if (fitBtn) fitBtn.addEventListener('click', fitMap);

        // Live filtering — wire all filter inputs in the sidebar
        const filterPanel = document.getElementById('filterSidebar');
        if (filterPanel) {
            filterPanel.addEventListener('change', applyFilters);
        }

        // Clear filters — shared logic used by both the header X and the bottom button
        function clearAllFilters() {
            document.querySelectorAll('#filterSidebar select').forEach(sel => {
                if (window.$ && $(sel).data('select2')) {
                    $(sel).val(null).trigger('change');
                } else {
                    Array.from(sel.options).forEach(o => { o.selected = false; });
                    sel.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
            applyFilters();
        }

        const clearBtn = document.getElementById('clearFilters');
        if (clearBtn) clearBtn.addEventListener('click', clearAllFilters);

        const clearHeaderBtn = document.getElementById('clearFiltersHeader');
        if (clearHeaderBtn) clearHeaderBtn.addEventListener('click', clearAllFilters);

        // Info card close button
        const infoCardClose = document.getElementById('infoCardClose');
        if (infoCardClose) {
            infoCardClose.addEventListener('click', hideInfoCard);
        }

        // Tile layer switcher
        initializeLayerSwitching(map);
    });

})();
