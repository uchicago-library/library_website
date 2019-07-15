# The University of Chicago Library Website

[2017-2018 Dev Priorities spreadsheet](https://docs.google.com/a/uchicago.edu/spreadsheets/d/1qn6ZDGs08tRcGPFchq75yyU04cNfdmhZ2BM3VvmqmH8/edit?usp=sharing)   *Viewable only to UChicago Staff*

## Running an Instance of the Site
*If you haven't run Vagrant yet, see the 'Setting up for Development' section below.*
1. Start the dev environment from the root of the project directory: `vagrant up`
5. ssh to the guest machine: `vagrant ssh`
6. Activate the virualenv and navigate to the root directory: `source lw/bin/activate && cd /vagrant/`
7. Start the Django dev server: `./manage.py runserver 0.0.0.0:8000`

## Setting up for Development

1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/downloads.html)
2. Clone this repo or fetch the newest code
3. Create a local config file (see example below)
4. Create the dev environment from the root of the project directory: `vagrant up` (this will take awhile)
5. ssh to the guest machine: `vagrant ssh`
6. Activate the virualenv and navigate to the root directory: `source lw/bin/activate && cd /vagrant/`
7. Start the Django dev server: `./manage.py runserver 0.0.0.0:8000`
8. In the Wagtail admin go to: `Settings > Sites` and delete ths site called `localhost`.
9. If you're not a regular contributor to the Library website, you will need to create a superuser by running `./manage.py createsuperuser`. This will allow you access to the admin. If you're a Library developer, however, this was already done for you.

### Local config file example

Create the file `library_website/settings/local.py`. It should look something like this:

```python
import sys

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'TEST': {
                'NAME': ':memory:',
            },
        },
    }
else:
     DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'lib_www_dev',
        }
    }

LOGGING = {
     'version': 1,
     'disable_existing_loggers': False,
     'handlers': {
         'file': {
             'level': 'DEBUG',
             'class': 'logging.FileHandler',
             'formatter': 'default',
             'filename': '/var/log/django-errors.log',
         },
     },
     'loggers': {
         'django.request': {
             'handlers': ['file'],
             'level': 'DEBUG',
             'propagate': True,
         },
     },

    'formatters': {
        'default': {
            'format': '[%(asctime)s] (%(process)d/%(thread)d) %(name)s %(levelname)s: %(message)s'
        }
    }
}

# ** You will also need to add settings for the following. Get these from another developer. ** 

DIRECTORY_USERNAME = #Get from another developer
DIRECTORY_WEB_SERVICE = #Get from another developer
DIRECTORY_PASSWORD = #Get from another developer
OWNCLOUD_PASSWORD = #Get from another developer

```

### Optional (but recommended)
#### Configure etc/hosts
Add the following lines to your `/etc/hosts` file

```bash
127.0.0.1 wwwdev
127.0.0.1 loopdev
```

This will allow you to access the public site at `http://wwwdev:8000` and the intranet at `http://loopdev:8000`.

#### Get development images
These are the images used on pages in the test database on the dev version of the site. Not having these
is fine, however, you will have broken image links if you don't get them.

All you need to do is [download the images from box](https://uchicago.box.com/s/kuib7g0hqhcf18wq51dq10sodfl2mhq0) and put them in `/media/original_images/`.
