import os

from .dev import *  # noqa: F403

# Import local settings to get any developer customizations
try:
    from .local import *  # noqa: F403
except ImportError:
    pass

# Docker-specific database configuration (overrides local.py)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "lib_www_dev"),
        "USER": os.environ.get("POSTGRES_USER", "vagrant"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Docker-specific Redis configuration (overrides local.py)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
    "pagecache": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(BASE_DIR, "cache"),  # noqa: 405
        "KEY_PREFIX": "wagtailcache",
        "TIMEOUT": 21600,
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
            "CULL_FREQUENCY": 5,
        },
    },
}
