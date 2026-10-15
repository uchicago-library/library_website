---
title: "Getting Started"
description: "How to load the design system in another project, every file it publishes, and where the rules for styling on top of it live."
---

## Loading it

Load the favicon, the stylesheet and the icon set in the `<head>`, and Bootstrap's JavaScript before `</body>`.

```html
<link rel="icon" type="image/x-icon" href="https://www.lib.uchicago.edu/web-resources/img/favicon-black.ico">
<link rel="stylesheet" href="https://www.lib.uchicago.edu/static/design_system/css/main.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">

<script src="https://www.lib.uchicago.edu/static/design_system/js/bootstrap.bundle.min.js"></script>
```

- **`main.css`** is Bootstrap compiled with the design system's tokens, plus its components and the UChicago Sans Serif typeface. It replaces Bootstrap's own CSS; load one or the other, not both.
- **`bootstrap.bundle.min.js`** is Bootstrap's JavaScript, with Popper, built from the same Bootstrap version as `main.css`. Load it rather than a CDN copy, so the two cannot drift apart.
- **Font Awesome 6.5.2** is the icon set the components are written against.
- **The favicon** is an ICO; the Library publishes no SVG version. Reference it from `lib.uchicago.edu` rather than copying it, so a change to the mark reaches every site at once. Three variants sit at that path: `favicon.ico` full colour, `favicon-black.ico` monochrome for light browser chrome, and `favicon-m.ico` for mobile. Serve a copy at `/favicon.ico` as well, since browsers request that path on their own, without reading the tag.

Both files always serve what the Library website currently has deployed. There are no versions to pin.

## Published files

Everything the Library website publishes under `https://www.lib.uchicago.edu/static/design_system/`: stylesheets in `css/`, scripts in `js/`. A project loads one stylesheet, never both.

| File | Load it when |
| --- | --- |
| `main.css` | Your project controls its own `<head>`. The full product stylesheet: Bootstrap with the design system's tokens, components and typeface. |
| `main-libapps.css` | The page is served by Springshare, which loads its own Bootstrap first. An override sheet, not a full build; see [Styling Springshare Pages](/design/implementation/springshare/). |
| `bootstrap.bundle.min.js` | Alongside either stylesheet, for components that need JavaScript: dropdowns, collapse, accordions, modals. |
| `meta.css` | Never. It styles these documentation pages and is not part of the product. |

No source maps are published. The SCSS source is in the [library website repository](https://github.com/uchicago-library/library_website/tree/master/design_system/scss).

## Styling on top of it

Take values from the [Token Tables](/design/implementation/token-tables/) rather than writing them out. The rules for your own CSS are the ones this project follows, in [Conventions](/design/methodology/conventions/): [BEM](/design/methodology/conventions/#css-classes-bem), [IDs versus classes](/design/methodology/conventions/#ids-versus-classes) and [Writing CSS](/design/methodology/conventions/#writing-css).

## Before you ship

Each item links to the page that holds the rule.

- One stylesheet is loaded: `main.css`, or `main-libapps.css` on Springshare. Bootstrap's own CSS is not loaded beside it.
- The header and footer use the markup in [Site Chrome](/design/implementation/site-chrome/).
- Each page starts from one of the [Page Layouts](/design/implementation/layouts/).
- No value that exists as a token is written out by hand. Search the [Token Tables](/design/implementation/token-tables/).
- A Bootstrap component class is used before utilities, and utilities before your own CSS. See [Writing CSS](/design/methodology/conventions/#writing-css).
- Each view has at most one `.btn-primary`. See [Components](/design/implementation/components/#section-buttons).
- The page meets the [WCAG 2.1 AA requirements](/design/foundation/design-standards/#accessibility-wcag-21-level-aa): one `<main>` with a skip link to it, a name on every form control, `alt` on every image, and no skipped heading levels.
- Interactive elements carry the `data-ga-*` attributes in [Event Tracking](/design/implementation/event-tracking/), if the site reports to GA4.
