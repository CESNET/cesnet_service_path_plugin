import json

from dcim.models import Region, Site
from django.urls import reverse
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from cesnet_service_path_plugin.filtersets import SegmentFilterSet
from cesnet_service_path_plugin.models import Segment
from cesnet_service_path_plugin.views.segment import build_segments_map_data


@register_model_view(Site, name="segment-map", path="segment-map")
class SiteSegmentMapTabView(generic.ObjectView):
    queryset = Site.objects.all()
    template_name = "cesnet_service_path_plugin/site_segment_map_tab.html"

    tab = ViewTab(
        label="Segment Map",
        badge=lambda obj: SegmentFilterSet(
            {"at_any_site": [obj.pk]}, queryset=Segment.objects.all()
        ).qs.count(),
        hide_if_empty=False,
        weight=500,
    )

    def get_extra_context(self, request, instance):
        queryset = SegmentFilterSet(
            {"at_any_site": [instance.pk]}, queryset=Segment.objects.all()
        ).qs
        segments_data, map_bounds, map_warning = build_segments_map_data(queryset)
        base_api_url = request.build_absolute_uri(
            reverse("plugins:cesnet_service_path_plugin:segments_map_api")
        )
        return {
            "map_api_url": f"{base_api_url}?at_any_site={instance.pk}",
            "map_card_title": f"Segment Map — {instance.name}",
            "map_element_id": "segment-map-site",
            "segments_data_json": json.dumps(segments_data),
            "map_bounds_json": json.dumps(map_bounds),
            "map_warning": map_warning,
        }


@register_model_view(Region, name="segment-map", path="segment-map")
class RegionSegmentMapTabView(generic.ObjectView):
    queryset = Region.objects.all()
    template_name = "cesnet_service_path_plugin/region_segment_map_tab.html"

    tab = ViewTab(
        label="Segment Map",
        badge=lambda obj: SegmentFilterSet(
            {"at_any_region": [obj.pk]}, queryset=Segment.objects.all()
        ).qs.count(),
        hide_if_empty=False,
        weight=500,
    )

    def get_extra_context(self, request, instance):
        queryset = SegmentFilterSet(
            {"at_any_region": [instance.pk]}, queryset=Segment.objects.all()
        ).qs
        segments_data, map_bounds, map_warning = build_segments_map_data(queryset)
        base_api_url = request.build_absolute_uri(
            reverse("plugins:cesnet_service_path_plugin:segments_map_api")
        )
        return {
            "map_api_url": f"{base_api_url}?at_any_region={instance.pk}",
            "map_card_title": f"Segment Map — {instance.name} (including sub-regions)",
            "map_element_id": "segment-map-region",
            "segments_data_json": json.dumps(segments_data),
            "map_bounds_json": json.dumps(map_bounds),
            "map_warning": map_warning,
        }
