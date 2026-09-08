"""
Template extensions must not render the "Segments" htmx card for users who cannot view
the embedded list. Otherwise the htmx table request 403s and leaves an empty card + console error.
"""

from circuits.models import Circuit, CircuitType, Provider
from dcim.models import Site
from users.models import User
from utilities.testing import TestCase

from cesnet_service_path_plugin.models import Segment, SegmentCircuitMapping
from cesnet_service_path_plugin.models.custom_choices import StatusChoices
from cesnet_service_path_plugin.models.segment_types import SegmentTypeChoices

SEGMENTS_HX = 'hx-get="/plugins/cesnet-service-path-plugin/segments/'
MAPPINGS_HX = 'hx-get="/plugins/cesnet-service-path-plugin/segment-circuit-mappings/'


class SegmentsCardPermissionTest(TestCase):
    PREFIX = "TTE__"

    @classmethod
    def setUpTestData(cls):
        p = cls.PREFIX
        cls.provider = Provider.objects.create(name=f"{p}Provider", slug=f"{p.lower()}provider")
        cls.site_a = Site.objects.create(name=f"{p}Site A", slug=f"{p.lower()}site-a")
        cls.site_b = Site.objects.create(name=f"{p}Site B", slug=f"{p.lower()}site-b")
        cls.segment = Segment.objects.create(
            name=f"{p}Segment",
            status=StatusChoices.ACTIVE,
            segment_type=SegmentTypeChoices.DARK_FIBER,
            ownership_type="leased",
            provider=cls.provider,
            site_a=cls.site_a,
            site_b=cls.site_b,
        )
        ctype = CircuitType.objects.create(name=f"{p}Type", slug=f"{p.lower()}type")
        cls.circuit = Circuit.objects.create(cid=f"{p}Circuit", provider=cls.provider, type=ctype)
        SegmentCircuitMapping.objects.create(segment=cls.segment, circuit=cls.circuit)
        cls.superuser = User.objects.create_superuser(username=f"{p}super")

    def setUp(self):
        super().setUp()
        # Restricted user: can view core objects, nothing from the plugin.
        self.add_permissions("dcim.view_site", "circuits.view_circuit")

    def test_restricted_user_site_page_has_no_segments_card(self):
        html = self.client.get(self.site_a.get_absolute_url()).content.decode()
        self.assertNotIn(SEGMENTS_HX, html)

    def test_restricted_user_circuit_page_has_no_segments_card(self):
        html = self.client.get(self.circuit.get_absolute_url()).content.decode()
        self.assertNotIn(MAPPINGS_HX, html)

    def test_restricted_user_embedded_table_is_403(self):
        resp = self.client.get(
            f"/plugins/cesnet-service-path-plugin/segments/?embedded=True&at_any_site={self.site_a.pk}",
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resp.status_code, 403)

    def test_superuser_sees_cards(self):
        self.client.force_login(self.superuser)
        html = self.client.get(self.site_a.get_absolute_url()).content.decode()
        self.assertIn(SEGMENTS_HX, html)
        html = self.client.get(self.circuit.get_absolute_url()).content.decode()
        self.assertIn(MAPPINGS_HX, html)
