---
title: "Styling Springshare Pages"
description: "How to apply the design system to LibGuides and other Springshare pages, which load their own Bootstrap at runtime."
---

## Why there is a second stylesheet

Springshare's LibApps products serve their own copy of Bootstrap 5 and their own base styles, and neither can be removed. `main-libapps.css` is therefore an override sheet rather than a full build: it assumes Bootstrap is already present and corrects styles to the UChicago branding, instead of shipping the framework a second time.

The main Library site uses `main.css`. The two compile from the same tokens but are not interchangeable. See [System Architecture](/design/contributing/architecture/) for all three stylesheet entry points.

## Loading it

The compiled stylesheet is published at `https://www.lib.uchicago.edu/static/design_system/css/main-libapps.css`.

In LibGuides it goes in the **Look & Feel → Custom JS/CSS** panel, which already loads after LibApps' own stylesheets. Order matters: this sheet overrides, so anything loading it earlier will be undone.

## What you can rely on

**Every design token.** Both stylesheets compile from the same `_variables.scss` and publish the same 29 `--ucl-*` custom properties. Anything on the [tokens page](/design/tokens/) is available on a Springshare page unchanged.

**The Bootstrap theme colours.** This sheet rewrites `--bs-primary`, `--bs-secondary` and the other theme slots to the brand palette, so the classes LibApps' own Bootstrap provides — `.text-primary`, `.bg-primary`, `.btn-primary` — pick up UChicago colours with no further work.

**Buttons, alerts, breadcrumbs, the header and the footer**, which are compiled into both stylesheets, and **Bootstrap's helpers** such as `.ratio`, `.stretched-link` and `.vstack`.

## What is not available

`main-libapps.scss` compiles a deliberate subset, because LibApps supplies the rest at runtime.

| Not compiled in | Consequence |
| --- | --- |
| `components/accordion` | `.accordion-two-column` does nothing. Bootstrap's own accordion is included and does pick up the accordion token overrides. |
| `components/panel` | `.panel` and `.panel-primary` do nothing. Use `.border.border-primary.rounded-3.p-3` instead — see [Grouping Content](/design/guidelines/grouping-content/). |
| `base/typography` | Heading sizes and inline `code` styling fall back to LibApps' own. |
| `base/layout` | `.sidebar` does nothing. |
| Bootstrap's utilities API | Utility classes come from LibApps' runtime Bootstrap, not from this sheet. Colour utilities still resolve to brand values because the theme slots are overridden. |

If you need one of these, uncomment its import in `design_system/scss/main-libapps.scss` and check the result against the demo below. Do not redefine the class locally.

## What is covered

The overrides target LibGuides specifically: guide pages, the A–Z database finder, and profile pages, plus the embedded LibChat widget. LibCal, LibAnswers, LibWizard and LibInsight have no overrides and render in LibApps' default styling.

## Validating a change

The reproduction of Springshare's own output is the [Database Finder demo](/design/demos/database-finder/), one self-contained file at `design_system/templates/design_system/pages/demos/database-finder.html`. It exists so this stylesheet can be tested against the markup it actually has to style, and it loads `main-libapps.css` rather than `main.css`. A guide page, or the LibGuides home page, would cover more of the stylesheet, and could replace it.

Two rules apply:

- The markup in that reproduction is Springshare's. Accessibility findings there are reported as warnings and must not be resolved by editing the reproduction — see [Conventions](/design/contributing/conventions/).
- Layouts we propose ourselves are mockups, not reproductions. They live in the [playground](https://github.com/uchicago-library/ucld) and are held to the full accessibility standard.
