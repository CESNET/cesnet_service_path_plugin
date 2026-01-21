from .segment import Segment
from .segment_circuit_mapping import SegmentCircuitMapping
from .contract_info import ContractInfo
from .segment_types import SegmentTypeChoices
from .service_path import ServicePath
from .service_path_segment_mapping import ServicePathSegmentMapping

# New type-specific data models
from .dark_fiber_data import DarkFiberSegmentData
from .optical_spectrum_data import OpticalSpectrumSegmentData
from .ethernet_service_data import EthernetServiceSegmentData

from .custom_choices import (
    CurrencyChoices,
    RecurringChargePeriodChoices,
    ContractTypeChoices,
    KindChoices,
    OwnershipTypeChoices,
    StatusChoices,
    # Type-specific choices
    FiberModeChoices,
    SingleModeFiberSubtypeChoices,
    MultimodeFiberSubtypeChoices,
    FiberJacketTypeChoices,
    ModulationFormatChoices,
    EncapsulationTypeChoices,
)

__all__ = [
    "Segment",
    "SegmentCircuitMapping",
    "ContractInfo",
    "SegmentTypeChoices",
    "ServicePath",
    "ServicePathSegmentMapping",
    # Type-specific data models
    "DarkFiberSegmentData",
    "OpticalSpectrumSegmentData",
    "EthernetServiceSegmentData",
    # Choices
    "CurrencyChoices",
    "RecurringChargePeriodChoices",
    "ContractTypeChoices",
    "KindChoices",
    "OwnershipTypeChoices",
    "StatusChoices",
    # Type-specific choices
    "FiberModeChoices",
    "SingleModeFiberSubtypeChoices",
    "MultimodeFiberSubtypeChoices",
    "FiberJacketTypeChoices",
    "ModulationFormatChoices",
    "EncapsulationTypeChoices",
    "InterfaceTypeChoices",
]
