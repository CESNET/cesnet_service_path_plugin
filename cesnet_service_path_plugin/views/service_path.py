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

    def _add_or_update_site(self, nodes, seen_sites, site, parent_id):
        """
        Add a site node to the topology or update it if already exists.

        Args:
            nodes: List of topology nodes
            seen_sites: Dict tracking site.pk -> parent segment.pk
            site: Site object to add
            parent_id: Parent segment ID for this site

        Returns:
            site_id: The ID of the site node
        """
        site_id = f"site-{site.pk}"

        if site.pk not in seen_sites:
            # First time seeing this site - add new node
            nodes.append(
                {
                    "data": {
                        "id": site_id,
                        "netbox_id": site.pk,
                        "label": site.name,
                        "type": "site",
                        "parent": parent_id,
                        "description": f"Site: {site.name}",
                        "location": getattr(site, "physical_address", "") or "",
                        "slug": getattr(site, "slug", ""),
                    }
                }
            )
            seen_sites[site.pk] = parent_id
        elif seen_sites[site.pk] != parent_id:
            # Site appears in multiple segments - mark as connection point
            for node in nodes:
                if node["data"]["id"] == site_id:
                    node["data"]["is_connection_point"] = True
                    node["data"]["description"] = f"Site: {site.name} (Connection Point)"
                    break

        return site_id

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
            service_path.segments.select_related("provider", "site_a", "site_b")
            .prefetch_related(
                "circuits",
                "circuits__provider",
                "circuits__type",
                "circuits__termination_a",
                "circuits__termination_a__termination",
                "circuits__termination_z",
                "circuits__termination_z__termination",
            )
            .all()
        )

        # Track unique sites and circuits to avoid duplicates
        seen_sites = {}  # site.pk -> parent segment.pk (which segment owns this site)
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

            # Process segment sites (A and B)
            segment_site_a_id = self._add_or_update_site(nodes, seen_sites, segment.site_a, segment_id)
            segment_site_b_id = self._add_or_update_site(nodes, seen_sites, segment.site_b, segment_id)

            # Process circuits for this segment
            circuits = segment.circuits.all()

            for circuit in circuits:
                circuit_key = f"circuit-{circuit.pk}"

                # Add circuit node if not already added
                if circuit.pk not in seen_circuits:
                    # Get circuit display name
                    circuit_label = circuit.cid if hasattr(circuit, "cid") else str(circuit)

                    # Build circuit node data
                    circuit_node_data = {
                        "id": circuit_key,
                        "netbox_id": circuit.pk,
                        "label": circuit_label,
                        "type": "circuit",
                        "parent": segment_id,
                        "description": f"Circuit: {circuit}",
                        "provider": circuit.provider.name if circuit.provider else "",
                    }

                    # Add status - try to get display label, otherwise use raw value
                    if hasattr(circuit, "status") and circuit.status:
                        if hasattr(circuit, "get_status_display"):
                            circuit_node_data["status"] = circuit.get_status_display()
                        else:
                            circuit_node_data["status"] = str(circuit.status)

                    # Add circuit type
                    if hasattr(circuit, "type") and circuit.type:
                        circuit_node_data["circuit_type"] = circuit.type.name

                    # Add bandwidth information
                    if hasattr(circuit, "commit_rate") and circuit.commit_rate:
                        circuit_node_data["bandwidth"] = str(circuit.commit_rate)

                    # Add additional circuit metadata
                    if hasattr(circuit, "install_date") and circuit.install_date:
                        circuit_node_data["install_date"] = str(circuit.install_date)
                    if hasattr(circuit, "termination_date") and circuit.termination_date:
                        circuit_node_data["termination_date"] = str(circuit.termination_date)

                    nodes.append({"data": circuit_node_data})
                    seen_circuits.add(circuit.pk)

                # Process circuit terminations to find connected sites
                termination_a_site = None
                termination_z_site = None

                # Extract termination A site
                if hasattr(circuit, "termination_a") and circuit.termination_a:
                    term_a = circuit.termination_a
                    if hasattr(term_a, "termination") and term_a.termination:
                        termination = term_a.termination
                        # Check if termination is a site
                        if hasattr(termination, "_meta") and termination._meta.model_name == "site":
                            termination_a_site = termination
                        # Also handle if termination_type indicates it's a site
                        elif hasattr(term_a, "termination_type") and "site" in term_a.termination_type.lower():
                            termination_a_site = termination

                # Extract termination Z site
                if hasattr(circuit, "termination_z") and circuit.termination_z:
                    term_z = circuit.termination_z
                    if hasattr(term_z, "termination") and term_z.termination:
                        termination = term_z.termination
                        # Check if termination is a site
                        if hasattr(termination, "_meta") and termination._meta.model_name == "site":
                            termination_z_site = termination
                        # Also handle if termination_type indicates it's a site
                        elif hasattr(term_z, "termination_type") and "site" in term_z.termination_type.lower():
                            termination_z_site = termination

                # Add termination sites if they exist and aren't already in the topology
                if termination_a_site:
                    term_a_site_id = self._add_or_update_site(nodes, seen_sites, termination_a_site, segment_id)
                else:
                    # Fallback to segment site A
                    term_a_site_id = segment_site_a_id

                if termination_z_site:
                    term_z_site_id = self._add_or_update_site(nodes, seen_sites, termination_z_site, segment_id)
                else:
                    # Fallback to segment site B
                    term_z_site_id = segment_site_b_id

                # Create edges connecting sites through circuit
                # Edge from termination A site to circuit
                edges.append(
                    {
                        "data": {
                            "source": term_a_site_id,
                            "target": circuit_key,
                            "label": "Term A",
                        }
                    }
                )

                # Edge from circuit to termination Z site
                edges.append(
                    {
                        "data": {
                            "source": circuit_key,
                            "target": term_z_site_id,
                            "label": "Term Z",
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
