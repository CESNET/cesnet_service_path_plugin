# API Usage Examples

## Retrieving Segment with Path Data (GET)

By default, the segment detail endpoint returns basic segment information without the full path geometry data. To include detailed path data (GeoJSON geometry), use the `pathdata` query parameter:

```bash
# Get segment without path data (default)
curl -H "Authorization: Token YOUR_API_TOKEN" \
  "http://localhost:8000/api/plugins/cesnet_service_path_plugin/segments/10/"

# Get segment WITH full path data (GeoJSON geometry included)
curl -H "Authorization: Token YOUR_API_TOKEN" \
  "http://localhost:8000/api/plugins/cesnet_service_path_plugin/segments/10/?pathdata=true"
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pathdata` | boolean | `false` | When set to `true`, returns the full path geometry data in GeoJSON format |

**Note:** The `pathdata` parameter only affects the detail endpoint (single segment retrieval). List endpoints always return segments without full path geometry to optimize performance.

## Creating a New Segment with Path Data (POST)

Create a new segment with all required fields and upload path geometry from a file:

```bash
curl -X POST "http://localhost:8000/api/plugins/cesnet_service_path_plugin/segments/" \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -F "name=Test Segment API" \
  -F "status=active" \
  -F "provider=32" \
  -F "site_a=314" \
  -F "location_a=387" \
  -F "site_b=36" \
  -F "location_b=24" \
  -F "network_label=API-TEST-01" \
  -F "provider_segment_id=API-TEST-SEGMENT-001" \
  -F "path_file=@/path/to/your/segment_path.kmz" \
  -F "path_notes=Path data uploaded via API" \
  -F "install_date=2024-01-15" \
  -F "termination_date=2024-12-31"
```

**Supported file formats:**
- GeoJSON files: `.geojson`, `.json`
- KML files: `.kml`
- KMZ files: `.kmz`

## Updating an Existing Segment (PATCH)

Update segment with ID 10 - you can update any combination of fields:

### Update Path Data Only
```bash
curl -X PATCH "http://localhost:8000/api/plugins/cesnet_service_path_plugin/segments/10/" \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -F "path_file=@/home/albert/cesnet/netbox/data/prubehy/segment_10_Mapa-Trasa.kmz" \
  -F "path_notes=Updated path data via API"
```

### Update Multiple Fields Including Path Data
```bash
curl -X PATCH "http://localhost:8000/api/plugins/cesnet_service_path_plugin/segments/10/" \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -F "network_label=UPDATED-LABEL" \
  -F "status=planned" \
  -F "path_file=@/path/to/updated_path.geojson" \
  -F "path_notes=Updated both metadata and path geometry" \
  -F "termination_date=2025-06-30"
```

## Important Notes

1. **Authentication**: Replace `YOUR_API_TOKEN` with your actual NetBox API token
2. **Content-Type**: Use `multipart/form-data` (automatic with `-F` flag) when uploading files
3. **File Path**: Use absolute paths for the `path_file` parameter
4. **Required Fields**: For POST requests, ensure all required fields are included:
   - `name`, `status`, `provider`, `site_a`, `site_b`
   - Optional: `location_a`, `location_b` (must belong to their respective sites if provided)
5. **Field IDs**: Use numeric IDs for foreign key fields (provider, sites, locations)
6. **Path Processing**: Files are automatically processed and geometry is calculated
7. **Error Handling**: Invalid files will return detailed error messages

## Response Example

Successful upload will return the segment data with path information:

```json
{
  "id": 10,
  "name": "Test Segment API",
  "status": "active",
  "path_length_km": "125.456",
  "path_source_format": "kmz",
  "path_notes": "Path data uploaded via API",
  "has_path_data": true,
  ...
}
```

## Getting Field IDs

To find the correct IDs for providers, sites, and locations:

```bash
# List providers
curl -H "Authorization: Token YOUR_API_TOKEN" \
  "http://localhost:8000/api/circuits/providers/"

# List sites
curl -H "Authorization: Token YOUR_API_TOKEN" \
  "http://localhost:8000/api/dcim/sites/"

# List locations for a specific site
curl -H "Authorization: Token YOUR_API_TOKEN" \
  "http://localhost:8000/api/dcim/locations/?site_id=314"
```