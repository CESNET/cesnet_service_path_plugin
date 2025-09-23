# 🚨 WARNING – Work in Progress! 🚨

⚠️ This plugin is **under heavy development** and is **NOT production-ready**.  
- Database changes that are required for the current implementation are **missing**.  
- Documentation of the data model and functionality is **incomplete**.  
- Expect breaking changes, unfinished features, and possible instability.  

Use this code **at your own risk** and only for testing or development purposes.  

---
# CESNET ServicePath Plugin for NetBox

A NetBox plugin for managing service paths and segments in network infrastructure with advanced geographic path visualization.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## Overview

The CESNET ServicePath Plugin extends NetBox's capabilities by providing comprehensive network service path management with:
- Interactive geographic path visualization using Leaflet maps, introduced in version 5.0.x
- Support for KML, KMZ, and GeoJSON path data
- Service path and segment relationship management
- Advanced filtering and search capabilities
- REST API and GraphQL support

## Compatibility Matrix

| NetBox Version | Plugin Version |
|----------------|----------------|
|     4.4        |      5.1.x     |
|     4.3        |      5.0.x     |
|     4.2        |      4.0.x     |
|     3.7        |      0.1.0     |

## Features

### Service Path Management
- Define experimental, core, and customer service paths
- Track service path status and metadata
- Link multiple segments to create complete paths
- Visual relationship mapping

### Segment Management
- Track network segments between locations
- Monitor installation and termination dates
- Manage provider relationships and contracts
- Link circuits to segments
- Automatic status tracking based on dates
- **Geographic path visualization with actual route data**
- segment types (dark fiber, optical spectrum, ethernet) with type specific data

### Geographic Features
- **Interactive map visualization** with multiple tile layers (OpenStreetMap, satellite, topographic) and multiple color schema (status, provider, segment type)
- **Path data upload** supporting KML, KMZ, and GeoJSON formats
- **Automatic path length calculation** in kilometers
- **Multi-segment path support** with complex routing
- **Fallback visualization** showing straight lines when path data unavailable
- **Overlapping segment detection** and selection on maps
- **Path data export** as GeoJSON for external use
- An example of a geographic service path visualized using the plugin:
    ![Sample Service Path Map](./docs/sample_path.png)

### Integration Features
- **Template extensions** for Circuits, Providers, Sites, and Locations
- **Custom table columns** showing segment relationships
- **Advanced filtering** including path data availability
- **REST API endpoints** with geographic data support
- **GraphQL schema** with geometry field support

## Data Model

### Service Path
- Name and status tracking
- Service type classification (experimental/core/customer)
- Multiple segment support through mappings
- Comments and tagging support

### Segment
- Provider and location tracking
- Date-based lifecycle management with visual status indicators
- Circuit associations
- **Geographic path geometry** storage (MultiLineString)
- **Path metadata** including length, source format, and notes
- Automated status monitoring

### Geographic Path Data
- **MultiLineString geometry** storage in WGS84 (EPSG:4326)
- **Multiple path segments** support for complex routes
- **Automatic 2D conversion** from 3D path data
- **Length calculation** using projected coordinates
- **Source format tracking** (KML, KMZ, GeoJSON, manual)

## Quick Start

1. Install the plugin:
```bash
pip install cesnet_service_path_plugin
```

2. Enable the plugin in your NetBox configuration:
```python
PLUGINS = [
    'cesnet_service_path_plugin'
]

PLUGINS_CONFIG = {
    "cesnet_service_path_plugin": {},
}
```

3. Run NetBox migrations:
```bash
python manage.py migrate
```

