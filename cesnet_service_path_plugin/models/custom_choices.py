from utilities.choices import ChoiceSet


class StatusChoices(ChoiceSet):
    key = "cesnet_service_path_plugin.choices.status"

    ACTIVE = "active"
    PLANNED = "planned"
    OFFLINE = "offline"
    DECOMMISSIONED = "decommissioned"
    SURVEYED = "surveyed"

    CHOICES = [
        (ACTIVE, "Active", "green"),
        (PLANNED, "Planned", "orange"),
        (OFFLINE, "Offline", "red"),
        (DECOMMISSIONED, "Decommissioned", "gray"),
        (SURVEYED, "Surveyed", "blue"),
    ]


class OwnershipTypeChoices(ChoiceSet):
    """
    owned
    leased
    shared
    foreign
    """

    key = "cesnet_service_path_plugin.choices.ownership_type"
    OWNED = "owned"
    LEASED = "leased"
    SHARED = "shared"
    FOREIGN = "foreign"

    CHOICES = [
        (OWNED, "Owned", "green"),
        (LEASED, "Leased", "blue"),
        (SHARED, "Shared", "yellow"),
        (FOREIGN, "Foreign", "red"),
    ]


class KindChoices(ChoiceSet):
    key = "cesnet_service_path_plugin.choices.kind"

    EXPERIMENTAL = "experimental"
    CORE = "core"
    CUSTOMER = "customer"

    CHOICES = [
        (EXPERIMENTAL, "Experimental", "cyan"),
        (CORE, "Core", "blue"),
        (CUSTOMER, "Customer", "green"),
    ]


class ContractTypeChoices(ChoiceSet):
    """
    Contract type indicates how the contract was created.
    - New: Original contract
    - Renewal: New contract period after previous expired
    - Amendment: Modification to existing contract terms
    """

    key = "cesnet_service_path_plugin.choices.contract_type"

    NEW = "new"
    RENEWAL = "renewal"
    AMENDMENT = "amendment"

    CHOICES = [
        (NEW, "New Contract", "blue"),
        (RENEWAL, "Renewal", "green"),
        (AMENDMENT, "Amendment", "orange"),
    ]


class CurrencyChoices(ChoiceSet):
    """
    Currency codes following ISO 4217 standard.
    Default choices can be overridden in plugin configuration.
    """

    key = "cesnet_service_path_plugin.choices.currency"

    CZK = "CZK"
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    PLN = "PLN"
    HUF = "HUF"

    CHOICES = [
        (CZK, "Czech Koruna (CZK)", "blue"),
        (EUR, "Euro (EUR)", "green"),
        (USD, "US Dollar (USD)", "cyan"),
        (GBP, "British Pound (GBP)", "purple"),
        (PLN, "Polish Zloty (PLN)", "orange"),
        (HUF, "Hungarian Forint (HUF)", "yellow"),
    ]


class RecurringChargePeriodChoices(ChoiceSet):
    """
    Frequency of recurring charges in contracts.
    """

    key = "cesnet_service_path_plugin.choices.recurring_charge_period"

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"

    CHOICES = [
        (MONTHLY, "Monthly", "blue"),
        (QUARTERLY, "Quarterly", "green"),
        (SEMI_ANNUALLY, "Semi-Annually", "orange"),
        (ANNUALLY, "Annually", "purple"),
    ]


# =============================================================================
# Type-Specific Choices for Segment Models
# =============================================================================


class FiberModeChoices(ChoiceSet):
    """
    Fiber mode type: Single-mode or Multimode.
    Can be overridden in plugin configuration.
    """

    key = "cesnet_service_path_plugin.choices.fiber_mode"

    SINGLE_MODE = "single_mode"
    MULTIMODE = "multimode"

    CHOICES = [
        (SINGLE_MODE, "Single-mode (SMF)", "blue"),
        (MULTIMODE, "Multimode (MMF)", "orange"),
    ]


