import json

from circuits.models import Circuit
from dcim.models import Region, Site
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from cesnet_service_path_plugin.filtersets import SegmentFilterSet
from cesnet_service_path_plugin.models import Segment
from cesnet_service_path_plugin.views.map import (
    MAX_OBJECTS,
    _build_circuits_data,
    _build_region_ancestors,
    _build_segments_data,
    _build_sites_data,
    _compute_bounds,
)


def _network_map_context(request, segments_data, sites_data, circuits_data, title, prefilter):
    """
    Build the shared context dict for the Network Map tab card.
    prefilter — dict of initial JS filter state, e.g. {"at_any_site": [pk]}
    """
    region_ancestors = _build_region_ancestors()
    map_bounds = _compute_bounds(sites_data, segments_data, circuits_data)

    if map_bounds["minLat"] is None:
        map_center = {"lat": 49.75, "lng": 15.5, "zoom": 7}
    else:
        map_center = {
            "lat": (map_bounds["minLat"] + map_bounds["maxLat"]) / 2,
            "lng": (map_bounds["minLng"] + map_bounds["maxLng"]) / 2,
            "zoom": 7,
        }

    return {
        "map_card_title": title,
        "sites_data_json":       json.dumps(sites_data),
        "segments_data_json":    json.dumps(segments_data),
        "circuits_data_json":    json.dumps(circuits_data),
        "region_ancestors_json": json.dumps(region_ancestors),
        "map_bounds_json":       json.dumps(map_bounds),
        "map_center_json":       json.dumps(map_center),
        "prefilter_json":        json.dumps(prefilter),
        "segments_api_url": request.build_absolute_uri(
            "/plugins/cesnet-service-path-plugin/segments/map/api/"
        ),
    }


@register_model_view(Site, name="segment-map", path="segment-map")
class SiteSegmentMapTabView(generic.ObjectView):
    queryset = Site.objects.all()
    template_name = "cesnet_service_path_plugin/site_segment_map_tab.html"

    tab = ViewTab(
        label="Network Map",
        badge=lambda obj: SegmentFilterSet(
            {"at_any_site": [obj.pk]}, queryset=Segment.objects.all()
        ).qs.count(),
        hide_if_empty=False,
        weight=500,
    )

    def get_extra_context(self, request, instance):
        site_qs = Site.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
        ).select_related("region", "group", "tenant")
        segment_qs = Segment.objects.all()
        circuit_qs = Circuit.objects.select_related(
            "termination_a___site",
            "termination_z___site",
            "provider",
            "type",
        )

        if site_qs.count()    > MAX_OBJECTS: site_qs    = site_qs[:MAX_OBJECTS]
        if segment_qs.count() > MAX_OBJECTS: segment_qs = segment_qs[:MAX_OBJECTS]
        if circuit_qs.count() > MAX_OBJECTS: circuit_qs = circuit_qs[:MAX_OBJECTS]

        sites_data    = _build_sites_data(site_qs)
        segments_data = _build_segments_data(segment_qs)
        circuits_data = _build_circuits_data(circuit_qs)

        return _network_map_context(
            request,
            segments_data, sites_data, circuits_data,
            title=f"Network Map — {instance.name}",
            prefilter={"at_any_site": [instance.pk]},
        )


@register_model_view(Region, name="segment-map", path="segment-map")
class RegionSegmentMapTabView(generic.ObjectView):
    queryset = Region.objects.all()
    template_name = "cesnet_service_path_plugin/region_segment_map_tab.html"

    tab = ViewTab(
        label="Network Map",
        badge=lambda obj: SegmentFilterSet(
            {"at_any_region": [obj.pk]}, queryset=Segment.objects.all()
        ).qs.count(),
        hide_if_empty=False,
        weight=500,
    )

    def get_extra_context(self, request, instance):
        # Collect all region PKs that are this region or any descendant
        descendant_pks = list(
            instance.get_descendants(include_self=True).values_list("pk", flat=True)
        )

        site_qs = Site.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            region__in=descendant_pks,
        ).select_related("region", "group", "tenant")
        segment_qs = SegmentFilterSet(
            {"at_any_region": [instance.pk]}, queryset=Segment.objects.all()
        ).qs
        circuit_qs = Circuit.objects.filter(
            termination_a___site__region__in=descendant_pks,
        ).select_related(
            "termination_a___site",
            "termination_z___site",
            "provider",
            "type",
        ) | Circuit.objects.filter(
            termination_z___site__region__in=descendant_pks,
        ).select_related(
            "termination_a___site",
            "termination_z___site",
            "provider",
            "type",
        )
        circuit_qs = circuit_qs.distinct()

        if site_qs.count()    > MAX_OBJECTS: site_qs    = site_qs[:MAX_OBJECTS]
        if segment_qs.count() > MAX_OBJECTS: segment_qs = segment_qs[:MAX_OBJECTS]
        if circuit_qs.count() > MAX_OBJECTS: circuit_qs = circuit_qs[:MAX_OBJECTS]

        sites_data    = _build_sites_data(site_qs)
        segments_data = _build_segments_data(segment_qs)
        circuits_data = _build_circuits_data(circuit_qs)

        return _network_map_context(
            request,
            segments_data, sites_data, circuits_data,
            title=f"Network Map — {instance.name} (including sub-regions)",
            prefilter={"region_id": [instance.pk]},
        )
