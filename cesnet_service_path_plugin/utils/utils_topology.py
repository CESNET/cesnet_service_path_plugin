"""
Utility functions for building network topology visualizations using Cytoscape.js

This module provides reusable functions for creating topology data structures
that can be rendered in the frontend using Cytoscape.js library.

Note about NetBox Circuit Terminations:
    In NetBox, CircuitTermination objects have relationships to sites through:
    - _site: Direct site relationship
    - _location: Location which has a site relationship
    - site/location: May also be available as non-private attributes

    We avoid using select_related('termination_a__termination') because
    'termination' is not a valid field on CircuitTermination objects.
"""

import logging
from typing import Dict, List, Set, Optional, Any

logger = logging.getLogger(__name__)


class TopologyBuilder:
    """
    Builder class for creating network topology data structures.

    Provides methods to add nodes, edges, and manage relationships between
    network elements like segments, sites, circuits, and service paths.
    """

    def __init__(self):
        self.nodes: List[Dict] = []
        self.edges: List[Dict] = []
        self.seen_sites: Dict[int, str] = {}  # site.pk -> parent_id
        self.seen_circuits: Set[int] = set()

    def get_topology_data(self) -> Dict[str, List[Dict]]:
        """Return the complete topology data structure"""
        return {
            "nodes": self.nodes,
            "edges": self.edges,
        }

    def sort_nodes_by_path_traversal(self) -> None:
        """
        Sort nodes (sites and circuits) within each segment by following the graph path.

        This method:
        1. Finds endpoint sites (sites with only one edge)
        2. Traverses the graph from an endpoint (preferring site_a)
        3. Reorders nodes to match the traversal order

        Only affects site and circuit nodes that are children of segments.
        Service and segment nodes maintain their original order.
        """
        # First pass: mark site_a nodes for each segment
        self._mark_site_a_nodes()

        # Group nodes by parent segment
        segments = {}
        non_segment_children = []

        for node in self.nodes:
            node_type = node["data"].get("type")
            parent = node["data"].get("parent")

            # Keep service and segment nodes separate
            if node_type in ["service", "segment"]:
                non_segment_children.append(node)
                continue

            # Group site and circuit nodes by their parent segment
            if parent and parent.startswith("segment-"):
                if parent not in segments:
                    segments[parent] = []
                segments[parent].append(node)
            else:
                non_segment_children.append(node)

        # Build edge lookup for quick traversal
        edge_map = self._build_edge_map()

        # Sort nodes within each segment
        sorted_segment_nodes = []
        for segment_id, segment_nodes in segments.items():
            sorted_nodes = self._sort_segment_nodes(segment_nodes, edge_map, segment_id)
            sorted_segment_nodes.extend(sorted_nodes)

        # Reconstruct nodes list: service/segment nodes first, then sorted segment children
        self.nodes = non_segment_children + sorted_segment_nodes

    def _mark_site_a_nodes(self) -> None:
        """
        Mark nodes that represent site_a in their segments.
        This helps determine the correct starting point for traversal.
        """
        # Build a map of segment_id -> site_a_id from segment nodes
        segment_site_a_map = {}

        for node in self.nodes:
            if node["data"].get("type") == "segment":
                segment_id = node["data"]["id"]
                # Look for site_a_id stored during segment creation
                if "site_a_id" in node["data"]:
                    segment_site_a_map[segment_id] = node["data"]["site_a_id"]

        # Mark site nodes that are site_a
        for node in self.nodes:
            if node["data"].get("type") == "site":
                parent_segment = node["data"].get("parent")
                if parent_segment and parent_segment in segment_site_a_map:
                    if node["data"]["id"] == segment_site_a_map[parent_segment]:
                        node["data"]["is_site_a"] = True

    def _build_edge_map(self) -> Dict[str, List[str]]:
        """
        Build a bidirectional edge map for graph traversal.

        Returns:
            Dict mapping node_id -> list of connected node_ids
        """
        edge_map = {}

        for edge in self.edges:
            source = edge["data"]["source"]
            target = edge["data"]["target"]

            # Add bidirectional connections
            if source not in edge_map:
                edge_map[source] = []
            edge_map[source].append(target)

            if target not in edge_map:
                edge_map[target] = []
            edge_map[target].append(source)

        return edge_map

    def _sort_segment_nodes(
        self, segment_nodes: List[Dict], edge_map: Dict[str, List[str]], segment_id: str = None
    ) -> List[Dict]:
        """
        Sort nodes within a segment by traversing the graph path.

        Args:
            segment_nodes: List of site and circuit nodes in this segment
            edge_map: Bidirectional edge mapping
            segment_id: Optional segment ID to determine site_a preference

        Returns:
            Sorted list of nodes following the graph path
        """
        if not segment_nodes:
            return []

        # Create lookup for quick node access
        node_lookup = {node["data"]["id"]: node for node in segment_nodes}
        node_ids = set(node_lookup.keys())

        # Find all endpoint sites (sites with only one connection)
        endpoint_sites = []
        for node_id in node_ids:
            node = node_lookup[node_id]
            if node["data"]["type"] == "site":
                # Count connections to other nodes in this segment
                connections = [conn for conn in edge_map.get(node_id, []) if conn in node_ids]
                if len(connections) == 1:
                    endpoint_sites.append(node_id)

        # Determine starting node
        start_node_id = None

        # If we have segment_id and can identify site_a, prefer it as start
        if segment_id and endpoint_sites:
            # Look for site_a marker in the segment nodes
            # Check if any endpoint has site_a_id in its data
            for node_id in endpoint_sites:
                node = node_lookup[node_id]
                # Check if this node has a marker indicating it's site_a
                if node["data"].get("is_site_a"):
                    start_node_id = node_id
                    break

            # If no site_a marker found, use first endpoint
            if start_node_id is None and endpoint_sites:
                start_node_id = endpoint_sites[0]
        elif endpoint_sites:
            # No segment context, just use first endpoint
            start_node_id = endpoint_sites[0]

        # If no endpoint found (shouldn't happen in a path), use first site
        if start_node_id is None:
            for node_id in node_ids:
                if node_lookup[node_id]["data"]["type"] == "site":
                    start_node_id = node_id
                    break

        # If still no start node, return original order
        if start_node_id is None:
            return segment_nodes

        # Traverse the graph
        sorted_nodes = []
        visited = set()
        current_id = start_node_id

        while current_id and current_id not in visited:
            # Add current node
            if current_id in node_lookup:
                sorted_nodes.append(node_lookup[current_id])
                visited.add(current_id)

            # Find next unvisited node
            next_id = None
            for connected_id in edge_map.get(current_id, []):
                if connected_id in node_ids and connected_id not in visited:
                    next_id = connected_id
                    break

            current_id = next_id

        # Add any remaining nodes that weren't in the main path (shouldn't happen)
        for node in segment_nodes:
            if node["data"]["id"] not in visited:
                sorted_nodes.append(node)

        return sorted_nodes

    def add_service_path_node(self, service_path) -> str:
        """
        Add a service path node to the topology.

        Args:
            service_path: ServicePath model instance

        Returns:
            str: The node ID for the service path
        """
        node_id = f"service-{service_path.pk}"
        self.nodes.append(
            {
                "data": {
                    "id": node_id,
                    "netbox_id": service_path.pk,
                    "label": service_path.name,
                    "type": "service",
                    "description": f"Service Path: {service_path.name}",
                    "status": service_path.get_status_display(),
                    "kind": service_path.get_kind_display(),
                }
            }
        )
        return node_id

    def add_segment_node(self, segment, parent_id: Optional[str] = None, site_a_id: Optional[str] = None) -> str:
        """
        Add a segment node to the topology.

        Args:
            segment: Segment model instance
            parent_id: Optional parent node ID (e.g., service path ID)
            site_a_id: Optional site_a ID for ordering reference

        Returns:
            str: The node ID for the segment
        """
        node_id = f"segment-{segment.pk}"
        node_data = {
            "id": node_id,
            "netbox_id": segment.pk,
            "label": segment.name,
            "type": "segment",
            "description": f"{segment.get_segment_type_display()} - {segment.provider.name}",
            "provider": segment.provider.name,
            "segment_type": segment.get_segment_type_display(),
        }

        if parent_id:
            node_data["parent"] = parent_id

        if site_a_id:
            node_data["site_a_id"] = site_a_id

        self.nodes.append({"data": node_data})
        return node_id

    def add_or_update_site_node(self, site, parent_id: str) -> str:
        """
        Add a site node to the topology or update it if already exists.

        If a site appears in multiple segments, it's marked as a connection point.

        Args:
            site: Site model instance
            parent_id: Parent node ID (typically a segment)

        Returns:
            str: The node ID for the site
        """
        site_id = f"site-{site.pk}"

        if site.pk not in self.seen_sites:
            # First time seeing this site - add new node
            self.nodes.append(
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
            self.seen_sites[site.pk] = parent_id
        elif self.seen_sites[site.pk] != parent_id:
            # Site appears in multiple segments - mark as connection point
            for node in self.nodes:
                if node["data"]["id"] == site_id:
                    node["data"]["is_connection_point"] = True
                    node["data"]["description"] = f"Site: {site.name} (Connection Point)"
                    break

        return site_id

    def add_circuit_node(self, circuit, parent_id: str) -> str:
        """
        Add a circuit node to the topology.

        Args:
            circuit: Circuit model instance
            parent_id: Parent node ID (typically a segment)

        Returns:
            str: The node ID for the circuit
        """
        circuit_id = f"circuit-{circuit.pk}"

        # Skip if already added
        if circuit.pk in self.seen_circuits:
            return circuit_id

        # Get circuit display name
        circuit_label = circuit.cid if hasattr(circuit, "cid") else str(circuit)

        # Build circuit node data
        circuit_node_data = {
            "id": circuit_id,
            "netbox_id": circuit.pk,
            "label": circuit_label,
            "type": "circuit",
            "parent": parent_id,
            "description": f"Circuit: {circuit}",
            "provider": circuit.provider.name if circuit.provider else "",
        }

        # Add status
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

        self.nodes.append({"data": circuit_node_data})
        self.seen_circuits.add(circuit.pk)

        return circuit_id

    def add_edge(self, source_id: str, target_id: str, label: Optional[str] = None) -> None:
        """
        Add an edge (connection) between two nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            label: Optional label for the edge
        """
        edge_data = {
            "source": source_id,
            "target": target_id,
        }

        if label:
            edge_data["label"] = label

        self.edges.append({"data": edge_data})

    def extract_circuit_termination_site(self, termination) -> Optional[Any]:
        """
        Extract site from a circuit termination.

        In NetBox, circuit terminations can be related to sites through different paths.
        We need to check multiple possible relationships.

        Args:
            termination: Circuit termination object

        Returns:
            Site object if found, None otherwise
        """
        if not termination:
            return None

        # Try to get site directly from termination attributes
        # NetBox circuit terminations may have _site, site, or location relationships
        if hasattr(termination, "_site") and termination._site:
            return termination._site

        if hasattr(termination, "site") and termination.site:
            return termination.site

        # Try through location
        if hasattr(termination, "_location") and termination._location:
            location = termination._location
            if hasattr(location, "site") and location.site:
                return location.site

        if hasattr(termination, "location") and termination.location:
            location = termination.location
            if hasattr(location, "site") and location.site:
                return location.site

        # Legacy approach - check if termination has a 'termination' attribute
        # (This was in the original code but may not be needed)
        if hasattr(termination, "termination") and termination.termination:
            term_obj = termination.termination
            # Check if termination is a site
            if hasattr(term_obj, "_meta") and term_obj._meta.model_name == "site":
                return term_obj

        return None

    def process_circuit_with_sites(
        self, circuit, segment_id: str, fallback_site_a_id: str, fallback_site_b_id: str
    ) -> None:
        """
        Process a circuit and create edges connecting it to sites.

        This method:
        1. Adds the circuit node if not already added
        2. Extracts termination sites from the circuit
        3. Adds termination sites if they're new
        4. Creates edges connecting sites through the circuit

        Args:
            circuit: Circuit model instance
            segment_id: Parent segment ID
            fallback_site_a_id: Fallback site A ID if termination A site not found
            fallback_site_b_id: Fallback site B ID if termination Z site not found
        """
        # Add circuit node
        circuit_id = self.add_circuit_node(circuit, segment_id)

        # Extract termination sites
        termination_a_site = None
        termination_z_site = None

        if hasattr(circuit, "termination_a"):
            termination_a_site = self.extract_circuit_termination_site(circuit.termination_a)

        if hasattr(circuit, "termination_z"):
            termination_z_site = self.extract_circuit_termination_site(circuit.termination_z)

        # Add termination sites or use fallbacks
        if termination_a_site:
            term_a_site_id = self.add_or_update_site_node(termination_a_site, segment_id)
        else:
            term_a_site_id = fallback_site_a_id

        if termination_z_site:
            term_z_site_id = self.add_or_update_site_node(termination_z_site, segment_id)
        else:
            term_z_site_id = fallback_site_b_id

        # Create edges
        self.add_edge(term_a_site_id, circuit_id, "Term A")
        self.add_edge(circuit_id, term_z_site_id, "Term Z")


def build_service_path_topology(service_path) -> Dict[str, List[Dict]]:
    """
    Build complete topology data for a service path.

    Structure:
    - Service Path (top level)
      - Segments (children of service path)
        - Sites (children of segments)
        - Circuits (children of segments, connected to sites)

    Args:
        service_path: ServicePath model instance with prefetched relationships

    Returns:
        Dict with 'nodes' and 'edges' lists for Cytoscape
    """
    builder = TopologyBuilder()

    # Add service path node
    service_path_id = builder.add_service_path_node(service_path)

    # Get segments with related data
    # Note: We don't use select_related on termination_a__termination
    # because 'termination' is not a valid field in NetBox's CircuitTermination model
    segments = (
        service_path.segments.select_related("provider", "site_a", "site_b")
        .prefetch_related(
            "circuits",
            "circuits__provider",
            "circuits__type",
            "circuits__termination_a",
            "circuits__termination_z",
        )
        .all()
    )

    # Process each segment
    for segment in segments:
        # Add segment sites first to get their IDs
        site_a_id = f"site-{segment.site_a.pk}"
        site_b_id = f"site-{segment.site_b.pk}"

        # Add segment node with site_a reference
        segment_id = builder.add_segment_node(segment, parent_id=service_path_id, site_a_id=site_a_id)

        # Add segment sites
        site_a_id = builder.add_or_update_site_node(segment.site_a, segment_id)
        site_b_id = builder.add_or_update_site_node(segment.site_b, segment_id)

        # Process circuits
        for circuit in segment.circuits.all():
            builder.process_circuit_with_sites(circuit, segment_id, site_a_id, site_b_id)

    # Sort nodes by path traversal order
    builder.sort_nodes_by_path_traversal()

    return builder.get_topology_data()


def build_segment_topology(segment) -> Dict[str, List[Dict]]:
    """
    Build topology data for a single segment.

    Structure:
    - Segment (top level)
      - Sites (children of segment)
      - Circuits (children of segment, connected to sites)

    Args:
        segment: Segment model instance with prefetched relationships

    Returns:
        Dict with 'nodes' and 'edges' lists for Cytoscape
    """
    builder = TopologyBuilder()

    # Get site IDs first
    site_a_id = f"site-{segment.site_a.pk}"
    site_b_id = f"site-{segment.site_b.pk}"

    # Add segment as root node (no parent) with site_a reference
    segment_id = builder.add_segment_node(segment, parent_id=None, site_a_id=site_a_id)

    # Add segment sites
    site_a_id = builder.add_or_update_site_node(segment.site_a, segment_id)
    site_b_id = builder.add_or_update_site_node(segment.site_b, segment_id)

    # Process circuits - use simpler prefetch without 'termination'
    # Circuit terminations in NetBox don't have a direct 'termination' relationship
    circuits = (
        segment.circuits.select_related(
            "provider",
            "type",
        )
        .prefetch_related(
            "termination_a",
            "termination_z",
        )
        .all()
    )

    for circuit in circuits:
        builder.process_circuit_with_sites(circuit, segment_id, site_a_id, site_b_id)

    # Sort nodes by path traversal order
    builder.sort_nodes_by_path_traversal()

    return builder.get_topology_data()
