"""
Tests for the Network Map view filtering logic.

Follows this patterns:
  - django.test.TestCase with setUpTestData
  - Plain dicts passed to FilterSets (same as NetBox convention)
  - Run via: manage.py test cesnet_service_path_plugin.tests.test_map_view_filtering

See configuration_testing.py in this directory for the required Django settings.
"""

from django.test import TestCase

from circuits.models import Provider
from dcim.choices import SiteStatusChoices
from dcim.filtersets import SiteFilterSet
from dcim.models import Region, Site, SiteGroup

from cesnet_service_path_plugin.filtersets import SegmentFilterSet
from cesnet_service_path_plugin.models import Segment
from cesnet_service_path_plugin.models.custom_choices import StatusChoices
from cesnet_service_path_plugin.models.segment_types import SegmentTypeChoices
from cesnet_service_path_plugin.views.map import (
    _extract_segment_params,
    _extract_site_params,
    _remap_params,
)


def make_get(params):
    """
    Return a minimal object whose .lists() method yields (key, [values]) pairs,
    matching the interface of Django's QueryDict used in the view.
    """

    class FakeGET:
        def lists(self):
            for k, v in params.items():
                yield k, v if isinstance(v, list) else [v]

    return FakeGET()


# ---------------------------------------------------------------------------
# _remap_params
# ---------------------------------------------------------------------------


class RemapParamsTest(TestCase):

    def test_passthrough_field_preserved(self):
        result = _remap_params(make_get({"region_id": ["1", "2"]}), mapping={}, passthrough={"region_id"})
        self.assertEqual(result["region_id"], ["1", "2"])

    def test_mapped_field_renamed(self):
        result = _remap_params(
            make_get({"site_status": ["active"]}), mapping={"site_status": "status"}, passthrough=set()
        )
        self.assertNotIn("site_status", result)
        self.assertEqual(result["status"], ["active"])

    def test_unknown_fields_excluded(self):
        result = _remap_params(make_get({"csrftoken": ["x"], "noise": ["y"]}), mapping={}, passthrough={"region_id"})
        self.assertNotIn("csrftoken", result)
        self.assertNotIn("noise", result)

    def test_multiple_values_preserved(self):
        result = _remap_params(make_get({"region_id": ["1", "2", "3"]}), mapping={}, passthrough={"region_id"})
        self.assertEqual(result["region_id"], ["1", "2", "3"])

    def test_empty_input_returns_empty_dict(self):
        result = _remap_params(make_get({}), mapping={}, passthrough={"region_id"})
        self.assertEqual(result, {})


# ---------------------------------------------------------------------------
# _extract_site_params
# ---------------------------------------------------------------------------


class ExtractSiteParamsTest(TestCase):

    def test_region_id_passes_through(self):
        result = _extract_site_params(make_get({"region_id": ["5", "6"]}))
        self.assertEqual(result["region_id"], ["5", "6"])

    def test_site_group_id_remapped(self):
        result = _extract_site_params(make_get({"site_group_id": ["3"]}))
        self.assertNotIn("site_group_id", result)
        self.assertEqual(result["group_id"], ["3"])

    def test_site_status_remapped(self):
        result = _extract_site_params(make_get({"site_status": ["active", "planned"]}))
        self.assertNotIn("site_status", result)
        self.assertEqual(result["status"], ["active", "planned"])

    def test_site_tenant_id_remapped(self):
        result = _extract_site_params(make_get({"site_tenant_id": ["7"]}))
        self.assertNotIn("site_tenant_id", result)
        self.assertEqual(result["tenant_id"], ["7"])

    def test_segment_fields_excluded(self):
        result = _extract_site_params(make_get({"segment_status": ["active"], "segment_type": ["dark_fiber"]}))
        self.assertNotIn("segment_status", result)
        self.assertNotIn("segment_type", result)
        self.assertNotIn("status", result)

    def test_at_any_site_excluded(self):
        result = _extract_site_params(make_get({"at_any_site": ["1"]}))
        self.assertNotIn("at_any_site", result)


# ---------------------------------------------------------------------------
# _extract_segment_params
# ---------------------------------------------------------------------------