class SingleModeFiberSubtypeChoices(ChoiceSet):
    """
    ITU-T single-mode fiber standards (G.652-G.657).
    Can be overridden in plugin configuration.
    """

    key = "cesnet_service_path_plugin.choices.single_mode_fiber_subtype"

    G652 = "g652"
    G652D = "g652d"
    G652B = "g652b"
    G652C = "g652c"
    G653 = "g653"
    G654 = "g654"
    G654E = "g654e"
    G655 = "g655"
    G657 = "g657"
    G657A1 = "g657a1"
    G657A2 = "g657a2"

    CHOICES = [
        (G652, "G.652 - Standard SMF", "blue"),
        (G652D, "G.652D - Standard SMF (ITU-T)", "blue"),
        (G652B, "G.652B - Standard SMF variant", "blue"),
        (G652C, "G.652C - Standard SMF variant", "blue"),
        (G653, "G.653 - Dispersion-shifted fiber (DSF)", "orange"),
        (G654, "G.654 - Cutoff-shifted fiber", "green"),
        (G654E, "G.654E - Cutoff-shifted fiber (low attenuation)", "green"),
        (G655, "G.655 - Non-zero dispersion-shifted fiber (NZDSF)", "purple"),
        (G657, "G.657 - Bend-insensitive SMF", "cyan"),
        (G657A1, "G.657A1 - Bend-insensitive SMF", "cyan"),
        (G657A2, "G.657A2 - Bend-insensitive SMF", "cyan"),
    ]


class MultimodeFiberSubtypeChoices(ChoiceSet):
    """
    ISO/IEC 11801 / TIA-492 multimode fiber standards (OM1-OM5).
    Can be overridden in plugin configuration.
    """

    key = "cesnet_service_path_plugin.choices.multimode_fiber_subtype"

    OM1 = "om1"
    OM2 = "om2"
    OM3 = "om3"
    OM4 = "om4"
    OM5 = "om5"

    CHOICES = [
        (OM1, "OM1 - 62.5µm core (legacy)", "gray"),
        (OM2, "OM2 - 50µm core (legacy)", "gray"),
        (OM3, "OM3 - 50µm laser-optimized", "orange"),
        (OM4, "OM4 - 50µm extended reach", "green"),
        (OM5, "OM5 - 50µm wideband (SWDM)", "blue"),
    ]


class FiberJacketTypeChoices(ChoiceSet):
    """
    Fiber cable jacket types.
    Can be overridden in plugin configuration.
    """

    key = "cesnet_service_path_plugin.choices.fiber_jacket_type"

    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    INDOOR_OUTDOOR = "indoor_outdoor"
    ARMORED = "armored"
    LOOSE_TUBE = "loose_tube"
    TIGHT_BUFFER = "tight_buffer"
    MICRODUCT = "microduct"
    AERIAL = "aerial"
    DIRECT_BURIAL = "direct_burial"

    CHOICES = [
        (INDOOR, "Indoor", "blue"),
        (OUTDOOR, "Outdoor", "green"),
        (INDOOR_OUTDOOR, "Indoor/Outdoor", "cyan"),
        (ARMORED, "Armored", "red"),
        (LOOSE_TUBE, "Loose tube", "orange"),
        (TIGHT_BUFFER, "Tight buffer", "purple"),
        (MICRODUCT, "Microduct", "yellow"),
        (AERIAL, "Aerial", "teal"),
        (DIRECT_BURIAL, "Direct burial", "brown"),
    ]


class ModulationFormatChoices(ChoiceSet):
    """
    Optical modulation formats for DWDM/optical spectrum.
    Can be overridden in plugin configuration.
    """

    key = "cesnet_service_path_plugin.choices.modulation_format"

    NRZ = "nrz"
    PAM4 = "pam4"
    QPSK = "qpsk"
    QAM16 = "16qam"
    QAM64 = "64qam"
    DP_QPSK = "dp_qpsk"
    DP_16QAM = "dp_16qam"

    CHOICES = [
        (NRZ, "NRZ", "blue"),
        (PAM4, "PAM4", "green"),
        (QPSK, "QPSK", "orange"),
        (QAM16, "16-QAM", "purple"),
        (QAM64, "64-QAM", "red"),
        (DP_QPSK, "DP-QPSK", "cyan"),
        (DP_16QAM, "DP-16QAM", "yellow"),
    ]


class EncapsulationTypeChoices(ChoiceSet):
    """
    Ethernet encapsulation types.
    Can be overridden in plugin configuration.
    """

    key = "cesnet_service_path_plugin.choices.encapsulation_type"

    UNTAGGED = "untagged"
    DOT1Q = "dot1q"
    DOT1AD = "dot1ad"
    DOT1AH = "dot1ah"
    MPLS = "mpls"
    MEF_E_LINE = "mef_e_line"
    MEF_E_LAN = "mef_e_lan"

    CHOICES = [
        (UNTAGGED, "Untagged", "gray"),
        (DOT1Q, "IEEE 802.1Q", "blue"),
        (DOT1AD, "IEEE 802.1ad (QinQ)", "green"),
        (DOT1AH, "IEEE 802.1ah (PBB)", "purple"),
        (MPLS, "MPLS", "orange"),
        (MEF_E_LINE, "MEF E-Line", "cyan"),
        (MEF_E_LAN, "MEF E-LAN", "yellow"),
    ]
