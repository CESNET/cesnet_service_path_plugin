# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## General Tips for Working on GitHub

* Register for a free [GitHub account](https://github.com/signup) if you haven't already.
* You can use [GitHub Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax) for formatting text and adding images.
* To help mitigate notification spam, please avoid "bumping" issues with no activity. (To vote an issue up or down, use a :thumbsup: or :thumbsdown: reaction.)
* Please avoid pinging members with `@` unless they've previously expressed interest or involvement with that particular issue.
* Familiarize yourself with [this list of discussion anti-patterns](https://github.com/bradfitz/issue-tracker-behaviors) and make every effort to avoid them.

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/CESNET/cesnet_service_path_plugin/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

Cesnet ServicePath Plugin could always use more documentation, whether as part of the
official Cesnet ServicePath Plugin docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/CESNET/cesnet_service_path_plugin/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Get Started!

The plugin requires a running NetBox instance with the plugin installed. You can set this up in several ways — choose whichever fits your workflow:

- **Docker** (recommended): use the `docker compose` stack from this repository (see `README.md`)
- **Dev container**: open the repository in VS Code with the provided devcontainer configuration
- **Local NetBox**: follow the [NetBox development setup guide](https://docs.netbox.dev/en/stable/development/getting-started/) and install the plugin into the same virtual environment

Regardless of the setup, the steps below apply.

1. Fork the `cesnet_service_path_plugin` repo on GitHub.

2. Clone your fork locally:

    ```bash
    git clone git@github.com:your_name_here/cesnet_service_path_plugin.git
    ```

3. Install the plugin in editable mode into your NetBox environment:

    ```bash
    # Local venv
    pip install -e /path/to/cesnet_service_path_plugin

    # Docker
    docker compose exec netbox pip install -e /opt/netbox/netbox/plugins/cesnet_service_path_plugin
    ```

    Editable mode creates a symlink so source changes are picked up without reinstalling.

4. Create a branch for local development:

    ```bash
    git checkout -b name-of-your-bugfix-or-feature
    ```

5. Run the tests to verify your changes (see the **Testing** section below).

6. Commit your changes and push your branch to GitHub:

    ```bash
    git add <specific files>
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

7. Submit a pull request through the GitHub website.

## Testing

The test suite runs inside the NetBox Docker container using Django's built-in test runner, following the same patterns as NetBox core and the `netbox-map` plugin.

### Test layout

```
cesnet_service_path_plugin/tests/
    __init__.py
    test_map_view_filtering.py      # unit tests for map view filter helpers
    test_type_specific_data_api.py  # API + model tests for dark fiber,
                                    # ethernet service, optical spectrum data
```

Tests use Django `TestCase` with `setUpTestData`, which wraps each test in a rolled-back transaction. No live data is required and no `.env` file is needed.

### Running the tests

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

### What is tested

| Module | Coverage |
|---|---|
| `test_map_view_filtering.py` | `_remap_params`, `_extract_site_params`, `_extract_segment_params`; `SiteFilterSet` and `SegmentFilterSet` integration |
| `test_type_specific_data_api.py` | Model validation (`clean()`), cascade deletes, OneToOne uniqueness, and full CRUD via the REST API for `DarkFiberSegmentData`, `EthernetServiceSegmentData`, `OpticalSpectrumSegmentData`; verifies `type_specific_data` field on the `Segment` endpoint |

### Adding new tests

Follow the `netbox-map` pattern:

- Use `django.test.TestCase` (not `pytest`)
- Place shared DB fixtures in `setUpTestData` (class-level, rolled back per-test)
- Prefix object names with a unique string (e.g. `"MYTEST__"`) if writing to a shared `--keepdb` database, to avoid collisions with production data
- For API tests, subclass `_APIBase` from `test_type_specific_data_api.py` which sets up a `rest_framework.test.APIClient` with a scoped user token

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.md.
3. The pull request should work with Python 3.12+ (required by NetBox 4.5+). Check
   https://github.com/CESNET/cesnet_service_path_plugin/actions
   and make sure that the tests pass.

## Deploying

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in CHANGELOG.md) and that all tests pass.
Then in the GitHub project go to `Releases` and create a new release with a new tag. This will automatically upload the release to PyPI.
