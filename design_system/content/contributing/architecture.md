---
title: "System Architecture"
description: "How the design system is built: the layers it is made of, where every file lives, what the build generates, and what it enforces."
---

## Core Concepts

- **Brand tokens** live in `design_system/scss/_variables.scss` and override Bootstrap's own variables. That file is imported before Bootstrap, so our values win.
- **Elements** (buttons, forms, inputs) are styled with Bootstrap classes first. Add a custom class only when Bootstrap genuinely cannot express the need.
- **Documentation pages** (`design_system/content/`) document the system: its foundations, guidelines and implementation, and this section. They are Markdown files served by the library website at `/design/`, and they hold every rule.
- **HTML pages** (`design_system/templates/design_system/pages/`) are the two kinds of page Markdown cannot express. The tokens page is generated from the stylesheets. The demos show the system in place at full page width: our own patterns, and markup reproduced from a real application so the stylesheets can be validated against the HTML they actually have to style. A documentation page states a rule; the demo shows it working.
- **Mockups** are experiments, and live outside this repository in the [playground](https://github.com/uchicago-library/ucld), which loads the stylesheets the library website publishes.

## The Three Layers of Styling

The system is a Bootstrap 5 build with three separate outputs, each compiled from its own entry point in `design_system/scss/`:

| Entry point | Output | Purpose |
| --- | --- | --- |
| `main.scss` | `main.css` | The product stylesheet. Everything the design system ships. |
| `main-libapps.scss` | `main-libapps.css` | Overrides for Springshare LibApps pages, which load their own Bootstrap at runtime. |
| `meta.scss` | `meta.css` | Styles for these documentation pages only. Never part of the product. |

Sass compiles the whole `design_system/scss` directory, so any `.scss` file at its top level becomes a stylesheet. Files prefixed with an underscore are partials and produce no output of their own.

The distinction that matters most: **`design_system/scss/meta/` is imported from `meta.scss` and never from `main.scss`.** Styling that exists only to document the system belongs there, not in `components/`.

These stylesheets are compiled with Dart Sass from npm. The rest of the library website's SCSS is still Bootstrap 3, compiled at request time by django-compressor with libsass; the two do not share a page.

## Design Tokens

Tokens are SCSS and CSS variables organised into three levels of abstraction, so the whole system can be adjusted from a small number of places.

| Level | Scope | Where it lives |
| --- | --- | --- |
| **1: Core** | Raw brand values | `_variables.scss` |
| **2: Semantic** | Generic roles built from core values | `_variables.scss` |
| **3: Component** | Role-specific values for one component | `components/`, or `_variables.scss` where Bootstrap reads them first |

### Where token documentation lives

The [tokens page](/design/tokens/) is generated from the stylesheets by `design_system/scripts/tokens.js`, so no token value, CSS variable name or utility class is ever transcribed by hand. The same data is published at [/design/tokens.json](/design/tokens.json) for tooling that wants the set directly, with each section's guidance beside the tokens.

The authoring conventions that drive it — the comment markers, the naming rule, and the guidance on when to use an SCSS variable versus a CSS variable — are documented in the header of `design_system/scss/_variables.scss`, because that is the file you are looking at when you need them.

Tokens are listed exhaustively and appear with empty cells if undocumented. Component classes are opt-in and appear only if annotated, since a stylesheet is mostly internal structure.

Three things the generator depends on, which fail quietly if broken:

- **The comment markers survive linting.** Stylelint's comment rules are turned off for `design_system/scss/`, in `.stylelintrc.js`, so the markers are not reformatted away.
- **`main.scss` is the entry point.** Component classes are documented from the partials it imports; a partial it does not import is not documented.
- **No `!default` on a `$ucl-*` token, and no reassignment downstream.** See the Auto-Exposure Constraint note in `_variables.scss`.

## Directory Structure

```text
design_system/                 # A Django app in the library website
├── CLAUDE.md                  # Points agents at this section
├── README.md                  # Points readers of the code at this section
├── content/                   # The Markdown pages
│   ├── index.md               # The /design/ home page
│   ├── foundations/           # What every decision answers to
│   ├── guidelines/            # How to use the system
│   ├── implementation/        # How to build with it
│   └── contributing/          # How to work on it (this folder)
├── data/
│   └── tokens.json            # Generated from the SCSS, committed
├── scripts/
│   └── tokens.js              # Generates data/tokens.json
├── scss/
│   ├── _variables.scss        # Level 1 and 2 tokens, Bootstrap overrides
│   ├── main.scss              # Product entry point
│   ├── main-libapps.scss      # LibApps entry point
│   ├── meta.scss              # Documentation entry point
│   ├── base/                  # Global element styles
│   ├── components/            # One file per component
│   └── meta/                  # Documentation-only styles, never shipped
├── static/design_system/      # Published at /static/design_system/
│   ├── css/                   # Compiled stylesheets, committed
│   └── js/                    # Bootstrap's bundle and the docs scripts
├── templates/design_system/
│   ├── base.html              # Layout for every page
│   ├── page.html              # A Markdown page, and a folder's listing
│   ├── 404.html               # Any missing page under /design/
│   ├── includes/              # Header, footer, breadcrumb, page list
│   └── pages/                 # The HTML pages
│       ├── tokens.html        # /design/tokens/
│       └── demos/             # /design/demos/ and each demo
├── urls.py                    # Every route under /design/
├── views.py                   # Renders both kinds of page, llms.txt and tokens.json
└── tests.py
```

## Page Structure

A documentation page is a Markdown file in `content/`. Its URL follows its path: `content/guidelines/color.md` is `/design/guidelines/color/`, and a folder's `index.md` is the folder's own page, so `content/guidelines/index.md` is `/design/guidelines/`. The front matter supplies the title and the lead paragraph, and the layout supplies the document head, header, breadcrumb, prose column and footer.

```text
---
title: "Page Title"
description: "Renders as the lead paragraph and the meta description."
---
```

One optional key, `order`, sorts a page or a folder ahead of its siblings, which otherwise sort by title. The top-level folders use it to set their order in listings and in the breadcrumb menu.

The body is plain Markdown, with no template syntax run in it, so the Markdown an agent reads is exactly the file.

### HTML pages

The tokens page and the demos are templates in `templates/design_system/pages/`, each with its own route in `urls.py`. Each demo is listed in `DEMOS` in `views.py`, which gives its title and description to its breadcrumb and to the demos index. A template extends `design_system/page.html` and overrides its `body` block, or extends `design_system/base.html` when it needs to escape the prose column. The database finder is the exception: it reproduces a LibGuides page whole, so it is a complete document of its own.

### The header

`includes/docs-header.html` is the header of every page, the demos included: it is built from the production header's classes, so it shows that component in place. Its links are written out rather than generated, since they change about once a year. Its own styling comes from `scss/meta/_docs-header.scss`, following the rule that anything existing only to document the system stays out of the product.

The database finder demo is the exception. It reproduces a LibGuides page whole, so it carries a static copy of the header LibGuides shows.

## What Is Generated

None of this needs a manual step. Adding a file is enough.

- **Listings and breadcrumbs.** Every folder lists its pages, nesting each subfolder under its landing page, and breadcrumbs follow the URL. The header's links, the demos index and the short lists on the home page and the entry points are the only hand-picked links.
- **The tokens page** and `/design/tokens.json`, from `data/tokens.json`.
- **Bootstrap's JavaScript** at `/static/design_system/js/bootstrap.bundle.min.js`, copied from the same installed package the CSS is compiled from, so the two cannot drift to different Bootstrap versions.
- **`/design/llms.txt`**, a discovery index for agents building against this design system, listing every Markdown page by its source. Its introduction is the `llms` key in the front matter of `content/implementation/index.md`. The HTML pages are left out: what they show is in `tokens.json` and the prose.
- **The Markdown source of every page**, at its URL with the trailing slash swapped for `.md`: `/design/guidelines/color.md`, and `/design/foundations.md` for a folder. The home page's is `/design/index.md`. It is the file, served as written.

None of the documentation is meant for search engines. Every page and file is served with `noindex`, as a meta tag on HTML and an `X-Robots-Tag` header on everything else. `llms.txt`, `tokens.json` and the `.md` files are exempt from the site's Turnstile bot check so agents can read them; the HTML pages are not.

A missing page gets the design system's own 404, with no navigation, rather than the library website's.

Because `/design/llms.txt` publishes the `description` front matter, every page needs a real one-line summary rather than a placeholder.

## What Is Enforced

These checks fail rather than publish something wrong:

1. **Unresolved Sass functions** in `_variables.scss`. An unknown function does not error in Sass — it degrades to a literal string — so the token generator asserts that every value resolved.
2. **Token exposure disagreement.** Every `$ucl-*` colour is published as a `--ucl-*` custom property. If the published variable and the compiled Sass value disagree, the token generator stops. See the Auto-Exposure Constraint note in `_variables.scss`.
3. **Stale build output.** CI rebuilds the stylesheets and `tokens.json` and fails if the committed copies differ.
4. **Broken pages.** The test suite renders every page, Markdown and HTML, and fails on an error or a broken `/design/` link.

## Deployment

The pages and stylesheets deploy with the library website. Production servers run no Node, so the compiled stylesheets, the Bootstrap bundle and `tokens.json` are committed alongside the SCSS, as the webpack bundles are. Changes reach `/design/` and every stylesheet consumer when the website is next deployed. The pages skip the site's page cache (wagtail-cache), so a deploy shows at once, and an edit shows on reload in development.

## Next Steps

- **[Coding conventions and the definition of done](/design/contributing/conventions/)**
- **[Setup and installation](/design/contributing/setup/)**
