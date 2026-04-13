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

ALLOWED_HOSTS = ["*"]

DATABASE = {
    "ENGINE": "django.contrib.gis.db.backends.postgis",
    "NAME": "netbox",
    "USER": "netbox",
    "PASSWORD": "J5brHrAXFLQSif0K",
    "HOST": "postgres",
    "PORT": "",
    "TEST": {
        "NAME": "netbox",   # reuse existing DB — avoids migration mismatch
    },
}

REDIS = {
    "tasks": {
        "HOST": "redis",
        "PORT": 6379,
        "PASSWORD": "H733Kdjndks81",
        "DATABASE": 0,
        "SSL": False,
    },
    "caching": {
        "HOST": "redis",
        "PORT": 6379,
        "PASSWORD": "H733Kdjndks81",
        "DATABASE": 1,
        "SSL": False,
    },
}

# Must be >=50 chars for NetBox
SECRET_KEY = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#"

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
