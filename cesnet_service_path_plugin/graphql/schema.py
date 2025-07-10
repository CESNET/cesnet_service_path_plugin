import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension

from .types import SegmentType, SegmentCircuitMappingType, ServicePathType, ServicePathSegmentMappingType


@strawberry.type(name="Query")
class CesnetServicePathQuery:
    segment: SegmentType = strawberry_django.field()
    segment_list: list[SegmentType] = strawberry_django.field()

    segment_circuit_mapping: SegmentCircuitMappingType = strawberry_django.field()
    segment_circuit_mapping_list: list[SegmentCircuitMappingType] = strawberry_django.field()

    service_path: ServicePathType = strawberry_django.field()
    service_path_list: list[ServicePathType] = strawberry_django.field()

    service_path_segment_mapping: ServicePathSegmentMappingType = strawberry_django.field()
    service_path_segment_mapping_list: list[ServicePathSegmentMappingType] = strawberry_django.field()


schema = strawberry.Schema(
    query=CesnetServicePathQuery,
    extensions=[
        DjangoOptimizerExtension,
    ],
)
