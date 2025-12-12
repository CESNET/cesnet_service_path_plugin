# CLAUDE.md - AI Assistant Context

## Project Overview

**cesnet_service_path_plugin** is a NetBox plugin for managing network service paths and segments with advanced geographic visualization, interactive topology visualization, and financial tracking capabilities.

- **Type**: NetBox Plugin (Django application)
- **Language**: Python 3.10+
- **Framework**: Django with NetBox Plugin Framework
- **Current Version**: 5.5.0
- **License**: Apache-2.0

## Core Purpose

This plugin extends NetBox to provide comprehensive network service path management with:
- Network segment tracking between locations
- Service path definitions connecting multiple segments
- Geographic path visualization using actual route data (KML, KMZ, GeoJSON)
- Interactive topology visualization using Cytoscape.js
- Financial information tracking with multi-currency support
- Contract management with versioning

## Architecture

### Directory Structure

```
cesnet_service_path_plugin/
├── cesnet_service_path_plugin/       # Main plugin package
│   ├── api/                          # REST API (views, serializers, URLs)
│   │   ├── views/                    # API ViewSets
│   │   └── serializers/              # DRF serializers
│   ├── filtersets/                   # Django filters for list views
│   ├── forms/                        # Django forms for CRUD operations
│   ├── graphql/                      # GraphQL schema and types
│   ├── migrations/                   # Django database migrations
│   ├── models/                       # Core data models
│   │   ├── segment.py               # Network segment model
│   │   ├── service_path.py          # Service path model
│   │   ├── contract_info.py         # Contract tracking with versioning
│   │   ├── segment_types.py         # Segment type definitions
│   │   └── custom_choices.py        # Status, currency, etc. choices
│   ├── tables/                       # django-tables2 definitions
│   ├── templates/                    # Django HTML templates
│   ├── templatetags/                 # Custom template filters/tags
│   ├── utils/                        # Utility functions
│   │   ├── utils_gis.py             # Geographic data processing
│   │   └── utils_topology.py        # Topology generation
│   └── views/                        # Django views
├── tests/                            # Test suite
└── docs/                             # Documentation

```

### Key Technologies

- **Django**: Web framework (NetBox is built on Django)
- **Django GIS (GeoDjango)**: Geographic database features
- **PostGIS**: PostgreSQL extension for geographic data
- **GDAL/GEOS/PROJ**: Geographic data processing libraries
- **GeoPandas/Fiona/Shapely**: Python geographic libraries
- **Leaflet.js**: Interactive map visualization
- **Cytoscape.js**: Network topology graphs
- **Django REST Framework**: API endpoints
- **Strawberry GraphQL**: GraphQL API (via NetBox)

### Database Requirements

- PostgreSQL with PostGIS extension enabled
- Must use `django.contrib.gis.db.backends.postgis` engine
- Stores geographic data using MultiLineString geometries (SRID 4326 - WGS84)

## Core Models

### 1. Segment (`models/segment.py`)

Represents a physical network segment between two locations.

**Key Fields:**
- `name`: Segment identifier
- `network_label`: Optional network label
- `provider`: Foreign key to NetBox Provider
- `site_a`, `site_b`: Start and end sites (required)
- `location_a`, `location_b`: Specific locations within sites (optional)
- `install_date`, `termination_date`: Lifecycle dates
- `status`: Active, Planned, Offline, etc. (customizable)
- `ownership_type`: Leased, Owned, etc.
- `segment_type`: Dark fiber, optical spectrum, ethernet service
- `path_geometry`: PostGIS MultiLineString (geographic route)
- `path_length_km`: Calculated path length
- `circuits`: Many-to-Many through SegmentCircuitMapping

**Type-Specific Data Models (OneToOne relationships):**
- `DarkFiberSegmentData`: Fiber mode, attenuation, connectors, etc.
- `OpticalSpectrumSegmentData`: Wavelength, dispersion, modulation, etc.
- `EthernetServiceSegmentData`: Port speed, VLAN, encapsulation, MTU, etc.

**Geographic Features:**
- Stores actual geographic paths (not just A-to-B lines)
- Supports KML, KMZ, and GeoJSON upload
- Automatic path length calculation
- Fallback to straight lines if no path data

### 2. ServicePath (`models/service_path.py`)

Represents a logical service path composed of multiple segments.

