---
title: "Page Layouts"
description: "The three standard page layouts, when each applies, and the markup for them."
---

Three layouts cover nearly every page. See them rendered at full width in the [layouts demo](/design/demos/layouts/).

## Main column with right sidebar

Primary content with a supplementary sidebar for navigation, related links or metadata.

```html
<main class="container-lg">
  <div class="row g-4">
    <div class="col-lg-8"><!-- Main content --></div>
    <div class="col-lg-4">
      <div class="sidebar p-4 rounded"><!-- Supporting content --></div>
    </div>
  </div>
</main>
```

The sidebar stacks below the main column under the `lg` breakpoint, so write the two columns in the order they should be read on a phone.

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

Use a surface token such as `bg-body-secondary` or `bg-primary` rather than a literal colour.
