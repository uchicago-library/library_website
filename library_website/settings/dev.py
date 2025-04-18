from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z%4u$f(8jjkp@qqd$4g+w_xrbco3xbakg9=abrb*1ic7g@o*xc'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Restricted directory locked down to campus by shib
RESTRICTED = 7163

try:
    from .local import *
except ImportError:
    pass

# Specific settings for GitHub Workflow Actions
if 'GITHUB' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'TEST': {
                'NAME': ':memory:',
            },
        },
    }

    COMPRESS_OFFLINE = False
