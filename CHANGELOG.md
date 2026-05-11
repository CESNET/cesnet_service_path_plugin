# Changelog

## [6.2.3] - 2026-05-11

### Changed

- **Compatibility — NetBox 4.6 support**: Raised `max_version` to `4.6.99` after successful
  testing against NetBox 4.6.x. Plugin version 6.2.x is now supported on both NetBox 4.5.4+
  and NetBox 4.6.x.

### Compatibility

| cesnet_service_path_plugin | NetBox |
|---|---|
| 6.2.x | 4.5.4 – 4.6.x |
| 6.1.x | 4.5.4+ |
| 6.0.x | 4.5.0 – 4.5.3 |

---

## [6.2.2] - 2026-05-07

### Added

- **Segment Map — Interactive path editor**: Authorised users can now draw and edit a segment's
  geographic path directly on the single-segment map view without uploading a file.
  - **Click-to-draw**: Click on the map to place vertices one by one, building up a LineString path.
  - **Drag to move**: Drag any existing vertex to reposition it; the polyline rubber-bands in real time.
  - **Click line to insert**: Click anywhere on the drawn polyline to insert a new vertex at that
    exact position. The new vertex immediately enters drag mode for precise placement.
  - **Right-click to delete**: Right-click any vertex to remove it from the path.
  - **Last vertex highlight**: The most recently placed vertex is rendered with a distinct solid fill
    so the path end is always obvious.
  - **Undo**: Step back through the edit history one action at a time.
  - **Clear**: Remove all vertices and start fresh without leaving edit mode.
  - **Delete Path**: Delete the stored geometry for the segment entirely (with confirmation).
  - **Proximity warnings**: If the path start or end is more than 100 m from the respective site
    marker, a confirmation dialog is shown before saving.
  - **Multi-segment auto-join**: Existing paths stored as MultiLineString (e.g. from file upload)
    are automatically joined into a single editable LineString when gaps between segments are ≤ 10 m.
    Paths with larger gaps are flagged as "too complex to edit here".
  - **Read-only layer hide**: The static GeoJSON path layer is hidden while the editor is active
    and restored on cancel, preventing visual overlap during editing.
  - **Permission-gated**: Edit controls are only shown to users with `change_segment` permission.
- **Segment Map — Context-sensitive map button**: The button on the segment detail page now adapts
  to four states based on path data availability and user permissions (View / View+Edit / Draw /
  hidden). View-only users with no stored path data but positioned sites still get a "View on Map"
  link to see the fallback straight line.
- **Segment list — Path length column**: The `path_length_km` value is now shown as a sortable
  column in the segment list table.
- **Segment filter — Has Editable Path**: New filter `has_editable_path` limits results to segments
  whose path geometry is a single LineString (i.e. directly editable in the map editor). Segments
  with disconnected multi-segment paths are excluded.
- **Segment API — Direct geometry write**: `PATCH /api/.../segments/{id}/` now accepts a
  `path_geometry` JSON field (`{"type": "LineString", "coordinates": [...]}`) to save a path from
  the map editor without a file upload. `path_source_format` is set to `"manual"` automatically.
  `POST` (create) also supports `path_geometry` with the same behaviour.

### Fixed

- **Segment serializer — `create()` missing manual geometry handling**: Creating a segment via
  `POST` with a `path_geometry` field did not set `path_source_format = "manual"`. Fixed to match
  the `update()` behaviour.

### Compatibility

| cesnet_service_path_plugin | NetBox |
|---|---|
| 6.2.x | 4.5.4+ |
| 6.1.x | 4.5.4+ |
| 6.0.x | 4.5.0 – 4.5.3 |

---

## [6.2.1] - 2026-05-04

### Added

- **Network Map — Edit mode**: A new "Edit Map" toggle lets authorised users modify the map
  directly from the Network Map view without leaving the page.
  - **Place unpositioned sites**: Drag sites that have no coordinates onto the map to assign
    their latitude/longitude via the NetBox API.
  - **Create sites**: Click an empty map location to open a form and create a new site with
    coordinates pre-filled.
  - **Create segments**: Select two sites and fill in the inline form to create a new segment
    (name, type, provider, ownership, status).
  - **Create circuits**: Select two sites and fill in the inline form to create a new circuit
    (CID, provider, type). Terminations A/Z are created automatically; the circuit is
    rolled back (deleted) if termination creation fails.
  - **Edit segment/circuit endpoints**: Click an existing segment or circuit, then click a
    different site to move one endpoint. A confirmation dialog shows the old and new site
    before saving.
  - **Confirmation dialog**: All endpoint replacement operations require explicit confirmation
    before the API call is made; pressing Escape or "Cancel" returns to the connection edit
    panel without changes.
  - **View links**: After creating a site, segment, or circuit, the success panel includes a
    direct link to the new object's detail page.

### Changed

- **Network Map — Viewport-fixed layout**: The map now fills the available browser viewport
  height and no longer scrolls off-screen. The right panel (filter sidebar, object list,
  edit mode panel) becomes independently scrollable within the same fixed height.