**Key Fields:**
- `name`: Service path identifier
- `status`: Active, Planned, Offline
- `kind`: Experimental, Core, Customer (customizable)
- `segments`: Many-to-Many through ServicePathSegmentMapping
- `comments`: Additional notes

**Purpose:**
- Group segments into logical end-to-end paths
- Visualize complete service topology
- Track service-level status and classification

### 3. ContractInfo (`models/contract_info.py`)

Tracks legal agreements and financial information for segments.

**Version Chain:**
- Contracts support version history using linked list pattern
- `previous_version` → points to older version
- `superseded_by` → points to newer version
- Contract types: New, Amendment, Renewal

**Key Fields:**
- `contract_number`: Provider's reference
- `contract_type`: New, Amendment, Renewal (auto-set)
- `effective_date`: When contract version takes effect
- `charge_currency`: Currency (fixed, cannot change in amendments)
- `non_recurring_charge`: One-time setup fees (cumulative)
- `recurring_charge`: Regular periodic charge
- `recurring_period`: Monthly, Quarterly, Annual
- `commitment_months`: Contract commitment period
- `change_reason`: Required for amendments/renewals
- `segments`: Many-to-Many through ContractSegmentMapping

**Financial Calculations:**
- Commitment end date based on effective date + commitment months
- Visual status badges (red >30 days, orange <30 days, green expired)
- Total costs calculated automatically

### 4. Mapping Models

**ServicePathSegmentMapping:**
- Links segments to service paths
- Tracks position/order in the path

**SegmentCircuitMapping:**
- Links segments to NetBox circuits
- Many-to-many relationship

**ContractSegmentMapping:**
- Links contract versions to segments
- Supports multiple segments per contract

### 5. Type-Specific Data Models

Three specialized models store technical parameters for different segment types using OneToOne relationships with Segment:

**DarkFiberSegmentData** (`models/dark_fiber_data.py`):
- `fiber_mode`: Single-mode or Multimode
- `single_mode_subtype`: G.652D, G.655, G.657A1, etc.
- `multimode_subtype`: OM1, OM2, OM3, OM4, OM5
- `jacket_type`: Indoor, Outdoor, Armored, etc.
- `fiber_attenuation_max`: Maximum attenuation (dB/km)
- `total_loss`: End-to-end optical loss (dB)
- `total_length`: Physical cable length (km)
- `number_of_fibers`: Fiber strand count
- `connector_type_side_a`, `connector_type_side_b`: LC/APC, SC/UPC, etc.

**OpticalSpectrumSegmentData** (`models/optical_spectrum_data.py`):
- `wavelength`: Center wavelength (nm) - C-band/L-band
- `spectral_slot_width`: Optical channel bandwidth (GHz)
- `itu_grid_position`: ITU-T G.694.1 channel number
- `chromatic_dispersion`: Dispersion at wavelength (ps/nm)
- `pmd_tolerance`: Polarization mode dispersion (ps)
- `modulation_format`: NRZ, PAM4, QPSK, 16QAM, etc.

**EthernetServiceSegmentData** (`models/ethernet_service_data.py`):
- `port_speed`: Bandwidth (Mbps)
- `vlan_id`: Primary VLAN tag (1-4094)
- `vlan_tags`: Additional VLANs for QinQ
- `encapsulation_type`: 802.1Q, 802.1ad, MPLS, MEF E-Line, etc.
- `interface_type`: RJ45, SFP, SFP+, QSFP+, QSFP28, etc.
- `mtu_size`: Maximum transmission unit (bytes)

**Architecture Benefits:**
- **Database constraints**: Field validation at DB level (NOT NULL, CHECK, ranges)
- **Indexed fields**: Fast queries on individual parameters
- **Type safety**: Django ORM prevents invalid data types
- **Maintainability**: Add fields via migrations, not JSON schema updates
- **API clarity**: Structured objects, not JSON blobs

**API Access:**
```python
# Computed field on Segment API
segment['type_specific_technicals']  # Returns appropriate model data
```

## Key Features

### 1. Geographic Visualization

**Map Features:**
- Interactive Leaflet maps with multiple tile layers
- OpenStreetMap, satellite, topographic views
- Status-based, provider-based, or segment-type color coding
- Click segments for detailed information
- Export GeoJSON data via API

**Path Data Processing:**
- Upload KML, KMZ, or GeoJSON files
- Automatic 3D to 2D conversion
- Multi-segment path support
- Length calculation using projected coordinates
- Path validation with error reporting

