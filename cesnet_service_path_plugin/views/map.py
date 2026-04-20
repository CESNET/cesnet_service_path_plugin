import json

from circuits.choices import CircuitStatusChoices
from circuits.models import Circuit
from dcim.choices import SiteStatusChoices
from dcim.models import Region, Site
from django.shortcuts import render
from django.views import View

from cesnet_service_path_plugin.forms.map import MapFilterForm
from cesnet_service_path_plugin.models import Segment
from cesnet_service_path_plugin.models.custom_choices import StatusChoices
from cesnet_service_path_plugin.models.segment_types import SegmentTypeChoices

MAX_OBJECTS = 500

# Bootstrap color variant for each status/type value — used by btn-check filter buttons.
_SITE_STATUS_COLORS = {
    "planned":         "warning",
    "staging":         "info",
    "active":          "success",
    "decommissioning": "warning",
    "retired":         "secondary",
}
_SEGMENT_STATUS_COLORS = {
    "active":         "success",
    "planned":        "warning",
    "offline":        "danger",
    "decommissioned": "secondary",
    "surveyed":       "info",
}
_SEGMENT_TYPE_COLORS = {
    "dark_fiber":       "secondary",
    "optical_spectrum": "warning",
    "ethernet_service": "success",
}
_CIRCUIT_STATUS_COLORS = {
    "planned":         "warning",
    "provisioning":    "info",
    "active":          "success",
    "offline":         "danger",
    "deprovisioning":  "warning",
    "decommissioned":  "secondary",
}


# ---------------------------------------------------------------------------
# The helpers below are kept for the unit tests — the view no longer uses
# server-side filtering (all filtering is done client-side in JS).
# ---------------------------------------------------------------------------

def _remap_params(get_params, mapping, passthrough):
    """
    Build a plain dict suitable for passing to a django-filter FilterSet.
    Values are kept as lists (getlist), matching the pattern used by NetBox's
    own filterset tests (e.g. {'region_id': [pk]}).

    mapping    — {form_field_name: filterset_field_name}
    passthrough — set of field names identical in both form and filterset
    """
    result = {}
    for key, values in get_params.lists():
        if key in passthrough:
            result[key] = values
        elif key in mapping:
            result[mapping[key]] = values
    return result


def _extract_site_params(get_params):
    return _remap_params(
        get_params,
        mapping={
            "site_status":    "status",
            "site_tenant_id": "tenant_id",
            "site_group_id":  "group_id",
        },
        passthrough={"region_id"},
    )


def _extract_segment_params(get_params):
    return _remap_params(
        get_params,
        mapping={
            "segment_status":      "status",
            "segment_type":        "segment_type",
            "segment_provider_id": "provider_id",
        },
        passthrough={"region_id", "at_any_site"},
    )


def _build_region_ancestors():
    """
    Return a dict mapping each region PK to the list of its ancestor PKs
    (including itself).  Used by JS to implement tree-aware region filtering:
    a site in region 250 (Brno) should match a filter on region 201
    (Jihomoravský kraj) because 201 is in Brno's ancestor chain.

    Example: { 250: [1, 201, 215, 250], 249: [1, 201, 214, 249], ... }
    """
    result = {}
    for region in Region.objects.all():
        result[region.pk] = list(
            region.get_ancestors(include_self=True).values_list("pk", flat=True)
        )
    return result


def _build_sites_data(site_qs):
    """
    Build the JS-ready list of site objects. Only sites with valid coordinates
    are included (the queryset is pre-filtered, but guard here too).
    """
    sites_data = []
    for site in site_qs:
        try:
            lat = float(site.latitude)
            lng = float(site.longitude)
        except (ValueError, TypeError, AttributeError):
            continue

        sites_data.append({
            "id": site.pk,
            "name": str(site),
            "status": site.get_status_display(),
            "status_color": site.get_status_color(),
            "region": str(site.region) if site.region else None,
            "region_id": site.region_id,
            "group": str(site.group) if site.group else None,
            "group_id": site.group_id,
            "tenant": str(site.tenant) if site.tenant else None,
            "tenant_id": site.tenant_id,
            "lat": lat,
            "lng": lng,
            "facility": site.facility or None,
            "physical_address": site.physical_address or None,
            "tags": [{"name": t.name, "color": t.color} for t in site.tags.all()],
            "url": site.get_absolute_url(),
        })
    return sites_data


