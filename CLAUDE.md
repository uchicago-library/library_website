# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup

**Docker (Recommended)**
- **Initial setup**: `./docker-setup.sh` - Builds containers, runs migrations, loads test data
- **Start services**: `docker compose up -d` - Start all services in background
- **Stop services**: `docker compose down` - Stop all services
- **Access shell**: `docker compose exec web bash` - SSH into web container (virtualenv activation and cd to /app happen automatically)
- **Run Django commands**: `docker compose exec web ./manage.py <command>` - Execute Django management commands
- **View logs**: `docker compose logs -f web` - Follow web container logs
- **Complete cleanup**: `./docker-cleanup.sh` - Remove all containers, volumes, and images
- **Skip Elasticsearch/NodeJS**: `ELASTICSEARCH=false NODEJS=false ./docker-setup.sh` - Faster startup for most development
- **Help**: `./docker-setup.sh --help` - Show development documentation and commands
- **Settings**: Uses `library_website/settings/docker.py` which handles database/Redis configuration automatically

**Vagrant (Alternative)**
- **Start environment**: `vagrant up` - Start the development environment
- **Access shell**: `vagrant ssh` - SSH into the VM (virtualenv activation and cd to /vagrant/ happen automatically via .bashrc)
- **Skip Elasticsearch/NodeJS**: `ELASTICSEARCH=false NODEJS=false vagrant up` - Faster startup
- **Settings**: Requires `library_website/settings/local.py` with database configuration

### Django Management
**Note**: When using Docker, prefix all commands with `docker compose exec web`
- **Start development server**: `./manage.py runserver 0.0.0.0:8000`
- **Database migrations**: `./manage.py migrate`
- **Create superuser**: `./manage.py createsuperuser`
- **Collect static files**: `./manage.py collectstatic`
- **Clear Wagtail cache**: `./manage.py clear_wagtail_cache`
- **Update image renditions**: `./manage.py wagtail_update_image_renditions`

### Frontend Build Tools
- **JavaScript bundling**: `npm run build` (webpack production build)
- **JavaScript watch mode**: `npm run watch` (webpack with file watching)

### Testing
- **Run all tests**: `./manage.py test --parallel` (this is what CI runs; under Docker, prefix with `docker compose exec web`)
- **Run a single app**: `./manage.py test <app>` (e.g., `./manage.py test lib_news`)
- Tests use an **in-memory SQLite** database and the **database search backend** (gated by `if "test" in sys.argv` in the settings), so **no Elasticsearch or Redis** needs to be running

### Code Style & Linting
CI (`.github/workflows/lint.yml`) gates every PR on these — run them before pushing (tools are in `requirements-dev.txt`):
- **Python**: `black .`, `isort .`, `flake8 .` (line length 88, isort uses the black profile — see `.flake8` and `pyproject.toml`)
- **JavaScript**: `npx eslint . --ext .js`, `npx prettier --check "**/*.js"`
- **SCSS/CSS**: `npx stylelint "**/*.{css,scss}"`, `npx prettier --check "**/*.{css,scss}"`
- **Django templates**: `djhtml` (2-space indent; CI runs `djhtml --check`)