**Implementation:** `utils/utils_gis.py`

### 2. Topology Visualization

**Features:**
- Interactive network graphs using Cytoscape.js
- Automatic topology generation for segments and service paths
- Multi-topology support (toggle between different views)
- Node types: locations, circuits, circuit terminations
- Hover tooltips with detailed information
- NetBox Blue themed styling

**Implementation:** `utils/utils_topology.py`

### 3. Contract Management

**Versioning System:**
- Linear version chain (linked list)
- Types: New contract, Amendment, Renewal
- Immutable currency across versions
- Change tracking with reason field

**Financial Tracking:**
- Multi-currency support (configurable)
- Recurring and non-recurring charges
- Commitment period tracking
- Automatic end date calculation
- Visual status indicators

### 4. API Support

**REST API:**
- Full CRUD operations for all models
- Geographic data in GeoJSON format
- Financial data with permission checks
- Endpoints: `/api/plugins/cesnet-service-path-plugin/`

**GraphQL API:**
- Query segments, service paths, contracts
- Geographic fields (geometry, bounds, coordinates)
- Advanced filtering
- Nested relationships
- Access: `/graphql/`

## Configuration

### Plugin Configuration (`configuration/plugins.py`)

```python
PLUGINS = [
    'cesnet_service_path_plugin',
]

PLUGINS_CONFIG = {
    "cesnet_service_path_plugin": {
        # Currency configuration
        'currencies': [
            ('CZK', 'Czech Koruna'),
            ('EUR', 'Euro'),
            ('USD', 'US Dollar'),
        ],
        'default_currency': 'EUR',
    },
}
```

### Custom Choices

Extend status, kind, or other choices in `configuration.py`:

```python
FIELD_CHOICES = {
    'cesnet_service_path_plugin.choices.status': (
        ('custom_status', 'Custom Status', 'blue'),
    ),
    'cesnet_service_path_plugin.choices.kind': (
        ('custom_kind', 'Custom Kind', 'purple'),
    )
}
```

## Development Guidelines

### Database Engine Requirement

Must configure NetBox to use PostGIS engine:

```python
DATABASE_ENGINE = "django.contrib.gis.db.backends.postgis"
```

### System Dependencies

Required for geographic features:
- PostgreSQL with PostGIS extension
- GDAL runtime libraries (`gdal-bin`, `libgdal34`)
- GEOS libraries (`libgeos-c1t64`)
- PROJ libraries (`libproj25`)

### Testing Geographic Features

```python
from cesnet_service_path_plugin.utils import check_gis_environment
check_gis_environment()
```

### Code Style

- Uses Black and autopep8 for formatting
- Ruff for linting (`.ruff.toml`)
- Django best practices
- NetBox plugin patterns

## Important Patterns

### 1. Model Registration

Models inherit from `NetBoxModel` which provides:
- Automatic primary key
- Created/last_updated timestamps
- Custom fields support
- Tags support
- Change logging

### 2. Geographic Data Handling

**Upload Path Data:**
1. User uploads KML/KMZ/GeoJSON file via form
2. `utils_gis.py` processes file (validation, conversion)
3. Stored as PostGIS MultiLineString
4. Length calculated and stored

**Display Path Data:**
1. API endpoint returns GeoJSON
2. Leaflet map renders paths
3. Click handlers show segment details

### 3. Permission-Based Visibility

Financial information respects Django permissions:
- View: `cesnet_service_path_plugin.view_contractinfo`
- Add: `cesnet_service_path_plugin.add_contractinfo`
- Change: `cesnet_service_path_plugin.change_contractinfo`
- Delete: `cesnet_service_path_plugin.delete_contractinfo`

API includes financial data only if user has view permission.

### 4. Template Extensions

Plugin extends NetBox core pages:
- Circuit pages: Show related segments
- Provider pages: List provider segments
- Site/Location pages: Display connected segments
- Uses NetBox template extension points

## Common Tasks

### Adding a New Model

1. Create model in `models/`
2. Add to `models/__init__.py`
3. Create migration: `python manage.py makemigrations cesnet_service_path_plugin`
4. Create serializer in `api/serializers/`
5. Create viewset in `api/views/`
6. Add URL route in `api/urls.py`
7. Create form in `forms/`
8. Create table in `tables/`
9. Create filterset in `filtersets/`
10. Create views in `views/`
11. Add URL routes in `urls.py`
12. Add to navigation in `navigation.py`
13. Update GraphQL schema if needed

