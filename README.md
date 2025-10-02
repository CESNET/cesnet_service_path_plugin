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
[![PyPI version](https://img.shields.io/pypi/v/cesnet-service-path-plugin.svg)](https://pypi.org/project/cesnet-service-path-plugin/)
[![Python versions](https://img.shields.io/pypi/pyversions/cesnet-service-path-plugin.svg)](https://pypi.org/project/cesnet-service-path-plugin/)
[![NetBox compatibility](https://img.shields.io/badge/NetBox-4.2%20|%204.3%20|%204.4-blue.svg)](https://github.com/netbox-community/netbox)

## 📑 Table of Contents

- [Overview](#overview)
- [Compatibility Matrix](#compatibility-matrix)
- [Features](#features)
- [Data Model](#data-model)
- [Installation and Configuration](#installation-and-configuration)
  - [Prerequisites](#prerequisites)
  - [Step-by-Step Installation](#step-1-enable-postgis-in-postgresql)
- [Additional Configuration](#additional-configuration)
  - [Custom Status Choices](#custom-status-choices)
  - [Custom Kind Choices](#custom-kind-choices)
- [Geographic Path Data](#geographic-path-data)
- [API Usage](#api-usage)
- [Development](#development)
- [Navigation and UI](#navigation-and-ui)
- [Troubleshooting](#troubleshooting)
- [Credits](#credits)
- [License](#license)

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

## Installation and Configuration

⚠️ **Important**: This plugin requires PostGIS and geographic libraries. Standard NetBox installations need additional setup steps.

### Prerequisites

Before installing the plugin, ensure you have:

1. **PostgreSQL with PostGIS extension** (version 3.0 or higher recommended)
2. **System libraries**: GDAL, GEOS, and PROJ
3. **NetBox 4.2 or higher**

#### Installing System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql-15-postgis-3 gdal-bin libgdal-dev libgeos-dev libproj-dev
```

**macOS:**
```bash
brew install postgresql postgis gdal geos proj
```

**Docker users**: The official `netboxcommunity/netbox` images do **NOT** include PostGIS and GDAL libraries by default. You will need to create a custom Docker image. See the Docker-specific instructions below.

### Step 1: Enable PostGIS in PostgreSQL

Connect to your NetBox database and enable the PostGIS extension:

```sql
-- Connect to your NetBox database
\c netbox

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Verify installation
SELECT PostGIS_version();
```

### Step 2: Configure NetBox Database Engine

**CRITICAL**: Update your NetBox `configuration.py` to use the PostGIS database engine:

```python
# Set the database engine to PostGIS
DATABASE_ENGINE = "django.contrib.gis.db.backends.postgis"

# PostgreSQL database configuration
DATABASE = {
    "ENGINE": DATABASE_ENGINE,  # Must use PostGIS engine
    "NAME": environ.get("DB_NAME", "netbox"),
    "USER": environ.get("DB_USER", ""),
    "PASSWORD": read_secret("db_password", environ.get("DB_PASSWORD", "")),
    "HOST": environ.get("DB_HOST", "localhost"),
    "PORT": environ.get("DB_PORT", ""),
    "OPTIONS": {"sslmode": environ.get("DB_SSLMODE", "prefer")},
    "CONN_MAX_AGE": int(environ.get("DB_CONN_MAX_AGE", "300")),
}
```

**Note**: This is just an example. If you're using NetBox Docker, this can be configured via environment variables in your `docker-compose.yml` or similar configuration files.

### Step 3: Install the Plugin

#### Standard Installation (pip)

```bash
pip install cesnet_service_path_plugin
```

#### Docker Installation

The official NetBox Docker images do not include the required geographic libraries. You need to create a custom Docker image.

**Option 1: Create a Custom Dockerfile**

Create a `Dockerfile` extending the official NetBox image:

```dockerfile
FROM netboxcommunity/netbox:v4.4

# Install PostGIS and geographic libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    postgis \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

# Copy plugin requirements
COPY plugin_requirements.txt /opt/netbox/
RUN /opt/netbox/venv/bin/pip install --no-cache-dir -r /opt/netbox/plugin_requirements.txt
```

Then create a `plugin_requirements.txt` file:
```
cesnet_service_path_plugin
```

Build your custom image:
```bash
docker build -t netbox-with-gis:latest .
```

Update your `docker-compose.yml` to use the custom image:
```yaml
services:
  netbox:
    image: netbox-with-gis:latest
    # ... rest of your configuration
```

**Option 2: Use docker-compose override**

Add a `docker-compose.override.yml` file:

```yaml
version: '3.8'
services:
  netbox:
    build:
      context: .
      dockerfile: Dockerfile.custom
```

For detailed Docker setup instructions, see [using netbox-docker with plugins](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

### Step 4: Enable the Plugin

Add the plugin to your NetBox `configuration.py`:

```python
PLUGINS = [
    'cesnet_service_path_plugin',
]

PLUGINS_CONFIG = {
    "cesnet_service_path_plugin": {},
}
```

### Step 5: Run Database Migrations

Apply the plugin's database migrations:

```bash
cd /opt/netbox/netbox
source venv/bin/activate
python manage.py migrate cesnet_service_path_plugin
```

**Docker users:**
```bash
docker exec -it netbox python /opt/netbox/netbox/manage.py migrate cesnet_service_path_plugin
```

### Step 6: Restart NetBox

Restart your NetBox services to load the plugin:

```bash
sudo systemctl restart netbox netbox-rq
```

**Docker users:**
```bash
docker-compose restart netbox netbox-worker
```

### Verification

To verify the installation:

1. Log into NetBox
2. Check that "Service Paths" appears in the navigation menu
3. Navigate to **Service Paths → Segments** to confirm the plugin is working

For geographic feature verification, you can use the diagnostic function in the Django shell:

```python
python manage.py nbshell

from cesnet_service_path_plugin.utils import check_gis_environment
check_gis_environment()
```

## Additional Configuration

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