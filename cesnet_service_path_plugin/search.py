from netbox.search import SearchIndex, register_search

from cesnet_service_path_plugin.models import Segment, ServicePath


@register_search
class SegmentIndex(SearchIndex):
    model = Segment
    fields = (
        ("name", 100),
        ("network_label", 110),
        ("provider_segment_id", 200),
        ("path_notes", 500),
        ("comments", 5000),
    )
    display_attrs = ("provider", "site_a", "site_b", "location_a", "location_b", "segment_type", "status")


@register_search
class ServicePathIndex(SearchIndex):
    model = ServicePath
    fields = (
        ("name", 100),
        ("comments", 5000),
    )
    display_attrs = ("status", "kind")
