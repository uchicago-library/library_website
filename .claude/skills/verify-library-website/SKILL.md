---
name: verify-library-website
description: Launch and drive an isolated instance of the UChicago Library Wagtail site (public site on wwwdev, Loop intranet on loopdev, Wagtail admin) in headless Chromium to prove a change works in the real app, with screenshots, ARIA snapshots and DB checks as evidence. Use when asked to verify, demo, screenshot or smoke-test a page, view, template, StreamField block or admin flow in library_website, beyond what unit tests show.
---

# Verify library_website

All commands run from the repo root. The helper is `.claude/skills/verify-library-website/bin/lwv`
(below: `lwv`, e.g. `alias lwv=.claude/skills/verify-library-website/bin/lwv`). `lwv help` lists every subcommand.

## What gets launched

`lwv up` starts a one-off container from the compose `web` image, named `lwv-<run>`, running
`manage.py runserver` on the first free port in 8010-8029 (bound to 127.0.0.1). It uses:

- **Its own Postgres database** `lwv_<run>`, cloned from a template `lib_www_verify_tpl` that holds
  `base/fixtures/test.json` (the same data `docker-setup.sh` loads). Building the template takes ~4 minutes
  the first time, then it is reused. It rebuilds automatically when the fixture changes.
- **Settings** `lib/verify_settings.py`, which extends `library_website.settings.docker` with a separate
  Redis DB and key prefix, a page cache under `/tmp` in the container, the database search backend,
  and run-specific session/CSRF cookie names. Cookies are not port-scoped, so the custom names keep
  your dev login on :8000 working.
- **The bind-mounted checkout**, so it serves the code as it is on disk. Runserver's reloader picks up
  Python and template edits (templates use the cached loader, which only resets through the reloader).
  New migrations need `lwv manage migrate`. Webpack bundles need `npm run build` first.
- A superuser `lwv_admin` with a random password, in the `Library` group (needed for Loop). Every Wagtail
  `Site` row gets the run's port, so generated links stay on the instance.

It shares the dev stack's `db` and `redis` containers (starting them if they are down), and also the
`media/` bind mount and the `static_files` volume. It never touches the `web` container, port 8000,
the `lib_www_dev` database, or Elasticsearch. Several runs can be up at once; each command acts on the
most recent run unless you set `LWV_RUN=<id>` (see `lwv list`).

Prerequisites: Docker with the compose image built (`./docker-setup.sh` once), `wwwdev` and `loopdev` resolving
to 127.0.0.1 in the hosts file (`/etc/hosts`, or `C:\Windows\System32\drivers\etc\hosts` on Windows), and
Node.js on the host. On Windows, run `lwv` from Git Bash. The first `lwv browse`/`lwv node` installs
Playwright 1.63.0 into `~/.cache/lw-verify/node`, which needs network access.

Service credentials are environment variables, the same names CI and Cursor Cloud Agent secrets use:
`DIRECTORY_USERNAME`, `DIRECTORY_PASSWORD`, `MARKLOGIC_LDR_USER` and `MARKLOGIC_LDR_PASSWORD`.
`lwv` passes them into the container, and also reads an optional gitignored
`.claude/skills/verify-library-website/.env` (`KEY=value` lines). Missing variables fall back to
`library_website/settings/local.py`, then to blank. With blank values the site still runs, but the
directory and MarkLogic features cannot reach their services; report those as unverified.
`DIRECTORY_WEB_SERVICE`, `MARKLOGIC_LDR_URL` and `SPARQL_ROOT` default to `base.py` and can be
overridden the same way.

## Launch

```bash
lwv up
```

Ready means it prints `RUN=`, `PUBLIC_URL=http://wwwdev:<port>`, `LOOP_URL=http://loopdev:<port>`,
`ADMIN_URL=` and `ARTIFACTS=`. It waits for the public homepage to return 200, which takes about
10 s once the template exists. If the container dies during startup, its log is saved to
`$ARTIFACTS/server.log`. `lwv env` prints the run state again, including `ADMIN_PASS`.

## Doctor

```bash
lwv doctor
```