class ExtractSegmentParamsTest(TestCase):

    def test_region_id_passes_through(self):
        result = _extract_segment_params(make_get({"region_id": ["5"]}))
        self.assertEqual(result["region_id"], ["5"])

    def test_at_any_site_passes_through(self):
        result = _extract_segment_params(make_get({"at_any_site": ["10", "11"]}))
        self.assertEqual(result["at_any_site"], ["10", "11"])

    def test_segment_status_remapped(self):
        result = _extract_segment_params(make_get({"segment_status": ["active"]}))
        self.assertNotIn("segment_status", result)
        self.assertEqual(result["status"], ["active"])

    def test_segment_type_remapped(self):
        result = _extract_segment_params(make_get({"segment_type": ["dark_fiber"]}))
        self.assertEqual(result["segment_type"], ["dark_fiber"])

    def test_segment_provider_id_remapped(self):
        result = _extract_segment_params(make_get({"segment_provider_id": ["3"]}))
        self.assertNotIn("segment_provider_id", result)
        self.assertEqual(result["provider_id"], ["3"])

    def test_site_fields_excluded(self):
        result = _extract_segment_params(make_get({"site_status": ["active"], "site_tenant_id": ["1"]}))
        self.assertNotIn("site_status", result)
        self.assertNotIn("site_tenant_id", result)
        self.assertNotIn("status", result)

    def test_site_group_id_excluded(self):
        result = _extract_segment_params(make_get({"site_group_id": ["2"]}))
        self.assertNotIn("site_group_id", result)


# ---------------------------------------------------------------------------
# Cross-contamination
# ---------------------------------------------------------------------------


class ParamIsolationTest(TestCase):

    def test_site_and_segment_params_independent(self):
        get = make_get(
            {
                "region_id": ["1"],
                "site_status": ["active"],
                "segment_status": ["planned"],
                "segment_provider_id": ["5"],
                "site_tenant_id": ["3"],
            }
        )
        site_p = _extract_site_params(get)
        seg_p = _extract_segment_params(get)

        self.assertEqual(site_p.get("status"), ["active"])
        self.assertEqual(site_p.get("tenant_id"), ["3"])
        self.assertEqual(site_p.get("region_id"), ["1"])
        self.assertIsNone(site_p.get("provider_id"))

        self.assertEqual(seg_p.get("status"), ["planned"])
        self.assertEqual(seg_p.get("provider_id"), ["5"])
        self.assertEqual(seg_p.get("region_id"), ["1"])
        self.assertIsNone(seg_p.get("tenant_id"))


# ---------------------------------------------------------------------------
# SiteFilterSet integration — remapped params actually filter the queryset
# ---------------------------------------------------------------------------


class SiteFilterSetIntegrationTest(TestCase):

    PREFIX = "TSFI__"  # unique prefix — keeps test objects isolated from production data

    @classmethod
    def setUpTestData(cls):
        p = cls.PREFIX
        cls.region_a = Region.objects.create(name=f"{p}Region A", slug=f"{p.lower()}region-a")
        cls.region_b = Region.objects.create(name=f"{p}Region B", slug=f"{p.lower()}region-b")
        cls.group = SiteGroup.objects.create(name=f"{p}Group X", slug=f"{p.lower()}group-x")

        Site.objects.create(
            name=f"{p}Site-A-Active",
            slug=f"{p.lower()}site-a-active",
            region=cls.region_a,
            group=cls.group,
            status=SiteStatusChoices.STATUS_ACTIVE,
            latitude=49.0,
            longitude=16.0,
        )
        Site.objects.create(
            name=f"{p}Site-A-Planned",
            slug=f"{p.lower()}site-a-planned",
            region=cls.region_a,
            status=SiteStatusChoices.STATUS_PLANNED,
            latitude=49.1,
            longitude=16.1,
        )
        Site.objects.create(
            name=f"{p}Site-B-Active",
            slug=f"{p.lower()}site-b-active",
            region=cls.region_b,
            status=SiteStatusChoices.STATUS_ACTIVE,
            latitude=50.0,
            longitude=15.0,
        )

    def _qs(self):
        """Queryset scoped to test objects only."""
        return Site.objects.filter(name__startswith=self.PREFIX)

    def _filter(self, **kwargs):
        params = _extract_site_params(make_get(kwargs))
        return set(SiteFilterSet(params, self._qs()).qs.values_list("name", flat=True))

    def test_region_filter(self):
        names = self._filter(region_id=[str(self.region_a.pk)])
        self.assertIn(f"{self.PREFIX}Site-A-Active", names)
        self.assertIn(f"{self.PREFIX}Site-A-Planned", names)
        self.assertNotIn(f"{self.PREFIX}Site-B-Active", names)

    def test_status_filter(self):
        names = self._filter(site_status=[SiteStatusChoices.STATUS_PLANNED])
        self.assertIn(f"{self.PREFIX}Site-A-Planned", names)
        self.assertNotIn(f"{self.PREFIX}Site-A-Active", names)
        self.assertNotIn(f"{self.PREFIX}Site-B-Active", names)

    def test_group_filter(self):
        names = self._filter(site_group_id=[str(self.group.pk)])
        self.assertEqual(names, {f"{self.PREFIX}Site-A-Active"})

    def test_combined_region_and_status(self):
        names = self._filter(region_id=[str(self.region_a.pk)], site_status=[SiteStatusChoices.STATUS_ACTIVE])
        self.assertEqual(names, {f"{self.PREFIX}Site-A-Active"})

    def test_empty_params_returns_all(self):
        names = self._filter()
        self.assertEqual(len(names), 3)

    def test_segment_params_do_not_leak_into_site_filter(self):
        names = self._filter(segment_status=["active"])
        self.assertEqual(len(names), 3)