- **Network Map — Sites always on top**: Sites render in a dedicated Leaflet pane above
  segments and circuits so they remain clickable even when overlapping connections.

### Fixed

- **Network Map — Object highlight cleared on click**: Clicking a segment or circuit
  immediately cleared the orange highlight because the background `map.click` deselect
  handler fired after every object click. Fixed by stopping event propagation in all object
  click handlers.
- **Network Map — Objects not clickable after edit mode exit**: Re-wiring click handlers
  for read mode was missing `stopPropagation`, causing the deselect handler to swallow
  clicks. Fixed in both site and connection handlers.
- **Network Map — Orphaned circuit on partial failure**: If creating circuit terminations
  failed after the circuit was created, the orphaned circuit record was left in the database.
  The API layer now issues a best-effort DELETE rollback before propagating the error.

### Compatibility

| cesnet_service_path_plugin | NetBox |
|---|---|
| 6.2.x | 4.5.4+ |
| 6.1.x | 4.5.4+ |
| 6.0.x | 4.5.0 – 4.5.3 |

---

## [6.2.0] - 2026-04-27

### Added

- **Network Map — Tag filters**: Tag filter dropdowns added for Sites, Segments, and Circuits.
  Filtering uses AND logic — an object must carry all selected tags to match.
- **Network Map — Object selection highlight**: Clicking a segment, circuit, or site now
  highlights the selected object on the map in orange. Highlight is restored when another
  object is selected or the info card is closed.
- **Network Map — Tag colors in info card**: Tag badges in the detail info card now use the
  tag's configured color (with automatic light/dark contrast text).
- **Network Map — Object list panel**: A second "List" tab in the right panel provides a
  searchable, scrollable list of all visible objects with type toggles and click-to-locate.
- **Network Map — Filter sidebar**: Permanent right-side filter column replaces the offcanvas
  sidebar. Includes two "Clear Filters" buttons (top and bottom of the column).
- **Network Map — Circuit termination details**: Info card shows cable connection, cross-connect
  ID, port speed, and a "Connect" dropdown button for unconnected terminations.

### Changed

- **Network Map — Status/type filter buttons**: Reverted from `<select multiple>` dropdowns
  back to btn-check pill buttons following user testing feedback. Button sizing reduced
  (0.65 rem, 20 px height) using flexbox to eliminate Bootstrap padding asymmetry.
- **Network Map — Map popup links**: Plain text links in segment, circuit, and site popups
  replaced with `btn-outline` buttons (View / Map) for better discoverability.
- **Network Map — Overlap popup**: Added `<hr>` separators between entries and View/Map
  buttons per segment. Segment names styled as blue links with hover underline and a
  "Click a name to show details" subtitle.
- **Network Map — Object list sync**: List type buttons (Sites / Segs / Circs) now mirror
  the state of the main toolbar visibility toggles. List count and rows update immediately
  when toolbar toggles change. Circuits list button starts unchecked to match default
  hidden state.
- **Network Map — Map height**: Increased to 1000 px for better usability on larger screens.
- **Network Map — Color palette**: Segment and circuit colors updated to avoid green tones
  that blend with OSM map background.

### Fixed

- **Network Map — Object list initial count**: List now populates via `applyFilters()` on
  first load so counts reflect server-side pre-filters (e.g. region in URL) immediately.
- **Network Map — List visibility respect**: Object list respects layer visibility flags;
  hidden layers are excluded from the list count and rows.
- **Network Map — Segment popup midpoint**: When selecting a segment from the list, the
  popup now anchors to the middle vertex of the actual rendered GeoJSON polyline instead
  of the midpoint between the two endpoint sites.
- **Network Map — Clear Filters Tom Select**: Region and other dynamic fields (Tom Select
  widgets) are now correctly cleared via `sel.tomselect.clear()` / `clearOptions()`.
- **Network Map — Nav-tabs dark theme**: Switched from `nav-tabs` to `nav-pills` for the
  Filters / List tab switcher so tab labels are visible in NetBox dark mode.
- **Network Map — Toggle button padding**: Fixed uneven top/bottom padding on btn-check
  filter pill buttons caused by Bootstrap `--bs-btn-padding-y` override.

### Compatibility

| cesnet_service_path_plugin | NetBox |
|---|---|
| 6.2.x | 4.5.4+ |
| 6.1.x | 4.5.4+ |
| 6.0.x | 4.5.0 – 4.5.3 |

---

## [6.1.1] - 2026-03-19

### Fixed

- Added `referrerPolicy: 'strict-origin-when-cross-origin'` to all Leaflet tile layer configurations
  (OpenStreetMap, Humanitarian OSM, CartoDB Positron, CartoDB Dark Matter, OpenTopoMap) to prevent
  map tile loading issues in environments with strict referrer policies.

### Compatibility

| cesnet_service_path_plugin | NetBox |
|---|---|
| 6.1.x | 4.5.4+ |
| 6.0.x | 4.5.0 – 4.5.3 |

---

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