import os
import sys

from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATES[0]["OPTIONS"]["debug"] = True  # noqa: F405

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "z%4u$f(8jjkp@qqd$4g+w_xrbco3xbakg9=abrb*1ic7g@o*xc"

# Restricted directory locked down to campus by shib
RESTRICTED = 7163

# CGIMail testing configuration
SECURE_REFERRER_POLICY = "origin"
CGI_MAIL_SERVICE = "https://www.lib.uchicago.edu/cgi-bin/cgimail/cgimail"

# Use database backend for search in dev (no Elasticsearch required)
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Skip in GitHub Actions - no file permissions
if os.getenv("GITHUB_ACTIONS") != "true":
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "formatter": "default",
                "filename": "/var/log/django-errors.log",
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
            "default": {
                "format": "[%(asctime)s] (%(process)d/%(thread)d) %(name)s %(levelname)s: %(message)s"
            }
        },
    }

# Database configuration for development
# Override in local.py if needed (e.g., for production secrets)
if "test" in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "TEST": {
                "NAME": ":memory:",
            },
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "lib_www_dev",
        }
    }

# FOLIO test environment
FOLIO_BASE_URL = "https://uchicago-test-okapi.folio.indexdata.com"

# Tiny Tiny RSS Feed for development
TTRSS_FEED = "http://10.0.2.2/get_feed_atom"

try:
    from .local import *  # noqa: F403 F401
except ImportError:
    pass

# Specific settings for GitHub Workflow Actions
if "GITHUB" in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "TEST": {
                "NAME": ":memory:",
            },
        },
    }

    COMPRESS_OFFLINE = False
