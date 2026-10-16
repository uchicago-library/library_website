---
title: "Conventions"
description: "Naming, class structure, SCSS rules, and the checks a change should pass before it is considered done."
---

Where [System Architecture](/design/methodology/architecture/) describes what exists, this page prescribes what to write.

## Naming

- **SCSS partials:** `_component-name.scss` — underscore prefix, kebab-case.
- **Pages:** `page-name.md` in `design_system/content/` — kebab-case and descriptive. A page with its own template also has `templates/design_system/pages/page-name.html`.
- **Folders:** kebab-case, or underscored where an existing group already uses it.
- **IDs:** kebab-case, and durable. Avoid renaming a shared ID without a coordinated change.

## CSS Classes: BEM

Use `block__element--modifier` for bespoke components.

- **Block** — the component itself: `.card`
- **Element** — a part of it, after `__`: `.card__header`
- **Modifier** — a variation, after `--`: `.card--featured`

Avoid over-nesting (`.card__content__inner__text`), and do not reach for BEM where a Bootstrap utility already says it.

| Situation | What to do |
| --- | --- |
| Layout and structure (columns, grids, spacing) | Don't BEM these. Use Bootstrap utilities. |
| Bespoke components (search box, quick-links panel) | BEM. |
| One-off adjustments | Use a utility, not a new class. |

## IDs versus Classes

Use IDs for things that are unique on the page; use classes for anything that repeats.

- **Unique landmarks:** `header`, `footer`, `main-content`.
- **One-to-one relationships:** `aria-labelledby`, `aria-controls`, and `<label for>`.
- **Stable JS hooks**, but only where the element is genuinely unique. Prefer a data attribute for repeated instances.
- **Never on a repeatable component.** IDs must be unique per rendered page, and a duplicate breaks every association that depends on it.

## Writing Pages

- **Review a page as code.** Its body runs as a Django template and can hold raw HTML, so a change to a `.md` file needs the same review as a change to a template.
- **Choose the format deliberately.** Markdown for prose; a `template` when the rendered markup is itself the documentation.
- **Do not restate the title or lead** in the body — `page.html` renders them from the `title` and `description` front matter.
- **Do not put heading display classes on headings** (`<h2 class="h4">`) in documentation pages.
- **Write a real `description`.** It is published in `/design/llms.txt`.
- **Use semantic elements:** `<header>`, `<main>`, `<article>`, `<nav>`.
- **No inline styles.** Page-specific demo styling goes in a `<style>` block at the top of the file, and moves to a dedicated SCSS file once it settles.
- **Code examples depend on the format.** A templated page carries none — it demonstrates itself. A prose page has only its Markdown, so a short snippet is how it supplies markup. Reach for one where the reader would otherwise have to work out which part of a page is structural and which is the documentation around it.

A page body is rendered as a Django template before it is rendered as Markdown, so it can include a live demo, and any literal template syntax you want to display has to be wrapped in a `verbatim` block. Internal links are plain `/design/...` paths. Use fenced code blocks, and indent nested lists by four spaces.

## Writing CSS

These apply to any project styling on top of the design system, not only to this one. [Getting Started](/design/implementation/using-ucld/) links here, along with the BEM and IDs sections above.

- **Never hardcode a value** that exists as a token.
- **Prefer the highest-level class available** — a Bootstrap component class over utilities, utilities over bespoke CSS.
- **Avoid `!important`.**
- **Honour `prefers-reduced-motion`.** Animate nothing that the user has asked to keep still.

## Writing SCSS in This Project

- **One file per component**, at `design_system/scss/components/_name.scss`, imported in `main.scss`.
- **Documentation-only styles** go in `design_system/scss/meta/` and are imported in `meta.scss`, never in `main.scss`.
- **Rules in `meta/_documentation.scss` use direct-child selectors** (`.documentation > h2`). Markdown output is flat, so this reaches everything Markdown emits while leaving nested demo markup alone.
- **Transitions go through Bootstrap's mixin**, not a bare `transition:` property. The mixin is what honours `prefers-reduced-motion`.

## Writing JavaScript

Keep it minimal. JavaScript is justified for initialising Bootstrap behaviour through data attributes, for build-time work, and where no markup-only alternative exists. Most Bootstrap components need no custom script at all.

## Where Things Go

| Content | Location |
| --- | --- |
| Component documentation | `design_system/content/implementation/` |
| Live demo of a pattern | `design_system/templates/design_system/demos/<group>/`, with a stub in `content/demos/<group>/` |
| Usage guidance | `design_system/content/guidelines/` |
| Principles and research | `design_system/content/foundation/` |
| Process documentation | `design_system/content/methodology/` |
| Experimental mockup | The [playground](https://github.com/uchicago-library/ucld) |
| Component SCSS | `design_system/scss/components/_name.scss`, imported in `main.scss` |
| Documentation-only SCSS | `design_system/scss/meta/_name.scss`, imported in `meta.scss` |
| Global element styles | `design_system/scss/base/_global.scss` |
| Layout styles | `design_system/scss/base/_layout.scss` |
| Shared partials | `design_system/templates/design_system/includes/` |
| Springshare markup for the LibApps demos | `design_system/templates/design_system/includes/libapps/` |

## Definition of Done

Run `npm run build:design-system` and commit its output, then `./manage.py test design_system`, which renders every page and fails on an error or a broken internal link.

Accessibility is checked by hand:

- **The page structure holds** — one `<main>` with a skip link to it, no skipped heading levels, no duplicate IDs, a name on every form control, and an `alt` attribute on every image.

- **Alt text is meaningful**, not merely present. A decorative image takes `alt=""`.
- **The keyboard path works** — every interactive element reachable by Tab, in a logical order, with a visible focus indicator, and Escape closes what it should.
- **The layout holds at each breakpoint.** These are Bootstrap's defaults, unmodified: 576, 768, 992, 1200 and 1400 pixels.
- **It reads correctly.** A control's accessible name should make sense read aloud on its own, without the surrounding page.
- **No console errors**, in current Chrome, Firefox and Safari.
- **Nothing a consumer may use is removed or renamed** — no class, token or custom property. Projects load the published stylesheet directly, with no version to pin, so a removal reaches them on the next deploy.

The [LibApps demos](/design/demos/libapps/) reproduce Springshare's own markup so the LibApps stylesheet can be tested against it. Accessibility findings there belong to Springshare, and should not be resolved by editing the reproduction.
