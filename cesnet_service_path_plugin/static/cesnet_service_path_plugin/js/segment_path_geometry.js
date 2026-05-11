/**
 * segment_path_geometry.js — Pure geometry utilities for the segment path editor.
 *
 * No Leaflet or DOM dependency — fully unit-testable in Node/Jest.
 *
 * Exports:
 *   haversineDistance(lat1, lng1, lat2, lng2) → number (metres)
 *   joinMultiLineString(coordArrays, toleranceMeters) → [lng,lat][] | null
 *   checkSiteProximity(coords, siteA, siteB, thresholdMeters)
 *     → { warnA, warnB, distA, distB }
 *
 * All coordinate arrays follow GeoJSON order: [lng, lat].
 */

(function (root, factory) {
    'use strict';
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = factory();
    } else {
        root.SegmentPathGeometry = factory();
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';

    // -------------------------------------------------------------------------
    // Tunable constants — adjust in code if needed, not via config.
    // -------------------------------------------------------------------------

    /** Maximum gap (metres) between consecutive LineString endpoints to attempt auto-join. */
    const PATH_JOIN_TOLERANCE_METERS = 10;

    /** Maximum distance (metres) from path endpoint to site marker before showing a warning. */
    const SITE_PROXIMITY_THRESHOLD_METERS = 100;

    // -------------------------------------------------------------------------
    // Haversine distance
    // -------------------------------------------------------------------------

    const EARTH_RADIUS_M = 6_371_000;

    /**
     * Returns the great-circle distance in metres between two WGS-84 points.
     * @param {number} lat1
     * @param {number} lng1
     * @param {number} lat2
     * @param {number} lng2
     * @returns {number} distance in metres
     */
    function haversineDistance(lat1, lng1, lat2, lng2) {
        const toRad = (deg) => (deg * Math.PI) / 180;
        const dLat = toRad(lat2 - lat1);
        const dLng = toRad(lng2 - lng1);
        const a =
            Math.sin(dLat / 2) ** 2 +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
        return 2 * EARTH_RADIUS_M * Math.asin(Math.sqrt(a));
    }

    // -------------------------------------------------------------------------
    // Multi-LineString auto-join
    // -------------------------------------------------------------------------

    /**
     * Attempts to join an array of GeoJSON LineString coordinate arrays into a
     * single continuous coordinate array.
     *
     * Each element of coordArrays is an array of [lng, lat] pairs representing
     * one LineString (as stored in a GeoJSON MultiLineString).
     *
     * The algorithm chains segments end-to-start in the order given.  It does
     * NOT attempt reordering or reversal of individual segments (v1 scope).
     *
     * @param {Array<Array<[number, number]>>} coordArrays  — MultiLineString coords
     * @param {number} [toleranceMeters]  — max gap to still consider "connected"
     * @returns {Array<[number, number]> | null}  joined coords, or null if gaps exist
     */
    function joinMultiLineString(coordArrays, toleranceMeters = PATH_JOIN_TOLERANCE_METERS) {
        if (!coordArrays || coordArrays.length === 0) return null;
        if (coordArrays.length === 1) return coordArrays[0].slice();

        const result = coordArrays[0].slice();

        for (let i = 1; i < coordArrays.length; i++) {
            const prev = result[result.length - 1];   // [lng, lat]
            const next = coordArrays[i][0];            // [lng, lat]

            // Haversine expects (lat, lng) — GeoJSON stores [lng, lat].
            const gap = haversineDistance(prev[1], prev[0], next[1], next[0]);

            if (gap > toleranceMeters) return null;

            // Skip the duplicate junction point then append the rest.
            result.push(...coordArrays[i].slice(1));
        }

        return result;
    }

    // -------------------------------------------------------------------------
    // Site proximity check
    // -------------------------------------------------------------------------

    /**
     * Checks whether the first and last points of a drawn path are close enough
     * to the segment's Site A and Site B respectively.
     *
     * @param {Array<[number, number]>} coords  — GeoJSON [lng, lat] pairs
     * @param {{ lat: number, lng: number }} siteA
     * @param {{ lat: number, lng: number }} siteB
     * @param {number} [thresholdMeters]
     * @returns {{ warnA: boolean, distA: number, warnB: boolean, distB: number }}
     */
    function checkSiteProximity(
        coords,
        siteA,
        siteB,
        thresholdMeters = SITE_PROXIMITY_THRESHOLD_METERS,
    ) {
        if (!coords || coords.length === 0) {
            return { warnA: true, distA: Infinity, warnB: true, distB: Infinity };
        }

        const first = coords[0];
        const last  = coords[coords.length - 1];

        const distA = haversineDistance(first[1], first[0], siteA.lat, siteA.lng);
        const distB = haversineDistance(last[1],  last[0],  siteB.lat, siteB.lng);

        return {
            warnA: distA > thresholdMeters,
            distA: Math.round(distA),
            warnB: distB > thresholdMeters,
            distB: Math.round(distB),
        };
    }

    // -------------------------------------------------------------------------

    return {
        PATH_JOIN_TOLERANCE_METERS,
        SITE_PROXIMITY_THRESHOLD_METERS,
        haversineDistance,
        joinMultiLineString,
        checkSiteProximity,
    };
}));