def _build_segments_data(segment_qs):
    """
    Build the JS-ready list of segment objects. Segments where either site
    has no coordinates are skipped. Includes site PKs for client-side
    cross-referencing with site markers.
    """
    segments_data = []
    for segment in segment_qs:
        site_a_data = None
        site_b_data = None

        try:
            site_a_data = {
                "id": segment.site_a.pk,
                "name": str(segment.site_a),
                "lat": float(segment.site_a.latitude),
                "lng": float(segment.site_a.longitude),
            }
        except (ValueError, TypeError, AttributeError):
            pass

        try:
            site_b_data = {
                "id": segment.site_b.pk,
                "name": str(segment.site_b),
                "lat": float(segment.site_b.latitude),
                "lng": float(segment.site_b.longitude),
            }
        except (ValueError, TypeError, AttributeError):
            pass

        # Type-specific technical data (brief summary for info card)
        type_data = None
        try:
            if segment.segment_type == SegmentTypeChoices.DARK_FIBER:
                d = segment.dark_fiber_data
                type_data = {k: v for k, v in {
                    "Fiber mode": d.get_fiber_mode_display() or None,
                    "Single-mode subtype": d.get_single_mode_subtype_display() or None,
                    "Multimode subtype": d.get_multimode_subtype_display() or None,
                    "Jacket type": d.get_jacket_type_display() or None,
                    "Attenuation max": f"{d.fiber_attenuation_max} dB/km" if d.fiber_attenuation_max else None,
                    "Total loss": f"{d.total_loss} dB" if d.total_loss else None,
                    "Total length": f"{d.total_length} km" if d.total_length else None,
                    "Fiber count": d.number_of_fibers,
                    "Connector A": d.get_connector_type_side_a_display() or None,
                    "Connector B": d.get_connector_type_side_b_display() or None,
                }.items() if v is not None}
            elif segment.segment_type == SegmentTypeChoices.OPTICAL_SPECTRUM:
                d = segment.optical_spectrum_data
                type_data = {k: v for k, v in {
                    "Wavelength": f"{d.wavelength} nm" if d.wavelength else None,
                    "Slot width": f"{d.spectral_slot_width} GHz" if d.spectral_slot_width else None,
                    "ITU grid position": d.itu_grid_position,
                    "Chromatic dispersion": f"{d.chromatic_dispersion} ps/nm" if d.chromatic_dispersion else None,
                    "PMD tolerance": f"{d.pmd_tolerance} ps" if d.pmd_tolerance else None,
                    "Modulation": d.get_modulation_format_display() or None,
                }.items() if v is not None}
            elif segment.segment_type == SegmentTypeChoices.ETHERNET_SERVICE:
                d = segment.ethernet_service_data
                type_data = {k: v for k, v in {
                    "Port speed": f"{d.port_speed} Mbps" if d.port_speed else None,
                    "VLAN ID": d.vlan_id,
                    "VLAN tags": d.vlan_tags or None,
                    "Encapsulation": d.get_encapsulation_type_display() or None,
                    "Interface type": d.get_interface_type_display() or None,
                    "MTU": f"{d.mtu_size} B" if d.mtu_size else None,
                }.items() if v is not None}
        except Exception:
            pass

        segments_data.append({
            "id": segment.pk,
            "name": segment.name,
            "provider": str(segment.provider) if segment.provider else None,
            "provider_id": segment.provider.pk if segment.provider else None,
            "provider_segment_id": segment.provider_segment_id or None,
            "status": segment.get_status_display(),
            "status_color": segment.get_status_color(),
            "segment_type": segment.get_segment_type_display(),
            "segment_type_color": segment.get_segment_type_color(),
            "ownership_type": segment.get_ownership_type_display(),
            "ownership_type_color": segment.get_ownership_type_color(),
            "path_length_km": float(segment.path_length_km) if segment.path_length_km else None,
            "site_a": site_a_data,
            "site_b": site_b_data,
            "has_path_data": segment.has_path_data(),
            "type_data": type_data,
            "tags": [{"name": t.name, "color": t.color} for t in segment.tags.all()],
            "url": segment.get_absolute_url(),
            "map_url": f"/plugins/cesnet-service-path-plugin/segments/{segment.pk}/map/",
        })
    return segments_data


