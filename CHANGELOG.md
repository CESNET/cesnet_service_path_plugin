# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.5.0] - 2025-12-12

### Removed (Phase 3 - Type-Specific Data Cleanup)

- **Database**: Removed `type_specific_data` JSONField column from Segment table (migration 0035)
- **Models**: Removed legacy JSON validation functions from `segment_types.py`:
  - `SEGMENT_TYPE_SCHEMAS` dictionary (174 lines of JSON schema definitions)
  - `validate_segment_type_data()` - Runtime JSON validation
  - `get_segment_type_schema()` - Schema retrieval
  - `get_all_segment_types()` - Segment type listing
- **Segment Model**: Removed JSONField-related helper methods:
  - `validate_type_specific_data()` - JSON validation method
  - `get_type_specific_display()` - JSON formatting for templates
  - `has_type_specific_data()` - JSON data check (model method; GraphQL method remains)
- **API**: `type_specific_data` field is now a computed field (no longer a JSONField)
  - Returns structured data from relational models (DarkFiberSegmentData, OpticalSpectrumSegmentData, EthernetServiceSegmentData)
  - Same field name as before, but underlying implementation is completely different
  - Data comes from OneToOne related models instead of JSON blob
- **Filters**: Removed `has_type_specific_data` filter from segment filtersets
- **Forms**: Removed `has_type_specific_data` form field from segment filter forms
- **Total code reduction**: ~405 lines of legacy code removed

### Changed

- **API**: `type_specific_data` field completely reimplemented as computed field
  - Now returns data from relational models instead of JSON blob
  - Field name intentionally kept the same for API familiarity
  - GraphQL field also renamed from `type_specific_technicals` to `type_specific_data`
- **Architecture**: Fully migrated to relational database schema for type-specific data
  - All type-specific data stored in dedicated models (Phase 2)
  - JSONField completely removed from database (Phase 3)
  - Clean, normalized schema with proper database constraints

### Technical Details

- **Migration 0035**: One-way migration removes `type_specific_data` column
- **Data Safety**: All existing data preserved in relational models (migrated in Phase 2)
- **Performance**: Improved query performance with indexed relational fields
- **Validation**: Database-level constraints replace runtime JSON validation
- **Maintainability**: Django model fields replace 272 lines of JSON schema code

### Non-Breaking Change Note

**API field name remains the same**: `type_specific_data`
- Field name is unchanged from previous versions
- However, the underlying implementation is completely different:
  - **Before 5.5.0**: Direct JSONField column in database
  - **After 5.5.0**: Computed field reading from relational models
- **No API client changes required** - the field name is identical
- Data structure is also similar, making the transition seamless

### Documentation

- Added `PHASE_3_PLAN.md` - Detailed implementation plan
- Added `PHASE_3_COMPLETE.md` - Completion summary with metrics
- Added `RUN_MIGRATION_0035.md` - Migration instructions
- Added `PHASE_3_QUICK_VERIFICATION.md` - Post-migration verification

## [5.4.0] - 2025-12-08

### Added

- **Contract Information Management System**: Complete replacement of SegmentFinancialInfo with ContractInfo
  - Versioned contract system with linear version chains (similar to Git commits)
  - Support for contract amendments and renewals through NetBox clone functionality
  - Many-to-many relationship between contracts and segments (one contract can cover multiple segments)
  - Contract metadata tracking: contract number, type (new/amendment/renewal), effective dates
  - Enhanced recurring charge tracking with configurable periods (monthly, quarterly, annually, etc.)
  - Commitment end date calculation and tracking with visual indicators
  - Contract version history visualization in UI

- **Contract Versioning Features**:
  - Linear version chain using linked list pattern (previous_version/superseded_by)
  - Automatic version numbering (v1, v2, v3...)
  - Version navigation: get first version, latest version, full version history
  - Active/superseded contract status tracking
  - Clone functionality for creating amendments and renewals

- **Contract Financial Tracking**:
  - Recurring charges with customizable periods (monthly, quarterly, semi-annually, annually, bi-annually)
  - Number of recurring charge periods tracking
  - Non-recurring charges for setup/installation fees
  - Multi-currency support with immutable currency (set at contract creation)
  - Automatic financial calculations:
    - Total recurring cost (recurring charge × number of periods)
    - Total contract value (recurring + non-recurring charges)
    - Commitment end date (start date + recurring periods)

