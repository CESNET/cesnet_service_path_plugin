from typing import List

import strawberry
import strawberry_django

from .types import (
    SegmentCircuitMappingType,
    SegmentFinancialInfoType,
    SegmentType,
    ServicePathSegmentMappingType,
    ServicePathType,
)


@strawberry.type(name="Query")
class CesnetServicePathQuery:
    segment: SegmentType = strawberry_django.field()
    segment_list: List[SegmentType] = strawberry_django.field()

    segment_circuit_mapping: SegmentCircuitMappingType = strawberry_django.field()
    segment_circuit_mapping_list: List[SegmentCircuitMappingType] = strawberry_django.field()

    segment_financial_info: SegmentFinancialInfoType = strawberry_django.field()
    segment_financial_info_list: List[SegmentFinancialInfoType] = strawberry_django.field()

    service_path: ServicePathType = strawberry_django.field()
    service_path_list: List[ServicePathType] = strawberry_django.field()

    service_path_segment_mapping: ServicePathSegmentMappingType = strawberry_django.field()
    service_path_segment_mapping_list: List[ServicePathSegmentMappingType] = strawberry_django.field()


schema = [
    CesnetServicePathQuery,
]
