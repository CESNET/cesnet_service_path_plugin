"""
Tests for the path_geometry write field on SegmentSerializer.

Covers the manual draw-path API: PATCH with a GeoJSON LineString geometry
object, validation errors, and interaction with the existing path_file field.

Run inside the NetBox container:
    NETBOX_CONFIGURATION=netbox.configuration_testing \
    python manage.py test cesnet_service_path_plugin.tests.test_segment_path_geometry_api -v2 --keepdb
"""

from circuits.models import Provider
from dcim.models import Site
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from users.constants import TOKEN_PREFIX
from users.models import ObjectPermission, Token, User

from cesnet_service_path_plugin.models import Segment


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_segment(name, provider, site_a, site_b):
    return Segment.objects.create(
        name=name,
        status="active",
        segment_type="dark_fiber",
        ownership_type="leased",
        provider=provider,
        site_a=site_a,
        site_b=site_b,
    )


def _segment_detail_url(pk):
    return reverse("plugins-api:cesnet_service_path_plugin-api:segment-detail", kwargs={"pk": pk})


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class _APIBase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        cls.provider = Provider.objects.create(name="GEO__Provider", slug="geo__provider")
        cls.site_a = Site.objects.create(name="GEO__Site-A", slug="geo__site-a")
        cls.site_b = Site.objects.create(name="GEO__Site-B", slug="geo__site-b")

    def setUp(self):
        self.user = User.objects.create_user(username="geo_api_user")

        ct = ContentType.objects.get(app_label="cesnet_service_path_plugin", model="segment")
        for action in ("view", "add", "change", "delete"):
            perm, _ = ObjectPermission.objects.get_or_create(
                name=f"geo_test_{action}_segment",
                defaults={"actions": [action]},
            )
            perm.object_types.set([ct])
            perm.users.add(self.user)

        self.token = Token.objects.create(user=self.user)
        self.header = {
            "HTTP_AUTHORIZATION": f"Bearer {TOKEN_PREFIX}{self.token.key}.{self.token.token}"
        }


# ---------------------------------------------------------------------------
# path_geometry write field tests
# ---------------------------------------------------------------------------

# A minimal valid LineString that crosses Central Europe.
VALID_LINESTRING = {
    "type": "LineString",
    "coordinates": [
        [14.0, 50.0],
        [15.0, 49.5],
        [16.0, 49.0],
    ],
}


class PathGeometryWriteTest(_APIBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.segment = _make_segment("GEO__Seg", cls.provider, cls.site_a, cls.site_b)

    def _patch(self, data):
        url = _segment_detail_url(self.segment.pk)
        return self.client.patch(url, data, format="json", **self.header)

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    def test_valid_linestring_returns_200(self):
        response = self._patch({"path_geometry": VALID_LINESTRING})
        self.assertEqual(response.status_code, 200, response.data)

    def test_valid_linestring_sets_source_format_to_manual(self):
        self._patch({"path_geometry": VALID_LINESTRING})
        self.segment.refresh_from_db()
        self.assertEqual(self.segment.path_source_format, "manual")

    def test_valid_linestring_stores_geometry_as_multilinestring(self):
        self._patch({"path_geometry": VALID_LINESTRING})
        self.segment.refresh_from_db()
        self.assertTrue(self.segment.has_path_data())
        self.assertEqual(self.segment.path_geometry.geom_type, "MultiLineString")

    def test_valid_linestring_recalculates_path_length(self):
        self._patch({"path_geometry": VALID_LINESTRING})
        self.segment.refresh_from_db()
        self.assertIsNotNone(self.segment.path_length_km)
        self.assertGreater(self.segment.path_length_km, 0)

    def test_stored_coordinates_match_input(self):
        self._patch({"path_geometry": VALID_LINESTRING})
        self.segment.refresh_from_db()
        # MultiLineString wraps a single LineString — check first sub-line.
        stored_coords = list(self.segment.path_geometry[0].coords)
        expected = [tuple(c) for c in VALID_LINESTRING["coordinates"]]
        self.assertEqual(stored_coords, expected)

    # ------------------------------------------------------------------
    # Absent field — no-op
    # ------------------------------------------------------------------

    def test_patch_without_path_geometry_leaves_geometry_unchanged(self):
        # Pre-set some geometry.
        self._patch({"path_geometry": VALID_LINESTRING})
        self.segment.refresh_from_db()
        original_length = self.segment.path_length_km

        # PATCH an unrelated field — geometry must not change.
        self._patch({"path_notes": "updated notes"})
        self.segment.refresh_from_db()
        self.assertEqual(self.segment.path_length_km, original_length)
        self.assertEqual(self.segment.path_source_format, "manual")

    # ------------------------------------------------------------------
    # Validation errors → 400
    # ------------------------------------------------------------------

    def test_non_linestring_type_returns_400(self):
        response = self._patch({
            "path_geometry": {
                "type": "Point",
                "coordinates": [14.0, 50.0],
            }
        })
        self.assertEqual(response.status_code, 400)

    def test_multilinestring_type_returns_400(self):
        response = self._patch({
            "path_geometry": {
                "type": "MultiLineString",
                "coordinates": [[[14.0, 50.0], [15.0, 49.5]]],
            }
        })
        self.assertEqual(response.status_code, 400)

    def test_missing_type_key_returns_400(self):
        response = self._patch({
            "path_geometry": {
                "coordinates": [[14.0, 50.0], [15.0, 49.5]],
            }
        })
        self.assertEqual(response.status_code, 400)

    def test_single_point_linestring_returns_400(self):
        response = self._patch({
            "path_geometry": {
                "type": "LineString",
                "coordinates": [[14.0, 50.0]],
            }
        })
        self.assertEqual(response.status_code, 400)

    def test_empty_coordinates_returns_400(self):
        response = self._patch({
            "path_geometry": {
                "type": "LineString",
                "coordinates": [],
            }
        })
        self.assertEqual(response.status_code, 400)

    def test_non_dict_geometry_returns_400(self):
        response = self._patch({"path_geometry": "not a dict"})
        self.assertEqual(response.status_code, 400)

    def test_invalid_coordinate_values_returns_400(self):
        response = self._patch({
            "path_geometry": {
                "type": "LineString",
                "coordinates": [["bad", "data"], [15.0, 49.5]],
            }
        })
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------
    # Geometry is not exposed in list serializer response
    # ------------------------------------------------------------------

    def test_path_geometry_not_in_response_body(self):
        response = self._patch({"path_geometry": VALID_LINESTRING})
        self.assertEqual(response.status_code, 200)
        # path_geometry is write_only — must not appear in the response.
        self.assertNotIn("path_geometry", response.data)

    # ------------------------------------------------------------------
    # has_path_data reflects new geometry
    # ------------------------------------------------------------------

    def test_has_path_data_true_after_write(self):
        # Start with a fresh segment with no geometry.
        seg = _make_segment("GEO__NoPth", self.provider, self.site_a, self.site_b)
        url = _segment_detail_url(seg.pk)
        response = self.client.patch(
            url,
            {"path_geometry": VALID_LINESTRING},
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["has_path_data"])
        seg.delete()