4. **Configure GeoDjango** (required for geographic features):
   - Install GDAL, GEOS, and PROJ libraries
   - Configure PostGIS extension in PostgreSQL
   - See [GeoDjango installation guide](https://docs.djangoproject.com/en/stable/ref/contrib/gis/install/)

## Installation

### Prerequisites

For geographic features, you need:
- **PostGIS-enabled PostgreSQL database**
- **GDAL, GEOS, and PROJ libraries**
- **Python packages**: `geopandas`, `fiona`, `shapely`

### Using pip
```bash
pip install cesnet_service_path_plugin
```

### Using Docker
For NetBox Docker installations, add to your `plugin_requirements.txt`:
```bash
cesnet_service_path_plugin
```

**Docker users**: Ensure your NetBox Docker image includes PostGIS and GDAL libraries.

For detailed Docker setup instructions, see [using netbox-docker with plugins](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

## Configuration

### Database Configuration

Ensure your NetBox database has PostGIS enabled:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### Custom Status Choices

Extend or override default status choices in your `configuration.py`:

```python
FIELD_CHOICES = {
    'cesnet_service_path_plugin.choices.status': (
        ('custom_status', 'Custom Status', 'blue'),
        # ('status_value', 'Display Name', 'color'),
    )
}
```

Status choice format:
- Value: Internal database value
- Name: UI display name
- Color: Badge color (blue, green, red, orange, yellow, purple, gray)

Default statuses (Active, Planned, Offline) will be merged with custom choices.

### Custom Kind Choices

Extend or override default kind choices in your `configuration.py`:

```python
FIELD_CHOICES = {
    'cesnet_service_path_plugin.choices.kind': (
        ('custom_kind', 'Custom Kind Name', 'purple'),
        # ('kind_value', 'Display Name', 'color'),
    )
}
```

Kind choice format:
- Value: Internal database value
- Name: UI display name
- Color: Badge color (blue, green, red, orange, yellow, purple, gray)

Default kinds:
- experimental: Experimentální (cyan)
- core: Páteřní (blue)
- customer: Zákaznická (green)

Custom kinds will be merged with the default choices.

## Geographic Path Data

### Supported Formats

- **GeoJSON** (.geojson, .json): Native web format
- **KML** (.kml): Google Earth format
- **KMZ** (.kmz): Compressed KML with enhanced support for complex files

### Path Data Features

- **Automatic format detection** from file extension
- **Multi-layer KMZ support** with comprehensive extraction
- **3D to 2D conversion** for compatibility
- **Path validation** with detailed error reporting
- **Length calculation** using accurate projections

### Map Visualization

- **Multiple tile layers**: OpenStreetMap, satellite imagery, topographic maps
- **Interactive controls**: Pan, zoom, fit-to-bounds
- **Segment information panels** with detailed metadata
- **Overlapping segment handling** with selection popups
- **Status-based color coding** for visual identification

## API Usage

The plugin provides comprehensive REST API and GraphQL support:

### REST API Endpoints

- `/api/plugins/cesnet-service-path-plugin/segments/` - Segment management
- `/api/plugins/cesnet-service-path-plugin/service-paths/` - Service path management
- `/api/plugins/cesnet-service-path-plugin/segments/{id}/geojson-api/` - Geographic data

#### Example of segment with path file PATCH and POST 
See [detailed example in docs](./docs/API_path.md).

### Geographic API Features

- **Lightweight list serializers** for performance
- **Detailed geometry serializers** for map views
- **GeoJSON export** endpoints
- **Path bounds and coordinates** in API responses

### GraphQL Support

Full GraphQL schema with:
- **Geographic field support** for path geometry
- **Filtering capabilities** on all geographic fields
- **Nested relationship queries**

## Development

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/CESNET/cesnet_service_path_plugin.git
cd cesnet_service_path_plugin
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Install geographic dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install gdal-bin libgdal-dev libgeos-dev libproj-dev

# macOS
brew install gdal geos proj

# Install Python packages
pip install geopandas fiona shapely
```

### Testing Geographic Features

Use the built-in diagnostic function:
```python
from cesnet_service_path_plugin.utils import check_gis_environment
check_gis_environment()
```

## Navigation and UI

The plugin adds a **Service Paths** menu with:
- **Segments** - List and manage network segments
- **Segments Map** - Interactive map view of all segments
- **Service Paths** - Manage service path definitions
- **Mappings** - Relationship management tools

### Template Extensions

Automatic integration with existing NetBox models:
- **Circuit pages**: Show related segments
- **Provider pages**: List provider segments
- **Site/Location pages**: Display connected segments
- **Tenant pages**: Show associated provider information

## Troubleshooting

### Common Issues

1. **PostGIS not enabled**: Ensure PostGIS extension is installed in your database
2. **GDAL library missing**: Install system GDAL libraries before Python packages
3. **Path upload fails**: Check file format and ensure it contains LineString geometries
4. **Map not loading**: Verify JavaScript console for tile layer errors

### Debug Mode

Enable detailed logging for geographic operations:
```python
LOGGING = {
    'loggers': {
        'cesnet_service_path_plugin.utils': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## Credits

- Created using [Cookiecutter](https://github.com/audreyr/cookiecutter) and [`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin)
- Based on the [NetBox plugin tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)
- Geographic features powered by [GeoPandas](https://geopandas.org/), [Leaflet](https://leafletjs.com/), and [PostGIS](https://postgis.net/)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.