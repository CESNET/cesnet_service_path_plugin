from netbox.views import generic
from utilities.views import register_model_view
import json
import logging


from cesnet_service_path_plugin.filtersets import ServicePathFilterSet
from cesnet_service_path_plugin.forms import (
    ServicePathBulkEditForm,
    ServicePathFilterForm,
    ServicePathForm,
)
from cesnet_service_path_plugin.models import ServicePath
from cesnet_service_path_plugin.tables import ServicePathTable

logger = logging.getLogger(__name__)


@register_model_view(ServicePath)
class ServicePathView(generic.ObjectView):
    queryset = ServicePath.objects.all()

    def get_extra_context(self, request, instance):
        """Build topology data for Cytoscape visualization"""
        context = super().get_extra_context(request, instance)

        # Build topology data
        topology_data = self._build_topology_data(instance)

        logger.debug(f"Topology data: {topology_data}")

        # Serialize to JSON for template
        context["topology_data"] = json.dumps(topology_data)

        return context

    def _build_topology_data(self, service_path):
        """
        Build nodes and edges for Cytoscape visualization

        Structure:
        - Service Path (top level)
          - Segments (middle level, children of service path)
            - Sites (children of segments)
            - Circuits (connections between sites)
        """
        nodes = []
        edges = []

        # Add service path node (top level)
        service_path_id = f"service-{service_path.pk}"
        nodes.append(
            {
                "data": {
                    "id": service_path_id,
                    "netbox_id": service_path.pk,
                    "label": service_path.name,
                    "type": "service",
                    "description": f"Service Path: {service_path.name}",
                    "status": service_path.get_status_display(),
                    "kind": service_path.get_kind_display(),
                }
            }
        )

        # Get segments with related data
        segments = (
            service_path.segments.select_related("provider", "site_a", "site_b").prefetch_related("circuits").all()
        )

        # Track unique sites and circuits to avoid duplicates
        seen_sites = {}  # site.pk -> segment.pk (which segment owns this site)
        seen_circuits = set()

        # Process each segment
        for segment in segments:
            segment_id = f"segment-{segment.pk}"

            # Add segment node
            nodes.append(
                {
                    "data": {
                        "id": segment_id,
                        "netbox_id": segment.pk,
                        "label": segment.name,
                        "type": "segment",
                        "parent": service_path_id,
                        "description": f"{segment.get_segment_type_display()} - {segment.provider.name}",
                        "provider": segment.provider.name,
                        "segment_type": segment.get_segment_type_display(),
                    }
                }
            )

            # Process sites (A and B)
            for site in [segment.site_a, segment.site_b]:
                site_id = f"site-{site.pk}"

                # Only add site if not seen, or if seen but in different segment
                # Sites can appear in multiple segments (connection points)
                if site.pk not in seen_sites:
                    # First time seeing this site
                    nodes.append(
                        {
                            "data": {
                                "id": site_id,
                                "netbox_id": site.pk,
                                "label": site.name,
                                "type": "site",
                                "parent": segment_id,
                                "description": f"Site: {site.name}",
                                "location": getattr(site, "physical_address", "") or "",
                            }
                        }
                    )
                    seen_sites[site.pk] = segment.pk
                elif seen_sites[site.pk] != segment.pk:
                    # Site appears in multiple segments - this is a connection point
                    # Don't change parent, just mark it as a connection point
                    for node in nodes:
                        if node["data"]["id"] == site_id:
                            node["data"]["is_connection_point"] = True
                            node["data"]["description"] = f"Site: {site.name} (Connection Point)"
                            break

            # Process circuits for this segment
            circuits = segment.circuits.all()

            for circuit in circuits:
                circuit_key = f"circuit-{circuit.pk}"

                # Add circuit node if not already added
                if circuit.pk not in seen_circuits:
                    # Get circuit display name
                    circuit_label = circuit.cid if hasattr(circuit, "cid") else str(circuit)

                    nodes.append(
                        {
                            "data": {
                                "id": circuit_key,
                                "netbox_id": circuit.pk,
                                "label": circuit_label,
                                "type": "circuit",
                                "parent": segment_id,  # Make circuit a child of the segment
                                "description": f"Circuit: {circuit}",
                                "provider": circuit.provider.name if circuit.provider else "",
                                "bandwidth": (
                                    str(circuit.commit_rate)
                                    if hasattr(circuit, "commit_rate") and circuit.commit_rate
                                    else ""
                                ),
                            }
                        }
                    )
                    seen_circuits.add(circuit.pk)

                # Connect sites through circuit
                site_a_id = f"site-{segment.site_a.pk}"
                site_b_id = f"site-{segment.site_b.pk}"

                # Add edges: site_a -> circuit -> site_b
                edges.append(
                    {
                        "data": {
                            "source": site_a_id,
                            "target": circuit_key,
                        }
                    }
                )
                edges.append(
                    {
                        "data": {
                            "source": circuit_key,
                            "target": site_b_id,
                        }
                    }
                )

        return {
            "nodes": nodes,
            "edges": edges,
        }


@register_model_view(ServicePath, "list", path="", detail=False)
class ServicePathListView(generic.ObjectListView):
    queryset = ServicePath.objects.all()
    table = ServicePathTable
    filterset = ServicePathFilterSet
    filterset_form = ServicePathFilterForm


@register_model_view(ServicePath, "add", detail=False)
@register_model_view(ServicePath, "edit")
class ServicePathEditView(generic.ObjectEditView):
    queryset = ServicePath.objects.all()
    form = ServicePathForm


@register_model_view(ServicePath, "delete")
class ServicePathDeleteView(generic.ObjectDeleteView):
    queryset = ServicePath.objects.all()


@register_model_view(ServicePath, "bulk_edit", path="edit", detail=False)
class ServicePathBulkEditView(generic.BulkEditView):
    queryset = ServicePath.objects.all()
    filterset = ServicePathFilterSet
    table = ServicePathTable
    form = ServicePathBulkEditForm


@register_model_view(ServicePath, "bulk_delete", path="delete", detail=False)
class ServicePathBulkDeleteView(generic.BulkDeleteView):
    queryset = ServicePath.objects.all()
    filterset = ServicePathFilterSet
    table = ServicePathTable


@register_model_view(ServicePath, "bulk_import", path="import", detail=False)
class ServicePathBulkImportView(generic.BulkImportView):
    queryset = ServicePath.objects.all()
    model_form = ServicePathForm
    table = ServicePathTable
