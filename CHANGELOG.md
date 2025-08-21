# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.0.2] - 2025-01-XX

### Added
- **Geographic Path Visualization**: Complete interactive map system with Leaflet
  - Multiple tile layer support (OpenStreetMap, satellite, topographic, CartoDB variants)
  - Individual segment map views with path geometry display
  - Comprehensive segments map view with filtering support
  - Overlapping segment detection and selection interface
  - Status-based color coding for visual segment identification

- **Path Data Management**: Full support for geographic path data
  - KML, KMZ, and GeoJSON file format support
  - Enhanced KMZ processing with multi-layer extraction
  - Automatic 3D to 2D coordinate conversion
  - Path geometry validation and error reporting
  - Automatic path length calculation using projected coordinates
  - Path data export as GeoJSON files

- **Advanced Map Features**:
  - Interactive controls (pan, zoom, fit-to-bounds)
  - Fallback visualization with straight lines when path data unavailable
  - Site markers for segment endpoints
  - Detailed segment information panels
  - Path data availability indicators
  - Responsive map controls and layer switching

- **Enhanced Data Model**:
  - `path_geometry` field for storing MultiLineString geometries
  - `path_length_km` field with automatic calculation
  - `path_source_format` field tracking data origin
  - `path_notes` field for additional metadata
  - Geographic helper methods for coordinate handling

- **UI/UX Improvements**:
  - Template extensions for Circuits, Providers, Sites, Locations, and Tenants
  - Custom table columns showing path data availability
  - Date status indicators with visual progress bars
  - Enhanced filtering including geographic data availability
  - Improved navigation with map view integration

- **API Enhancements**:
  - Separate serializers for list and detail views (performance optimization)
  - Geographic data endpoints for map visualization
  - GeoJSON export capabilities
  - Path bounds and coordinate data in API responses
  - Enhanced filtering on geographic fields

- **GraphQL Support**:
  - Complete GraphQL schema with geographic field support
  - Custom scalar types for path bounds and coordinates
  - Lazy-loaded relationship fields for performance
  - Geographic data queries and filtering

### Changed
- **Breaking**: Upgraded to Django 5.2.3 with GeoDjango support
- **Breaking**: Added PostGIS dependency for geographic features
- **Breaking**: Modified database schema to include geographic fields
- Improved segment form with path data upload capability
- Enhanced segment detail view with geographic information
- Updated table layouts with new path-related columns
- Refactored status choices to use configurable ChoiceSet system
- Improved error handling for geographic data processing

### Fixed
- Resolved migration conflicts during table renaming process
- Fixed segment validation to properly handle location-site relationships
- Improved date validation with better error messaging
- Enhanced KMZ file processing for complex archive structures
- Fixed coordinate system handling for accurate length calculations

### Technical Details
- Added `geopandas`, `fiona`, and `shapely` as core dependencies
- Implemented comprehensive GIS utility functions
- Added extensive JavaScript map handling with modular design
- Created reusable template components for map functionality
- Enhanced error handling and logging for geographic operations
- Implemented proper geometric validation and sanitization

### Migration Notes
- **Database Migration Required**: New geographic fields require PostGIS
- **Dependency Installation**: Geographic libraries (GDAL, GEOS, PROJ) required
- **Configuration Updates**: May need GeoDjango configuration updates
- **Data Migration**: Existing installations will have empty path geometry fields

## [0.1.0] - 2024-04-23

### Added
- Initial release on PyPI
- Basic segment and service path management
- Provider and circuit relationship tracking
- Simple filtering and table views
- REST API endpoints
- NetBox 3.7 compatibility

### Features
- Segment model with provider, site, and date tracking
- Service path model with status and kind classification
- Mapping models for segment-circuit and service path-segment relationships
- Basic NetBox integration with standard views and forms
- Template extensions for related model pages

---

## Development Guidelines

When updating this changelog:
1. Add new entries at the top under "Unreleased" section
2. Move completed features to version sections when releasing
3. Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format
4. Include breaking changes with **Breaking** prefix
5. Group changes by type: Added, Changed, Deprecated, Removed, Fixed, Security
6. Include migration notes for database or configuration changes