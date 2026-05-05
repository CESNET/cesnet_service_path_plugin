/**
 * edit_mode_api.js — Network / fetch layer for edit mode operations.
 *
 * Pure network logic: no DOM, no Leaflet, no state machine references.
 * Every function returns a Promise that resolves with parsed JSON on success
 * and rejects with an Error (message contains HTTP status + body) on failure.
 *
 * The caller (editModeUI / object_map.js) is responsible for:
 *   - calling sm.beginSave() before the fetch
 *   - calling sm.completeSave() or sm.failSave() based on the result
 *
 * CSRF token is read from the csrftoken cookie, which Django sets on every
 * page load.  Session credentials are sent automatically via same-origin fetch.
 *
 * Usage in the browser:
 *   const api = new EditModeApi();
 *
 * Usage in Node tests:
 *   const { EditModeApi } = require('./edit_mode_api');
 */

(function (root, factory) {
    'use strict';
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = factory();
    } else {
        root.EditModeApi = factory().EditModeApi;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';

    // -------------------------------------------------------------------------
    // CSRF helper
    // -------------------------------------------------------------------------

    function getCsrfToken() {
        // NetBox injects window.CSRF_TOKEN from the base template — prefer it.
        if (typeof window !== 'undefined' && window.CSRF_TOKEN) {
            return window.CSRF_TOKEN;
        }
        // Fallback: parse the csrftoken cookie directly.
        const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    // -------------------------------------------------------------------------
    // Core request helpers (module-level, used as defaults only)
    // -------------------------------------------------------------------------

    function request(method, url, body) {
        const opts = {
            method,
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken':      getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest',
                'Accept':           'application/json',
            },
        };
        if (body !== undefined) {
            opts.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(body);
        }
        return fetch(url, opts).then(resp => {
            if (resp.status === 204) return {};   // No Content — treat as success
            return resp.json().then(data => {
                if (!resp.ok) {
                    const msg = _extractErrorMessage(data) || `HTTP ${resp.status}`;
                    throw new Error(msg);
                }
                return data;
            });
        });
    }

    function get(url) {
        return fetch(url, {
            method:      'GET',
            credentials: 'same-origin',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept':           'application/json',
            },
        }).then(resp =>
            resp.json().then(data => {
                if (!resp.ok) {
                    throw new Error(_extractErrorMessage(data) || `HTTP ${resp.status}`);
                }
                return data;
            })
        );
    }

    // DRF error responses can be { detail: "..." } or { field: ["msg"] } objects.
    function _extractErrorMessage(data) {
        if (!data || typeof data !== 'object') return null;
        if (typeof data.detail === 'string') return data.detail;
        // Collect the first field-level error message
        for (const [key, val] of Object.entries(data)) {
            if (Array.isArray(val) && val.length > 0) return `${key}: ${val[0]}`;
            if (typeof val === 'string') return `${key}: ${val}`;
        }
        return null;
    }

    // -------------------------------------------------------------------------
    // Class definition — injectable fetch for tests
    // -------------------------------------------------------------------------

    /**
     * @param {object} [opts]
     * @param {function} [opts.fetchFn]       Override fetch (for tests)
     * @param {function} [opts.getCsrfToken]  Override CSRF reader (for tests)
     */
    class EditModeApi {
        constructor(opts = {}) {
            this._fetch   = opts.fetchFn      || (typeof fetch !== 'undefined' ? fetch.bind(typeof globalThis !== 'undefined' ? globalThis : window) : null);
            this._getCsrf = opts.getCsrfToken || getCsrfToken;
            this._request = this._makeRequest.bind(this);
            this._get     = this._makeGet.bind(this);
        }

        _makeRequest(method, url, body) {
            const opts = {
                method,
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken':      this._getCsrf(),
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept':           'application/json',
                },
            };
            if (body !== undefined) {
                opts.headers['Content-Type'] = 'application/json';
                opts.body = JSON.stringify(body);
            }
            return this._fetch(url, opts).then(resp => {
                if (resp.status === 204) return {};
                return resp.json().then(data => {
                    if (!resp.ok) {
                        const msg = _extractErrorMessage(data) || `HTTP ${resp.status}`;
                        throw new Error(msg);
                    }
                    return data;
                });
            });
        }

        _makeGet(url) {
            return this._fetch(url, {
                method:      'GET',
                credentials: 'same-origin',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept':           'application/json',
                },
            }).then(resp =>
                resp.json().then(data => {
                    if (!resp.ok) {
                        throw new Error(_extractErrorMessage(data) || `HTTP ${resp.status}`);
                    }
                    return data;
                })
            );
        }

        // -------------------------------------------------------------------------
        // Reference data — loaded once when edit mode is entered
        // -------------------------------------------------------------------------

        /**
         * Load all three reference datasets in parallel.
         * Resolves with { unpositionedSites, providers, circuitTypes }.
         */
        loadReferenceData() {
            return Promise.all([
                this._get('/api/dcim/sites/?latitude__empty=true&limit=500'),
                this._get('/api/circuits/providers/?limit=500'),
                this._get('/api/circuits/circuit-types/?limit=500'),
            ]).then(([sites, providers, circuitTypes]) => ({
                unpositionedSites: sites.results        || [],
                providers:         providers.results    || [],
                circuitTypes:      circuitTypes.results || [],
            }));
        }

        // -------------------------------------------------------------------------
        // Site operations
        // -------------------------------------------------------------------------

        /**
         * Update lat/lng of an existing site.
         * Resolves with the full updated site object from the API.
         */
        updateSiteCoordinates(siteId, lat, lng) {
            return this._request('PATCH', `/api/dcim/sites/${siteId}/`, {
                latitude:  lat,
                longitude: lng,
            });
        }

        /**
         * Create a new site with minimal required fields.
         * Resolves with the created site object.
         */
        createSite(name, slug, lat, lng) {
            return this._request('POST', '/api/dcim/sites/', {
                name,
                slug,
                latitude:  lat,
                longitude: lng,
            });
        }

        /**
         * Fetch a single site by id (used after create to get the full data shape
         * matching what the map expects).
         */
        fetchSite(siteId) {
            return this._get(`/api/dcim/sites/${siteId}/`);
        }

        // -------------------------------------------------------------------------
        // Segment operations
        // -------------------------------------------------------------------------

        /**
         * Create a new segment.
         * @param {object} data  { name, segment_type, provider, ownership_type, status, site_a, site_b }
         *                       provider, site_a, site_b are numeric IDs.
         */
        createSegment(data) {
            return this._request('POST', '/api/plugins/cesnet-service-path-plugin/segments/', data);
        }

        /**
         * Change one endpoint of an existing segment.
         * @param {number} segmentId
         * @param {'a'|'b'} end
         * @param {number} siteId
         */
        updateSegmentEndpoint(segmentId, end, siteId) {
            // Always clear the corresponding location when changing a site — the location
            // must belong to its site, so keeping the old location would fail validation.
            const body = end === 'a'
                ? { site_a: siteId, location_a: null }
                : { site_b: siteId, location_b: null };
            return this._request(
                'PATCH',
                `/api/plugins/cesnet-service-path-plugin/segments/${segmentId}/`,
                body
            );
        }

        /**
         * Fetch a single segment by id.
         */
        fetchSegment(segmentId) {
            return this._get(`/api/plugins/cesnet-service-path-plugin/segments/${segmentId}/`);
        }

        // -------------------------------------------------------------------------
        // Circuit operations
        // -------------------------------------------------------------------------

        /**
         * Create a new circuit then its two terminations.
         * @param {object} data  { cid, provider, type, siteA, siteB }
         *                       provider, type are numeric IDs; siteA/siteB are numeric site IDs.
         * Resolves with the created circuit object (terminations are a side-effect).
         */
        createCircuit(data) {
            return this._request('POST', '/api/circuits/circuits/', {
                cid:      data.cid,
                provider: data.provider,
                type:     data.type,
            }).then(circuit => {
                const termA = this._request('POST', '/api/circuits/circuit-terminations/', {
                    circuit:          circuit.id,
                    term_side:        'A',
                    termination_type: 'dcim.site',
                    termination_id:   data.siteA,
                });
                const termZ = this._request('POST', '/api/circuits/circuit-terminations/', {
                    circuit:          circuit.id,
                    term_side:        'Z',
                    termination_type: 'dcim.site',
                    termination_id:   data.siteB,
                });
                return Promise.all([termA, termZ])
                    .then(() => circuit)
                    .catch(err => {
                        // Roll back the orphaned circuit before propagating the error.
                        return this._request('DELETE', `/api/circuits/circuits/${circuit.id}/`)
                            .catch(() => {})   // ignore rollback failure — best effort
                            .then(() => { throw err; });
                    });
            });
        }

        /**
         * Change the site of an existing circuit termination.
         * @param {number} terminationPk  The CircuitTermination primary key
         * @param {number} siteId
         */
        updateCircuitTerminationSite(terminationPk, siteId) {
            return this._request(
                'PATCH',
                `/api/circuits/circuit-terminations/${terminationPk}/`,
                { termination_type: 'dcim.site', termination_id: siteId }
            );
        }

        /**
         * Fetch a single circuit by id.
         */
        fetchCircuit(circuitId) {
            return this._get(`/api/circuits/circuits/${circuitId}/`);
        }
    }

    return { EditModeApi };
}));
