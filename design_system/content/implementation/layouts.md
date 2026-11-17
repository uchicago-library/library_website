---
title: "Page Layouts"
description: "The standard page layouts, when each applies, and the markup for them."
---

Four layouts cover nearly every page. See them rendered at full width in the [layouts demo](/design/demos/layouts/).

## Main column width

Never let the main column get narrower than 540px beside a sidebar: below that, collapse a sidebar instead. At the 16px body size, 540px holds about 65 characters a line. That is within the 45 to 75 characters typographers recommend for reading, and close to the 56 to 66 that large news sites set for their articles. The layouts below follow the rule; the narrowest main column is 546px, with both sidebars at `xl`.

## Main column with right sidebar

Primary content with a supplementary sidebar for navigation, related links or metadata.

```html
<div class="container-lg">
  <div id="content" tabindex="-1">
    <h1>Page title</h1>
    <div class="row g-4">
      <main class="col-lg-8"><!-- Main content --></main>
      <aside class="col-lg-4" aria-label="Related">
        <div class="sidebar p-4 rounded"><!-- Supporting content --></div>
      </aside>
    </div>
  </div>
</div>
```

The sidebar stacks below the main column under the `lg` breakpoint, so write the two columns in the order they should be read on a phone.

Put the sidebar in an `<aside>` beside the `<main>`, not inside it, and give it an `aria-label`. When it holds several groups, give each one an `<h2>`: the sidebar sits beside the page's own sections, not under them. Style the heading smaller with a class such as `.h5`, so the main column's headings stay the most prominent.

Put the page title above the row, so it spans the main column and the sidebar instead of wrapping in the narrower main column. That puts the title outside `<main>`, so point the skip link at a wrapper around the title and the row (`id="content"` above).

## Section navigation

A column of links to the other pages in the current section, on the left. From `lg` it is a column of three; below `lg` it moves into an offcanvas panel opened by an "In this section" button, so the content starts near the top of a phone screen. With a right sidebar too, it collapses at `xl` instead (see below). Mark the current page with `aria-current="page"` as well as `.active`.

```html
<div class="container-lg">
  <div class="row g-4">
    <div class="col-lg-3">
      <button class="btn btn-default d-lg-none" type="button" data-bs-toggle="offcanvas"
              data-bs-target="#section-nav" aria-controls="section-nav">In this section</button>
      <div class="offcanvas-lg offcanvas-start" tabindex="-1" id="section-nav"
           aria-labelledby="section-nav-title">
        <div class="offcanvas-header">
          <p class="h5 offcanvas-title" id="section-nav-title">In this section</p>
          <button type="button" class="btn-close" data-bs-dismiss="offcanvas"
                  data-bs-target="#section-nav" aria-label="Close"></button>
        </div>
        <div class="offcanvas-body flex-column">
          <nav aria-label="Section">
            <ul class="nav flex-column"><!-- .nav-item > .nav-link --></ul>
          </nav>
        </div>
      </div>
    </div>
    <div class="col-lg-9" id="content" tabindex="-1">
      <h1>Page title</h1>
      <div class="row g-4">
        <main class="col-12"><!-- Main content --></main>
      </div>
    </div>
  </div>
</div>
```

With a right sidebar too, the page splits 3/6/3 from `xl`. Narrower, the section navigation collapses first: swap each `lg` above for `xl` (`col-xl-3`, `d-xl-none`, `offcanvas-xl`, `col-xl-9`) and split the inner row `col-lg-8` / `col-lg-4`, so at `lg` the main column and the sidebar share the row 8/4. Below `lg` the sidebar stacks under the content. Three columns at `lg` would leave each side column too narrow for tables and lists.

## Single column

The default. `col-lg-10 mx-auto` holds the line length near a comfortable reading measure, which is why every documentation page here uses it. Best for articles, documentation and forms.

```html
<main class="container-md">
  <div class="row">
    <div class="col-lg-10 mx-auto"><!-- Content --></div>
  </div>
</main>
```

## Full-width sections with centred content

Each band spans the viewport while its content stays in the standard container, so a background can change without the text shifting. Useful for landing pages that need visual rhythm.

```html
<section class="py-5">
  <div class="container-md">
    <div class="row">
      <div class="col-lg-10 mx-auto"><!-- Content --></div>
    </div>
  </div>
</section>

<section class="py-5 bg-body-secondary">
  <!-- Same inner structure, different surface -->
</section>
```

Use a surface token such as `bg-body-secondary` or `bg-primary` rather than a literal colour. For a dark band, use `text-bg-dark`, sparingly: see [Dark Surfaces](/design/guidelines/color/#dark-surfaces).
