# Package Testing

The test suite runs inside the NetBox Docker container using Django's built-in test runner, following the same patterns as NetBox core.

## Test layout

```
cesnet_service_path_plugin/tests/
    __init__.py
    test_map_view_filtering.py      # unit tests for map view filter helpers
    test_type_specific_data_api.py  # API + model tests for dark fiber,
                                    # ethernet service, optical spectrum data
```

Tests use Django `TestCase` with `setUpTestData`, which wraps each test in a rolled-back transaction. No live data is required and no `.env` file is needed.

## Running the tests

**1. Make the test configuration available to NetBox** (one-time setup):

The file `configuration_testing.py` in the plugin root contains Django settings for the test database. It needs to be placed where NetBox can import it as `netbox.configuration_testing_plugin`.

```bash
# Docker
docker compose cp \
  plugins/cesnet_service_path_plugin/configuration_testing.py \
  netbox:/opt/netbox/netbox/netbox/configuration_testing_plugin.py

# Local NetBox — copy into the netbox/netbox/ package directory
cp configuration_testing.py /path/to/netbox/netbox/netbox/configuration_testing_plugin.py
```

**2. Run a specific test module:**

```bash
# Docker
docker compose exec netbox bash -c "
  cd /opt/netbox/netbox &&
  NETBOX_CONFIGURATION=netbox.configuration_testing_plugin \
  python manage.py test \
    cesnet_service_path_plugin.tests.test_type_specific_data_api \
    -v2 --keepdb"

# Local NetBox
cd /path/to/netbox/netbox
NETBOX_CONFIGURATION=netbox.configuration_testing_plugin \
python manage.py test \
  cesnet_service_path_plugin.tests.test_type_specific_data_api \
  -v2 --keepdb
```

**3. Run the full plugin test suite:**

```bash
# Docker
docker compose exec netbox bash -c "
  cd /opt/netbox/netbox &&
  NETBOX_CONFIGURATION=netbox.configuration_testing_plugin \
  python manage.py test cesnet_service_path_plugin.tests -v2 --keepdb"

# Local NetBox
cd /path/to/netbox/netbox
NETBOX_CONFIGURATION=netbox.configuration_testing_plugin \
python manage.py test cesnet_service_path_plugin.tests -v2 --keepdb
```

`--keepdb` reuses the existing database and skips migration re-runs, which makes repeated runs significantly faster.

## Code coverage status

| Module | Coverage |
|---|---|
| `test_map_view_filtering.py` | `_remap_params`, `_extract_site_params`, `_extract_segment_params`; `SiteFilterSet` and `SegmentFilterSet` integration |
| `test_type_specific_data_api.py` | Model validation (`clean()`), cascade deletes, OneToOne uniqueness, and full CRUD via the REST API for `DarkFiberSegmentData`, `EthernetServiceSegmentData`, `OpticalSpectrumSegmentData`; verifies `type_specific_data` field on the `Segment` endpoint |

## Adding new tests

Follow this pattern:

- Use `django.test.TestCase` (not `pytest`)
- Place shared DB fixtures in `setUpTestData` (class-level, rolled back per-test)
- Prefix object names with a unique string (e.g. `"MYTEST__"`) if writing to a shared `--keepdb` database, to avoid collisions with production data
- For API tests, subclass `_APIBase` from `test_type_specific_data_api.py` which sets up a `rest_framework.test.APIClient` with a scoped user token
