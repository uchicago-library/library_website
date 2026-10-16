---
title: "Contributing"
order: 4
description: "How this project is built and documented: who reads what, what the system does on its own, and the files it publishes with the systems that load them."
---

## Where Each Reader Starts

Every reader has one entry point, and it must surface what that reader cannot afford to miss — stated there, or linked from it prominently, never left for them to find. When something critical changes for a reader, check that their entry point still surfaces it.

| Reader | Entry point | It must cover |
| --- | --- | --- |
| **Stakeholder** reviewing the system | [Home](/design/) | The goals and priorities; how foundations, guidelines and implementation fit together; the status, the roadmap and the systems using it |
| **Builder**: a designer or developer using the system, in this project or another | [Implementation](/design/implementation/) | The one stylesheet to load and its URL; the standards, writing rules and guidelines to read first; the tokens; the demos and the playground |
| **Contributor** changing the system | This page | How to build and check a change ([Setup](/design/contributing/setup/)); where every file lives ([Architecture](/design/contributing/architecture/)); the conventions and the definition of done ([Conventions](/design/contributing/conventions/)); that consumers load the stylesheet unversioned, so nothing public is renamed or removed |
| **Builder agent** | [/design/llms.txt](/design/llms.txt) | Every Markdown page with its description; the three pages to read before producing any interface; `tokens.json` |
| **Contributor agent** | `design_system/CLAUDE.md`, which loads whenever an agent works in that folder | That these pages are the documentation, and are updated in the same change as the code; the definition of done |

`design_system/README.md`, which GitHub shows when the folder is opened, points readers of the code here.

## What It Does on Its Own

- **Token and class tables from the SCSS.** `scripts/tokens.js` reads comment markers in the stylesheets and builds the [tokens page](/design/tokens/) and `tokens.json`. Stylelint's comment rules are turned off for `scss/` so the markers survive.
- **Pages with no routing to maintain.** A Markdown file in `content/` is a page: its URL follows its path, its front matter gives its title and description, and every folder lists its own pages.
- **Hidden from search engines, open to agents.** No page is indexed, but every page is listed in `llms.txt` and readable as Markdown.
- **Annotations.** Notes laid over the demos, which a reader can show or hide. See [Annotations](/design/contributing/annotations/).
- **One stylesheet per platform**, all compiled from the same tokens.
- **Self-checking.** CI fails if the compiled stylesheets or `tokens.json` are out of date, and the tests render every page and follow every internal link.

How each of these works, where every file lives and what the stack is: [System Architecture](/design/contributing/architecture/).

## Published Files and Who Uses Them

Other systems load these from `https://www.lib.uchicago.edu` directly, with no version to pin. Do not move or rename them, and do not remove a class, token or custom property they may use.

| URL | Load it when | Used by |
| --- | --- | --- |
| `/static/design_system/css/main.css` | The project controls its own `<head>`. The full product stylesheet: Bootstrap with the design system's tokens, components and typeface. | [Day Pass](https://github.com/uchicago-library/daypass#design-system), which could benefit from a leaner build |
| `/static/design_system/css/main-libapps.css` | The page is served by Springshare, which loads its own Bootstrap first. An override sheet, not a full build; see [Styling Springshare Pages](/design/implementation/springshare/). | [LibGuides](https://guides.lib.uchicago.edu/LibGuides), in Look & Feel → Custom JS/CSS |
| `/static/design_system/js/bootstrap.bundle.min.js` | Alongside either stylesheet, for components that need JavaScript: dropdowns, collapse, accordions, modals. | Both of the above |
| `/static/design_system/css/meta.css` | Never, in a product. It styles these pages and the annotations. | These pages, and the [playground](https://github.com/uchicago-library/ucld) for its annotations |
| `/design/llms.txt`, `/design/tokens.json` and `/design/<page>.md` | An agent reads the documentation. These are exempt from the site's Turnstile bot check; the HTML pages are not. | Agents, including the playground's `new-mockup` skill |

Not using it yet: the [main website](https://www.lib.uchicago.edu/), the [Catalog](https://catalog.lib.uchicago.edu/vufind/search), [Book a Room](https://rooms.lib.uchicago.edu/r/search/seats#s-lc-public-pt), the [Digital Repository](https://repository.lib.uchicago.edu), [Knowledge@UChicago](https://knowledge.uchicago.edu/), and the other Library websites and services.

No source maps are published. The SCSS source is in the [library website repository](https://github.com/uchicago-library/library_website/tree/master/design_system/scss).

## How This Project Is Documented

Documentation drifts when two places can hold the same fact. The rule here is that **a fact lives at the lowest layer that can hold it, and the build distributes it upward.**

| Layer | Where | Who reads it |
| --- | --- | --- |
| **Code and annotations** | `_variables.scss`, `base/`, `components/` | The source of truth. Travels with the change. |
| **Generated output** | The tokens page, `tokens.json`, `/design/llms.txt`, the Markdown source of each page | Anyone consuming the system, including agents |
| **Design system pages** | `design_system/content/foundations/`, `guidelines/`, `implementation/` | Stakeholders and builders |
| **Contributing** | `design_system/content/contributing/` (this section) | People working *on* this project |
| **Agent instructions** | `design_system/CLAUDE.md`, pointed to from `CLAUDE.md` in the repository root | AI agents working on this project. Points here rather than restating it |
| **Code entry point** | `design_system/README.md` | Readers of the code on GitHub. A pointer here, and nothing else |

Three rules follow from it:

1. **If it can be generated, it must be.** Token values, class lists, page indexes and breadcrumbs are all derived from the source. None of them is maintained by hand.
2. **If it is in the code, annotate the code.** A note beside a token or a class cannot be separated from the thing it describes. A paragraph on another page can.
3. **These pages hold only what cannot be derived** — the reasoning, the conventions, and the process. Where an agent and a person need the same fact, it is written here once and `CLAUDE.md` points at it.

Standards that constrain the design itself, rather than the process of working on the repository, live with the system they constrain: see [Design Standards](/design/foundations/design-standards/).
