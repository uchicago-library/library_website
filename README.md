# The University of Chicago Library Website

## Workflows and Documentation
- [Developer workflows](https://github.com/uchicago-library/uchicago-library.github.io/blob/master/docs/README.md#developer) (for pull requests and creating branches)
- [ADA Documentation and code](https://github.com/uchicago-library/uchicago-library.github.io/blob/master/docs/code-resources.md#documentation)

## Development Setup

### Docker (Recommended)
*Docker is the preferred development environment - it's faster to set up and more consistent across different systems.*

#### Initial Setup:
1. **Install Docker**: [Get Docker](https://docs.docker.com/get-docker/) for your platform
2. **Clone the repo**: `git clone <repo-url>` or fetch the newest code
3. **Set Up Secrets**: `cd /path/to/library_website && make create-repo install` (see Setting Up Secrets Repo section below)
4. **Run setup**: `./docker-setup.sh` (this will take a while on first run)

#### Daily Development:
- **Install Secrets**: `make secrets`
- **Start development server**: `docker compose exec web ./manage.py runserver 0.0.0.0:8000`
- **Access shell**: `docker compose exec web bash`
- **View help**: `./docker-setup.sh --help`

#### Docker Commands:
- **Start services**: `docker compose up -d`
- **Stop services**: `docker compose down`
- **Complete cleanup**: `./docker-cleanup.sh`
- **View logs**: `docker compose logs -f web`

#### Build without Elasticsearch or NodeJS:
Since most development tasks don't require Elasticsearch or NodeJS, you can build faster by skipping them:
```bash
ELASTICSEARCH=false NODEJS=false ./docker-setup.sh
```

The Docker setup automatically:
- Creates and loads the development database
- Sets up all dependencies
- Configures services (PostgreSQL, Redis, optional Elasticsearch)
- Shows development documentation

### Vagrant (Alternative)
*If you prefer Vagrant or need it for specific development tasks.*

#### Initial Setup:
1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/downloads.html)
2. Clone this repo or fetch the newest code
3. Create a local config file: `library_website/settings/local.py` (see Local Configuration File section below)
4. Create the dev environment from the root of the project directory: `vagrant up` (this will take awhile)

#### Daily Development:
1. ssh to the guest machine: `vagrant ssh`
2. The following commands run automatically after `vagrant ssh` to activate the virtualenv and move to the working directory: `source lw/bin/activate && cd /vagrant/`
3. Start the Django dev server: `./manage.py runserver 0.0.0.0:8000`
4. In the Wagtail admin go to: `Settings > Sites` and delete the site called `localhost`.
5. If you're not a regular contributor to the Library website, you will need to create a superuser by running `./manage.py createsuperuser`. This will allow you access to the admin. If you're a Library developer, however, this was already done for you.

#### Build without Elasticsearch or NodeJS:
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

#### Vagrant Troubleshooting:
If you have issues loading your local instance, try:
```
vagrant halt
vagrant destroy
vagrant up
pip install -r requirements.txt
```

### Turnstile Configuration
By default, Turnstile (Cloudflare's CAPTCHA service) is disabled in both Docker and Vagrant dev environments, and CI.

If you need to test or develop with Turnstile enabled in the Vagrant environment, the recommended approach is:

1. SSH into the Vagrant machine: `vagrant ssh`
2. Set the environment variable for your current session:

```
export TURNSTILE_ENABLED=True
```

Note that this will only affect the current session. When you log out and log back in, `TURNSTILE_ENABLED` will be set back to "False".

### Setting Up Secrets Repository

In order to run, the library website requires a file called `./library_website/settings/secrets.py` to exist.  This Python module contains login credentials for several websites and web applications, and therefore is excluded from this public repository by our `.gitignore` file.  `secrets.py` is part of a separate private `git` repository called `lw-config`, which is hosted on `vault.lib.uchicago.edu`.  In this project, we provide a Makefile which will clone that repository down, and install `secrets.py` from the secrets repository into this `library_website` repository, in the place where the Wagtail application will expect it to be.

To clone the secrets repository to your machine, you can use our makefile:

```
$ cd /path/to/library_website && make create-repo
```

These make rules require `git` to be installed.

Some observations:

- you will need to obtain permission from our sysadmins to clone repositories owned by the `wagtail` user on `vault`
- by default, our makefile will assume that `~/lw-config` is the path to the secrets repository both for cloning and for installing the secrets
- it is possible to override this path either using environment variables or using Make variables

Once the repository has been cloned down, run one of the following Make rules from the root of the `library_website` project:

```
$ make install
$ make secrets
```

`make install` copies the `secrets.py` file from the secrets repository over into this repository, setting the permissions on the file to 444 to remind any developer doing Wagtail development to edit the original in the secrets repository rather than this copy.  `make secrets` does the same thing, but before installing `secrets.py` it pulls down the latest changes from the branch that is checked out in the secrets repository on the user's machine.

This will put the `library_website` project in the state it needs to be in to run `docker-setup.sh`.

#### Overriding The Path

If you are running our makefile as part of a script, especially while
provisioning a production environment for the Wagtail site, you will
likely want the secrets repository to live somewhere other than
`~/lw-config`.

Our makefile provides two ways to override the path to the secrets repository.
The first is to pass a Make variable called `SECRETS_REPO_PATH` in
when running every Make rule, e.g.:

```
$ make create-repo SECRETS_REPO_PATH=/data/local/secret-repos
$ make secrets SECRETS_REPO_PATH=/data/local/secret-repos
```

The other way is to customize the `SECRETS_REPO_PATH` environment variable, which only requires exporting it once before running our Make rules:

```
$ export SECRETS_REPO_PATH=/data/local/secret-repos
$ make create-repo
$ make secrets
```

In both of these examples, the makefile will operate under the assumption that the secrets repository is located at `/data/local/secret-repos/lw-config`.

## Bot IP Management
The site uses the [Good-Bots
package](https://github.com/bbusenius/Good-Bots) to automatically
manage IP exclusions for legitimate search engine bots and
crawlers. This ensures they aren't blocked by Turnstile protection.

The package generates a `bot_ips_config.py` file with ~1,700 bot IP ranges that gets updated daily via cron. This file is automatically imported in Django settings and excluded from version control.

## SCSS/CSS Compilation
Both the public site and Loop (intranet) use Django Compressor with django-libsass for SCSS compilation. SCSS files are automatically compiled when templates are rendered. Edit the `.scss` source files in `base/static/base/css/` and `base/static/base/css/loop/` - do not edit the compiled `.css` files directly.

## Optional Configuration

### Configure /etc/hosts
Add the following lines to your `/etc/hosts` file

```bash
127.0.0.1 wwwdev
127.0.0.1 loopdev
```

This will allow you to access the public site at `http://wwwdev:8000` and the intranet at `http://loopdev:8000`. Alternatively, you can access the site at `http://localhost:8000`.

### Get Development Images
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
