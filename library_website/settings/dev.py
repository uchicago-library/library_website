from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z%4u$f(8jjkp@qqd$4g+w_xrbco3xbakg9=abrb*1ic7g@o*xc'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

try:
    from .local import *
except ImportError:
    pass
