Current Implementation Testing (Ready to Use)
1. Basic Segment Type Filtering
graphqlquery {
  segment_list(filters: {segment_type: {exact: "dark_fiber"}}) {
    id
    name
    segment_type
    segment_type_display
    type_specific_data
    type_specific_display
    type_specific_schema
    has_type_specific_data
  }
}
2. Multiple Segment Types
graphqlquery {
  segment_list(filters: {segment_type: {in_: ["dark_fiber", "optical_spectrum"]}}) {
    id
    name
    segment_type
    segment_type_display
    type_specific_data
    type_specific_display
  }
}
3. Filter by Status and Segment Type
graphqlquery {
  segment_list(filters: {
    segment_type: {exact: "optical_spectrum"},
    status: {exact: "active"}
  }) {
    id
    name
    status
    segment_type
    type_specific_data
    type_specific_display
  }
}
4. Complete Segment Information with Relations
graphqlquery {
  segment_list(filters: {segment_type: {exact: "dark_fiber"}}) {
    id
    name
    segment_type
    segment_type_display
    status
    network_label
    install_date
    termination_date
    type_specific_data
    type_specific_display
    type_specific_schema
    has_type_specific_data
    has_path_data
    path_length_km
    path_source_format
    path_notes
    provider {
      id
      name
    }
    site_a {
      id
      name
      region {
        name
      }
    }
    site_b {
      id
      name
      region {
        name
      }
    }
    location_a {
      id
      name
    }
    location_b {
      id
      name
    }
    circuits {
      id
      cid
      status
    }
  }
}
5. Path Data Analysis
graphqlquery {
  segments_with_paths: segment_list(filters: {path_geometry: {isnull: false}}) {
    id
    name
    segment_type
    has_path_data
    path_length_km
    path_source_format
    path_segment_count
    path_total_points
    path_bounds {
      xmin
      ymin
      xmax
      ymax
    }
  }
  
  segments_without_paths: segment_list(filters: {path_geometry: {isnull: true}}) {
    id
    name
    segment_type
    has_path_data
  }
}
Advanced Filtering Examples (Requires Enhanced Implementation)
6. Dark Fiber Technical Specifications
graphql# Note: These filters require the enhanced GraphQL implementation
query PremiumDarkFiber {
  segment_list(filters: {
    segment_type: {exact: "dark_fiber"},
    fiber_type: {exact: "G.652D"},
    total_loss: {lte: 20.0},
    number_of_fibers: {gte: 48},
    connector_type: {exact: "LC/APC"}
  }) {
    id
    name
    type_specific_data
    type_specific_display
  }
}
7. Optical Spectrum C-Band Filtering
graphql# Note: Requires enhanced implementation
query CBandChannels {
  segment_list(filters: {
    segment_type: {exact: "optical_spectrum"},
    wavelength: {gte: 1530.0, lte: 1565.0},
    modulation_format: {exact: "DP-QPSK"}
  }) {
    id
    name
    type_specific_data
    type_specific_display
  }
}
8. High-Speed Ethernet Services
graphql# Note: Requires enhanced implementation
query HighSpeedEthernet {
  segment_list(filters: {
    segment_type: {exact: "ethernet_service"},
    port_speed: {gte: 1000},
    vlan_id: {gte: 100, lte: 4000},
    interface_type: {in_: ["SFP+", "QSFP+", "QSFP28"]}
  }) {
    id
    name
    type_specific_data
    type_specific_display
  }
}
Specialized Queries for Different Use Cases
9. Network Inventory Analysis
graphqlquery NetworkInventoryByType {
  dark_fiber_count: segment_list(filters: {segment_type: {exact: "dark_fiber"}}) {
    totalCount
  }
  
  optical_spectrum_count: segment_list(filters: {segment_type: {exact: "optical_spectrum"}}) {
    totalCount
  }
  
  ethernet_service_count: segment_list(filters: {segment_type: {exact: "ethernet_service"}}) {
    totalCount
  }
  
  active_segments: segment_list(filters: {status: {exact: "active"}}) {
    totalCount
  }
  
  segments_with_specs: segment_list(filters: {type_specific_data: {ne: "{}"}}) {
    totalCount
  }
}
10. Provider Analysis
graphqlquery ProviderSegmentAnalysis($provider_name: String!) {
  provider_segments: segment_list(filters: {
    provider: {name: {icontains: $provider_name}}
  }) {
    id
    name
    segment_type
    segment_type_display
    status
    network_label
    provider {
      name
    }
    site_a {
      name
    }
    site_b {
      name
    }
    has_type_specific_data
    type_specific_data
  }
}

