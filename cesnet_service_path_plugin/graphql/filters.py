import strawberry_django
from netbox.graphql.filter_mixins import BaseFilterMixin

from cesnet_service_path_plugin.filtersets import (
    SegmentCircuitMappingFilterSet,
    SegmentFilterSet,
    ServicePathFilterSet,
    ServicePathSegmentMappingFilterSet,
)
from cesnet_service_path_plugin.models import (
    Segment,
    SegmentCircuitMapping,
    ServicePath,
    ServicePathSegmentMapping,
)


@strawberry_django.filter(Segment, lookups=True)
class SegmentFilter(BaseFilterMixin):
    class Meta:
        filterset_class = SegmentFilterSet


@strawberry_django.filter(ServicePath, lookups=True)
class ServicePathFilter(BaseFilterMixin):
    class Meta:
        filterset_class = ServicePathFilterSet


@strawberry_django.filter(SegmentCircuitMapping, lookups=True)
class SegmentCircuitMappingFilter(SegmentCircuitMappingFilterSet):
    class Meta:
        filterset_class = SegmentCircuitMappingFilterSet


@strawberry_django.filter(ServicePathSegmentMapping, lookups=True)
class ServicePathSegmentMappingFilter(ServicePathSegmentMappingFilterSet):
    class Meta:
        filterset_class = ServicePathSegmentMappingFilterSet