- **Contract UI Components**:
  - ContractInfo list view with advanced filtering
  - Contract detail view with version history timeline
  - Color-coded date badges for contract status (green/orange/red/gray)
  - Interactive tooltips showing days remaining and contract status
  - Version chain visualization showing contract evolution
  - Financial summary panel with all calculations
  - Navigation menu integration

- **Contract API Enhancements**:
  - New `/api/plugins/cesnet-service-path-plugin/contract-info/` endpoint
  - Support for versioning fields in API:
    - `previous_version`: Link to previous contract version
    - `superseded_by`: Link to superseding contract version
    - `is_active`: Boolean indicating if contract is current version
    - `version`: Calculated version number
  - Computed financial fields in API responses
  - Advanced filtering: by active status, version status, contract type, currency, dates

- **Segment View Enhancements**:
  - M:N contract relationship support in segment detail view
  - Display all contracts associated with a segment
  - Color-coded contract status indicators
  - Contract end date and commitment end date visualization

- **GraphQL Support**:
  - Updated GraphQL schema for ContractInfo model
  - Support for querying contract versions and relationships
  - Financial calculations available in GraphQL queries

### Changed

- **Breaking**: Replaced SegmentFinancialInfo model with ContractInfo model
  - Changed from 1:1 segment-financial relationship to M:N segment-contract relationship
  - Financial information now managed through contracts rather than directly on segments
  - API endpoint changed from `/segment-financial-info/` to `/contract-info/`

- **Database Schema**:
  - Removed SegmentFinancialInfo table
  - Added ContractInfo table with versioning support
  - Added ContractSegmentMapping join table for M:N relationships
  - Migration automatically converts existing financial data to contracts

- **Financial Field Changes**:
  - Renamed `monthly_charge` to `recurring_charge` with configurable period
  - Added `recurring_charge_period` field (monthly, quarterly, annually, etc.)
  - Renamed `commitment_period_months` to `number_of_recurring_charges`
  - Renamed `recurring_charge_end_date` to `commitment_end_date` for clarity
  - Made recurring charge fields nullable to support amendments without recurring charges

- **Model Improvements**:
  - Currency is now immutable after contract creation (cannot be changed in amendments)
  - All contract attributes can be updated through versioning (except currency)
  - Enhanced clone functionality for proper M2M relationship handling
  - Improved date calculations and validations

- **Color-Coded Date Visualization**:
  - Contract end dates now show color-coded status badges
  - Commitment end dates display with visual indicators:
    - Green: Date has passed
    - Orange: Within 30 days of expiration
    - Red: More than 30 days remaining
    - Gray: Date not set
  - Interactive tooltips showing exact dates and days remaining

### Removed

- **Breaking**: SegmentFinancialInfo model and related components
  - Removed `/api/plugins/cesnet-service-path-plugin/segment-financial-info/` endpoint
  - Removed SegmentFinancialInfo views, forms, tables, and serializers
  - Removed direct financial relationship from segments

### Fixed

- Improved decimal handling in financial calculations
- Enhanced date validation for contract periods
- Better error handling for version chain operations
- Fixed M2M relationship serialization in API responses

### Migration Notes

- **Database Migration Required**: Migration 0033 automatically converts SegmentFinancialInfo to ContractInfo
- **Data Preservation**: All existing financial data is preserved during migration:
  - Monthly charges → recurring charges (monthly period)
  - Commitment period months → number of recurring charges
  - Segment install/termination dates → contract start/end dates
  - Notes and tags are fully preserved
  - Created/updated timestamps are maintained
- **API Breaking Change**: Update API clients to use `/contract-info/` endpoint instead of `/segment-financial-info/`
- **Permission Updates**: New permissions for ContractInfo (view, add, change, delete)
- **M:N Relationships**: Segments can now be associated with multiple contracts
- **Versioning Workflow**: Use NetBox clone functionality to create contract amendments

### Upgrade Instructions

1. **Backup your database** before upgrading (important for any major version)
2. Update the plugin: `pip install --upgrade cesnet_service_path_plugin`
3. Run migrations: `python manage.py migrate cesnet_service_path_plugin`
4. Update API integrations to use new `/contract-info/` endpoint
5. Review and update user permissions for ContractInfo model
6. Test contract creation and amendment workflow in UI

## [5.3.0] - 2025-11-19

### Added

  - **Introduced ownership type support attribute**
  - New **database migration** adding ownership_type to segments.
  - New constants in custom_choices and model methods for ownership type labels and colors.
  - Added backend and frontend color mappings for ownership type (badges + map line colors).
  - Added new "Ownership Type" color scheme to the Segments Map, including:
  - Optimized Segments map color scheme change for faster rendering