# ---------------------------------------------------------------------------
# SegmentFilterSet integration
# ---------------------------------------------------------------------------


class SegmentFilterSetIntegrationTest(TestCase):

    PREFIX = "TSEG__"  # unique prefix — keeps test objects isolated from production data

    @classmethod
    def setUpTestData(cls):
        p = cls.PREFIX
        cls.region = Region.objects.create(name=f"{p}Region", slug=f"{p.lower()}region")
        cls.provider = Provider.objects.create(name=f"{p}Provider", slug=f"{p.lower()}provider")
        cls.site_a = Site.objects.create(
            name=f"{p}Site-A", slug=f"{p.lower()}site-a", region=cls.region, latitude=49.0, longitude=16.0
        )
        cls.site_b = Site.objects.create(
            name=f"{p}Site-B", slug=f"{p.lower()}site-b", region=cls.region, latitude=49.5, longitude=16.5
        )

        Segment.objects.create(
            name=f"{p}Active",
            status=StatusChoices.ACTIVE,
            segment_type=SegmentTypeChoices.DARK_FIBER,
            ownership_type="leased",
            provider=cls.provider,
            site_a=cls.site_a,
            site_b=cls.site_b,
        )
        Segment.objects.create(
            name=f"{p}Planned",
            status=StatusChoices.PLANNED,
            segment_type=SegmentTypeChoices.OPTICAL_SPECTRUM,
            ownership_type="owned",
            provider=cls.provider,
            site_a=cls.site_a,
            site_b=cls.site_b,
        )

    def _qs(self):
        """Queryset scoped to test objects only."""
        return Segment.objects.filter(name__startswith=self.PREFIX)

    def _filter(self, **kwargs):
        params = _extract_segment_params(make_get(kwargs))
        return set(SegmentFilterSet(params, self._qs()).qs.values_list("name", flat=True))

    def test_status_filter(self):
        names = self._filter(segment_status=[StatusChoices.ACTIVE])
        self.assertIn(f"{self.PREFIX}Active", names)
        self.assertNotIn(f"{self.PREFIX}Planned", names)

    def test_provider_filter(self):
        names = self._filter(segment_provider_id=[str(self.provider.pk)])
        self.assertEqual(len(names), 2)

    def test_at_any_site_filter(self):
        names = self._filter(at_any_site=[str(self.site_a.pk)])
        self.assertEqual(len(names), 2)

    def test_segment_type_filter(self):
        names = self._filter(segment_type=[SegmentTypeChoices.DARK_FIBER])
        self.assertIn(f"{self.PREFIX}Active", names)
        self.assertNotIn(f"{self.PREFIX}Planned", names)

    def test_site_params_do_not_leak_into_segment_filter(self):
        names = self._filter(site_status=["active"])
        self.assertEqual(len(names), 2)

    def test_empty_params_returns_all(self):
        names = self._filter()
        self.assertEqual(len(names), 2)
