# Settings for an isolated verification instance. Mounted read-only into a
# one-off web container by bin/lwv; never used by the regular dev stack.
import os

from library_website.settings.docker import *  # noqa: F401,F403

RUN = os.environ["LWV_RUN"]

# Per-run database cloned from the verification template.
DATABASES["default"]["NAME"] = os.environ["LWV_DB"]  # noqa: F405

# Keep Redis keys and the page cache away from the dev instance.
CACHES["default"]["LOCATION"] = "redis://redis:6379/7"  # noqa: F405
CACHES["default"]["KEY_PREFIX"] = f"lwv-{RUN}"  # noqa: F405
CACHES["pagecache"]["LOCATION"] = f"/tmp/lwv-pagecache-{RUN}"  # noqa: F405

# Database search backend so no shared Elasticsearch index is touched.
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Cookies are not port-scoped; distinct names keep the dev session intact.
SESSION_COOKIE_NAME = f"lwv_sessionid_{RUN}"
CSRF_COOKIE_NAME = f"lwv_csrftoken_{RUN}"

WAGTAILADMIN_BASE_URL = f"http://wwwdev:{os.environ['LWV_PORT']}"