### Changed

  - Improved segment map UI:
    - Popups and detail panels now show both status badge and ownership type badge.
    - Map legend updated to support ownership types.
    - Optimized color scheme switching with a new updateSegmentColors() function to avoid full redraw.
    - Status color mapping corrected (duplicate “Planned” entry resolved).
    - Enhanced fall-back line logic to correctly show straight-line path only when path data is missing.
    - Adjusted styling of badges and map-line colors for better consistency with Bootstrap and existing segment status colors.

### Fixed

  - Several UI inconsistencies in map popups where status badges were duplicated or missing label formatting.
  - Missing ownership fields in multiple API outputs and templates.

### Removed

  - Deprecated static color entries in map_status_colors.html.

## [5.2.1] - 2025-11-07

### Added
- **Topology Visualization**: Interactive network topology visualization using Cytoscape.js
  - Visual representation of segment connections and circuit terminations
  - Multi-topology support for service paths with multiple segments
  - Automatic topology generation for both segments and service paths
  - Clean NetBox Blue styled visualization with gradients and shadows
  - Interactive topology viewer with hover tooltips showing node details
  - Topology visualization integrated into segment and service path detail views
  - Topology visualization added to circuit detail pages showing related segments/service paths
  - Toggle between multiple topologies when segment belongs to multiple service paths

- **Commitment End Date Tracking**: Enhanced financial commitment monitoring
  - Automatic calculation of commitment end date based on install date and commitment period
  - Color-coded commitment status indicators:
    - Red: More than 30 days until end
    - Orange: Within 30 days of end
    - Green: Commitment period has ended
    - Gray: No commitment period set
  - Interactive tooltips showing days remaining until commitment end
  - Visual feedback for commitment periods that have ended
  - Commitment end date displayed in segment detail view with badge styling
  - GraphQL API support for commitment end dates with ISO format

### Changed
- **Circuit Extensions Refactoring**: Improved code organization
  - Renamed `CircuitKomoraSegmentExtension` to `CircuitSegmentExtension` for better naming consistency
  - Enhanced circuit detail view with topology visualization support
  - Better separation of concerns in template content extensions
  - Circuit pages now show topology visualizations for associated segments

- **Currency Field Enhancement**: Made charge_currency field required
  - Removed default currency value to ensure explicit currency selection
  - Migration `0031` updates currency field constraints
  - Currency must now be explicitly set when creating financial information
  - Prevents accidental use of default currency when not intended

- **Table Improvements**: Enhanced data presentation
  - Circuit column in SegmentCircuitMappingTable now orders by CID instead of name
  - Improved ordering logic for better data organization and searchability

- **Version Update**: Updated to version 5.2.1b5 in pyproject.toml

### Fixed
- Added missing `python-dateutil` dependency to pyproject.toml for date calculations
- Improved commitment end date calculation with proper timezone handling using `django.utils.timezone`
- Enhanced tooltip rendering with proper Bootstrap integration
- Fixed tooltip data attributes for proper display of commitment information

### Technical Details
- New utility module `utils_topology.py` with `TopologyBuilder` class for generating network graphs
- Cytoscape.js (v3.28.1) integration for advanced graph visualization
- Reusable topology visualization templates:
  - `topology_visualization.html` - Core Cytoscape includes and initialization
  - `topology_segment_card.html` - Topology display card with multi-topology support
  - `topology_styles.html` - Styling for topology containers and tooltips
- Support for multiple topologies on single page with tab switching functionality
- Topology data stored as JSON and rendered client-side for performance
- Color-coding system for commitment status based on time remaining (30-day threshold)
- New GraphQL field resolver for `commitment_end_date` with ISO format output
- Template extensions now check for service path membership to generate appropriate topologies

### Migration Notes
- **Migration 0031**: Updates `charge_currency` field to remove default value - requires explicit currency selection
- **New Dependencies**: Added `python-dateutil` for relativedelta calculations in commitment period tracking
- **Template Updates**: New topology visualization templates require Cytoscape.js CDN (included automatically)
- **API Changes**: GraphQL API now includes `commitment_end_date` field in SegmentFinancialInfoType

### Upgrade Instructions
1. Run migrations: `python manage.py migrate cesnet_service_path_plugin`
2. Install new dependency: `pip install python-dateutil` (or upgrade plugin package)
3. Update existing financial records to set currency explicitly if using default
4. Refresh browser cache to load new topology visualization assets

## [5.2.0] - 2025-10-29

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