from netbox.search import SearchIndex, register_search

from cesnet_service_path_plugin.models import Segment, ServicePath


@register_search
class SegmentIndex(SearchIndex):
    model = Segment

    fields = (
        ("name", 100),
        ("network_label", 100),
        ("provider_segment_id", 200),
        ("provider_segment_name", 200),
        ("provider_segment_contract", 200),
    )
    display_attrs = ("provider", "site_a", "site_b")


@register_search
class ServicePathIndex(SearchIndex):
    model = ServicePath

    fields = (("name", 100),)
    display_attrs = ("status", "kind")
