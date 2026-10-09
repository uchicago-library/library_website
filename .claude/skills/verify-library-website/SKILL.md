---
name: verify-library-website
description: >-
  Launch a throwaway Docker copy of the library website (Wagtail public site
  and the Loop intranet), sign in, drive pages in headless Chrome, and keep
  screenshots, ARIA snapshots, and logs as proof. Use when you need to show
  that a change works in the running site, not only in unit tests.
---

# Verify the library website

This skill runs its own copy of the site from this checkout, with the dev fixture `base/fixtures/test.json` loaded. It never reuses or touches a developer's `docker compose` stack. All commands below run from the repo root and use this shorthand:

```bash
V=.claude/skills/verify-library-website/scripts/verify-site.sh
```

The feature map in [`features/README.md`](features/README.md) has one recipe per user-facing feature. Read it before you drive anything.

## What runs where

- The public site is the Wagtail site `wwwdev` and Loop (the intranet) is the Wagtail site `loopdev`. Both sites are served by the same Django process. Wagtail picks the site from the `Host` header, so each site needs its own host name.
- The helper serves both sites on `127.0.0.1:$VERIFY_HTTP_PORT` (default `18000`). It points `wwwdev` and `loopdev` at `127.0.0.1` inside its own curl and Chrome calls, so you do not need `/etc/hosts` entries.
- [`compose.yml`](compose.yml) in this folder defines `web`, `db` (Postgres 15), and `redis`. Only `web` publishes a host port, and only on `127.0.0.1`. Postgres and Redis publish nothing, so the stack does not collide with a dev stack on 5432 or 6379. Elasticsearch does not run, because the dev settings use Wagtail's database search backend.
- The Compose project name is `$VERIFY_PROJECT` (default `lw-verify`). Every container and volume carries the label `verify-library-website=true`. `up` and `down` refuse a project that holds unlabeled resources.
- `web` bind-mounts this checkout at `/app` and runs `manage.py runserver`, so it serves your working tree and reloads on edits. The wagtail-cache page cache goes to a tmpfs, not to the checkout's `cache/` folder.

To run two copies side by side, give each one its own `VERIFY_PROJECT` and `VERIFY_HTTP_PORT`. Never drive a stack that this skill did not start. A developer's own stack from `docker-setup.sh` uses port 8000, its own database, and real session data.

## Launch

```bash
export VERIFY_EVIDENCE_DIR=/path/outside/the/repo/evidence   # where proof goes
$V up
```

`up` does the following, in order:

1. It refuses to start if `VERIFY_HTTP_PORT` is taken by anything outside the project.
2. It builds the image from the repo `Dockerfile` with `ELASTICSEARCH=false NODEJS=false`.
3. It starts `db` and `redis`, waits for `pg_isready`, starts `web`, and runs `migrate`.
4. On a new database it runs `loaddata base/fixtures/test.json` and `update_index`, as `docker-setup.sh` does. This step takes about five minutes. When the fixture is already loaded, `up` skips it.
5. It deletes the default `localhost` site, sets both fixture sites to `VERIFY_HTTP_PORT`, and gives the four fixture users (`darthvader`, `skywalker`, `jyn`, `zoran`) one random password for this run. `$V creds` prints it.
6. It copies `base/fixtures/news-feed-test.json` into the static volume.

The stack is ready when `up` prints `Ready.` and the two site URLs. That line appears only after `http://wwwdev:$VERIFY_HTTP_PORT/` answers with a 2xx status.

If `VERIFY_EVIDENCE_DIR` is unset, evidence goes to `${TMPDIR:-/tmp}/verify-library-website/$VERIFY_PROJECT/evidence`. Keep evidence outside the repo so it never lands in a commit.

## Doctor

Run the doctor first, and again whenever a page looks wrong:

```bash
$V doctor | tee "$VERIFY_EVIDENCE_DIR/doctor.txt"
```

It is read-only. It prints the checkout path, the git revision, and the count of uncommitted files. Then it prints one `PASS` or `FAIL` line per check and exits non-zero if any check fails. The checks are:

- The Docker daemon answers, and the project's resources carry the skill label.
- `web`, `db`, and `redis` are running.
- `web` mounts this checkout at `/app` and publishes `127.0.0.1:$VERIFY_HTTP_PORT`.
- The image matches the current `Dockerfile`, requirements files, and `compose.yml`. If not, rerun `$V up`.
- Both fixture sites use port `$VERIFY_HTTP_PORT`.
- `/` on the public site has the title `The University of Chicago Library`.
- An anonymous request for Loop `/` redirects to `https://www.lib.uchicago.edu/no-permission/`. This redirect proves that Loop routing and its permission hook work.
- `darthvader` can log in with this run's password.

