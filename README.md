# CESNET ServicePath Plugin for NetBox

A NetBox plugin for managing service paths and segments in network infrastructure.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## Overview

The CESNET ServicePath Plugin extends NetBox's capabilities by:
- Managing service paths across your network
- Creating and tracking service segments
- Visualizing service routing

## Compatibility Matrix

| NetBox Version | Plugin Version |
|----------------|----------------|
|     4.2        |      4.0.0     |
|     3.7        |      0.1.0     |

## Features

- Service Path Management
  - Define experimental, core, and customer service paths
  - Track service path status and metadata
  - Link multiple segments to create complete paths

- Segment Management
  - Track network segments between locations
  - Monitor installation and termination dates
  - Manage provider relationships and contracts
  - Link circuits to segments
  - Automatic status tracking based on dates

## Data Model

### Service Path
- Name and status tracking
- Service type classification (experimental/core/customer)
- Multiple segment support through mappings

### Segment
- Provider and location tracking
- Date-based lifecycle management
- Circuit associations
- Automated status monitoring

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

## Installation

### Using pip
```bash
pip install git+https://gitlab.cesnet.cz/701/netbox/cesnet_service_path_plugin.git
```

### Using Docker
For NetBox Docker installations, add to your `plugin_requirements.txt`:
```bash
cesnet_service_path_plugin
```

For detailed Docker setup instructions, see [using netbox-docker with plugins](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

## Configuration

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

## API Usage

The plugin provides a REST API for managing service paths and segments:

## Development

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://gitlab.cesnet.cz/701/netbox/cesnet_service_path_plugin.git
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

## Credits

- Created using [Cookiecutter](https://github.com/audreyr/cookiecutter) and [`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin)
- Based on the [NetBox plugin tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
