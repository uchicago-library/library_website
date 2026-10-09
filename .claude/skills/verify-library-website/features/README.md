# Library website verification map

This directory is the maintained source for verifying the user-facing behavior of the library website: the public site (`wwwdev`) and the Loop intranet (`loopdev`). Read this index before you drive the site, then use the matching feature file as the recipe.

## Baseline preconditions

- Run commands from the repo root with `V=.claude/skills/verify-library-website/scripts/verify-site.sh`.
- Export `VERIFY_EVIDENCE_DIR` to a directory outside the repo.
- Start the stack with `$V up`. The stack loads `base/fixtures/test.json` into its own database.
- Require every check to pass in `$V doctor | tee "$VERIFY_EVIDENCE_DIR/doctor.txt"`.
- The public site is `$V url public` and Loop is `$V url loop`. Both use port `$VERIFY_HTTP_PORT`, default `18000`.
- Fixture users are `darthvader` (superuser), `skywalker`, `jyn`, and `zoran`. All four are in the `Library` group and share the password from `$V creds`.
- Never drive an instance that this run did not start.

## Driving conventions

- Start each recipe from a freshly loaded fixture unless its preconditions say otherwise. Recipes that publish content change the database until `$V down`.
- Use `$V browse --out <feature-id> ...` for browser actions, so each feature's artifacts land in their own folder.
- Use `$V curl` for status codes and redirects, and `$V manage shell -c` for database reads.
- Prefer ARIA roles and accessible names. Every handle in these recipes appears in an `aria` snapshot of the fixture site.
- Treat quoted names as literal. `click` matches a name as a substring, so use the full name.
- Loop needs a local login first. See "Logging in to Loop" in `../SKILL.md`.

## Proof and skip reporting

- Capture the user action and the resulting state. `actions.log` records each step. Add `shot` and `aria` at the step that proves the behavior.
- Mutation proof includes a database read after the change, saved as a `.txt` file in the feature folder.
- Record the feature ID and entry point used with every artifact.
- If a path depends on an unconfigured external service, report it as unverified, with the command you ran and the response you saw.
- Do not report a skipped entry point as verified through a different path.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph that describes the user-visible behavior. It then has exactly four H2 sections, in this order:

1. `Sub-features` lists short IDs, one line per behavior.
2. `How to get to it (user POV)` lists every user entry point.
3. `Driving it with verify-site.sh` starts with `Preconditions:` and pairs each user action with an exact command and an observable result.
4. `Gotchas` lists traps that can waste or invalidate a run.

Keep implementation details out of the map. Name only user paths, stable handles, required state, commands, and observable proof.

## Features

- [Public pages](./public-pages.md) covers the home page, main navigation, and fixture content pages.
- [Loop intranet](./loop-intranet.md) covers the anonymous redirect, local login, and Loop home, departments, groups, and staff pages.
- [Site search](./site-search.md) covers public website search from the home page and its results page, and Loop search, with matches and empty results.
- [Staff directory](./staff-directory.md) covers the public staff list, directory search, departments view, and empty results.
- [Admin edit and publish](./admin-publish.md) covers editing a page in Wagtail admin, publishing it, and seeing the change on the public site.

Not yet mapped: collections and exhibits (`/collex/`), events (`/about/news-events/events/`, which depends on LibCal), the MyLib dashboard, CGIMail forms, and the Wagtail admin outside page editing.
