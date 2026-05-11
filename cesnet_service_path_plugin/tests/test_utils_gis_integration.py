"""
Integration tests for cesnet_service_path_plugin.utils.utils_gis

Requires a running PostGIS database. Run inside the NetBox container:

    NETBOX_CONFIGURATION=netbox.configuration_testing \
    python manage.py test \
      cesnet_service_path_plugin.tests.test_utils_gis_integration \
      -v2 --keepdb

Fixtures are synthetic files in unit_tests/fixtures/gis/ — no real network data.
"""

import json
from pathlib import Path

import geopandas as gpd
from django.contrib.gis.geos import LineString, MultiLineString
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from shapely.geometry import LineString as ShapelyLineString, MultiLineString as ShapelyMultiLineString

from cesnet_service_path_plugin.utils.utils_gis import (
    gdf_to_multilinestring,
    process_path_file,
    validate_path_geometry,
    ensure_2d_geometry,
    export_segment_paths_as_geojson,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "gis"
SAMPLE_GEOJSON = FIXTURES_DIR / "sample.geojson"
SAMPLE_KML = FIXTURES_DIR / "sample.kml"
SAMPLE_KMZ = FIXTURES_DIR / "sample.kmz"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_line_gdf(*coord_lists, has_z=False):
    """Build a GeoDataFrame with LineString geometries from coordinate lists."""
    if has_z:
        geoms = [ShapelyLineString(coords) for coords in coord_lists]
    else:
        geoms = [ShapelyLineString(coords) for coords in coord_lists]
    return gpd.GeoDataFrame(geometry=geoms, crs="EPSG:4326")


def _uploaded_file(path: Path) -> SimpleUploadedFile:
    """Wrap a fixture file as a Django SimpleUploadedFile."""
    return SimpleUploadedFile(path.name, path.read_bytes())


# ---------------------------------------------------------------------------
# gdf_to_multilinestring
# ---------------------------------------------------------------------------

class GdfToMultilinestringTest(TestCase):

    def test_simple_linestring_gdf_returns_multilinestring(self):
        gdf = _make_line_gdf(
            [(14.1, 50.1), (14.2, 50.2), (14.3, 50.3)],
        )
        result = gdf_to_multilinestring(gdf)
        self.assertIsInstance(result, MultiLineString)

    def test_result_has_correct_srid(self):
        gdf = _make_line_gdf([(14.1, 50.1), (14.2, 50.2)])
        result = gdf_to_multilinestring(gdf)
        self.assertEqual(result.srid, 4326)

    def test_multiple_lines_all_preserved(self):
        gdf = _make_line_gdf(
            [(14.1, 50.1), (14.2, 50.2)],
            [(15.1, 49.8), (15.2, 49.9)],
        )
        result = gdf_to_multilinestring(gdf)
        self.assertEqual(result.num_geom, 2)

    def test_3d_coordinates_are_stripped_to_2d(self):
        gdf = _make_line_gdf(
            [(14.1, 50.1, 200.0), (14.2, 50.2, 210.0), (14.3, 50.3, 220.0)],
            has_z=True,
        )
        result = gdf_to_multilinestring(gdf)
        for line in result:
            for coord in line.coords:
                self.assertEqual(len(coord), 2, f"Expected 2D coord, got {coord}")

    def test_multilinestring_geometry_is_handled(self):
        gdf = gpd.GeoDataFrame(
            geometry=[ShapelyMultiLineString([
                [(14.1, 50.1), (14.2, 50.2)],
                [(14.2, 50.2), (14.3, 50.3)],
            ])],
            crs="EPSG:4326",
        )
        result = gdf_to_multilinestring(gdf)
        self.assertIsInstance(result, MultiLineString)
        self.assertGreaterEqual(result.num_geom, 1)

    def test_empty_gdf_raises_validation_error(self):
        gdf = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        with self.assertRaises(ValidationError):
            gdf_to_multilinestring(gdf)

    def test_non_line_geometry_raises_with_type_name(self):
        from shapely.geometry import Point
        gdf = gpd.GeoDataFrame(geometry=[Point(14.1, 50.1)], crs="EPSG:4326")
        with self.assertRaises(ValidationError) as ctx:
            gdf_to_multilinestring(gdf)
        self.assertIn("Point", str(ctx.exception))


# ---------------------------------------------------------------------------
# validate_path_geometry
# ---------------------------------------------------------------------------

class ValidatePathGeometryTest(TestCase):

    def _make_multilinestring(self):
        return MultiLineString(
            LineString([(14.1, 50.1), (14.2, 50.2), (14.3, 50.3)], srid=4326),
            srid=4326,
        )

    def test_valid_multilinestring_passes(self):
        mls = self._make_multilinestring()
        # Should not raise
        validate_path_geometry(mls)

    def test_empty_geometry_raises(self):
        with self.assertRaises(ValidationError):
            validate_path_geometry(None)

    def test_wrong_type_raises(self):
        line = LineString([(14.1, 50.1), (14.2, 50.2)], srid=4326)
        with self.assertRaises(ValidationError):
            validate_path_geometry(line)


# ---------------------------------------------------------------------------
# ensure_2d_geometry
# ---------------------------------------------------------------------------

class Ensure2dGeometryTest(TestCase):

    def test_3d_multilinestring_is_flattened(self):
        mls = MultiLineString(
            LineString([(14.1, 50.1, 200.0), (14.2, 50.2, 210.0)], srid=4326),
            srid=4326,
        )
        result = ensure_2d_geometry(mls)
        for line in result:
            for coord in line.coords:
                self.assertEqual(len(coord), 2)

    def test_2d_geometry_returned_unchanged(self):
        mls = MultiLineString(
            LineString([(14.1, 50.1), (14.2, 50.2)], srid=4326),
            srid=4326,
        )
        result = ensure_2d_geometry(mls)
        self.assertIs(result, mls)


# ---------------------------------------------------------------------------
# process_path_file — full round-trip
# ---------------------------------------------------------------------------

class ProcessPathFileTest(TestCase):

    def _wrap(self, path: Path) -> SimpleUploadedFile:
        return _uploaded_file(path)

    def test_geojson_file_round_trip(self):
        uploaded = self._wrap(SAMPLE_GEOJSON)
        result = process_path_file(uploaded, "geojson")
        self.assertIsInstance(result, MultiLineString)
        self.assertGreater(result.num_geom, 0)

    def test_kml_file_round_trip(self):
        uploaded = self._wrap(SAMPLE_KML)
        result = process_path_file(uploaded, "kml")
        self.assertIsInstance(result, MultiLineString)
        self.assertGreater(result.num_geom, 0)

    def test_kmz_file_round_trip(self):
        uploaded = self._wrap(SAMPLE_KMZ)
        result = process_path_file(uploaded, "kmz")
        self.assertIsInstance(result, MultiLineString)
        self.assertGreater(result.num_geom, 0)

    def test_result_is_always_2d(self):
        # GeoJSON fixture contains 3D coords — result must be 2D
        uploaded = self._wrap(SAMPLE_GEOJSON)
        result = process_path_file(uploaded, "geojson")
        for line in result:
            for coord in line.coords:
                self.assertEqual(len(coord), 2, f"Expected 2D coord, got {coord}")

    def test_result_srid_is_4326(self):
        uploaded = self._wrap(SAMPLE_GEOJSON)
        result = process_path_file(uploaded, "geojson")
        self.assertEqual(result.srid, 4326)

    def test_unsupported_format_raises_validation_error(self):
        uploaded = SimpleUploadedFile("data.shp", b"dummy content")
        with self.assertRaises(ValidationError):
            process_path_file(uploaded, "shp")


# ---------------------------------------------------------------------------
# export_segment_paths_as_geojson
# ---------------------------------------------------------------------------

class ExportSegmentPathsTest(TestCase):

    def _make_mock_segment(self, name, coords_per_line):
        """Return a minimal mock object that satisfies export_segment_paths_as_geojson."""
        class MockLine:
            def __init__(self, coords):
                self.coords = coords

        class MockMultiLineString:
            def __init__(self, lines):
                self._lines = lines

            def __iter__(self):
                return iter(self._lines)

        class MockSegment:
            def __init__(self, seg_name, lines):
                self.name = seg_name
                self.pk = 1
                self.network_label = "TEST"
                self.status = "active"
                self.path_length_km = None
                self.provider = "TestProvider"
                self.site_a = "SiteA"
                self.site_b = "SiteB"
                self.path_geometry = MockMultiLineString(
                    [MockLine(coords) for coords in lines]
                )

            def get_path_segment_count(self):
                return len(self.path_geometry._lines)

            def get_total_points(self):
                return sum(len(l.coords) for l in self.path_geometry._lines)

        return MockSegment(name, coords_per_line)

    def test_export_returns_valid_geojson_string(self):
        seg = self._make_mock_segment(
            "Seg1",
            [[(14.1, 50.1), (14.2, 50.2), (14.3, 50.3)]],
        )
        result = export_segment_paths_as_geojson([seg])
        parsed = json.loads(result)
        self.assertEqual(parsed["type"], "FeatureCollection")
        self.assertEqual(len(parsed["features"]), 1)

    def test_export_empty_list_returns_feature_collection(self):
        result = export_segment_paths_as_geojson([])
        parsed = json.loads(result)
        self.assertEqual(parsed["type"], "FeatureCollection")
        self.assertEqual(parsed["features"], [])

    def test_export_multiple_segments(self):
        segments = [
            self._make_mock_segment("Seg1", [[(14.1, 50.1), (14.2, 50.2)]]),
            self._make_mock_segment("Seg2", [[(15.1, 49.8), (15.2, 49.9)]]),
        ]
        result = export_segment_paths_as_geojson(segments)
        parsed = json.loads(result)
        self.assertEqual(len(parsed["features"]), 2)
