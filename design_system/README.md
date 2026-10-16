# Design system

The source of the UChicago Library Design System (UCLD): its SCSS, the
stylesheets compiled from it, and its documentation, served at `/design/`.

Bootstrap 5. The rest of this site's SCSS is still Bootstrap 3, compiled by
django-compressor with libsass; the two cannot share a page.

How this app works is documented in its own pages, under
[Methodology](https://www.lib.uchicago.edu/design/methodology/): locally,
`content/methodology/`. Start with `architecture.md`.

## Build

- **Styles:** edit `scss/`, then run `npm run build:design-system` and commit
  everything it changes. Production deploys run no Node, so the compiled files
  are committed, and CI fails if they are stale. `npm run build` runs it too.
  `npm run watch:design-system` recompiles the CSS on every save, but does not
  regenerate `data/tokens.json`, so run the full build before committing.
- **Documentation:** add or edit Markdown in `content/`. A page is listed,
  linked and published to `/design/llms.txt` without any other edit.
- **Checks:** `./manage.py test design_system`.

## Traps

- In `main.scss`, `pkg:bootstrap/scss/functions` must be imported before
  `_variables.scss`. An unresolved Sass function does not error, it degrades
  to a literal string, so the order is load-bearing.
- `scss/meta/` is imported from `meta.scss` and never from `main.scss`.
  Styling that exists only to document the system belongs there.
- Write transitions as `@include transition(...)`, never a bare `transition:`.
  The mixin is what honours `prefers-reduced-motion`.
- `scripts/tokens.js` reads the SCSS itself, and builds the Token Tables from:
  - **The comment markers** in `_variables.scss`: `// === Tab ===`,
    `// == Section ==`, `//!` guidance and `///` notes. The header of that file
    documents them. Stylelint's comment rules are turned off for `scss/` so
    they survive.
  - **`main.scss` as the entry point.** Component classes are documented from
    the partials it imports.
  - **No `!default` on a `$ucl-*` token, and no reassignment downstream.** See
    the Auto-Exposure Constraint note in `_variables.scss`; the token build
    fails if the published `--ucl-*` values disagree with the compiled Sass.
- A page body in `content/` runs as a Django template, so review a change to a
  `.md` file as you would a template.

## Public URLs

Other systems load these directly, with no version to pin. Do not move or
rename them, and do not remove a class, token or custom property they may use.

| URL | Used by |
| --- | --- |
| `/static/design_system/css/main.css` | Projects that control their own `<head>`, such as Day Pass |
| `/static/design_system/css/main-libapps.css` | LibGuides (Look & Feel → Custom JS/CSS) |
| `/static/design_system/css/meta.css` | The playground, for annotations. Never loaded by a product |
| `/static/design_system/js/bootstrap.bundle.min.js` | Alongside either stylesheet |
| `/design/llms.txt`, `/design/tokens.json`, `/design/**.md` | Agents reading the docs. Excluded from Turnstile in `TURNSTILE_EXCLUDED_PATHS`; the HTML pages are not |

Mockups and experiments live in the separate
[playground](https://github.com/uchicago-library/ucld) repository, which loads
these stylesheets by URL.
