'use strict';

const { EditModeApi } = require(
    '../cesnet_service_path_plugin/static/cesnet_service_path_plugin/js/edit_mode_api'
);

// ---------------------------------------------------------------------------
// Mock fetch builder
//
// makeResp(status, body) — returns a Response-like object.
// mockFetch(...responses) — returns a jest.fn() that returns each response in
//   sequence; extra calls repeat the last entry.
// ---------------------------------------------------------------------------

function makeResp(status, body) {
    return {
        status,
        ok: status >= 200 && status < 300,
        json: () => Promise.resolve(body),
    };
}

function mockFetch(...responses) {
    let i = 0;
    return jest.fn(() => {
        const resp = responses[Math.min(i, responses.length - 1)];
        i++;
        return Promise.resolve(resp);
    });
}

function makeApi(fetchFn) {
    return new EditModeApi({
        fetchFn,
        getCsrfToken: () => 'test-csrf-token',
    });
}

// ---------------------------------------------------------------------------
// Helpers to inspect fetch calls
// ---------------------------------------------------------------------------

function calledWith(fn, callIndex = 0) {
    return {
        url:    fn.mock.calls[callIndex][0],
        opts:   fn.mock.calls[callIndex][1],
        body:   fn.mock.calls[callIndex][1].body
                    ? JSON.parse(fn.mock.calls[callIndex][1].body)
                    : undefined,
    };
}

// ---------------------------------------------------------------------------
// Reference data
// ---------------------------------------------------------------------------

describe('loadReferenceData', () => {
    test('fires three GET requests in parallel', async () => {
        const fn = mockFetch(
            makeResp(200, { results: [{ id: 1, name: 'Site X' }] }),
            makeResp(200, { results: [{ id: 2, name: 'Provider Y' }] }),
            makeResp(200, { results: [{ id: 3, name: 'CT Z' }] }),
        );
        const api = makeApi(fn);
        await api.loadReferenceData();
        expect(fn).toHaveBeenCalledTimes(3);
    });

    test('GET urls are correct', async () => {
        const fn = mockFetch(
            makeResp(200, { results: [] }),
            makeResp(200, { results: [] }),
            makeResp(200, { results: [] }),
        );
        const api = makeApi(fn);
        await api.loadReferenceData();
        const urls = fn.mock.calls.map(c => c[0]);
        expect(urls).toContain('/api/dcim/sites/?latitude__empty=true&limit=500');
        expect(urls).toContain('/api/circuits/providers/?limit=500');
        expect(urls).toContain('/api/circuits/circuit-types/?limit=500');
    });

    test('resolves with shaped object', async () => {
        const fn = mockFetch(
            makeResp(200, { results: [{ id: 10 }] }),
            makeResp(200, { results: [{ id: 20 }] }),
            makeResp(200, { results: [{ id: 30 }] }),
        );
        const api = makeApi(fn);
        const result = await api.loadReferenceData();
        expect(result.unpositionedSites).toEqual([{ id: 10 }]);
        expect(result.providers).toEqual([{ id: 20 }]);
        expect(result.circuitTypes).toEqual([{ id: 30 }]);
    });

    test('missing results key falls back to empty array', async () => {
        const fn = mockFetch(
            makeResp(200, {}),
            makeResp(200, {}),
            makeResp(200, {}),
        );
        const api = makeApi(fn);
        const result = await api.loadReferenceData();
        expect(result.unpositionedSites).toEqual([]);
        expect(result.providers).toEqual([]);
        expect(result.circuitTypes).toEqual([]);
    });

    test('rejects when any request fails', async () => {
        const fn = mockFetch(
            makeResp(200, { results: [] }),
            makeResp(500, { detail: 'Server error' }),
            makeResp(200, { results: [] }),
        );
        const api = makeApi(fn);
        await expect(api.loadReferenceData()).rejects.toThrow('Server error');
    });
});

// ---------------------------------------------------------------------------
// Site operations
// ---------------------------------------------------------------------------

describe('updateSiteCoordinates', () => {
    test('sends PATCH to correct URL', async () => {
        const fn = mockFetch(makeResp(200, { id: 42 }));
        const api = makeApi(fn);
        await api.updateSiteCoordinates(42, 50.1, 14.4);
        const { url, opts } = calledWith(fn);
        expect(url).toBe('/api/dcim/sites/42/');
        expect(opts.method).toBe('PATCH');
    });

    test('sends lat/lng in body', async () => {
        const fn = mockFetch(makeResp(200, { id: 42 }));
        const api = makeApi(fn);
        await api.updateSiteCoordinates(42, 50.1, 14.4);
        const { body } = calledWith(fn);
        expect(body.latitude).toBe(50.1);
        expect(body.longitude).toBe(14.4);
    });

    test('sends CSRF token header', async () => {
        const fn = mockFetch(makeResp(200, { id: 42 }));
        const api = makeApi(fn);
        await api.updateSiteCoordinates(42, 50.1, 14.4);
        const { opts } = calledWith(fn);
        expect(opts.headers['X-CSRFToken']).toBe('test-csrf-token');
    });

    test('resolves with response data', async () => {
        const site = { id: 42, name: 'Prague' };
        const fn = mockFetch(makeResp(200, site));
        const api = makeApi(fn);
        const result = await api.updateSiteCoordinates(42, 50.1, 14.4);
        expect(result).toEqual(site);
    });

    test('rejects on non-OK response with detail message', async () => {
        const fn = mockFetch(makeResp(403, { detail: 'Permission denied.' }));
        const api = makeApi(fn);
        await expect(api.updateSiteCoordinates(42, 50.1, 14.4)).rejects.toThrow('Permission denied.');
    });

    test('rejects on non-OK with field error message', async () => {
        const fn = mockFetch(makeResp(400, { latitude: ['A valid number is required.'] }));
        const api = makeApi(fn);
        await expect(api.updateSiteCoordinates(42, 'bad', 14.4)).rejects.toThrow('latitude: A valid number is required.');
    });
});

