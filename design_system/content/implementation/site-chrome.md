---
title: "Site Chrome"
description: "The header and footer that frame every Library page, and the markup to reuse them."
---

## Header

Two bands. `.logo-bar` carries the logo, the shortcut links and the mobile toggle; `.global-navbar` carries the dropdown menus and the search field. Link content comes from `design_system/data/globalNav.json`, not from the markup, so the same partial renders whatever that file defines. See it rendered in the [site chrome demo](/design/demos/global/site-chrome/).

```html
<header role="banner">
  <div class="logo-bar bg-white">
    <div class="container-md"><!-- logo, shortcut links, mobile toggle --></div>
  </div>
  <nav id="global-navbar" class="navbar navbar-expand-md navbar-dark global-navbar p-0" aria-label="Main navigation">
    <div class="container-md"><!-- dropdowns, search --></div>
  </nav>
</header>
```

`role="banner"` is required rather than decorative: LibGuides injects this header inside a `<header>` of its own, and a nested `<header>` loses the implicit banner role. The stylesheet also hangs a rule on it.

The `id` is the analytics hook only — `custom-event-tracking.js` uses it to attribute navigation events. All styling is on the `.global-navbar` class, so a second navigation bar can reuse the appearance without claiming the id.

## Simple header

A header without navigation: a maroon band with the white logo. It reuses `.global-navbar`, so the colour follows the brand token.

```html
<header role="banner">
  <div class="global-navbar py-2">
    <div class="container-md">
      <a href="https://www.lib.uchicago.edu/">
        <img src="https://www.lib.uchicago.edu/web-resources/img/white-logo.png"
             alt="University of Chicago Library" height="35">
      </a>
    </div>
  </div>
</header>
```

## Footer

```html
<footer role="contentinfo" class="footer">
  <div class="container-md">
    <h2 class="footer-heading">Column heading</h2>
    <div class="centerdiv"><!-- logo and closing text --></div>
  </div>
</footer>
```

`.footer` supplies the dark surface, white links and unstyled lists — Bootstrap has no footer component, so this one is ours. `.footer-heading` styles a column heading. `.centerdiv` is the centred block at the foot holding the logo and closing text; the block is current, only its name predates the naming convention.

