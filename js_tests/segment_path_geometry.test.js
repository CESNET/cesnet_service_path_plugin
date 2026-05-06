'use strict';

const {
    haversineDistance,
    joinMultiLineString,
    checkSiteProximity,
    PATH_JOIN_TOLERANCE_METERS,
    SITE_PROXIMITY_THRESHOLD_METERS,
} = require(
    '../cesnet_service_path_plugin/static/cesnet_service_path_plugin/js/segment_path_geometry'
);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Build a GeoJSON [lng, lat] pair */
const pt = (lng, lat) => [lng, lat];

// ---------------------------------------------------------------------------
// haversineDistance
// ---------------------------------------------------------------------------

describe('haversineDistance', () => {
    test('same point returns 0', () => {
        expect(haversineDistance(50.0, 14.0, 50.0, 14.0)).toBe(0);
    });

    test('Prague → Brno is approximately 184 km', () => {
        // Prague: 50.0755, 14.4378  Brno: 49.1951, 16.6068
        const dist = haversineDistance(50.0755, 14.4378, 49.1951, 16.6068);
        expect(dist).toBeGreaterThan(180_000);
        expect(dist).toBeLessThan(190_000);
    });

    test('1 degree latitude north is approximately 111 km', () => {
        const dist = haversineDistance(50.0, 15.0, 51.0, 15.0);
        expect(dist).toBeGreaterThan(110_000);
        expect(dist).toBeLessThan(112_000);
    });

    test('very small distance (5 m) is computed correctly', () => {
        // Move ~5 m north from a point (1 degree lat ≈ 111 km → 0.000045° ≈ 5 m)
        const dist = haversineDistance(50.0, 14.0, 50.000045, 14.0);
        expect(dist).toBeGreaterThan(4);
        expect(dist).toBeLessThan(6);
    });

    test('symmetric — distance(A,B) === distance(B,A)', () => {
        const d1 = haversineDistance(50.0, 14.0, 49.0, 16.0);
        const d2 = haversineDistance(49.0, 16.0, 50.0, 14.0);
        expect(Math.abs(d1 - d2)).toBeLessThan(0.001);
    });
});

// ---------------------------------------------------------------------------
// joinMultiLineString
// ---------------------------------------------------------------------------

describe('joinMultiLineString', () => {
    test('null input returns null', () => {
        expect(joinMultiLineString(null)).toBeNull();
    });

    test('empty array returns null', () => {
        expect(joinMultiLineString([])).toBeNull();
    });

    test('single segment is returned unchanged', () => {
        const seg = [pt(14.0, 50.0), pt(14.1, 50.1), pt(14.2, 50.2)];
        const result = joinMultiLineString([seg]);
        expect(result).toEqual(seg);
    });

    test('single segment returns a copy, not the original array', () => {
        const seg = [pt(14.0, 50.0), pt(14.1, 50.1)];
        const result = joinMultiLineString([seg]);
        expect(result).not.toBe(seg);
    });

    test('two perfectly connected segments join into one', () => {
        // Segment 1 ends at [14.1, 50.1]; Segment 2 starts at exactly the same point.
        const seg1 = [pt(14.0, 50.0), pt(14.1, 50.1)];
        const seg2 = [pt(14.1, 50.1), pt(14.2, 50.2)];
        const result = joinMultiLineString([seg1, seg2]);
        expect(result).toEqual([pt(14.0, 50.0), pt(14.1, 50.1), pt(14.2, 50.2)]);
    });

    test('junction duplicate point is not included twice', () => {
        const seg1 = [pt(14.0, 50.0), pt(14.1, 50.1)];
        const seg2 = [pt(14.1, 50.1), pt(14.2, 50.2)];
        const result = joinMultiLineString([seg1, seg2]);
        expect(result).toHaveLength(3);
    });

    test('three connected segments join into one', () => {
        const seg1 = [pt(14.0, 50.0), pt(14.1, 50.1)];
        const seg2 = [pt(14.1, 50.1), pt(14.2, 50.2)];
        const seg3 = [pt(14.2, 50.2), pt(14.3, 50.3)];
        const result = joinMultiLineString([seg1, seg2, seg3]);
        expect(result).toHaveLength(4);
        expect(result[0]).toEqual(pt(14.0, 50.0));
        expect(result[3]).toEqual(pt(14.3, 50.3));
    });

    test('gap within tolerance (< 10 m) is joined', () => {
        // Shift end of seg1 by ~5 m north (≈ 0.000045° lat)
        const seg1 = [pt(14.0, 50.0), pt(14.1, 50.000045)];
        const seg2 = [pt(14.1, 50.1),  pt(14.2, 50.2)];
        // gap between 50.000045 and 50.1 is huge — use a tiny shift instead
        const seg1b = [pt(14.0, 50.0), pt(14.1, 50.1)];
        const seg2b = [pt(14.1, 50.100040), pt(14.2, 50.2)]; // ~4.5 m gap
        const result = joinMultiLineString([seg1b, seg2b], 10);
        expect(result).not.toBeNull();
        expect(result).toHaveLength(3);
    });

    test('gap just over tolerance (> 10 m) returns null', () => {
        // ~12 m gap: 0.000108° lat ≈ 12 m
        const seg1 = [pt(14.0, 50.0), pt(14.1, 50.1)];
        const seg2 = [pt(14.1, 50.100108), pt(14.2, 50.2)];
        const result = joinMultiLineString([seg1, seg2], 10);
        expect(result).toBeNull();
    });

    test('genuine gap returns null', () => {
        const seg1 = [pt(14.0, 50.0), pt(14.1, 50.1)];
        const seg2 = [pt(16.0, 49.0), pt(16.1, 49.1)]; // hundreds of km away
        expect(joinMultiLineString([seg1, seg2])).toBeNull();
    });

    test('custom tolerance parameter is respected', () => {
        // ~50 m gap — fails at default 10 m, passes at 100 m
        const seg1 = [pt(14.0, 50.0), pt(14.1, 50.1)];
        const seg2 = [pt(14.1, 50.100450), pt(14.2, 50.2)]; // ~50 m gap
        expect(joinMultiLineString([seg1, seg2], 10)).toBeNull();
        expect(joinMultiLineString([seg1, seg2], 100)).not.toBeNull();
    });
});

