# The University of Chicago Library Website

## Workflows and Documentation
- [Developer workflows](https://github.com/uchicago-library/uchicago-library.github.io/blob/master/docs/README.md#developer) (for pull requests and creating branches)
- [ADA Documentation and code](https://github.com/uchicago-library/uchicago-library.github.io/blob/master/docs/code-resources.md#documentation)

## Running an Instance of the Site

### Docker (Recommended)
*Docker is the preferred development environment - it's faster to set up and more consistent across different systems.*

1. **Initial setup**: `./docker-setup.sh`
2. **Start development server**: `docker compose exec web ./manage.py runserver 0.0.0.0:8000`
3. **Access shell**: `docker compose exec web bash`
4. **View help**: `./docker-setup.sh --help`

#### Build without Elasticsearch or NodeJS
Since most development tasks don't require Elasticsearch or NodeJS, you can build faster by skipping them:
```bash
ELASTICSEARCH=false NODEJS=false ./docker-setup.sh
```

#### Docker Commands
- **Start services**: `docker compose up -d`
- **Stop services**: `docker compose down`
- **Complete cleanup**: `./docker-cleanup.sh`
- **View logs**: `docker compose logs -f web`

### Vagrant (Alternative)
*If you prefer Vagrant or need it for specific development tasks.*

1. Start the dev environment from the root of the project directory: `vagrant up`
2. ssh to the guest machine: `vagrant ssh`
3. The following commands run automatically after `vagrant ssh` to activate the virtualenv and move to the working directory: `source lw/bin/activate && cd /vagrant/`
4. Start the Django dev server: `./manage.py runserver 0.0.0.0:8000`

#### Build without Elasticsearch or NodeJS (Vagrant)
```
ELASTICSEARCH=false NODEJS=false vagrant up
```
Note: If you build without Elasticsearch, you will need the following in your `local.py`:
```
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}
```

### Turnstile Configuration
By default, Turnstile (Cloudflare's CAPTCHA service) is disabled in the Vagrant dev environment and CI. 

If you need to test or develop with Turnstile enabled in the Vagrant environment, the recommended approach is:

1. SSH into the Vagrant machine: `vagrant ssh`
2. Set the environment variable for your current session:
```
export TURNSTILE_ENABLED=True
```

Note that this will only affect the current session. When you log out and log back in, `TURNSTILE_ENABLED` will be set back to "False".

### Bot IP Management
The site uses the [Good-Bots package](https://github.com/bbusenius/Good-Bots) to automatically manage IP exclusions for legitimate search engine bots and crawlers. This ensures they aren't blocked by Turnstile protection.

The package generates a `bot_ips_config.py` file with ~1,700 bot IP ranges that gets updated daily via cron. This file is automatically imported in Django settings and excluded from version control.

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

### Docker Setup (Recommended)

1. **Install Docker**: [Get Docker](https://docs.docker.com/get-docker/) for your platform
2. **Clone the repo**: `git clone <repo-url>` or fetch the newest code
3. **Run setup**: `./docker-setup.sh` (this will take a while on first run)
4. **Start development**: `docker compose exec web ./manage.py runserver 0.0.0.0:8000`

The Docker setup automatically:
- Creates and loads the development database
- Sets up all dependencies
- Configures services (PostgreSQL, Redis, optional Elasticsearch)
- Shows development documentation

### Vagrant Setup (Alternative)

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

### Optional (but recommended for both Docker and Vagrant)
#### Configure /etc/hosts
Add the following lines to your `/etc/hosts` file

```bash
127.0.0.1 wwwdev
127.0.0.1 loopdev
```

This will allow you to access the public site at `http://wwwdev:8000` and the intranet at `http://loopdev:8000`. Alternatively, you can access the site at `http://localhost:8000`.

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
- `./manage.py collectstatic`
- `sudo service apache24 restart`

### Caching Issues
If your changes aren't loading into production, try:
- Collectstatic, and restart apache again
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
- `./manage.py collectstatic`
- `sudo service apache24 restart`