A failure on the first four checks means that this is not your stack, or that it is down. Run `$V up` again. Do not drive it.

## Drive

Use `browse` for anything a user does in a browser. It runs headless Chrome through `playwright-core`. On first use, it installs `playwright-core` into the tools directory (`${XDG_CACHE_HOME:-$HOME/.cache}/verify-library-website`). It uses the first `google-chrome`, `chromium`, or `chromium-browser` on `PATH`. Set `VERIFY_CHROME` to choose a binary.

```bash
$V browse [--site public|loop] [--out NAME] [--user NAME] [--fresh] STEP...
```

| Step | Effect |
| --- | --- |
| `goto PATH` | Open `PATH` on the chosen site, or a full URL. |
| `login` | Sign in through `/admin/login/` as `--user` (default `darthvader`), then return to the last local page. |
| `click ROLE NAME` | Click the element with ARIA role `ROLE` and accessible name `NAME`. |
| `fill LABEL VALUE` | Type into the field whose label, accessible name, or placeholder is `LABEL`. |
| `press KEY` | Press a key, for example `Enter`. |
| `expect TEXT` | Fail unless `TEXT` is visible. |
| `expect-url TEXT` | Fail unless the current URL contains `TEXT`. |
| `shot NAME` | Save `NAME.png`, a full-page screenshot. |
| `aria NAME` | Save `NAME.aria.yml`, the ARIA snapshot of `<body>`. |
| `html NAME` | Save `NAME.html`. |

Steps run in order and stop at the first failure. A failed step saves `FAILED-stepN.png` and makes `browse` exit with code 1. Each step appends one line to `$VERIFY_EVIDENCE_DIR/<out>/actions.log` with the time, site, step, HTTP status, URL, and page title.

Cookies persist between `browse` calls in the run's state directory. A session is per host, so log in once with `--site public` and once with `--site loop`. `--fresh` starts an anonymous browser. When it exits, it replaces only the saved cookies for its own site.

Find handles in an ARIA snapshot (`aria NAME`), not in templates. Prefer roles and accessible names (`click button "Find"`, `fill "Search Loop" ...`) over CSS.

For plain HTTP checks, use `$V curl SITE PATH [CURL_ARGS...]`. For server-side state, use `$V manage shell -c "..."`. Example:

```bash
$V curl loop / -o /dev/null -w '%{http_code} %{redirect_url}\n'
$V manage shell -c "from wagtail.models import Page; print(Page.objects.get(id=1755).title)"
```

### Logging in to Loop

Every Loop page sits under page 6, and `PERMISSIONS_MAPPING` in `library_website/settings/base.py` limits that tree to members of the `Library` group. A request without a local session, or from a user outside that group, is redirected to the live `https://www.lib.uchicago.edu/no-permission/` page. On the live site, Turnstile then shows "Site Protection - Verification Required". When you see that page, the local Loop login failed. It is not an outage. Fix it by logging in to local Loop:

```bash
$V browse --site loop --out loop-intranet goto / login expect-url loopdev
```

All four fixture users are in `Library`. `browse` prints a warning whenever a `goto` passes through the no-permission URL.

## Evidence

Everything goes under `$VERIFY_EVIDENCE_DIR`, one subfolder per feature ID from the map (`--out <feature-id>`):

- `<feature-id>/actions.log`: one line per browser action, with the resulting URL, status, and title.
- `<feature-id>/*.png` and `*.aria.yml`: the page after each key action. Take them at the action that proves the behavior, not only at the end.
- `<feature-id>/*.txt`: what you redirect there yourself. Save `curl` output and `manage shell` reads of database state, for example `> "$VERIFY_EVIDENCE_DIR/admin-publish/db-after.txt"`.
- `doctor.txt`: doctor output from the start of the run.
- `web-<timestamp>.log`: `runserver` output and `/var/log/django-errors.log`. `$V logs` writes one, and so does `$V down`.

Proof standards:

- Drive the real user path: the form, link, or button a user would use. Do not call views, set model fields, or hit test-only endpoints to make a page show the result.
- Capture the action and the resulting state. A screenshot of the final page alone is not proof.
- Check side effects alongside what is visible. After a publish, read the page title and revision from the database. After a login, read `last_login`.
- External services (directory, LibCal, FOLIO, MarkLogic) are not reachable or not configured here. Report the pages that depend on them as unverified. Do not mock them.
- Record which entry point you used. A feature with three entry points in the map is not verified through one of them.