// ---------------------------------------------------------------------------
// checkSiteProximity
// ---------------------------------------------------------------------------

const SITE_A = { lat: 50.0, lng: 14.0 };
const SITE_B = { lat: 49.0, lng: 16.0 };
const THRESHOLD = SITE_PROXIMITY_THRESHOLD_METERS; // 100 m

describe('checkSiteProximity', () => {
    test('empty coords returns warnings for both sites', () => {
        const result = checkSiteProximity([], SITE_A, SITE_B, THRESHOLD);
        expect(result.warnA).toBe(true);
        expect(result.warnB).toBe(true);
    });

    test('null coords returns warnings for both sites', () => {
        const result = checkSiteProximity(null, SITE_A, SITE_B, THRESHOLD);
        expect(result.warnA).toBe(true);
        expect(result.warnB).toBe(true);
    });

    test('path starting and ending exactly on sites — no warnings', () => {
        const coords = [
            pt(SITE_A.lng, SITE_A.lat),
            pt(15.0, 49.5),
            pt(SITE_B.lng, SITE_B.lat),
        ];
        const result = checkSiteProximity(coords, SITE_A, SITE_B, THRESHOLD);
        expect(result.warnA).toBe(false);
        expect(result.warnB).toBe(false);
        expect(result.distA).toBe(0);
        expect(result.distB).toBe(0);
    });

    test('first point far from Site A — warnA true, warnB false', () => {
        const coords = [
            pt(16.0, 49.0),          // far from Site A, coincides with Site B
            pt(SITE_B.lng, SITE_B.lat),
        ];
        const result = checkSiteProximity(coords, SITE_A, SITE_B, THRESHOLD);
        expect(result.warnA).toBe(true);
        expect(result.warnB).toBe(false);
    });

    test('last point far from Site B — warnA false, warnB true', () => {
        const coords = [
            pt(SITE_A.lng, SITE_A.lat),
            pt(16.0, 50.0),          // far from Site B
        ];
        const result = checkSiteProximity(coords, SITE_A, SITE_B, THRESHOLD);
        expect(result.warnA).toBe(false);
        expect(result.warnB).toBe(true);
    });

    test('distA is reported in whole metres', () => {
        // Place first point ~200 m north of Site A
        const coords = [
            pt(SITE_A.lng, SITE_A.lat + 0.0018), // ~200 m
            pt(SITE_B.lng, SITE_B.lat),
        ];
        const result = checkSiteProximity(coords, SITE_A, SITE_B, THRESHOLD);
        expect(result.distA).toBeGreaterThan(150);
        expect(result.distA).toBeLessThan(250);
        expect(Number.isInteger(result.distA)).toBe(true);
    });

    test('single-point path checks the one point against both sites', () => {
        const coords = [pt(SITE_A.lng, SITE_A.lat)];
        const result = checkSiteProximity(coords, SITE_A, SITE_B, THRESHOLD);
        expect(result.warnA).toBe(false); // first === Site A
        expect(result.warnB).toBe(true);  // last === first, far from Site B
    });

    test('custom threshold is respected', () => {
        // ~50 m away from both sites — within 100 m, outside 10 m
        const coords = [
            pt(SITE_A.lng, SITE_A.lat + 0.00045), // ~50 m north
            pt(SITE_B.lng, SITE_B.lat + 0.00045),
        ];
        const tight = checkSiteProximity(coords, SITE_A, SITE_B, 10);
        expect(tight.warnA).toBe(true);
        expect(tight.warnB).toBe(true);

        const loose = checkSiteProximity(coords, SITE_A, SITE_B, 100);
        expect(loose.warnA).toBe(false);
        expect(loose.warnB).toBe(false);
    });
});

// ---------------------------------------------------------------------------
// Exported constants
// ---------------------------------------------------------------------------

describe('exported constants', () => {
    test('PATH_JOIN_TOLERANCE_METERS is 10', () => {
        expect(PATH_JOIN_TOLERANCE_METERS).toBe(10);
    });

    test('SITE_PROXIMITY_THRESHOLD_METERS is 100', () => {
        expect(SITE_PROXIMITY_THRESHOLD_METERS).toBe(100);
    });
});
