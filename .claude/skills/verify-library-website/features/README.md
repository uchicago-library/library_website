# library_website verification map

This directory is the maintained source for verifying the user-facing behavior of the library website: the public site, the Loop intranet and the Wagtail admin. Read this index before driving the app, then follow the matching feature file as the recipe.

## Baseline preconditions

- Start an instance with `lwv up`. Never drive the dev server on port 8000 or a run you did not start.
- Run `lwv doctor` and require every line to be `ok`.
- Load the run's URLs with `eval "$(lwv env)"`, which sets `$PUBLIC_URL`, `$LOOP_URL`, `$ADMIN_USER`, `$ADMIN_PASS` and `$ARTIFACTS`.
- Data is the `base/fixtures/test.json` fixture, a Star Trek-themed copy of the real page tree. Page ids and titles cited in these files come from it.
- `lwv` means `.claude/skills/verify-library-website/bin/lwv`, run from the repo root.

## Driving conventions

- Paths like `/borrow/` are on the public host. `loop:/...` means the intranet host.
- Prefer ARIA roles and accessible names (`getByRole`) and Wagtail form ids (`#id_title`). Use `exact: true` for short names like `About` and `Search`, which match several elements.
- For a click that navigates, wrap it as `await Promise.all([page.waitForURL(/expected/), locator.click()])`. `waitForLoadState` resolves immediately on the old page, so you would assert against stale state.
- For a single page, use `lwv browse <path> --shot F --aria F`. For anything with clicks, write a script and run it with `lwv node script.mjs`, importing from `$LWV_LIB/lwv.mjs`.
- Each run has its own database, so mutations do not need restoring. Later recipes in the same run do see earlier mutations, so run mutation recipes last or start a fresh run.
- Anonymous public responses are served from wagtail-cache. After any content change, run `lwv manage clear_wagtail_cache` before you load the page anonymously, or check the `X-Wagtail-Cache` header to tell which response you got.

## Proof and skip reporting

- Capture the user action and the resulting state, not only the final screen.
- UI proof includes an ARIA snapshot and a screenshot (`capture()` or `lwv browse --shot --aria`).
- HTTP proof includes the URL, status, relevant headers and a body excerpt.
- Mutation proof includes a read-only second view: `lwv sql` on the run DB plus an anonymous page load.
- Record the feature id and entry point with every artifact (put them in the artifact name or path).
- Report an unreachable path with the command you tried and the unmet precondition (for example "LibCal unreachable: /json-hours/ 500").
- Do not report a skipped entry point as verified through a different path.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph describing the user-visible behavior. It then has exactly four H2 sections, in this order:

1. `Sub-features` lists short ids, one line per behavior.
2. `How to get to it (user POV)` lists every user entry point.
3. `Driving it with lwv` starts with `Preconditions:` and uses labeled bullets that pair each user action with an exact command and an observable result.
4. `Gotchas` lists traps that can waste or invalidate a verification run.

## Features

- [Public pages and navigation](./public-pages.md): homepage, standard pages, mega-menu, breadcrumbs, alert banner.
- [Website search](./website-search.md): public `/results/` search with match, no-match and empty states.
- [Library directory](./library-directory.md): staff, department and org chart views with search and department filters.
- [Collections & Exhibits](./collex.md): `/collex/` browse views, search, digital/web limits.
- [Loop intranet](./loop-intranet.md): permission gate, intranet home, Loop search.
- [Admin edit and publish](./admin-edit-publish.md): Wagtail login, edit a page, publish, see it live.
