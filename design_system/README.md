# Design system

The source of the UChicago Library Design System (UCLD): its SCSS, the
stylesheets compiled from it, and its documentation, served at `/design/`.

Bootstrap 5. The rest of this site's SCSS is still Bootstrap 3, compiled by
django-compressor with libsass; the two cannot share a page.

The full documentation of how this app works is in its own pages, under
[Methodology](https://www.lib.uchicago.edu/design/methodology/) — locally,
`content/methodology/`. Start with `architecture.md`.

## Day to day

- **Styles:** edit `scss/`, then run `npm run build:design-system` and commit
  everything it changes. `npm run watch:design-system` recompiles the CSS on
  every save while you work, but does not regenerate `tokens.json`, so run the
  full build before committing. `npm run build` runs it too.
- **Documentation:** add or edit Markdown in `content/`. Nothing else needs
  updating.
- **Checks:** `./manage.py test design_system`. CI also fails if the compiled
  files are stale.

## What this app does

| Feature | How it works | Where it lives |
| --- | --- | --- |
| **Stylesheets** | Dart Sass compiles `main.css`, `main-libapps.css` and `meta.css`. They are committed because production deploys run no Node. | `scss/`, `static/design_system/css/`, `package.json` scripts |
| **Page generation** | Each `.md` file in `content/` is a page at the matching URL under `/design/`. Front matter sets the title, description, `order` and an optional `template` for pages whose markup is too rich for Markdown. Bodies render as a Django template, then as Markdown, so they can include live demos. | `content/`, `views.py`, `templates/design_system/page.html` |
| **Navigation** | Folders list their own pages, the header lists the top-level folders, and breadcrumbs follow the URL. None of it is maintained by hand. | `views.py` (`children`, `breadcrumbs`) |
| **Token Tables** | `scripts/tokens.js` runs Sass over `_variables.scss` and the component partials, reading values, CSS variables, utility classes and the annotation comments, and writes `data/tokens.json`. The page renders that file. | `scripts/tokens.js`, `data/tokens.json`, `pages/token-tables.html` |
| **Agent endpoints** | `/design/llms.txt` indexes every page, each page's Markdown is at its path plus `.md`, and `/design/tokens.json` publishes every token and class. These three are excluded from the site's Turnstile bot check so coding agents can discover and read them; the HTML pages are not. | `views.py`, `urls.py`, `TURNSTILE_EXCLUDED_PATHS` in `library_website/settings/base.py` |
| **Annotations** | An overlay of notes on demo pages, authored as `<template class="ds-annotations-template">` blocks. | `static/design_system/js/annotations.js`, `content/methodology/annotations.md` |
| **Demos** | Full-page renderings, including reproductions of Springshare's LibGuides markup for testing `main-libapps.css`. | `templates/design_system/demos/`, `templates/design_system/libapps/` |
| **Not for search engines** | Every response is `noindex`, by meta tag on HTML and `X-Robots-Tag` on everything else. There is deliberately no `robots.txt` rule, which agents fetching on someone's behalf would also obey. | `views.py` (`noindex`), `templates/design_system/base.html` |

## What the token docs depend on

`scripts/tokens.js` reads the SCSS itself. Keep:

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
| `/design/llms.txt`, `/design/tokens.json`, `/design/**.md` | Agents reading the docs |

Mockups and experiments live in the separate
[playground](https://github.com/uchicago-library/ucld) repository, which loads
these stylesheets by URL.
