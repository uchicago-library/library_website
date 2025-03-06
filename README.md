# The University of Chicago Library Website

## Workflows and Documentation
- [Developer workflows](https://github.com/uchicago-library/uchicago-library.github.io/blob/master/docs/README.md#developer) (for pull requests and creating branches)
- [ADA Documentation and code](https://github.com/uchicago-library/uchicago-library.github.io/blob/master/docs/code-resources.md#documentation)

## Running an Instance of the Site
*If you haven't run Vagrant yet, see the 'Setting up for Development' section below.*
1. Start the dev environment from the root of the project directory: `vagrant up`
2. ssh to the guest machine: `vagrant ssh`
3. The following commands run automatically after `vagrant ssh` to activate the virtualenv and move to the working directory: `source lw/bin/activate && cd /vagrant/`
4. Start the Django dev server: `./manage.py runserver 0.0.0.0:8000`

### Build the site withouth Elasticsearch or NodeJS
Since the majority of development tasks don't require Elasticsearch or NodeJS it is often faster and more desireable to build the site without these things. This can be accomplished by running `vagrant up` with the `ELASTICSEARCH` or `NODEJS` environment variables set to `false`:
```
ELASTICSEARCH=false NODEJS=false vagrant up
```
Note: If you build the site withouth Elasticsearch, you will need the following in your `local.py`:
```
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}
```

### Vagrant Troubleshooting
If you have issues loading your local instance, try:
```
vagrant halt
vagrant destroy
vagrant up
pip install -r requirements.txt
```

## Loop style changes
Loop Sass file compression is separate from the public site compression. If you want to compress new Sass code into an updated CSS file, in a terminal that is not running Vagrant, run 'gulp' in the root directory. This command should start a watch on all Loop Sass files and compress anytime a Sass file is saved.

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

All you need to do is [download the images from box](https://uchicago.box.com/s/kuib7g0hqhcf18wq51dq10sodfl2mhq0), put them in `/media/original_images/`,
and run `./manage.py wagtail_update_image_renditions`.

## Pushing to Production
- ssh to motacilla
- `cd /data/local/ ; source venv/bin/activate ; cd sites/library_website`
- `git remote update`
- `git status`
- `git pull origin master`
- `./manage.py migrate` _only needed if made migrations_
- `./manage.py compress`
- `./manage.py collectstatic`
- `sudo service apache24 restart`

### Caching Issues
If your changes aren't loading into production, try:
- Compress, collectstatic, and restart apache again
- Clear the Wagtail cache in Wagtail settings or run `./manage.py clear_wagtail_cache`
- Clear the Django cache manually
```
./manage.py shell
from django.core.cache import cache
cache.clear()
```

## Pushing a branch to Nest
For testing purposes, you may want to push a branch that is not master to Nest.
- ssh to nest
- `cd /data/local/ ; source venv/bin/activate ; cd sites/library_website`
- `git remote update`
- `git status`
- `git checkout {{ branch-name }}`
- `git pull origin {{ branch-name }}`
- `./manage.py migrate` _only needed if made migrations_
- `./manage.py compress`
- `./manage.py collectstatic`
- `sudo service apache24 restart`
