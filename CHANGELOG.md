# Changelog

## [6.1.0] - 2026-03-09

> ⚠️ Requires NetBox >= 4.5.4. NetBox 4.5.0–4.5.3 is not supported by this release — use v6.0.x for those versions.

### Breaking Changes

- **Minimum NetBox version raised to 4.5.4.**
  This release uses `StrFilterLookup` from strawberry-graphql-django >= 0.79.0, which ships with
  NetBox 4.5.4. Starting the plugin on NetBox 4.5.0–4.5.3 will raise an `ImportError`.

- **GraphQL CharField filter types changed.**
  All string filter fields migrated from `FilterLookup[str]` → `StrFilterLookup[str]` to eliminate
  `DuplicatedTypeName` schema errors introduced in strawberry-graphql-django 0.79.0.
  GraphQL clients relying on type introspection may need updating.

### Fixed

- GraphQL `@field` resolver methods now correctly declare `Info` type annotations, resolving
  startup errors on NetBox 4.5.4+ with stricter strawberry-django introspection.

### Compatibility

| cesnet_service_path_plugin | NetBox |
|---|---|
| 6.1.0+ | 4.5.4+ |
| 6.0.x | 4.5.0 – 4.5.3 |

## [6.0.0] - 2026-01-21
### Added
- New features and improvements.  

### Changed
- Enhancements to existing functionalities.

### Fixed
- Bugs addressed in this release.

### Deprecated
- Features that will be removed in future releases.

### Removed
- Obsolete features from the previous versions.

### Security
- Security improvements implemented.