This check is read-only. It confirms the container is running and belongs to the run, owns the
port, and reports the run's database. It also checks that the public homepage and `/admin/login/`
return 200, that the anonymous Loop root returns 302 to `https://www.lib.uchicago.edu/no-permission/`
(the expected gate), and that the checkout's git revision matches the one at launch. It exits
non-zero on any `FAIL`. Run it after `lwv up`, and again whenever something looks off; it needs a running instance. A `WARN` about the revision means
the checkout changed since launch. Edits are live, but label your evidence with the current revision.

## Drive

Three levels, from cheapest to richest:

1. **HTTP**: `curl -s -D- "$PUBLIC_URL/path"`. Use this for status codes, redirects, JSON endpoints and the
   `X-Wagtail-Cache: hit|miss` header. Get the URLs with `eval "$(lwv env)"`.
2. **One page in a real browser**:
   ```bash
   lwv browse /borrow/ --shot borrow.png --aria borrow.aria.txt
   lwv browse loop:/ --login --shot loop-home.png          # loop: prefix = intranet host
   lwv browse /admin/pages/3007/edit/ --login --shot edit.png --wait "#id_title"
   ```
   It prints JSON with the final URL, HTTP status, title and artifact paths. Relative artifact paths
   go under `$ARTIFACTS`.
3. **Multi-step flows**: write a script in your scratch dir and run it with `lwv node script.mjs`. Import the
   helpers as below. `pathToFileURL` is needed because `import()` rejects Windows paths.
   ```js
   import { pathToFileURL } from "node:url";
   const { launch, url, adminLogin, capture, fullShot, artifact, env } = await import(
     pathToFileURL(process.env.LWV_LIB + "/lwv.mjs")
   );
   ```
   - `url("/x")` gives the public URL and `url("loop:/x")` the intranet URL.
   - `adminLogin(page, { loop })` signs in through the real `/admin/login/` form. Sessions are per host,
     so pass `{ loop: true }` before visiting Loop pages.
   - `capture(page, "name")` writes `name.png` and `name.aria.txt` into `$ARTIFACTS`.
   - A shipped flow, `lib/flows/admin-edit-publish.mjs`, is the model for mutation proofs (see
     `features/admin-edit-publish.md`).

Locate elements by role and accessible name (`getByRole("button", { name: "About", exact: true })`)
or by Wagtail's form ids (`#id_title`). Avoid CSS layout classes. `lwv manage <cmd>` runs manage.py
inside the run's container. `lwv sql "<query>"` queries the run's database.

Some features call external services that are unreachable here: LibCal hours (`/json-hours/` returns 500),
events (`/about/news-events/events/` hangs past 60 s), `/switchboard/` (500), FOLIO/MyLib (needs the SOCKS
tunnel), and LibGuides. Treat those as environment limits and report them as unverified. They are not
regressions unless your change touched them.

## Evidence

Everything goes to `$ARTIFACTS` = `~/.local/state/lw-verify/runs/<run>/artifacts/`, outside the repo.
This directory survives `lwv down`. `lwv down` also saves `server.log` there (runserver output,
including tracebacks).

A proof must:
- Use the real user path: navigate and click as a visitor or editor would. Do not set model fields in
  `lwv manage shell` and then screenshot the result.
- Capture the action and the resulting state: a before capture, the action (for example the admin
  success message), and an after capture. For UI, take an ARIA snapshot plus a screenshot.
- Check side effects with a second, read-only view. After an admin mutation, query `lwv sql` (for
  example `wagtailcore_page.title`, `has_unpublished_changes`, `latest_revision_id`) and load the
  page anonymously.
- Name the feature id and entry point used with each artifact. If an entry point was not reachable,
  report it as skipped with the reason. Do not count it as verified through another path.

## Cleanup

```bash
lwv down            # most recent run; or LWV_RUN=<id> lwv down
lwv list            # confirm it shows "down"
```

`down` saves the server log, stops and removes the `lwv-<run>` container, drops `lwv_<run>` and
deletes the run's Redis keys. It stops `db`/`redis` only if this run started them and nothing else
is using them. It never removes `$ARTIFACTS` or the template DB. To refresh the template, run
`lwv rebuild-template`. Run `lwv down` after failed attempts too. Never `docker compose down` or kill
processes by name to clean up: that hits the user's dev stack.

## Feature map

`features/README.md` indexes the user-facing features and their driving recipes. Read it before
proving a feature, and cover every entry point it lists for that feature.
