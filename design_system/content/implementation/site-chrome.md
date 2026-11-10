---
title: "Site Chrome"
description: "The header and footer that frame every Library page, and the markup to reuse them."
---

On the Library website itself, the header and footer are `base/templates/base/includes/bs5/header.html` and `footer.html`, included by the public base template `base/templates/base/public_base_bs5.html`.

## Header

Two bands. `.logo-bar` carries the logo, the shortcut links and the mobile toggle; `.global-navbar` carries the dropdown menus and the search field. The header at the top of these pages is an instance of it, carrying the documentation's links in place of the Library's; the [Database Finder demo](/design/demos/database-finder/) shows it with the Library's.

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

The `id` is the analytics hook only — `jquery.track-everything.js` uses it to attribute navigation events. All styling is on the `.global-navbar` class, so a second navigation bar can reuse the appearance without claiming the id.

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
    <div class="row justify-content-xl-between">
      <div class="col-12 col-md-6 col-lg-3 col-xl-auto mb-4">
        <h2 class="footer-heading">Column heading</h2>
        <!-- list of links -->
      </div>
      <div class="col-12 col-xl-auto order-2 order-xl-3 mb-4 text-xl-center">
        <!-- logo, address and closing text -->
      </div>
    </div>
  </div>
</footer>
```

`.footer` supplies the dark surface, white links and unstyled lists — Bootstrap has no footer component, so this one is ours. `.footer-heading` styles a column heading. The grid has four link columns and a logo and address column. The four link columns share a row from `lg`. From `xl`, the logo and address column joins them, centred with `text-xl-center`; every column is sized to its content (`col-xl-auto`) and the row spreads them evenly (`justify-content-xl-between`), so no heading or link wraps. Fixed widths such as `col-xl-2` are too narrow for the longer labels. Below `xl` the logo and address sit under the links, left-aligned. Give icons in the lists `fa-fw`, so the labels line up.

