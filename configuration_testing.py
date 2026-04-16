###################################################################
#  NetBox configuration for running plugin unit tests.            #
#  NOT for production use.                                        #
#                                                                 #
#  Copy this file to /opt/netbox/netbox/netbox/ inside the        #
#  netbox container (e.g. via docker cp), then run:               #
#                                                                 #
#    docker compose exec netbox bash -c "                         #
#      cd /opt/netbox/netbox &&                                   #
#      NETBOX_CONFIGURATION=netbox.configuration_testing_plugin   #
#      python manage.py test                                      #
#        cesnet_service_path_plugin.tests.test_map_view_filtering #
#        -v2 --keepdb"                                            #
#                                                                 #
#  NOTE: Uses the existing 'netbox' DB as the test DB (--keepdb). #
#  Tests use prefixed object names to isolate from production     #
#  data.  TestCase wraps each test in a transaction that is       #
#  rolled back, so production data is never modified.             #
###################################################################

import os

ALLOWED_HOSTS = ["*"]

DATABASE = {
    "ENGINE": "django.contrib.gis.db.backends.postgis",
    "NAME": os.environ.get("DB_NAME", "netbox"),
    "USER": os.environ.get("DB_USER", "netbox"),
    "PASSWORD": os.environ["DB_PASSWORD"],   # required — no default
    "HOST": os.environ.get("DB_HOST", "postgres"),
    "PORT": os.environ.get("DB_PORT", ""),
    "TEST": {
        "NAME": os.environ.get("DB_NAME", "netbox"),   # reuse existing DB — avoids migration mismatch
    },
}

REDIS = {
    "tasks": {
        "HOST": os.environ.get("REDIS_HOST", "redis"),
        "PORT": int(os.environ.get("REDIS_PORT", 6379)),
        "PASSWORD": os.environ["REDIS_PASSWORD"],   # required — no default
        "DATABASE": int(os.environ.get("REDIS_DATABASE", 0)),
        "SSL": False,
    },
    "caching": {
        "HOST": os.environ.get("REDIS_CACHE_HOST", os.environ.get("REDIS_HOST", "redis")),
        "PORT": int(os.environ.get("REDIS_CACHE_PORT", os.environ.get("REDIS_PORT", 6379))),
        "PASSWORD": os.environ.get("REDIS_CACHE_PASSWORD", os.environ["REDIS_PASSWORD"]),
        "DATABASE": int(os.environ.get("REDIS_CACHE_DATABASE", 1)),
        "SSL": False,
    },
}

SECRET_KEY = os.environ["SECRET_KEY"]   # required — no default

# Must be >=50 chars per key
API_TOKEN_PEPPERS = {1: "test-pepper-value-do-not-use-in-production-at-all-ever"}

PLUGINS = [
    "cesnet_service_path_plugin",
]

DEFAULT_PERMISSIONS = {}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
}
