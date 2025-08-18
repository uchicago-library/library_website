from .base import *

DEBUG = False
TEMPLATE_DEBUG = False

try:
    from .local import *
except ImportError:
    pass

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CSRF_COOKIE_SECURE = True
