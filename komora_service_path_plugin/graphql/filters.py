import strawberry_django
from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

from komora_service_path_plugin.models import Segment, ServicePath, ServicePathSegmentMapping, SegmentCircuitMapping
from komora_service_path_plugin.filtersets import SegmentFilterSet, ServicePathFilterSet


@strawberry_django.filter(Segment, lookups=True)
@autotype_decorator(SegmentFilterSet)
class SegmentFilter(BaseFilterMixin):
    pass


"""
@strawberry_django.filter(ServicePath, lookups=True)
@autotype_decorator(ServicePathFilterSet)
class ServicePathFilter(BaseFilterMixin):
    pass
"""
