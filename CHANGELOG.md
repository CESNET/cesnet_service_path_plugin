# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.2.0] - TBD

### Added
- **Financial Information Management**: New segment financial tracking system
  - `SegmentFinancialInfo` model for tracking segment costs and commitments
  - Monthly charge and non-recurring charge fields
  - Multi-currency support with configurable currency list
  - Commitment period tracking (months)
  - Automatic cost calculations (total commitment cost, total with setup)
  - Permission-based access control for financial data
  - Integration with segment detail view
  - REST API support with nested serialization in segment endpoints
  - Financial info displayed only to users with view permissions

- **Plugin Configuration**: Enhanced configuration options
  - Configurable currency list in plugin settings
  - Default currency selection
  - Example configuration in README

- **Plugin Metadata**: Added `netbox-plugin.yaml`
  - Official plugin metadata file for NetBox plugin registry
  - Compatibility matrix with NetBox versions
  - Package information and versioning

### Changed
- **API Enhancements**:
  - Improved error handling in segment serializer with detailed logging
  - Financial info included in segment API responses (permission-based)
  - Cleaner error messages for path file upload failures
  - Better separation of validation and processing errors

- **Permission System**:
  - Financial data visibility controlled by Django permissions
  - View, add, change, and delete permissions for financial info
  - Automatic permission checks in views and API

- **Documentation Updates**:
  - Updated plugin configuration examples with currency settings
  - Corrected file path references (configuration.py → configuration/plugins.py)
  - Updated compatibility badge to reflect NetBox 4.4 support

- **Development Dependencies**:
  - Unpinned development dependency versions for flexibility
  - Updated Python version requirement to >= 3.10
  - Corrected license classifier to Apache 2.0

### Technical Details
- Financial info uses one-to-one relationship with Segment model
- Currency choices are dynamically loaded from plugin configuration
- Financial data is optional - segments can exist without financial info
- API serializer uses method field for conditional financial data inclusion
- Redirect-based views for better UX (financial detail redirects to segment detail)
- Custom return URL handling for create/edit/delete operations

### Migration Notes
- **New Model**: `SegmentFinancialInfo` table will be created
- **Permissions**: Four new permissions added for financial info management
- **Configuration**: Optional currency configuration can be added to plugin settings
- **API Change**: Segment API responses now include `financial_info` field (null if no data or no permission)

## [5.1.0] - 2025-09-23

### Added
- **Segment Type System**: Complete implementation of segment type classification
  - `segment_type` field with Dark Fiber, Optical Spectrum, and Ethernet Service types
  - Type-specific data fields stored as JSON with dynamic schemas
  - Smart numeric filtering for type-specific fields with operators (>, <, >=, <=, ranges)
  - Dynamic form generation based on selected segment type
  - Type-specific field validation and conversion (Decimal, Integer)
  - Enhanced GraphQL API with type-specific data filtering (`has_type_specific_data`)

- **Enhanced Map Visualization**: Advanced mapping features
  - Segment type-based coloring and legend in map views
  - Color schemes: by status and by provider
  - Improved overlapping segment detection and selection
  - Multiple background map layers (OpenStreetMap, satellite, topographic, CartoDB)

- **Smart Filtering System**: Advanced filtering capabilities
  - Smart numeric filters for JSON fields with operator support
  - Type-specific field filters (fiber_type, connector_type, modulation_format, etc.)
  - Range filters for numeric fields (fiber_attenuation_max, wavelength, port_speed, etc.)
  - Boolean value parsing improvements
  - Enhanced search functionality including segment_type

### Changed
- Updated segment form to preserve type-specific field values during type changes
- Enhanced JavaScript form handling to hide fields without clearing values
- Improved field initialization and population logic
- Updated segment table to include segment_type column
- Modified API serializers to handle path file uploads
- Removed unnecessary SegmentListSerializer, unified with SegmentSerializer

### Fixed
- Fixed form rendering issues with type-specific fields
- Improved value preservation when switching segment types
- Enhanced JSON field conversion for Decimal types
- Fixed smart numeric filtering edge cases
- Resolved issues with dynamic field visibility


## [5.0.3] - 2025-08-29