## Cleanup

```bash
$V down
```

`down` saves the web logs into the evidence directory first. It then runs `docker compose -p $VERIFY_PROJECT -f compose.yml down -v --remove-orphans` on the skill's own project only, and deletes the run's state directory (password and browser cookies). It refuses to run if the project contains anything without the skill label. It keeps `$VERIFY_EVIDENCE_DIR`, the tools directory, and the built image (`$VERIFY_PROJECT-web`), which makes the next build fast.

Run `down` after every run, including failed ones. Never use `./docker-cleanup.sh`, `docker compose down -v` without `-p $VERIFY_PROJECT -f compose.yml`, `docker system prune`, `docker volume prune`, `docker network prune`, or `pkill` by process name. Those commands reach a developer's stack and database.

After `down`, confirm that the proof survived: `ls -R "$VERIFY_EVIDENCE_DIR"`.

## Helpers

All helpers live in `scripts/` and are executable.

- `scripts/verify-site.sh` has the subcommands `up`, `doctor`, `url SITE [PATH]`, `curl SITE PATH [ARGS]`, `browse ...`, `manage ARGS`, `logs`, `creds`, `down`, and `tools`. Run it with no arguments for usage and the current values of every `VERIFY_*` variable.
- `scripts/browse.cjs` is the browser driver behind `$V browse`. Run it through `verify-site.sh`, which sets `NODE_PATH` and the environment it reads.

| Variable | Default | Purpose |
| --- | --- | --- |
| `VERIFY_PROJECT` | `lw-verify` | Compose project name. |
| `VERIFY_HTTP_PORT` | `18000` | Host port on `127.0.0.1`. |
| `VERIFY_EVIDENCE_DIR` | `${TMPDIR:-/tmp}/verify-library-website/<project>/evidence` | Proof artifacts. `down` keeps this directory. |
| `VERIFY_STATE_DIR` | `${TMPDIR:-/tmp}/verify-library-website/<project>/state` | Password, cookies, and build fingerprint. `down` deletes this directory. |
| `VERIFY_TOOLS_DIR` | `${XDG_CACHE_HOME:-$HOME/.cache}/verify-library-website` | The `playwright-core` install. |
| `VERIFY_CHROME` | first Chrome or Chromium on `PATH` | Browser binary. |

## Gotchas

- Secrets are optional. Without `library_website/settings/secrets.py`, `compose.yml` passes empty `DIRECTORY_USERNAME`, `DIRECTORY_PASSWORD`, `MARKLOGIC_LDR_USER`, and `MARKLOGIC_LDR_PASSWORD`. With empty values the site runs, but lookups against the campus directory and MarkLogic fail. `staff/test_integration.py` errors without the directory secret. To use real values, export them before `$V up`. If the checkout has `secrets.py`, the container uses it through the bind mount.
- Some pages call external services while they render. In this stack, `/about/news-events/events/` returned 500 after about two minutes, `/switchboard/` returned 500 on a direct GET, and `/mailaliases/` shows "We're having a problem with our systems". Do not treat those results as regressions from your change unless they also fail on `master`.
- Some templates load third-party scripts with protocol-relative URLs (`//ajax.googleapis.com/...`). On the local `http://` site, those URLs use plain HTTP. `browse` fetches them over HTTPS, as production does, because some networks block outbound port 80. A blocked script holds up `DOMContentLoaded`. Plain `curl` is not affected.
- Anonymous GETs can come from the page cache. Look for the `X-Wagtail-Cache: hit` response header. After an admin change, run `$V manage clear_wagtail_cache` before you trust an anonymous view.
- `manage.py` prints the warning `staticfiles.W004` because `library_website/static` does not exist in a fresh clone. The warning does not affect the site.
- Fixture images point at files under `media/` that a fresh clone does not have, so images show as broken. Admin uploads write into the checkout's `media/` folder through the bind mount.
- On some Docker hosts, containers cannot reach each other on a user-defined bridge network because forwarded traffic is dropped. For that reason `compose.yml` puts the services on the default `bridge` network with `links`, and the project creates no network.
- The repo has CI in `.github/workflows/`. `lint.yml` runs black, isort, flake8, eslint, prettier, stylelint, and djhtml. `test.yml` runs `./manage.py test --parallel`. CI checks code, and this skill checks behavior in a running site. This skill does not copy CI's setup. To run unit tests in the verification container, use `$V manage test <app>`. Tests create and destroy their own test database, so the loaded fixture stays as it was.

To keep the feature map in step with the app, use `/maintain-verification-skill`.