# Variables for the query above:
# {"provider_name": "cesnet"}
11. Geographic Analysis
graphqlquery GeographicSegmentAnalysis($site_name: String!) {
  segments_from_site: segment_list(filters: {
    site_a: {name: {icontains: $site_name}}
  }) {
    id
    name
    segment_type
    site_a { name }
    site_b { name }
    path_length_km
    has_path_data
  }
  
  segments_to_site: segment_list(filters: {
    site_b: {name: {icontains: $site_name}}
  }) {
    id
    name
    segment_type
    site_a { name }
    site_b { name }
    path_length_km
    has_path_data
  }
}

# Variables: {"site_name": "prague"}
12. Technical Capacity Overview
graphqlquery TechnicalCapacityOverview {
  # Get all segments with their type-specific data
  all_segments: segment_list(filters: {type_specific_data: {ne: "{}"}}) {
    id
    name
    segment_type
    segment_type_display
    type_specific_data
    type_specific_display
    type_specific_schema
    provider {
      name
    }
    path_length_km
  }
}
Data Validation and Schema Exploration
13. Schema Introspection
graphqlquery SchemaExploration {
  # Get available fields for SegmentType
  __type(name: "SegmentType") {
    name
    description
    fields {
      name
      type {
        name
        kind
        ofType {
          name
        }
      }
      description
      isDeprecated
    }
  }
}
14. Filter Options Discovery
graphqlquery FilterOptionsDiscovery {
  # Discover available filter options
  __type(name: "SegmentFilter") {
    name
    inputFields {
      name
      type {
        name
        kind
        inputFields {
          name
          type {
            name
            kind
          }
        }
      }
      description
    }
  }
}
15. Validate Type-Specific Data Consistency
graphqlquery DataConsistencyCheck {
  dark_fiber_segments: segment_list(filters: {segment_type: {exact: "dark_fiber"}}) {
    id
    name
    segment_type
    has_type_specific_data
    type_specific_data
    type_specific_schema
  }
  
  optical_spectrum_segments: segment_list(filters: {segment_type: {exact: "optical_spectrum"}}) {
    id
    name
    segment_type
    has_type_specific_data
    type_specific_data
    type_specific_schema
  }
  
  ethernet_service_segments: segment_list(filters: {segment_type: {exact: "ethernet_service"}}) {
    id
    name
    segment_type
    has_type_specific_data
    type_specific_data
    type_specific_schema
  }
}
Pagination and Performance Testing
16. Paginated Results with Cursor-Based Pagination
graphqlquery PaginatedSegments($first: Int!, $after: String) {
  segment_list(
    first: $first,
    after: $after,
    filters: {segment_type: {exact: "dark_fiber"}}
  ) {
    edges {
      node {
        id
        name
        segment_type
        type_specific_data
        provider {
          name
        }
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}

# Variables: {"first": 10, "after": null}
17. Performance Testing with Large Result Sets
graphqlquery PerformanceTest {
  # Request minimal fields for performance testing
  all_segments_minimal: segment_list {
    id
    name
    segment_type
  }
  
  # Request full data for comparison
  segments_with_all_data: segment_list(first: 5) {
    id
    name
    segment_type
    segment_type_display
    status
    network_label
    install_date
    termination_date
    type_specific_data
    type_specific_display
    type_specific_schema
    has_type_specific_data
    has_path_data
    path_length_km
    provider {
      id
      name
    }
    site_a {
      id
      name
    }
    site_b {
      id
      name
    }
    circuits {
      id
      cid
    }
  }
}
Service Path Integration
18. Service Paths with Segment Details
graphqlquery ServicePathAnalysis {
  service_path_list(filters: {status: {exact: "active"}}) {
    id
    name
    kind
    status
    segments {
      id
      name
      segment_type
      segment_type_display
      type_specific_data
      path_length_km
      has_path_data
      provider {
        name
      }
      site_a {
        name
      }
      site_b {
        name
      }
    }
  }
}
19. Circuit Mapping Analysis
graphqlquery CircuitMappingAnalysis {
  segment_circuit_mapping_list {
    id
    segment {
      id
      name
      segment_type
      type_specific_data
    }
    circuit {
      id
      cid
      status
      provider {
        name
      }
    }
  }
}
Error Testing and Edge Cases
20. Test Invalid Filters (Should Return Empty or Error)
graphqlquery ErrorTesting {
  # Test non-existent segment type
  invalid_type: segment_list(filters: {segment_type: {exact: "non_existent_type"}}) {
    id
    name
  }
  
  # Test with empty filters
  empty_filters: segment_list(filters: {}) {
    totalCount
  }
  
  # Test complex combination
  complex_filter: segment_list(filters: {
    segment_type: {exact: "dark_fiber"},
    status: {exact: "active"},
    install_date: {gte: "2020-01-01"},
    termination_date: {lte: "2030-12-31"}
  }) {
    id
    name
    install_date
    termination_date
  }
}