def _term_connection(term):
    """
    Return a human-readable connection string for a CircuitTermination, or None.
    Mirrors the logic in circuits/inc/circuit_termination_fields.html:
      "<cable> to <device> / <peer port>"
    Requires cable__terminations to be prefetched on the termination.
    """
    if not term:
        return None
    if term.mark_connected:
        return "Marked as connected"
    if not term.cable:
        return None
    parts = [str(term.cable)]
    try:
        for peer in term.link_peers:
            peer_parts = []
            if hasattr(peer, 'device') and peer.device:
                peer_parts.append(str(peer.device))
            elif hasattr(peer, 'circuit') and peer.circuit:
                peer_parts.append(str(peer.circuit))
            peer_parts.append(str(peer))
            parts.append(" / ".join(peer_parts))
    except Exception:
        pass
    return " → ".join(parts)


def _term_info(term, resolved_site):
    """
    Build a dict of termination details for the info card.
    resolved_site is the already-resolved Site object (from term._site
    traversal earlier in the loop) — we use it directly rather than
    re-reading term._site, which relies on a cached FK that may not be
    populated for all termination types.
    """
    if not term:
        return None
    info = {
        "site":           str(resolved_site),
        "termination_pk": term.pk,
    }
    conn = _term_connection(term)
    if conn:
        info["connection"] = conn
    if term.xconnect_id:
        info["xconnect_id"] = term.xconnect_id
    if term.pp_info:
        info["pp_info"] = term.pp_info
    if term.port_speed:
        info["port_speed"] = f"{term.port_speed} Kbps"
    if term.description:
        info["description"] = term.description
    return info


def _build_circuits_data(circuit_qs):
    """
    Build the JS-ready list of circuit objects.
    Circuits without both termination sites having valid coordinates are skipped.
    """
    circuits_data = []
    for circuit in circuit_qs:
        site_a = None
        site_z = None
        site_a_data = None
        site_b_data = None

        try:
            site_a = circuit.termination_a._site
            site_a_data = {
                "id":   site_a.pk,
                "name": str(site_a),
                "lat":  float(site_a.latitude),
                "lng":  float(site_a.longitude),
            }
        except (ValueError, TypeError, AttributeError):
            pass

        try:
            site_z = circuit.termination_z._site
            site_b_data = {
                "id":   site_z.pk,
                "name": str(site_z),
                "lat":  float(site_z.latitude),
                "lng":  float(site_z.longitude),
            }
        except (ValueError, TypeError, AttributeError):
            pass

        if not site_a_data or not site_b_data:
            continue

        circuits_data.append({
            "id":               circuit.pk,
            "cid":              circuit.cid,
            "provider":         str(circuit.provider) if circuit.provider else None,
            "provider_id":      circuit.provider.pk if circuit.provider else None,
            "status":           circuit.get_status_display(),
            "type":             str(circuit.type) if circuit.type else None,
            "type_id":          circuit.type.pk if circuit.type else None,
            "tenant":           str(circuit.tenant) if circuit.tenant else None,
            "tenant_id":        circuit.tenant.pk if circuit.tenant else None,
            "install_date":     str(circuit.install_date) if circuit.install_date else None,
            "termination_date": str(circuit.termination_date) if circuit.termination_date else None,
            "tags":             [{"name": t.name, "color": t.color} for t in circuit.tags.all()],
            "term_a":           _term_info(circuit.termination_a, site_a),
            "term_z":           _term_info(circuit.termination_z, site_z),
            "site_a":           site_a_data,
            "site_b":           site_b_data,
            "url":              circuit.get_absolute_url(),
        })
    return circuits_data


