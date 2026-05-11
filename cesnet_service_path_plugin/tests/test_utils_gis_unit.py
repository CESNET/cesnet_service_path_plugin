"""
Unit-style tests for cesnet_service_path_plugin.utils.utils_gis

These tests do NOT interact with the database. They cover pure-Python logic:
file format detection, KMZ extraction, KML layer reading, and coordinate
stripping. Uses Django's SimpleTestCase so no DB setup is required.

Run with:
    make test-module m=test_utils_gis_unit
"""

import tempfile
import zipfile
from pathlib import Path

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from cesnet_service_path_plugin.utils.utils_gis import (
    determine_file_format_from_extension,
    ensure_2d_geometry,
    extract_all_kml_from_kmz,
    read_all_kml_layers,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "gis"
SAMPLE_KML = FIXTURES_DIR / "sample.kml"
SAMPLE_KMZ = FIXTURES_DIR / "sample.kmz"

_KML_STUB = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
    '<Placemark><name>X</name>'
    '<LineString><coordinates>14.1,50.1,0 14.2,50.2,0</coordinates></LineString>'
    '</Placemark></Document></kml>'
)


# ---------------------------------------------------------------------------
# determine_file_format_from_extension
# ---------------------------------------------------------------------------

class DetermineFileFormatTest(SimpleTestCase):

    def test_geojson_extension(self):
        self.assertEqual(determine_file_format_from_extension("path.geojson"), "geojson")

    def test_json_extension(self):
        self.assertEqual(determine_file_format_from_extension("path.json"), "geojson")

    def test_kml_extension(self):
        self.assertEqual(determine_file_format_from_extension("route.kml"), "kml")

    def test_kmz_extension(self):
        self.assertEqual(determine_file_format_from_extension("route.kmz"), "kmz")

    def test_uppercase_geojson(self):
        self.assertEqual(determine_file_format_from_extension("PATH.GEOJSON"), "geojson")

    def test_uppercase_kml(self):
        self.assertEqual(determine_file_format_from_extension("ROUTE.KML"), "kml")

    def test_uppercase_kmz(self):
        self.assertEqual(determine_file_format_from_extension("ROUTE.KMZ"), "kmz")

    def test_unsupported_extension_raises(self):
        with self.assertRaises(ValidationError):
            determine_file_format_from_extension("data.shp")

    def test_no_extension_raises(self):
        with self.assertRaises(ValidationError):
            determine_file_format_from_extension("noextension")


# ---------------------------------------------------------------------------
# extract_all_kml_from_kmz
# ---------------------------------------------------------------------------

class ExtractKmlFromKmzTest(SimpleTestCase):

    def test_extracts_at_least_one_kml_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = extract_all_kml_from_kmz(str(SAMPLE_KMZ), tmp)
            self.assertGreaterEqual(len(result), 1)

    def test_output_files_exist_and_are_nonempty(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = extract_all_kml_from_kmz(str(SAMPLE_KMZ), tmp)
            for path in result:
                self.assertTrue(Path(path).exists())
                self.assertGreater(Path(path).stat().st_size, 0)

    def test_output_files_have_kml_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = extract_all_kml_from_kmz(str(SAMPLE_KMZ), tmp)
            for path in result:
                self.assertTrue(path.endswith(".kml"), path)

    def test_duplicate_filenames_get_counter_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            kmz_path = Path(tmp) / "multi.kmz"
            with zipfile.ZipFile(kmz_path, "w") as zf:
                zf.writestr("dir_a/doc.kml", _KML_STUB)
                zf.writestr("dir_b/doc.kml", _KML_STUB)

            out_dir = Path(tmp) / "out"
            out_dir.mkdir()
            result = extract_all_kml_from_kmz(str(kmz_path), str(out_dir))
            self.assertEqual(len(result), 2)
            self.assertNotEqual(result[0], result[1])

    def test_kmz_without_kml_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            kmz_path = Path(tmp) / "empty.kmz"
            with zipfile.ZipFile(kmz_path, "w") as zf:
                zf.writestr("readme.txt", "no kml here")
            with self.assertRaises(FileNotFoundError):
                extract_all_kml_from_kmz(str(kmz_path), tmp)


# ---------------------------------------------------------------------------
# read_all_kml_layers
# ---------------------------------------------------------------------------

class ReadAllKmlLayersTest(SimpleTestCase):

    def test_returns_list(self):
        result = read_all_kml_layers(str(SAMPLE_KML))
        self.assertIsInstance(result, list)

    def test_returns_nonempty_list(self):
        result = read_all_kml_layers(str(SAMPLE_KML))
        self.assertGreaterEqual(len(result), 1)

    def test_dataframes_are_nonempty(self):
        result = read_all_kml_layers(str(SAMPLE_KML))
        for gdf in result:
            self.assertFalse(gdf.empty)

    def test_source_kml_metadata_column_present(self):
        result = read_all_kml_layers(str(SAMPLE_KML))
        for gdf in result:
            self.assertIn("source_kml", gdf.columns)

    def test_source_layer_metadata_column_present(self):
        result = read_all_kml_layers(str(SAMPLE_KML))
        for gdf in result:
            self.assertIn("source_layer", gdf.columns)

    def test_source_kml_value_matches_filename(self):
        result = read_all_kml_layers(str(SAMPLE_KML))
        for gdf in result:
            self.assertEqual(gdf["source_kml"].iloc[0], SAMPLE_KML.name)

    def test_nonexistent_file_returns_empty_list(self):
        result = read_all_kml_layers("/tmp/does_not_exist_xyz.kml")
        self.assertEqual(result, [])

    def test_kmz_layers_readable_after_extraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            kml_files = extract_all_kml_from_kmz(str(SAMPLE_KMZ), tmp)
            self.assertGreaterEqual(len(kml_files), 1)
            result = read_all_kml_layers(kml_files[0])
            self.assertGreaterEqual(len(result), 1)
            self.assertFalse(result[0].empty)


# ---------------------------------------------------------------------------
# ensure_2d_geometry  (uses Django GIS objects but no DB queries)
# ---------------------------------------------------------------------------

class Ensure2dGeometryTest(SimpleTestCase):

    def _make_mls(self, coord_lists):
        from django.contrib.gis.geos import LineString, MultiLineString
        lines = [LineString(coords, srid=4326) for coords in coord_lists]
        return MultiLineString(*lines, srid=4326)

    def test_3d_geometry_is_flattened_to_2d(self):
        mls = self._make_mls([
            [(14.1, 50.1, 200.0), (14.2, 50.2, 210.0), (14.3, 50.3, 220.0)],
        ])
        result = ensure_2d_geometry(mls)
        for line in result:
            for coord in line.coords:
                self.assertEqual(len(coord), 2, f"Expected 2D coord, got {coord}")

    def test_2d_geometry_returned_unchanged(self):
        mls = self._make_mls([[(14.1, 50.1), (14.2, 50.2)]])
        result = ensure_2d_geometry(mls)
        self.assertIs(result, mls)
