# Design system

The source of the UChicago Library Design System (UCLD): its SCSS, the
stylesheets compiled from it, and its documentation, served at `/design/`.

Bootstrap 5. The rest of this site's SCSS is still Bootstrap 3, compiled by
django-compressor with libsass; the two cannot share a page.

## Editing

- **Styles:** `scss/`. Then run `npm run build:design-system` and commit
  everything it changes: `static/design_system/css/`,
  `static/design_system/js/bootstrap.bundle.min.js` and `data/tokens.json`.
  Production deploys run no Node, so the compiled files must be committed.
  CI fails if they are stale. `npm run watch:design-system` recompiles the CSS
  on every save, but not `tokens.json`.
- **Documentation:** `content/`. One Markdown file per page; its URL follows
  its path. Folders list their own pages, so a new file needs no other edit.
  See [Architecture](https://www.lib.uchicago.edu/design/methodology/architecture/)
  for front matter and templates.
- **Checks:** `./manage.py test design_system` renders every page and fails on
  an error or a broken `/design/` link.

## What the token docs depend on

`scripts/tokens.js` reads the SCSS itself to build the Token Tables. Keep:

- **The comment markers** in `_variables.scss`: `// === Tab ===`,
  `// == Section ==`, `//!` guidance and `///` notes. The header of that file
  documents them. Stylelint's comment rules are turned off for `scss/` so they
  survive.
- **`main.scss` as the entry point.** Component classes are documented from
  the partials it imports.
- **No `!default` on a `$ucl-*` token, and no reassignment downstream.** See
  the Auto-Exposure Constraint note in `_variables.scss`; the token build fails
  if the published `--ucl-*` values disagree with the compiled Sass.

## Traps

- In `main.scss`, `pkg:bootstrap/scss/functions` must be imported before
  `_variables.scss`. An unresolved Sass function does not error, it degrades
  to a literal string, so the order is load-bearing.
- `scss/meta/` is imported from `meta.scss` and never from `main.scss`.
  Styling that exists only to document the system belongs there.
- Write transitions as `@include transition(...)`, never a bare `transition:`.
  The mixin is what honours `prefers-reduced-motion`.

## Public URLs

Other systems load these directly, with no version to pin. Do not move or
rename them, and do not remove a class, token or custom property they may use.

| URL | Used by |
| --- | --- |
| `/static/design_system/css/main.css` | Projects that control their own `<head>`, such as Day Pass |
| `/static/design_system/css/main-libapps.css` | LibGuides (Look & Feel → Custom JS/CSS) |
| `/static/design_system/js/bootstrap.bundle.min.js` | Alongside either stylesheet |
| `/design/`, `/design/llms.txt`, `/design/tokens.json` | People and agents reading the docs |

Mockups and experiments live in the separate
[playground](https://github.com/uchicago-library/ucld) repository, which loads
these stylesheets by URL.