### Adding a Geographic Feature

1. Use GeoDjango fields (`gis_models.MultiLineStringField`)
2. Process with GeoPandas/Fiona in `utils_gis.py`
3. Serialize as GeoJSON in API
4. Render with Leaflet in templates

### Working with Contracts

**Creating New Contract:**
- Use `ContractTypeChoices.NEW`
- No previous_version

**Creating Amendment:**
- Clone existing contract data
- Set `previous_version` to current active
- Set `superseded_by` on old contract
- Use `ContractTypeChoices.AMENDMENT`
- Currency must match original

**Creating Renewal:**
- Similar to amendment
- Use `ContractTypeChoices.RENEWAL`
- Typically extends commitment period

## Testing

Run tests:
```bash
pytest
```

Key test files:
- `tests/test_komora_service_path_plugin.py`: Main integration tests
- `tests/test_integration_segment_type_specific_data.py`: Type-specific data tests
- `tests/test_integration_segment_financial_info_api.py`: Financial API tests

## Troubleshooting

### PostGIS Not Available

**Symptoms:** GeoDjango errors, cannot create geographic fields

**Solution:**
1. Enable PostGIS: `CREATE EXTENSION IF NOT EXISTS postgis;`
2. Configure engine: `DATABASE_ENGINE = "django.contrib.gis.db.backends.postgis"`
3. Install system libraries: `gdal-bin`, `libgdal34`, `libgeos-c1t64`, `libproj25`

### Path Upload Fails

**Symptoms:** File upload rejected, validation errors

**Solution:**
- Check file format (KML, KMZ, GeoJSON)
- Verify file contains LineString/MultiLineString geometries
- Check for 3D coordinates (will auto-convert to 2D)
- Review error messages in UI

### Financial Data Not Visible

**Symptoms:** Contract info not showing in UI or API

**Solution:**
- Check user has `view_contractinfo` permission
- Verify contract exists and is linked to segment
- Check API response for null financial_info field

### Map Not Loading

**Symptoms:** Blank map, JavaScript errors

**Solution:**
- Check browser console for tile layer errors
- Verify internet connectivity (tile layers from CDN)
- Check segment has valid path_geometry data

## URLs and Endpoints

### Web UI
- Segments List: `/plugins/cesnet-service-path-plugin/segments/`
- Segments Map: `/plugins/cesnet-service-path-plugin/segments-map/`
- Service Paths: `/plugins/cesnet-service-path-plugin/service-paths/`
- Contracts: `/plugins/cesnet-service-path-plugin/contracts/`

### API
- Base: `/api/plugins/cesnet-service-path-plugin/`
- Segments: `/api/plugins/cesnet-service-path-plugin/segments/`
- Service Paths: `/api/plugins/cesnet-service-path-plugin/service-paths/`
- Contracts: `/api/plugins/cesnet-service-path-plugin/contracts/`
- GeoJSON Export: `/api/plugins/cesnet-service-path-plugin/segments/{id}/geojson-api/`

### GraphQL
- Endpoint: `/graphql/`
- Queries: `segment_list`, `service_path_list`, `contract_info_list`

## Resources

- **Repository**: https://github.com/CESNET/cesnet_service_path_plugin
- **Issues**: https://github.com/CESNET/cesnet_service_path_plugin/issues
- **NetBox Docs**: https://docs.netbox.dev/
- **NetBox Plugin Dev**: https://github.com/netbox-community/netbox-plugin-tutorial
- **GeoDjango**: https://docs.djangoproject.com/en/stable/ref/contrib/gis/
- **PostGIS**: https://postgis.net/documentation/
- **Leaflet**: https://leafletjs.com/reference.html
- **Cytoscape.js**: https://js.cytoscape.org/

## Recent Changes (v5.3.0)

- Implemented versioned contract system with M:N segment relationships
- Contract versioning using linear chain (linked list) pattern
- Support for contract amendments and renewals
- Immutable attributes and cumulative charges across versions
- Removed direct provider relationship from contract model
- Enhanced contract filtering and display

## Authors

- Jan Krupa (jan.krupa@cesnet.cz)
- Jiri Vrany (jiri.vrany@cesnet.cz)

---

**Last Updated**: Based on version 5.3.0 analysis
**For AI Assistants**: This document provides context for understanding and working with the cesnet_service_path_plugin codebase. Use it to answer questions, make changes, or debug issues.
