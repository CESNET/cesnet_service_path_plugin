# GraphQL examples for testing
## 1. Segments
### All Segments
```graphql
query AllSegments {
  segment_list {
    id
    name
    network_label
    status
    segment_type
    segment_type_display
    install_date
    termination_date
    comments
  }
}
```
### Segment detail
```graphql
query SegmentDetails($id: ID!) {
  segment(id: $id) {
    id
    name
    network_label
    status
    segment_type
    segment_type_display
    provider {
      id
      name
    }
    provider_segment_id
    site_a {
      id
      name
    }
    location_a {
      id
      name
    }
    site_b {
      id
      name
    }
    location_b {
      id
      name
    }
    type_specific_technicals
    has_type_specific_data
    has_path_data
    path_length_km
    path_source_format
    path_notes
    comments
  }
}
```
Variable must be set
```json
{
  "id": 10
}
```

### Exact segment type with specific data
```graphql
query DarkFiber {
  segment_list(
    filters: {
      segment_type: { exact: "dark_fiber" },
      has_type_specific_data: true
    }
  ) {
    id
    name
    segment_type
    type_specific_technicals
    has_path_data
    has_type_specific_data
  }
}
```

### Type-Specific Technical Data Examples

#### Dark Fiber Segment with Technical Details
```graphql
query DarkFiberDetails($id: ID!) {
  segment(id: $id) {
    id
    name
    segment_type
    type_specific_technicals
  }
}
```
Example response for `type_specific_technicals`:
```json
{
  "id": 1,
  "segment": {
    "id": 123,
    "url": "http://netbox/api/plugins/cesnet-service-path-plugin/segments/123/",
    "display": "Segment 123"
  },
  "fiber_mode": "single_mode",
  "single_mode_subtype": "g652d",
  "multimode_subtype": null,
  "jacket_type": "lszh",
  "fiber_attenuation_max": "0.25",
  "total_loss": "5.50",
  "total_length": "22.00",
  "number_of_fibers": 48,
  "connector_type_side_a": "lc_apc",
  "connector_type_side_b": "lc_apc",
  "comments": ""
}
```

#### Optical Spectrum Segment with Technical Details
```graphql
query OpticalSpectrumDetails($id: ID!) {
  segment(id: $id) {
    id
    name
    segment_type
    type_specific_technicals
  }
}
```
Example response for `type_specific_technicals`:
```json
{
  "id": 2,
  "segment": {
    "id": 456,
    "url": "http://netbox/api/plugins/cesnet-service-path-plugin/segments/456/",
    "display": "Segment 456"
  },
  "wavelength": "1550.12",
  "spectral_slot_width": "50.00",
  "itu_grid_position": 23,
  "chromatic_dispersion": "16.50",
  "pmd_tolerance": "2.10",
  "modulation_format": "dp_qpsk",
  "comments": ""
}
```

#### Ethernet Service Segment with Technical Details
```graphql
query EthernetServiceDetails($id: ID!) {
  segment(id: $id) {
    id
    name
    segment_type
    type_specific_technicals
  }
}
```
Example response for `type_specific_technicals`:
```json
{
  "id": 3,
  "segment": {
    "id": 789,
    "url": "http://netbox/api/plugins/cesnet-service-path-plugin/segments/789/",
    "display": "Segment 789"
  },
  "port_speed": 10000,
  "vlan_id": 100,
  "vlan_tags": "100,200,300",
  "encapsulation_type": "dot1q",
  "interface_type": "sfp_plus",
  "mtu_size": 9000,
  "comments": ""
}
```

**Note**: The `type_specific_technicals` field returns `null` if no technical data exists for the segment.
### Complex filtering - Active dark fiber segments with path data
```graphql
query ActiveDarkFiberWithPaths {
  segment_list(
    filters: {
      segment_type: { exact: "dark_fiber" },
      status: { exact: "active" },
      has_path_data: true
    }
  ) {
    id
    name
    segment_type_display
    has_path_data
    path_length_km
    path_source_format
  }
}
```
### Segments with path geometry data 
Heavy load - with all paths in GeoJSON
```graphql
query SegmentsWithPaths {
  segment_list(
    filters: {
      has_path_data: true
    }
  ) {
    id
    name
    has_path_data
    path_length_km
    path_coordinates
    path_bounds {
      xmin
      ymin
      xmax
      ymax
    }
    path_geometry_geojson
  }
}
```

## 2. Service paths
### Get all service paths with their segments
```graphql
query AllServicePaths {
  service_path_list {
    id
    name
    status
    kind
    segments {
      id
      name
      segment_type
      status
    }
    comments
  }
}
```
### Get a specific service path with detailed segment information
```graphql
query ServicePathDetails($id: ID!) {
  service_path(id: $id) {
    id
    name
    status
    kind
    segments {
      id
      name
      segment_type
      segment_type_display
      provider {
        name
      }
      site_a {
        name
      }
      site_b {
        name
      }
      path_length_km
      has_path_data
    }
    comments
  }
}
```
Variable must be set
```json
{
  "id": 10
}
```
### Filtering - active core service paths 
```graphql
query ActiveCore {
  service_path_list(
    filters: {
      status: { exact: "active" },
      kind: { exact: "core" }
    }
  ) {
    id
    name
    status
    kind
    segments {
      id
      name
    }
  }
}
```
## 3. Circuit Mapping
### Get all segment-circuit mappings
```graphql
query SegmentCircuitMappings {
  segment_circuit_mapping_list {
    id
    segment {
      id
      name
      segment_type
    }
    circuit {
      id
      cid
      provider {
        name
      }
    }
  }
}
```
### Get circuits for a specific segment
```graphql
query CircuitsForSegment($segmentId: ID!) {
  segment_circuit_mapping_list(
    filters: {
      segment: { id: $segmentId }
    }
  ) {
    id
    circuit {
      id
      cid
      provider {
        name
      }
      status
    }
  }
}
```
Variable must be set
```json
{
  "segmentId": 10
}
```
### Get segments for a specific circuit
```graphql
query SegmentsForCircuit($circuitId: ID!) {
  segment_circuit_mapping_list(
    filters: {
      circuit: { id: $circuitId }
    }
  ) {
    id
    segment {
      id
      name
      segment_type
      status
    }
  }
}
```
Variable must be set
```json
{
  "circuitId": 10
}
```