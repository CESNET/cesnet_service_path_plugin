"""
Tests for type-specific segment data API endpoints and model validation.

Covers DarkFiberSegmentData, EthernetServiceSegmentData, and OpticalSpectrumSegmentData.

Run inside the NetBox container:
    NETBOX_CONFIGURATION=netbox.configuration_testing \
    python manage.py test cesnet_service_path_plugin.tests.test_type_specific_data_api -v2 --keepdb
"""

from decimal import Decimal

from circuits.models import Provider
from dcim.models import Site
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from users.constants import TOKEN_PREFIX
from users.models import ObjectPermission, Token, User
from utilities.testing import disable_warnings

from cesnet_service_path_plugin.models import (
    DarkFiberSegmentData,
    EthernetServiceSegmentData,
    OpticalSpectrumSegmentData,
    Segment,
)
from cesnet_service_path_plugin.models.segment_types import SegmentTypeChoices


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_segment(name, segment_type, provider, site_a, site_b):
    return Segment.objects.create(
        name=name,
        status="active",
        segment_type=segment_type,
        ownership_type="leased",
        provider=provider,
        site_a=site_a,
        site_b=site_b,
    )


class _APIBase(TestCase):
    """
    Minimal API test base: creates a user with full plugin permissions and
    wires up a Bearer token header so self.client (DRF APIClient) can hit the API.
    """
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        cls.provider = Provider.objects.create(name="TEST__Provider", slug="test__provider")
        cls.site_a = Site.objects.create(name="TEST__Site-A", slug="test__site-a")
        cls.site_b = Site.objects.create(name="TEST__Site-B", slug="test__site-b")

    def setUp(self):
        self.user = User.objects.create_user(username="test_api_user")

        plugin_models = [
            "segment",
            "darkfibersegmentdata",
            "ethernetservicesegmentdata",
            "opticalspectrumsegmentdata",
        ]
        for action in ("view", "add", "change", "delete"):
            for model_name in plugin_models:
                ct = ContentType.objects.get(
                    app_label="cesnet_service_path_plugin",
                    model=model_name,
                )
                perm, _ = ObjectPermission.objects.get_or_create(
                    name=f"test_{action}_{model_name}",
                    defaults={"actions": [action]},
                )
                perm.object_types.set([ct])
                perm.users.add(self.user)

        self.token = Token.objects.create(user=self.user)
        self.header = {"HTTP_AUTHORIZATION": f"Bearer {TOKEN_PREFIX}{self.token.key}.{self.token.token}"}


# ---------------------------------------------------------------------------
# Dark Fiber Data — model tests
# ---------------------------------------------------------------------------

class DarkFiberDataModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        provider = Provider.objects.create(name="DF__Provider", slug="df__provider")
        site_a = Site.objects.create(name="DF__Site-A", slug="df__site-a")
        site_b = Site.objects.create(name="DF__Site-B", slug="df__site-b")
        cls.segment = _make_segment("DF__Seg", SegmentTypeChoices.DARK_FIBER, provider, site_a, site_b)

    def test_create_and_str(self):
        df = DarkFiberSegmentData.objects.create(
            segment=self.segment,
            fiber_mode="single_mode",
            total_loss=Decimal("8.5"),
        )
        self.assertIn(self.segment.name, str(df))
        df.delete()

    def test_cascade_delete(self):
        seg = _make_segment(
            "DF__Cascade", SegmentTypeChoices.DARK_FIBER,
            self.segment.provider, self.segment.site_a, self.segment.site_b,
        )
        df = DarkFiberSegmentData.objects.create(segment=seg, fiber_mode="single_mode")
        df_pk = df.pk
        seg.delete()
        self.assertFalse(DarkFiberSegmentData.objects.filter(pk=df_pk).exists())

    def test_single_mode_subtype_valid(self):
        df = DarkFiberSegmentData(
            segment=self.segment,
            fiber_mode="single_mode",
            single_mode_subtype="g652d",
        )
        df.clean()  # should not raise

    def test_multimode_subtype_on_single_mode_raises(self):
        df = DarkFiberSegmentData(
            segment=self.segment,
            fiber_mode="single_mode",
            multimode_subtype="om3",
        )
        with self.assertRaises(ValidationError) as ctx:
            df.clean()
        self.assertIn("multimode_subtype", ctx.exception.message_dict)

    def test_single_mode_subtype_on_multimode_raises(self):
        df = DarkFiberSegmentData(
            segment=self.segment,
            fiber_mode="multimode",
            single_mode_subtype="g652d",
        )
        with self.assertRaises(ValidationError) as ctx:
            df.clean()
        self.assertIn("single_mode_subtype", ctx.exception.message_dict)

    def test_onetoone_uniqueness(self):
        DarkFiberSegmentData.objects.create(segment=self.segment, fiber_mode="single_mode")
        with self.assertRaises(Exception):
            with transaction.atomic():
                DarkFiberSegmentData.objects.create(segment=self.segment, fiber_mode="multimode")