def _compute_bounds(sites_data, segments_data, circuits_data=None):
    """
    Compute the geographic bounding box across all renderable objects.
    """
    bounds = {"minLat": None, "maxLat": None, "minLng": None, "maxLng": None}

    coords = []
    for site in sites_data:
        coords.append((site["lat"], site["lng"]))
    for seg in segments_data:
        if seg["site_a"]:
            coords.append((seg["site_a"]["lat"], seg["site_a"]["lng"]))
        if seg["site_b"]:
            coords.append((seg["site_b"]["lat"], seg["site_b"]["lng"]))
    for circ in (circuits_data or []):
        if circ["site_a"]:
            coords.append((circ["site_a"]["lat"], circ["site_a"]["lng"]))
        if circ["site_b"]:
            coords.append((circ["site_b"]["lat"], circ["site_b"]["lng"]))

    for lat, lng in coords:
        if bounds["minLat"] is None or lat < bounds["minLat"]:
            bounds["minLat"] = lat
        if bounds["maxLat"] is None or lat > bounds["maxLat"]:
            bounds["maxLat"] = lat
        if bounds["minLng"] is None or lng < bounds["minLng"]:
            bounds["minLng"] = lng
        if bounds["maxLng"] is None or lng > bounds["maxLng"]:
            bounds["maxLng"] = lng

    return bounds


class ObjectMapView(View):
    template_name = "cesnet_service_path_plugin/object_map.html"

    def get(self, request):
        filter_form = MapFilterForm()

        # Always load all renderable objects — filtering is done client-side in JS.
        site_qs = Site.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
        ).select_related("region", "group", "tenant")
        segment_qs = Segment.objects.all()
        circuit_qs = Circuit.objects.select_related(
            "termination_a",
            "termination_z",
            "provider",
            "type",
        ).prefetch_related(
            "termination_a__cable__terminations",
            "termination_z__cable__terminations",
        )

        # Cap at MAX_OBJECTS to keep the page load fast; JS filters within that set.
        sites_truncated    = site_qs.count()    > MAX_OBJECTS
        segments_truncated = segment_qs.count() > MAX_OBJECTS
        circuits_truncated = circuit_qs.count() > MAX_OBJECTS
        if sites_truncated:
            site_qs = site_qs[:MAX_OBJECTS]
        if segments_truncated:
            segment_qs = segment_qs[:MAX_OBJECTS]
        if circuits_truncated:
            circuit_qs = circuit_qs[:MAX_OBJECTS]

        sites_data       = _build_sites_data(site_qs)
        segments_data    = _build_segments_data(segment_qs)
        circuits_data    = _build_circuits_data(circuit_qs)
        region_ancestors = _build_region_ancestors()
        map_bounds       = _compute_bounds(sites_data, segments_data, circuits_data)

        if map_bounds["minLat"] is None:
            map_center = {"lat": 49.75, "lng": 15.5, "zoom": 7}
        else:
            map_center = {
                "lat": (map_bounds["minLat"] + map_bounds["maxLat"]) / 2,
                "lng": (map_bounds["minLng"] + map_bounds["maxLng"]) / 2,
                "zoom": 7,
            }

        context = {
            "filter_form": filter_form,
            "site_status_choices": [
                (v, label, _SITE_STATUS_COLORS.get(v, "secondary"))
                for v, label in SiteStatusChoices
            ],
            "segment_status_choices": [
                (v, label, _SEGMENT_STATUS_COLORS.get(v, "secondary"))
                for v, label in StatusChoices
            ],
            "segment_type_choices": [
                (v, label, _SEGMENT_TYPE_COLORS.get(v, "secondary"))
                for v, label in SegmentTypeChoices
            ],
            "circuit_status_choices": [
                (v, label, _CIRCUIT_STATUS_COLORS.get(v, "secondary"))
                for v, label in CircuitStatusChoices
            ],
            "sites_data_json":         json.dumps(sites_data),
            "segments_data_json":      json.dumps(segments_data),
            "circuits_data_json":      json.dumps(circuits_data),
            "region_ancestors_json":   json.dumps(region_ancestors),
            "map_bounds_json":         json.dumps(map_bounds),
            "map_center_json":         json.dumps(map_center),
            "total_sites":             len(sites_data),
            "total_segments":          len(segments_data),
            "total_circuits":          len(circuits_data),
            "sites_truncated":         sites_truncated,
            "segments_truncated":      segments_truncated,
            "circuits_truncated":      circuits_truncated,
            "segments_api_url": request.build_absolute_uri(
                "/plugins/cesnet-service-path-plugin/segments/map/api/"
            ),
        }
        return render(request, self.template_name, context)