describe('createSite', () => {
    test('sends POST to /api/dcim/sites/', async () => {
        const fn = mockFetch(makeResp(201, { id: 99 }));
        const api = makeApi(fn);
        await api.createSite('New Site', 'new-site', 50.0, 14.0);
        const { url, opts } = calledWith(fn);
        expect(url).toBe('/api/dcim/sites/');
        expect(opts.method).toBe('POST');
    });

    test('body contains all required fields', async () => {
        const fn = mockFetch(makeResp(201, { id: 99 }));
        const api = makeApi(fn);
        await api.createSite('New Site', 'new-site', 50.0, 14.0);
        const { body } = calledWith(fn);
        expect(body.name).toBe('New Site');
        expect(body.slug).toBe('new-site');
        expect(body.latitude).toBe(50.0);
        expect(body.longitude).toBe(14.0);
    });

    test('resolves with created site', async () => {
        const site = { id: 99, name: 'New Site' };
        const fn = mockFetch(makeResp(201, site));
        const api = makeApi(fn);
        const result = await api.createSite('New Site', 'new-site', 50.0, 14.0);
        expect(result).toEqual(site);
    });
});

describe('fetchSite', () => {
    test('sends GET to correct URL', async () => {
        const fn = mockFetch(makeResp(200, { id: 7 }));
        const api = makeApi(fn);
        await api.fetchSite(7);
        expect(calledWith(fn).url).toBe('/api/dcim/sites/7/');
        expect(calledWith(fn).opts.method).toBe('GET');
    });
});

// ---------------------------------------------------------------------------
// Segment operations
// ---------------------------------------------------------------------------

describe('createSegment', () => {
    test('sends POST to plugin segments endpoint', async () => {
        const fn = mockFetch(makeResp(201, { id: 55 }));
        const api = makeApi(fn);
        await api.createSegment({
            name: 'SEG-01', segment_type: 'dark_fiber',
            provider: 1, ownership_type: 'owned', status: 'active',
            site_a: 10, site_b: 20,
        });
        const { url, opts } = calledWith(fn);
        expect(url).toBe('/api/plugins/cesnet-service-path-plugin/segments/');
        expect(opts.method).toBe('POST');
    });

    test('body is passed through unchanged', async () => {
        const fn = mockFetch(makeResp(201, { id: 55 }));
        const api = makeApi(fn);
        const data = {
            name: 'SEG-01', segment_type: 'dark_fiber',
            provider: 1, ownership_type: 'owned', status: 'active',
            site_a: 10, site_b: 20,
        };
        await api.createSegment(data);
        expect(calledWith(fn).body).toEqual(data);
    });
});

describe('updateSegmentEndpoint', () => {
    test('PATCH end "a" sends site_a', async () => {
        const fn = mockFetch(makeResp(200, { id: 55 }));
        const api = makeApi(fn);
        await api.updateSegmentEndpoint(55, 'a', 10);
        const { url, body } = calledWith(fn);
        expect(url).toBe('/api/plugins/cesnet-service-path-plugin/segments/55/');
        expect(body).toEqual({ site_a: 10, location_a: null });
    });

    test('PATCH end "b" sends site_b', async () => {
        const fn = mockFetch(makeResp(200, { id: 55 }));
        const api = makeApi(fn);
        await api.updateSegmentEndpoint(55, 'b', 20);
        expect(calledWith(fn).body).toEqual({ site_b: 20, location_b: null });
    });
});

describe('fetchSegment', () => {
    test('GET to correct URL', async () => {
        const fn = mockFetch(makeResp(200, { id: 55 }));
        const api = makeApi(fn);
        await api.fetchSegment(55);
        expect(calledWith(fn).url).toBe('/api/plugins/cesnet-service-path-plugin/segments/55/');
    });
});

// ---------------------------------------------------------------------------
// Circuit operations
// ---------------------------------------------------------------------------