# ---------------------------------------------------------------------------
# Dark Fiber Data — API tests
# ---------------------------------------------------------------------------

class DarkFiberDataAPITest(_APIBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.segment = _make_segment(
            "DF__API__Seg", SegmentTypeChoices.DARK_FIBER, cls.provider, cls.site_a, cls.site_b
        )

    def _list_url(self):
        return reverse("plugins-api:cesnet_service_path_plugin-api:darkfibersegmentdata-list")

    def _detail_url(self, segment):
        return reverse(
            "plugins-api:cesnet_service_path_plugin-api:darkfibersegmentdata-detail",
            kwargs={"segment_id": segment.pk},
        )

    def _segment_url(self, segment):
        return reverse(
            "plugins-api:cesnet_service_path_plugin-api:segment-detail",
            kwargs={"pk": segment.pk},
        )

    def test_create(self):
        response = self.client.post(
            self._list_url(),
            {
                "segment_id": self.segment.pk,
                "fiber_mode": "single_mode",
                "single_mode_subtype": "g652d",
                "jacket_type": "outdoor",
                "fiber_attenuation_max": "0.25",
                "total_loss": "8.5",
                "total_length": "125.5",
                "number_of_fibers": 48,
                "connector_type_side_a": "lc-apc",
                "connector_type_side_b": "sc-apc",
            },
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, 201, response.data)
        data = response.data
        self.assertEqual(data["segment"]["id"], self.segment.pk)
        self.assertEqual(data["fiber_mode"], "single_mode")
        self.assertEqual(data["single_mode_subtype"], "g652d")
        self.assertEqual(Decimal(data["total_loss"]), Decimal("8.5"))
        self.assertIn("created", data)
        DarkFiberSegmentData.objects.filter(segment=self.segment).delete()

    def test_retrieve(self):
        df = DarkFiberSegmentData.objects.create(
            segment=self.segment, fiber_mode="single_mode", total_loss=Decimal("8.5")
        )
        response = self.client.get(self._detail_url(self.segment), **self.header)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["segment"]["id"], self.segment.pk)
        self.assertEqual(Decimal(response.data["total_loss"]), Decimal("8.5"))
        df.delete()

    def test_segment_type_specific_data_populated(self):
        """Segment detail endpoint must include populated type_specific_data."""
        df = DarkFiberSegmentData.objects.create(
            segment=self.segment, fiber_mode="single_mode", total_loss=Decimal("8.5")
        )
        response = self.client.get(self._segment_url(self.segment), **self.header)
        self.assertEqual(response.status_code, 200)
        tsd = response.data["type_specific_data"]
        self.assertIsNotNone(tsd)
        self.assertEqual(tsd["segment"]["id"], self.segment.pk)
        self.assertEqual(tsd["fiber_mode"], "single_mode")
        df.delete()

    def test_segment_type_specific_data_none_when_absent(self):
        response = self.client.get(self._segment_url(self.segment), **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["type_specific_data"])

    def test_update(self):
        df = DarkFiberSegmentData.objects.create(
            segment=self.segment, fiber_mode="single_mode",
            total_loss=Decimal("8.5"), number_of_fibers=48,
        )
        response = self.client.patch(
            self._detail_url(self.segment),
            {"total_loss": "7.2", "number_of_fibers": 96},
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(Decimal(response.data["total_loss"]), Decimal("7.2"))
        self.assertEqual(response.data["number_of_fibers"], 96)
        df.delete()

    def test_delete(self):
        df = DarkFiberSegmentData.objects.create(segment=self.segment, fiber_mode="single_mode")
        response = self.client.delete(self._detail_url(self.segment), **self.header)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(DarkFiberSegmentData.objects.filter(segment=self.segment).exists())
        self.assertTrue(Segment.objects.filter(pk=self.segment.pk).exists())

    def test_create_duplicate_rejected(self):
        df = DarkFiberSegmentData.objects.create(segment=self.segment, fiber_mode="single_mode")
        with disable_warnings("django.request"):
            response = self.client.post(
                self._list_url(),
                {"segment_id": self.segment.pk, "fiber_mode": "multimode"},
                format="json",
                **self.header,
            )
        self.assertEqual(response.status_code, 400)
        df.delete()

    def test_wrong_subtype_rejected(self):
        """single_mode + multimode_subtype must be rejected at the API level."""
        with disable_warnings("django.request"):
            response = self.client.post(
                self._list_url(),
                {
                    "segment_id": self.segment.pk,
                    "fiber_mode": "single_mode",
                    "multimode_subtype": "om3",
                },
                format="json",
                **self.header,
            )
        self.assertEqual(response.status_code, 400)

    def test_retrieve_after_segment_delete_returns_404(self):
        seg = _make_segment(
            "DF__API__Del", SegmentTypeChoices.DARK_FIBER, self.provider, self.site_a, self.site_b
        )
        DarkFiberSegmentData.objects.create(segment=seg, fiber_mode="single_mode")
        detail_url = self._detail_url(seg)
        seg.delete()  # cascades to DarkFiberSegmentData
        response = self.client.get(detail_url, **self.header)
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# Ethernet Service Data — model tests
# ---------------------------------------------------------------------------

class EthernetServiceDataModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        provider = Provider.objects.create(name="ES__Provider", slug="es__provider")
        site_a = Site.objects.create(name="ES__Site-A", slug="es__site-a")
        site_b = Site.objects.create(name="ES__Site-B", slug="es__site-b")
        cls.segment = _make_segment(
            "ES__Seg", SegmentTypeChoices.ETHERNET_SERVICE, provider, site_a, site_b
        )

    def test_create_and_str(self):
        es = EthernetServiceSegmentData.objects.create(segment=self.segment, port_speed=10000)
        self.assertIn(self.segment.name, str(es))
        self.assertIn("10000", str(es))
        es.delete()

    def test_cascade_delete(self):
        seg = _make_segment(
            "ES__Cascade", SegmentTypeChoices.ETHERNET_SERVICE,
            self.segment.provider, self.segment.site_a, self.segment.site_b,
        )
        es = EthernetServiceSegmentData.objects.create(segment=seg, port_speed=1000)
        es_pk = es.pk
        seg.delete()
        self.assertFalse(EthernetServiceSegmentData.objects.filter(pk=es_pk).exists())

    def test_vlan_id_zero_raises(self):
        es = EthernetServiceSegmentData(segment=self.segment, vlan_id=0)
        with self.assertRaises(ValidationError) as ctx:
            es.clean()
        self.assertIn("vlan_id", ctx.exception.message_dict)

    def test_vlan_id_4095_raises(self):
        es = EthernetServiceSegmentData(segment=self.segment, vlan_id=4095)
        with self.assertRaises(ValidationError) as ctx:
            es.clean()
        self.assertIn("vlan_id", ctx.exception.message_dict)

    def test_mtu_below_576_raises(self):
        es = EthernetServiceSegmentData(segment=self.segment, mtu_size=500)
        with self.assertRaises(ValidationError) as ctx:
            es.clean()
        self.assertIn("mtu_size", ctx.exception.message_dict)

    def test_vlan_tags_non_numeric_raises(self):
        es = EthernetServiceSegmentData(segment=self.segment, vlan_tags="100,abc,300")
        with self.assertRaises(ValidationError) as ctx:
            es.clean()
        self.assertIn("vlan_tags", ctx.exception.message_dict)

    def test_valid_data_passes_clean(self):
        es = EthernetServiceSegmentData(
            segment=self.segment,
            port_speed=10000,
            vlan_id=100,
            vlan_tags="100,200,300",
            mtu_size=9000,
        )
        es.clean()  # should not raise


# ---------------------------------------------------------------------------
# Ethernet Service Data — API tests
# ---------------------------------------------------------------------------

class EthernetServiceDataAPITest(_APIBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.segment = _make_segment(
            "ES__API__Seg", SegmentTypeChoices.ETHERNET_SERVICE, cls.provider, cls.site_a, cls.site_b
        )

    def _list_url(self):
        return reverse("plugins-api:cesnet_service_path_plugin-api:ethernetservicesegmentdata-list")

    def _detail_url(self, segment):
        return reverse(
            "plugins-api:cesnet_service_path_plugin-api:ethernetservicesegmentdata-detail",
            kwargs={"segment_id": segment.pk},
        )

    def _segment_url(self, segment):
        return reverse(
            "plugins-api:cesnet_service_path_plugin-api:segment-detail",
            kwargs={"pk": segment.pk},
        )

    def test_create(self):
        response = self.client.post(
            self._list_url(),
            {
                "segment_id": self.segment.pk,
                "port_speed": 10000,
                "vlan_id": 100,
                "vlan_tags": "100,200,300",
                "encapsulation_type": "dot1q",
                "interface_type": "10gbase-x-sfpp",
                "mtu_size": 9000,
            },
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, 201, response.data)
        data = response.data
        self.assertEqual(data["segment"]["id"], self.segment.pk)
        self.assertEqual(data["port_speed"], 10000)
        self.assertEqual(data["vlan_id"], 100)
        self.assertEqual(data["mtu_size"], 9000)
        EthernetServiceSegmentData.objects.filter(segment=self.segment).delete()

    def test_retrieve(self):
        es = EthernetServiceSegmentData.objects.create(
            segment=self.segment, port_speed=10000, vlan_id=100
        )
        response = self.client.get(self._detail_url(self.segment), **self.header)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["port_speed"], 10000)
        es.delete()

    def test_segment_type_specific_data_populated(self):
        es = EthernetServiceSegmentData.objects.create(
            segment=self.segment, port_speed=10000, vlan_id=100
        )
        response = self.client.get(self._segment_url(self.segment), **self.header)
        self.assertEqual(response.status_code, 200)
        tsd = response.data["type_specific_data"]
        self.assertIsNotNone(tsd)
        self.assertEqual(tsd["port_speed"], 10000)
        es.delete()

    def test_update(self):
        es = EthernetServiceSegmentData.objects.create(
            segment=self.segment, port_speed=10000,
            interface_type="10gbase-x-sfpp", mtu_size=9000,
        )
        response = self.client.patch(
            self._detail_url(self.segment),
            {"port_speed": 100000, "interface_type": "100gbase-x-qsfp28", "mtu_size": 9216},
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["port_speed"], 100000)
        self.assertEqual(response.data["mtu_size"], 9216)
        es.delete()

    def test_delete(self):
        es = EthernetServiceSegmentData.objects.create(segment=self.segment, port_speed=10000)
        response = self.client.delete(self._detail_url(self.segment), **self.header)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(EthernetServiceSegmentData.objects.filter(segment=self.segment).exists())
        self.assertTrue(Segment.objects.filter(pk=self.segment.pk).exists())

    def test_vlan_id_zero_rejected(self):
        with disable_warnings("django.request"):
            response = self.client.post(
                self._list_url(),
                {"segment_id": self.segment.pk, "vlan_id": 0},
                format="json",
                **self.header,
            )
        self.assertEqual(response.status_code, 400)

    def test_mtu_below_576_rejected(self):
        with disable_warnings("django.request"):
            response = self.client.post(
                self._list_url(),
                {"segment_id": self.segment.pk, "mtu_size": 500},
                format="json",
                **self.header,
            )
        self.assertEqual(response.status_code, 400)

    def test_invalid_vlan_tags_rejected(self):
        with disable_warnings("django.request"):
            response = self.client.post(
                self._list_url(),
                {"segment_id": self.segment.pk, "vlan_tags": "100,abc,300"},
                format="json",
                **self.header,
            )
        self.assertEqual(response.status_code, 400)


# ---------------------------------------------------------------------------
# Optical Spectrum Data — model tests
# ---------------------------------------------------------------------------

class OpticalSpectrumDataModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        provider = Provider.objects.create(name="OS__Provider", slug="os__provider")
        site_a = Site.objects.create(name="OS__Site-A", slug="os__site-a")
        site_b = Site.objects.create(name="OS__Site-B", slug="os__site-b")
        cls.segment = _make_segment(
            "OS__Seg", SegmentTypeChoices.OPTICAL_SPECTRUM, provider, site_a, site_b
        )

    def test_create_and_str(self):
        os_data = OpticalSpectrumSegmentData.objects.create(
            segment=self.segment, wavelength=Decimal("1550.12")
        )
        self.assertIn(self.segment.name, str(os_data))
        self.assertIn("1550.12", str(os_data))
        os_data.delete()

    def test_cascade_delete(self):
        seg = _make_segment(
            "OS__Cascade", SegmentTypeChoices.OPTICAL_SPECTRUM,
            self.segment.provider, self.segment.site_a, self.segment.site_b,
        )
        os_data = OpticalSpectrumSegmentData.objects.create(
            segment=seg, wavelength=Decimal("1550.0")
        )
        os_pk = os_data.pk
        seg.delete()
        self.assertFalse(OpticalSpectrumSegmentData.objects.filter(pk=os_pk).exists())

    def test_valid_wavelength_passes_clean(self):
        os_data = OpticalSpectrumSegmentData(
            segment=self.segment, wavelength=Decimal("1550.0")
        )
        os_data.clean()  # should not raise

    def test_onetoone_uniqueness(self):
        OpticalSpectrumSegmentData.objects.create(
            segment=self.segment, wavelength=Decimal("1550.0")
        )
        with self.assertRaises(Exception):
            with transaction.atomic():
                OpticalSpectrumSegmentData.objects.create(
                    segment=self.segment, wavelength=Decimal("1552.0")
                )


# ---------------------------------------------------------------------------
# Optical Spectrum Data — API tests
# ---------------------------------------------------------------------------

class OpticalSpectrumDataAPITest(_APIBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.segment = _make_segment(
            "OS__API__Seg", SegmentTypeChoices.OPTICAL_SPECTRUM, cls.provider, cls.site_a, cls.site_b
        )

    def _list_url(self):
        return reverse("plugins-api:cesnet_service_path_plugin-api:opticalspectrumsegmentdata-list")

    def _detail_url(self, segment):
        return reverse(
            "plugins-api:cesnet_service_path_plugin-api:opticalspectrumsegmentdata-detail",
            kwargs={"segment_id": segment.pk},
        )

    def _segment_url(self, segment):
        return reverse(
            "plugins-api:cesnet_service_path_plugin-api:segment-detail",
            kwargs={"pk": segment.pk},
        )

    def test_create(self):
        response = self.client.post(
            self._list_url(),
            {
                "segment_id": self.segment.pk,
                "wavelength": "1550.120",
                "spectral_slot_width": "50.0",
                "itu_grid_position": 35,
                "chromatic_dispersion": "17.5",
                "pmd_tolerance": "2.5",
                "modulation_format": "dp_qpsk",
            },
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, 201, response.data)
        data = response.data
        self.assertEqual(data["segment"]["id"], self.segment.pk)
        self.assertEqual(Decimal(data["wavelength"]), Decimal("1550.120"))
        self.assertEqual(data["modulation_format"], "dp_qpsk")
        OpticalSpectrumSegmentData.objects.filter(segment=self.segment).delete()

    def test_retrieve(self):
        os_data = OpticalSpectrumSegmentData.objects.create(
            segment=self.segment, wavelength=Decimal("1550.12"), modulation_format="dp_qpsk"
        )
        response = self.client.get(self._detail_url(self.segment), **self.header)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(Decimal(response.data["wavelength"]), Decimal("1550.12"))
        os_data.delete()

    def test_segment_type_specific_data_populated(self):
        os_data = OpticalSpectrumSegmentData.objects.create(
            segment=self.segment, wavelength=Decimal("1550.12"), modulation_format="dp_qpsk"
        )
        response = self.client.get(self._segment_url(self.segment), **self.header)
        self.assertEqual(response.status_code, 200)
        tsd = response.data["type_specific_data"]
        self.assertIsNotNone(tsd)
        self.assertEqual(tsd["modulation_format"], "dp_qpsk")
        os_data.delete()

    def test_update(self):
        os_data = OpticalSpectrumSegmentData.objects.create(
            segment=self.segment, wavelength=Decimal("1550.12"), modulation_format="dp_qpsk"
        )
        response = self.client.patch(
            self._detail_url(self.segment),
            {"wavelength": "1552.520", "modulation_format": "dp_16qam"},
            format="json",
            **self.header,
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(Decimal(response.data["wavelength"]), Decimal("1552.520"))
        self.assertEqual(response.data["modulation_format"], "dp_16qam")
        os_data.delete()

    def test_delete(self):
        os_data = OpticalSpectrumSegmentData.objects.create(
            segment=self.segment, wavelength=Decimal("1550.0")
        )
        response = self.client.delete(self._detail_url(self.segment), **self.header)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(OpticalSpectrumSegmentData.objects.filter(segment=self.segment).exists())
        self.assertTrue(Segment.objects.filter(pk=self.segment.pk).exists())

    def test_out_of_range_wavelength_rejected(self):
        """Wavelength > 1625 nm must be rejected by the model validator."""
        with disable_warnings("django.request"):
            response = self.client.post(
                self._list_url(),
                {"segment_id": self.segment.pk, "wavelength": "2000.0"},
                format="json",
                **self.header,
            )
        self.assertEqual(response.status_code, 400)

    def test_retrieve_after_segment_delete_returns_404(self):
        seg = _make_segment(
            "OS__API__Del", SegmentTypeChoices.OPTICAL_SPECTRUM,
            self.provider, self.site_a, self.site_b,
        )
        OpticalSpectrumSegmentData.objects.create(segment=seg, wavelength=Decimal("1550.0"))
        detail_url = self._detail_url(seg)
        seg.delete()  # cascades to OpticalSpectrumSegmentData
        response = self.client.get(detail_url, **self.header)
        self.assertEqual(response.status_code, 404)