### Fixed
- **Critical**: Added save_m2m() call to SegmentForm to properly save tags
  - Fixed missing many-to-many relationship saving (tags were being lost)
  - Ensured proper persistence of all many-to-many fields

### Changed
- Updated documentation with sample map in README
- Added Apache 2.0 License (same as NetBox)
- Updated pyproject.toml with repository information

## [5.0.2] - 2025-08-21

### Added
- **Documentation Improvements**: Enhanced README and licensing
  - Apache 2.0 License badge and full license file
  - Sample map visualization in README
  - Updated repository information in pyproject.toml

### Changed
- Repository metadata and documentation updates
- Warning about work-in-progress status

## [5.0.1] - 2025-08-04

### Added
- **Comprehensive Segment Map**: Interactive map view for all segments
  - Map utilizes list view filtering capabilities
  - Multiple background layer options
  - Improved navigation and user experience

### Fixed
- Fixed button types to prevent form submission when changing map layers
- Enhanced map layer switching controls

## [5.0.0] - 2025-08-01

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
- Fixed segment detail view table rendering and typos

### Technical Details
- Added `geopandas`, `fiona`, and `shapely` as core dependencies
- Implemented comprehensive GIS utility functions
- Added extensive JavaScript map handling with modular design
- Created reusable template components for map functionality
- Enhanced error handling and logging for geographic operations
- Implemented proper geometric validation and sanitization
- Replaced setup.py with pyproject.toml for modern Python packaging

### Migration Notes
- **Database Migration Required**: New geographic fields require PostGIS
- **Dependency Installation**: Geographic libraries (GDAL, GEOS, PROJ) required
- **Configuration Updates**: May need GeoDjango configuration updates
- **Data Migration**: Existing installations will have empty path geometry fields

## [4.3.0] - 2025-05-16

### Added
- **NetBox 4.3 Compatibility**: Updated for NetBox 4.3 support
  - New URL patterns for bulk operations on service paths, segment mappings, and circuit mappings
  - Enhanced Meta classes for filter consistency
  - Improved import structure for better maintainability

### Changed
- Updated imports in filters.py for better readability
- Changed `model` to `models` in template_content.py for multi-model compatibility
- Removed unused imports and decorators for cleaner code
- Updated plugin version to 4.3.0

## [4.0.1] - 2025-02-24

### Fixed
- **Bookmark and Subscription Issues**: Resolved non-functional bookmark and subscription features
- Updated plugin configuration and version management
- Removed unused imports for cleaner codebase

## [4.0.0] - 2025-02-19

### Added
- **Enhanced Service Management**: Comprehensive service path and segment management
  - Ability to assign segments to circuits or service paths from segment detail view
  - Improved ServicePath kind field with ChoiceSet system
  - Enhanced date validation logic in SegmentForm
  - Date status display in table and detail views with color-coded progress bars

### Changed
- **Breaking**: Refactored from "Komora" to "CESNET" branding throughout
  - Plugin renamed from `komora_service_path_plugin` to `cesnet_service_path_plugin`
  - Database table names changed from `komora_*` to `cesnet_*`
  - URL patterns and configuration updated
  - All references and documentation updated

- **Model Improvements**:
  - Replaced `state` field with `status` field in ServicePath and Segment models
  - Added StatusChoices for consistent status options
  - Made provider field required in SegmentForm
  - Enhanced date validation with install_date/termination_date constraints

- **Data Cleanup**:
  - Removed sync_status from all models
  - Removed device_ and port_ fields from Segment model
  - Merged segment notes (note_a, note_b) into unified comments field
  - Removed imported_data and komora_id fields
  - Removed unnecessary db_table options from models

### Fixed
- Fixed link for adding segment to a circuit
- Fixed EditForm for SegmentCircuitMapping model
- Enabled ID linkify for mapping tables
- Fixed date status logic and display
- Enhanced form validation and error handling

### Migration Notes
- **Breaking**: Database table renaming requires careful migration
- **Data Migration**: Existing installations need to migrate from old table names
- **Configuration**: Update plugin configuration from komora to cesnet references

## [0.1.0] - 2024-04-23

### Added
- **Initial Release**: First version published on PyPI
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