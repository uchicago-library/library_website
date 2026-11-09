---
title: "Getting Started"
description: "How to load the design system in another project, the rules for styling on top of it, and the checklist before you ship."
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
- **On a Springshare page**, load `main-libapps.css` instead of `main.css`. See [Styling Springshare Pages](/design/implementation/springshare/).
- **Font Awesome 6.5.2** is the icon set the components are written against.
- **The favicon** is an ICO; the Library publishes no SVG version. Reference it from `lib.uchicago.edu` rather than copying it, so a change to the mark reaches every site at once. Three variants sit at that path: `favicon.ico` full colour, `favicon-black.ico` monochrome for light browser chrome, and `favicon-m.ico` for mobile. Serve a copy at `/favicon.ico` as well, since browsers request that path on their own, without reading the tag.

Both files always serve what the Library website currently has deployed. There are no versions to pin.

Every file the Library website publishes, and the systems that load each one, are listed under [Published Files and Who Uses Them](/design/contributing/#published-files-and-who-uses-them).

## Styling on top of it

Take values from the [tokens page](/design/tokens/) rather than writing them out. The rules for your own CSS are the ones this project follows, in [Conventions](/design/contributing/conventions/): [BEM](/design/contributing/conventions/#css-classes-bem), [IDs versus classes](/design/contributing/conventions/#ids-versus-classes) and [Writing CSS](/design/contributing/conventions/#writing-css).

## Before you ship

Each item links to the page that holds the rule.

- One stylesheet is loaded: `main.css`, or `main-libapps.css` on Springshare. Bootstrap's own CSS is not loaded beside it.
- The header and footer use the markup in [Site Chrome](/design/implementation/site-chrome/).
- Each page starts from one of the [Page Layouts](/design/implementation/layouts/).
- No value that exists as a token is written out by hand. Search the [tokens page](/design/tokens/).
- A Bootstrap component class is used before utilities, and utilities before your own CSS. See [Writing CSS](/design/contributing/conventions/#writing-css).
- Each view has at most one `.btn-primary`. See [Components](/design/implementation/components/#buttons).
- The page meets the [WCAG 2.1 AA requirements](/design/foundations/design-standards/#accessibility-wcag-21-level-aa): one `<main>` with a skip link to it, a name on every form control, `alt` on every image, and no skipped heading levels.
- Interface text follows [Writing](/design/foundations/writing/).
- Interactive elements carry the `data-ga-*` attributes in [Event Tracking](/design/implementation/event-tracking/), if the site reports to GA4.