describe('createCircuit', () => {
    function circuitSetup() {
        // call 1: POST /circuits/   → circuit
        // call 2: POST /terminations/ term_A
        // call 3: POST /terminations/ term_Z
        const fn = mockFetch(
            makeResp(201, { id: 77, cid: 'CID-01' }),
            makeResp(201, { id: 101 }),
            makeResp(201, { id: 102 }),
        );
        const api = makeApi(fn);
        return { fn, api };
    }

    test('first POST creates the circuit', async () => {
        const { fn, api } = circuitSetup();
        await api.createCircuit({ cid: 'CID-01', provider: 3, type: 5, siteA: 10, siteB: 20 });
        const { url, opts, body } = calledWith(fn, 0);
        expect(url).toBe('/api/circuits/circuits/');
        expect(opts.method).toBe('POST');
        expect(body).toEqual({ cid: 'CID-01', provider: 3, type: 5 });
    });

    test('second POST creates term_A with circuit id and site', async () => {
        const { fn, api } = circuitSetup();
        await api.createCircuit({ cid: 'CID-01', provider: 3, type: 5, siteA: 10, siteB: 20 });
        const { url, body } = calledWith(fn, 1);
        expect(url).toBe('/api/circuits/circuit-terminations/');
        expect(body.term_side).toBe('A');
        expect(body.circuit).toBe(77);
        expect(body.termination_type).toBe('dcim.site');
        expect(body.termination_id).toBe(10);
    });

    test('third POST creates term_Z with correct site', async () => {
        const { fn, api } = circuitSetup();
        await api.createCircuit({ cid: 'CID-01', provider: 3, type: 5, siteA: 10, siteB: 20 });
        const { body } = calledWith(fn, 2);
        expect(body.term_side).toBe('Z');
        expect(body.termination_type).toBe('dcim.site');
        expect(body.termination_id).toBe(20);
    });

    test('resolves with the circuit object (not terminations)', async () => {
        const { fn, api } = circuitSetup();
        const result = await api.createCircuit({ cid: 'CID-01', provider: 3, type: 5, siteA: 10, siteB: 20 });
        expect(result).toEqual({ id: 77, cid: 'CID-01' });
    });

    test('rejects if circuit creation fails', async () => {
        const fn = mockFetch(makeResp(400, { cid: ['Circuit with this ID already exists.'] }));
        const api = makeApi(fn);
        await expect(
            api.createCircuit({ cid: 'DUP', provider: 3, type: 5, siteA: 10, siteB: 20 })
        ).rejects.toThrow('cid: Circuit with this ID already exists.');
    });

    test('rejects if termination creation fails', async () => {
        const fn = mockFetch(
            makeResp(201, { id: 77 }),
            makeResp(400, { detail: 'Site not found.' }),
            makeResp(201, { id: 102 }),
        );
        const api = makeApi(fn);
        await expect(
            api.createCircuit({ cid: 'CID-01', provider: 3, type: 5, siteA: 999, siteB: 20 })
        ).rejects.toThrow('Site not found.');
    });
});

describe('updateCircuitTerminationSite', () => {
    test('sends PATCH to termination URL with site', async () => {
        const fn = mockFetch(makeResp(200, { id: 101 }));
        const api = makeApi(fn);
        await api.updateCircuitTerminationSite(101, 42);
        const { url, opts, body } = calledWith(fn);
        expect(url).toBe('/api/circuits/circuit-terminations/101/');
        expect(opts.method).toBe('PATCH');
        expect(body).toEqual({ termination_type: 'dcim.site', termination_id: 42 });
    });
});

describe('fetchCircuit', () => {
    test('GET to correct URL', async () => {
        const fn = mockFetch(makeResp(200, { id: 77 }));
        const api = makeApi(fn);
        await api.fetchCircuit(77);
        expect(calledWith(fn).url).toBe('/api/circuits/circuits/77/');
    });
});

// ---------------------------------------------------------------------------
// 204 No Content
// ---------------------------------------------------------------------------

describe('204 No Content response', () => {
    test('resolves with empty object instead of trying to parse JSON', async () => {
        const fn = jest.fn(() => Promise.resolve({ status: 204, ok: true, json: () => Promise.reject(new Error('no body')) }));
        const api = makeApi(fn);
        const result = await api.updateSiteCoordinates(1, 50, 14);
        expect(result).toEqual({});
    });
});

// ---------------------------------------------------------------------------
// credentials and headers on all mutating methods
// ---------------------------------------------------------------------------

describe('request headers', () => {
    test.each([
        ['updateSiteCoordinates', api => api.updateSiteCoordinates(1, 50, 14)],
        ['createSite',            api => api.createSite('S', 's', 50, 14)],
        ['createSegment',         api => api.createSegment({ name: 'S', segment_type: 'dark_fiber', provider: 1, ownership_type: 'owned', status: 'active', site_a: 1, site_b: 2 })],
        ['updateSegmentEndpoint', api => api.updateSegmentEndpoint(1, 'a', 2)],
        ['updateCircuitTerminationSite', api => api.updateCircuitTerminationSite(1, 2)],
    ])('%s sends CSRF token and same-origin credentials', async (label, call) => {
        const fn = mockFetch(makeResp(200, { id: 1 }), makeResp(201, {}), makeResp(201, {}));
        const api = makeApi(fn);
        await call(api);
        const opts = fn.mock.calls[0][1];
        expect(opts.credentials).toBe('same-origin');
        expect(opts.headers['X-CSRFToken']).toBe('test-csrf-token');
    });
});
