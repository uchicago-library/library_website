from .base import *  # noqa: F401,F403

DEBUG = False
TEMPLATE_DEBUG = False

WAGTAILUSERS_PASSWORD_REQUIRED = False

FOLIO_BASE_URL = "https://uchicago-okapi.folio.indexdata.com"

# Logging configuration for production
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "myFormatter",
            "filename": "/data/local/django-errors.log",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
    "formatters": {
        "myFormatter": {
            "format": "[%(asctime)s] (%(process)d/%(thread)d) %(name)s %(levelname)s: %(message)s",
        }
    },
}

# Shibboleth authentication configuration
AUTHENTICATION_BACKENDS = ("shibboleth.backends.ShibbolethRemoteUserBackend",)

SHIBBOLETH_ATTRIBUTE_MAP = {
    "uid": (True, "username"),
    "givenName": (True, "first_name"),
    "sn": (True, "last_name"),
}

# Create a new user by default upon auth via shibboleth
CREATE_UNKNOWN_USER = False
LOGIN_URL = "/Shibboleth.sso/Login?forceAuthn=true"

# Shibboleth logout documentation:
# https://wiki.uchicago.edu/display/idm/Shibboleth+Non-SLO+Logout
# https://wiki.shibboleth.net/confluence/display/CONCEPT/SLOIssues
SHIBBOLETH_LOGOUT_URL = "https://shibboleth2.uchicago.edu/idp/logout.html?target=%s"

# Import secrets
try:
    from .secrets import *  # noqa: F401,F403
except ImportError:
    pass

try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass

CSRF_COOKIE_SECURE = True
