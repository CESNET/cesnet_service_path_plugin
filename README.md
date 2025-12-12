# CESNET ServicePath Plugin for NetBox

A NetBox plugin for managing service paths and segments in network infrastructure with advanced geographic path visualization, interactive topology visualization, and financial tracking.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/cesnet-service-path-plugin.svg)](https://pypi.org/project/cesnet-service-path-plugin/)
[![Python versions](https://img.shields.io/pypi/pyversions/cesnet-service-path-plugin.svg)](https://pypi.org/project/cesnet-service-path-plugin/)
[![NetBox compatibility](https://img.shields.io/badge/NetBox-4.4-blue.svg)](https://github.com/netbox-community/netbox)

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
  - [Currency Configuration](#currency-configuration)
- [Geographic Path Data](#geographic-path-data)
- [Topology Visualization](#topology-visualization)
- [Contract Information Management](#contract-information-management)
- [API Usage](#api-usage)
- [Development](#development)
- [Navigation and UI](#navigation-and-ui)
- [Troubleshooting](#troubleshooting)
- [Credits](#credits)
- [License](#license)

## Overview

The CESNET ServicePath Plugin extends NetBox's capabilities by providing comprehensive network service path management with:
- Interactive geographic path visualization using Leaflet maps (introduced in version 5.0.x)
- **Interactive topology visualization using Cytoscape.js** (new in 5.2.1)
- Support for KML, KMZ, and GeoJSON path data
- **Contract Information Management System with versioning** (new in 5.4.0, replaces financial info from 5.2.x)
- **Versioned contract tracking for segments** with amendment and renewal support
- **Commitment end date tracking with visual indicators**
- Service path and segment relationship management
- Advanced filtering and search capabilities
- REST API and GraphQL support

## Compatibility Matrix

| NetBox Version | Plugin Version |
|----------------|----------------|
|     4.4        |      5.5.x     |
|     4.4        |      5.4.x     |
|     4.4        |      5.3.x     |
|     4.4        |      5.2.x     |
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
- **Interactive topology visualization** showing complete service path topology

### Segment Management
- Track network segments between locations
- Monitor installation and termination dates
- Manage provider relationships and contracts
- Link circuits to segments
- **One-click Circuit generation** from Segment data with auto-filled forms
- Automatic status tracking based on dates
- **Geographic path visualization with actual route data**
- **Interactive topology visualization** showing segment connections and circuit terminations
- **Segment types with relational data models** (dark fiber, optical spectrum, ethernet service) - type-specific technical parameters stored in dedicated models (improved in 5.5.0)
- **Contract information tracking with versioning support** (new in 5.4.0)
- **Many-to-many contract relationships** - segments can have multiple contracts
- **Commitment end date tracking** with color-coded status indicators
- Define ownership type (new in 5.3.0)

### Topology Visualization (New in 5.2.1)
- **Interactive network topology graphs** powered by Cytoscape.js
- **Automatic topology generation** for segments and service paths
- **Visual representation** of segment connections, circuits, and terminations
- **Multi-topology support** - view multiple service paths when a segment belongs to multiple paths
- **Clean NetBox Blue styling** with gradients and modern design
- **Interactive hover tooltips** displaying detailed node information
- **Integrated views**:
  - Segment detail pages show segment topology or service path topology
  - Service path detail pages show complete path topology
  - Circuit detail pages show topologies for related segments/service paths
- **Toggle between topologies** when multiple topologies are available

### Contract Information Management (New in 5.4.0)
- **Versioned contract system** with linear version chains (similar to Git)
  - Create contract amendments and renewals using NetBox clone functionality
  - Automatic version numbering (v1, v2, v3...)
  - Version history timeline showing contract evolution
  - Active/superseded contract status tracking
- **Many-to-many segment relationships** - one contract can cover multiple segments
- **Contract metadata tracking**:
  - Contract number and type (new/amendment/renewal)
  - Contract start and end dates
  - Effective dates for amendments
  - Change reason documentation
- **Enhanced financial tracking**:
  - **Recurring charges** with customizable periods (monthly, quarterly, annually, etc.)
  - Number of recurring charge periods
  - **Non-recurring charges** for setup/installation fees
  - **Multi-currency support** with immutable currency (set at contract creation)
- **Commitment end date** automatic calculation and tracking
- **Visual status indicators** with color coding:
  - 🔴 Red: More than 30 days remaining
  - 🟠 Orange: Within 30 days of expiration
  - 🟢 Green: Contract/commitment period ended
  - ⚫ Gray: Date not set
- **Interactive tooltips** showing days remaining and contract status
- **Automatic cost calculations**:
  - Total recurring cost (recurring charge × number of periods)
  - Total contract value (recurring + non-recurring charges)
- **Permission-based access control** - contract data visible only to authorized users
- **Full REST API and GraphQL support** with versioning fields
- **Advanced filtering**: by active status, contract type, currency, dates

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
- **GraphQL API** with full geometry field support and complex filtering
- **Quick action buttons** in navigation menu (Add/Import)
- **Modernized views** using NetBox 4.x @register_model_view pattern

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
- **Contract relationships** (many-to-many through ContractSegmentMapping)
- **Type-specific technical data** stored in relational models (OneToOne relationships):
  - `DarkFiberSegmentData`: Fiber specifications, attenuation, connectors
  - `OpticalSpectrumSegmentData`: Wavelength, dispersion, modulation
  - `EthernetServiceSegmentData`: Port speed, VLAN, encapsulation, MTU
- Automated status monitoring

### Contract Info (New in 5.4.0)
- **Version chain management** using linked list pattern (previous_version/superseded_by)
- **Contract metadata**: number, type (new/amendment/renewal), effective dates
- **Recurring charges** with configurable periods (monthly, quarterly, annually, etc.)
- **Non-recurring charges** for setup/installation
- **Number of recurring charge periods** for contract commitment
- **Multi-currency support** with immutable currency (set at contract creation)
- **Start and end dates** for contract validity period
- **Commitment end date** automatic calculation
- **Many-to-many segment relationships** via ContractSegmentMapping
- **Automatic version numbering** and history tracking
- **Permission-based visibility**

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
2. **System libraries**: GDAL, GEOS, and PROJ runtime binaries
3. **NetBox 4.4 or higher**

#### Installing System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql-15-postgis-3 gdal-bin libgdal34 libgeos-c1t64 libproj25
```

**Note**: Package names may vary by Ubuntu/Debian version. Use `apt-cache search libgdal` to find the correct version for your system.

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

# copy plugin requirements
COPY ./plugin_requirements.txt /opt/netbox/

# Install git and minimal PostGIS runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    gdal-bin \
    libgdal34 \
    libgeos-c1t64 \
    libproj25 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install PostGIS and geospatial Python dependencies
RUN /usr/local/bin/uv pip install \
    psycopg2-binary \
    -r /opt/netbox/plugin_requirements.txt
```

**Note**: Library package names (like `libgdal34`) may vary depending on the base image's Ubuntu/Debian version. Check available packages if you encounter errors.

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

### Step 4: Enable and configure the Plugin

Add the plugin to your NetBox `configuration/plugins.py`:

```python
PLUGINS = [
    'cesnet_service_path_plugin',
]

PLUGINS_CONFIG = {
    "cesnet_service_path_plugin": {
        'currencies': [
            ('CZK', 'Czech Koruna'),
            ('EUR', 'Euro'),
            ('USD', 'US Dollar'),
        ],
        'default_currency': 'EUR',
    },
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

### Currency Configuration

Configure available currencies and default currency for financial information:

```python
PLUGINS_CONFIG = {
    "cesnet_service_path_plugin": {
        'currencies': [
            ('CZK', 'Czech Koruna'),
            ('EUR', 'Euro'),
            ('USD', 'US Dollar'),
            ('GBP', 'British Pound'),
            ('JPY', 'Japanese Yen'),
        ],
        'default_currency': 'EUR',
    },
}
```

*Note: This example shows EUR as the configured default currency. If not configured, the application will use CZK as the fallback default.*

**Configuration options:**
- `currencies`: List of (code, name) tuples for available currencies
- `default_currency`: Default currency code to use when creating new financial records

**Default values if not configured:**
- Currencies: CZK, EUR, USD
- Default currency: CZK

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

## Topology Visualization

### Overview (New in 5.2.1)

The plugin includes interactive network topology visualization using Cytoscape.js, providing a graph-based view of your network segments, circuits, and their interconnections.

### Features

- **Automatic topology generation**: Topologies are automatically generated for segments and service paths
- **Interactive graph visualization**: Pan, zoom, and hover over nodes to see details
- **Multi-topology support**: When a segment belongs to multiple service paths, you can toggle between different topology views
- **Clean visual design**: NetBox Blue themed styling with gradients and modern aesthetics
- **Node information**: Hover tooltips display detailed information about locations, circuits, and segments

### Where Topologies Appear

Topologies are automatically displayed in:

1. **Segment Detail Pages**:
   - Shows segment topology with connected circuits and terminations
   - If segment belongs to service paths, shows service path topology instead
   - Multiple topology tabs if segment is part of multiple service paths

2. **Service Path Detail Pages**:
   - Shows complete service path topology
   - Visualizes all segments in the path and their connections

3. **Circuit Detail Pages**:
   - Shows topology for segments associated with the circuit
   - Displays service path topology if the segment belongs to a service path

### Topology Components

Topologies visualize:
- **Location nodes**: Sites and locations where segments terminate
- **Circuit nodes**: Circuits connected to segments
- **Circuit termination nodes**: A-side and B-side terminations
- **Edges**: Connections between nodes showing network relationships

### Technical Details

- Uses Cytoscape.js v3.28.1 for graph rendering
- Client-side rendering for performance
- Responsive design adapts to different screen sizes
- Automatic layout algorithms for optimal node placement

## Contract Information Management

### Overview

Version 5.4.0 introduces a comprehensive Contract Information Management system that replaces the previous financial information model. The new system supports:
- **Versioned contracts** with amendment and renewal tracking
- **Many-to-many relationships** between contracts and segments
- **Enhanced financial tracking** with flexible recurring charge periods
- **Contract lifecycle management** with version history

### Creating Contracts

Contracts can be created and managed through the Contract Info menu:

1. Navigate to **Service Paths → Contract Info**
2. Click "Add" to create a new contract
3. Fill in the contract details:
   - **Contract Number**: Provider's contract reference
   - **Segments**: Select one or more segments covered by this contract
   - **Recurring Charge**: Regular fee amount (optional for amendments)
   - **Recurring Charge Period**: Frequency (monthly, quarterly, annually, etc.)
   - **Number of Periods**: How many charge periods in the contract
   - **Currency**: Select currency (cannot be changed later)
   - **Non-recurring Charge**: One-time setup/installation fees
   - **Start/End Dates**: Contract validity period
   - **Notes**: Additional context or details

### Creating Contract Amendments

To create an amendment to an existing contract:

1. Navigate to the contract detail page
2. Use the **Clone** button in NetBox
3. The system will:
   - Create a new version linked to the original
   - Set the contract type to "Amendment"
   - Preserve the currency (immutable)
   - Allow you to modify all other fields
4. Fill in the **Change Reason** to document what changed
5. Save the amendment

The original contract will be marked as superseded, and the new version becomes active.

### Viewing Contract Information

Contract detail pages show:
- **Version information**: Version number, type (new/amendment/renewal)
- **Version history timeline**: All versions of the contract with navigation
- **Segment relationships**: All segments covered by this contract
- **Financial summary**: All charges and automatic calculations
- **Date visualization**: Color-coded badges for contract and commitment end dates

Segments detail pages show:
- All contracts associated with the segment
- Contract status and version information
- Contract end dates with visual indicators
- Quick links to contract details

### Commitment End Date Tracking

The plugin automatically calculates and tracks commitment end dates:

- **Automatic calculation**: Based on contract start date + number of recurring periods
- **Visual status indicators** with color coding:
  - 🔴 **Red badge**: More than 30 days remaining
  - 🟠 **Orange badge**: Within 30 days of expiration (action required soon)
  - 🟢 **Green badge**: Contract/commitment period has ended
  - ⚫ **Gray badge**: Date not set
- **Interactive tooltips**: Hover over badges to see:
  - Exact end dates
  - Days remaining until expiration
  - Contract status

### Contract Versioning

The versioning system works like a Git commit chain:

- **Linear history**: Each contract version links to its predecessor
- **Active version**: The latest version in the chain is the active contract
- **Version navigation**: View any version in the history
- **Automatic numbering**: Versions are automatically numbered (v1, v2, v3...)
- **Superseding**: Older versions are marked as superseded by newer ones

### Permission Requirements

Contract information has separate permissions:
- **View**: `cesnet_service_path_plugin.view_contractinfo`
- **Add**: `cesnet_service_path_plugin.add_contractinfo`
- **Change**: `cesnet_service_path_plugin.change_contractinfo`
- **Delete**: `cesnet_service_path_plugin.delete_contractinfo`

Users without view permission will not see contract information in the UI or API responses.

### Financial Calculations

The plugin automatically calculates:
- **Total Recurring Cost**: Recurring charge × Number of periods
- **Total Contract Value**: Total recurring cost + Non-recurring charge
- **Commitment End Date**: Start date + (Number of periods × Period frequency)

These calculations are available in both the UI and API responses.

### Migration from Financial Info

If upgrading from version 5.2.x or 5.3.x:
- Migration 0033 automatically converts all SegmentFinancialInfo to ContractInfo
- All data is preserved: charges, currencies, notes, tags, timestamps
- Monthly charges become recurring charges (monthly period)
- Commitment period months become number of recurring charges
- Segment dates are used for contract start/end dates
- One-to-one relationships become many-to-many via ContractSegmentMapping

## API Usage

The plugin provides comprehensive REST API and GraphQL support:

### REST API Endpoints

- `/api/plugins/cesnet-service-path-plugin/segments/` - Segment management
- `/api/plugins/cesnet-service-path-plugin/service-paths/` - Service path management
- `/api/plugins/cesnet-service-path-plugin/segments/{id}/geojson-api/` - Geographic data
- `/api/plugins/cesnet-service-path-plugin/contract-info/` - Contract information management (new in 5.4.0)

#### Example of segment with path file PATCH and POST
See [detailed example in docs](./docs/API_path.md).

#### Type-Specific Technical Data in API (Architecture improved in 5.5.0)

Segment API responses include type-specific technical parameters via the `type_specific_data` computed field:

```json
{
  "id": 1,
  "name": "Example Dark Fiber Segment",
  "segment_type": "dark_fiber",
  "type_specific_data": {
    "id": 1,
    "segment": 1,
    "fiber_mode": "single_mode",
    "single_mode_subtype": "G.652D",
    "fiber_attenuation_max": "0.3500",
    "total_loss": "2.50",
    "connector_type_side_a": "LC/APC",
    "connector_type_side_b": "LC/APC"
  }
}
```

**What changed in 5.5.0**: `type_specific_data` is now a computed field that returns structured data from relational models (DarkFiberSegmentData, OpticalSpectrumSegmentData, or EthernetServiceSegmentData) instead of a JSON blob. The field name remains the same for API compatibility, but the underlying architecture is now fully relational with proper database constraints and validation.

**Type-Specific Data Endpoints**:
- `/api/plugins/cesnet-service-path-plugin/dark-fiber-segment-data/` - Dark fiber specifications
- `/api/plugins/cesnet-service-path-plugin/optical-spectrum-segment-data/` - Optical spectrum parameters
- `/api/plugins/cesnet-service-path-plugin/ethernet-service-segment-data/` - Ethernet service details

#### Contract Information in API (New in 5.4.0)

Contract API responses include versioning and financial fields:
```json
{
  "id": 1,
  "contract_number": "CTR-2025-001",
  "contract_type": "amendment",
  "version": 2,
  "is_active": true,
  "previous_version": 1,
  "superseded_by": null,
  "segments": [1, 2, 3],
  "recurring_charge": "1000.00",
  "recurring_charge_period": "monthly",
  "number_of_recurring_charges": 36,
  "charge_currency": "EUR",
  "non_recurring_charge": "5000.00",
  "start_date": "2025-01-01",
  "end_date": "2028-01-01",
  "commitment_end_date": "2028-01-01",
  "total_recurring_cost": "36000.00",
  "total_contract_value": "41000.00",
  "notes": "Price adjustment"
}
```

**Versioning Fields**:
- `version`: Calculated version number
- `is_active`: Boolean indicating if this is the current version
- `previous_version`: ID of the previous contract version (null for v1)
- `superseded_by`: ID of the newer version that supersedes this one (null if active)

**Note**: Contract information will only be visible to users with view permissions.

### Geographic API Features

- **Lightweight list serializers** for performance
- **Detailed geometry serializers** for map views
- **GeoJSON export** endpoints
- **Path bounds and coordinates** in API responses

### GraphQL API

Access the GraphQL API at `/graphql/` with full support for:

#### Query Examples

```graphql
# Query segments with path data and type-specific information
query {
  segment_list(filters: {hasPathData: true}) {
    id
    name
    networkLabel
    segmentType
    typeSpecificData
    pathLengthKm
    pathGeometryGeojson
    provider {
      name
    }
    siteA {
      name
    }
    siteB {
      name
    }
  }
}

# Query service paths with segments
query {
  service_path_list(filters: {status: "active"}) {
    id
    name
    kind
    segments {
      name
      pathLengthKm
    }
  }
}

# Query contract information with versioning (new in 5.4.0)
query {
  contract_info_list(filters: {isActive: true}) {
    id
    contractNumber
    contractType
    version
    isActive
    recurringCharge
    recurringChargePeriod
    numberOfRecurringCharges
    chargeCurrency
    commitmentEndDate
    totalRecurringCost
    totalContractValue
    segments {
      id
      name
    }
  }
}
```

#### GraphQL Features

- **Full model access**: Query Segments, ServicePaths, ContractInfo, and all mapping types
- **Geographic fields**: GeoJSON geometry, path coordinates, bounding boxes
- **Advanced filtering**: Status, dates, providers, sites, path data availability, contract versioning
- **Nested relationships**: Query related circuits, providers, locations, contracts in single request
- **Type-specific technical data**: Query dark fiber, optical spectrum, or ethernet service parameters via relational models
- **Contract versioning**: Query contract versions, version chains, and active contracts (new in 5.4.0)
- **Financial calculations**: Query commitment end dates and contract value calculations

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
# Ubuntu/Debian - only runtime libraries needed
sudo apt-get install gdal-bin libgdal34 libgeos-c1t64 libproj25

# macOS
brew install gdal geos proj

# Install Python packages
pip install geopandas fiona shapely python-dateutil
```

**Note**: For development, you typically only need the runtime libraries. The Python packages (geopandas, fiona, shapely) use precompiled wheels that already include the necessary bindings. Development headers (`-dev` packages) are only needed if you're compiling these libraries from source.

### Testing Geographic Features

Use the built-in diagnostic function:
```python
from cesnet_service_path_plugin.utils import check_gis_environment
check_gis_environment()
```

## Navigation and UI

The plugin adds a **Service Paths** menu with:
- **Segments** - List and manage network segments with quick Add/Import buttons
- **Segments Map** - Interactive map view of all segments
- **Service Paths** - Manage service path definitions with quick Add/Import buttons
- **Contract Info** - Manage contracts with versioning support (new in 5.4.0)
- **Mappings** - Relationship management tools with quick Add/Import buttons

### UI Features

- **Generate Circuit button**: One-click Circuit creation from Segment with auto-filled:
  - Provider and CID (suggested as CIR-{segment_name})
  - Network label and route description
  - Installation and termination dates
  - Comments with Segment reference
  - Return URL to navigate back after creation
- **Quick action buttons**: Add and Import shortcuts in navigation menu
- **Bulk operations**: Edit, delete, and import multiple records at once
- **Advanced search**: Full-text search across names, comments, network labels, and path notes
- **Topology visualization cards**: Interactive network graphs on detail pages (new in 5.2.1)
- **Contract version timeline**: Visual representation of contract history and amendments (new in 5.4.0)
- **Commitment status badges**: Color-coded indicators for contract commitments (new in 5.4.0)

### Template Extensions

Automatic integration with existing NetBox models:
- **Circuit pages**: Show related segments with topology visualization (enhanced in 5.2.1)
- **Provider pages**: List provider segments
- **Site/Location pages**: Display connected segments
- **Tenant pages**: Show associated provider information

### Contract Information Display

Contract information appears on segment detail pages when:
- User has view permission
- Segment has contract relationships
- Displayed in a dedicated panel showing all associated contracts
- Shows contract version, status, and commitment end dates with color-coded badges (new in 5.4.0)

## Troubleshooting

### Common Issues

1. **PostGIS not enabled**: Ensure PostGIS extension is installed in your database
2. **GDAL library missing**: Install system GDAL runtime libraries (`gdal-bin`, `libgdal34`) before Python packages
3. **Path upload fails**: Check file format and ensure it contains LineString geometries
4. **Map not loading**: Verify JavaScript console for tile layer errors
5. **Library version mismatch**: If you encounter errors about missing libraries, check that library package names match your OS version (e.g., `libgdal34` vs `libgdal32`)
6. **Contract info not visible**: Check user permissions for `view_contractinfo`
7. **Currency not appearing**: Verify plugin configuration in `configuration/plugins.py`
8. **Topology not rendering**: Check browser console for Cytoscape.js CDN errors
9. **Commitment end date not showing**: Ensure contract has start date and number of recurring charges defined
10. **Migration from 5.2.x/5.3.x**: If upgrading, ensure migration 0033 runs successfully to convert SegmentFinancialInfo to ContractInfo

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
- Topology visualization powered by [Cytoscape.js](https://js.cytoscape.org/)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.