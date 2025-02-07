import strawberry_django
from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

from cesnet_service_path_plugin.models import Segment, ServicePath, ServicePathSegmentMapping, SegmentCircuitMapping
from cesnet_service_path_plugin.filtersets import (
    SegmentFilterSet,
    ServicePathFilterSet,
    SegmentCircuitMappingFilterSet,
    ServicePathSegmentMappingFilterSet,
)


@strawberry_django.filter(Segment, lookups=True)
@autotype_decorator(SegmentFilterSet)
class SegmentFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(ServicePath, lookups=True)
@autotype_decorator(ServicePathFilterSet)
class ServicePathFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(SegmentCircuitMapping, lookups=True)
class SegmentCircuitMappingFilter(SegmentCircuitMappingFilterSet):
    pass


@strawberry_django.filter(ServicePathSegmentMapping, lookups=True)
class ServicePathSegmentMappingFilter(ServicePathSegmentMappingFilterSet):
    pass