**Running CI locally (optional):** With Docker and the [`act`](https://github.com/nektos/act) `gh` extension, you can run the CI jobs locally for exact parity: `gh act -j python-lint`, `-j javascript-lint`, `-j scss-lint`, `-j template-lint`, `-j test`. The lint jobs need no secrets. The `test` job reads the values wired to `${{ secrets.* }}` in `test.yml` — `DIRECTORY_USERNAME`, `DIRECTORY_PASSWORD`, `MARKLOGIC_LDR_USER`, `MARKLOGIC_LDR_PASSWORD`, and `GITHUB` — so supply them to `act` via a secrets file (`--secret-file`) or `-s KEY=VALUE`.

## Code Architecture

### Framework & Core Technology
- **Wagtail/Django CMS**: Wagtail 7.0.7 on Django 5.2 (see requirements.txt for the full pin list)
- **Python version**: Python 3.11 (defined in the Dockerfile and Vagrantfile)
- **Database**: PostgreSQL (dev and production); in-memory SQLite (tests)
- **Frontend**: React components with Webpack bundling, SCSS for styling
- **Caching**: wagtail-cache stores rendered pages in a file-based `pagecache` backend; the `default` cache is Redis (django-redis). Clear cached pages with `./manage.py clear_wagtail_cache`

### App Structure
The project follows Django's modular app structure with the following key apps:

**Content Management Apps:**
- `base` - Core models, shared functionality, and base page types
- `home` - Homepage-specific functionality
- `public` - Public-facing content and utilities
- `news` - News management system
- `lib_news` - Library-specific news features
- `events` - Event management
- `alerts` - Site-wide alert system
- `reusable_content` - Reusable content snippets shared across pages
- `icon_list_boxes` - Reusable icon list StreamField blocks
- `redirects` - Redirect page types (public site and intranet)
- `cgimail_editor` - CGIMail form editor pages
- `projects` - Project pages and index
- `site_settings` - Site-wide settings (hours, contact info, quick numbers, news feeds)

**Library-Specific Apps:**
- `staff` - Staff directory and profiles
- `units` - Organizational unit management  
- `lib_collections` - Digital collections and exhibits
- `ask_a_librarian` - Help desk functionality
- `conferences` - Conference management
- `subjects` - Subject guide management
- `findingaids` - Finding aids functionality
- `mylib_dashboard` - Consolidated patron account dashboard (MyLib)
- `searchable_content` - External content (e.g., LibGuides) indexed for search
- `item_servlet` - Catalog item holdings/availability data endpoint

**Administrative Apps:**
- `group` - Group/committee management for intranet
- `intranetforms` - Internal forms system
- `intranethome` - Intranet homepage
- `intranetunits` - Intranet unit pages
- `intranettocs` - Intranet table of contents
- `dirbrowse` - Directory browsing functionality

### Page Types
Wagtail page models inherit from an abstract base in `base/models.py`:
- `BasePage` — abstract root for all page types; used directly by intranet pages and some public pages (e.g., units)
- `PublicBasePage(BasePage)` — extends `BasePage` with public-site fields; the usual base for public-facing content pages

When adding a page type, follow the base class used by existing pages in the same app.

### Configuration
- **Settings**: Located in `library_website/settings/` with base.py, dev.py, docker.py, production.py
- **Docker config**: Uses `library_website/settings/docker.py` (automatically configured via docker-compose.yml)
- **Vagrant config**: Create `library_website/settings/local.py` for Vagrant development settings
- **URLs**: Main URL configuration in `library_website/urls.py`

### Key Features
- **Wagtail CMS**: Content management through Wagtail admin interface
- **Shibboleth**: Authentication integration for university systems
- **Elasticsearch**: Search functionality (optional in development)
- **Turnstile**: CAPTCHA protection (Cloudflare)
- **Good-Bots**: Automated bot IP management for search engines
- **Multi-site**: Supports both public website and intranet (loop)

### Development Workflow
- **Local development**:
  - Access public site at `http://wwwdev:8000` or `http://localhost:8000`
  - Access intranet at `http://loopdev:8000`
  - Requires adding `127.0.0.1 wwwdev` and `127.0.0.1 loopdev` to `/etc/hosts` for named hosts
- **Docker vs Vagrant**: Docker is recommended for faster setup and consistency. Vagrant is available for specific use cases.
- **Production deployment**: Manual deployment to motacilla server
- **Staging**: Can deploy branches to nest server for testing
- **Media files**: Development images available from Box link in README

### Management Commands
The project includes numerous Django management commands for:
- Staff data synchronization
- Content reporting and analysis  
- Database maintenance
- News import/export
- Form submission reports
- Page maintenance operations

All commands are in `*/management/commands/` directories within individual apps.
