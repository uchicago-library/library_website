---
title: "Annotations on This Project"
description: "Annotations are a documentation-only overlay used on the demos and the tokens page to surface accessibility concerns, behavioral rules, event tracking details, responsive considerations, and general context directly alongside live component demos."
---

## Purpose

Component demos should remain clean, copy-pasteable HTML. But many components carry implicit requirements — heading hierarchy for accordions, `aria-label` on pagination, event tracking attributes — that are easy to forget when reusing the markup.

Annotations make those requirements visible without polluting the component source. They are part of these documentation pages, and of the [playground](https://github.com/uchicago-library/ucld), which loads `meta.css` for them. No product loads them.

---

## Categories

Each annotation belongs to one of five categories, identified by color and icon:

| Category | Icon | Color | Use for |
| --- | --- | --- | --- |
| Accessibility | <i class="fa-solid fa-universal-access" aria-hidden="true"></i> | <span class="annotation-swatch annotation-swatch--a11y">--ucl-violet</span> | ARIA attributes, heading hierarchy, label association, color contrast, screen reader concerns |
| Behavior | <i class="fa-solid fa-hand-pointer" aria-hidden="true"></i> | <span class="annotation-swatch annotation-swatch--behavior">--ucl-lake</span> | UI rules, interaction constraints (e.g. "one primary button per view"), state management |
| Tracking | <i class="fa-solid fa-chart-simple" aria-hidden="true"></i> | <span class="annotation-swatch annotation-swatch--tracking">--ucl-terracotta</span> | GA4 event tracking attributes, event type inference, position tracking |
| Responsive | <i class="fa-solid fa-mobile-screen" aria-hidden="true"></i> | <span class="annotation-swatch annotation-swatch--responsive">--ucl-ivy</span> | Breakpoint behavior, scrollable wrappers, stacking order on mobile |
| Info | <i class="fa-solid fa-circle-info" aria-hidden="true"></i> | <span class="annotation-swatch annotation-swatch--info">--ucl-greystone</span> | General context that does not fit the other four: why a pattern exists, what it replaced, a caveat worth knowing. Neutral rather than vivid, so it does not compete for attention with a real concern. |

---

## How It Works

### Architecture

The annotation system has three parts:

1. **SCSS** — `design_system/scss/meta/_annotations.scss` defines styles for marker badges, dashed outlines on annotated elements, the floating toggle button, and hidden state.
2. **JavaScript** — `design_system/static/design_system/js/annotations.js` (loaded on every page by `includes/annotations.html`, from `base.html`) reads annotation definitions, creates markers dynamically, and initializes Bootstrap popovers.
3. **Per-page template** — Each page that needs annotations includes a `<template class="ds-annotations-template">` at the end. This is where annotation content is authored. Only the HTML pages in `templates/design_system/pages/` have them: the demos and the tokens page.

### Separation of concerns

Annotation definitions live in a `<template>` element, which the browser does not render. The JavaScript reads the template's children at page load, groups them by target selector, and injects marker badges into the DOM. This means component demo HTML stays clean — no annotation markup mixed in.

The toggle button and its state are managed globally so pages without annotations simply show no UI.

---

## Adding Annotations to a Page

### 1. Add section IDs

Each annotated element needs a CSS selector the script can find. The simplest approach is adding an `id` to the `<section>` wrapping each component demo.

### 2. Add the template block

Before the footer include, add a `<template class="ds-annotations-template">` element containing one `<div>` per annotation:

```html
<template class="ds-annotations-template">
  <div data-target="#section-buttons"
       data-category="a11y"
       data-title="Button semantics">
    When an <code>&lt;a&gt;</code> is styled as a button
    but triggers in-page behavior, add
    <code>role="button"</code>.
  </div>
</template>
```

Annotation bodies are raw HTML, so this block belongs in an HTML page. A Markdown page cannot carry annotations: what one would say belongs in its prose.

### Attributes

| Attribute | Required | Description |
| --- | --- | --- |
| `data-target` | Yes | A CSS selector for the element to annotate (e.g. `#section-buttons`, `#accordionDemo`). |
| `data-category` | Yes | One of `a11y`, `behavior`, `tracking`, `responsive`, `info`. |
| `data-title` | No | Popover heading text. Defaults to the category name if omitted. |
| innerHTML | Yes | The popover body content. HTML is supported. |

### 3. Multiple annotations per target

Multiple `<div>` elements can share the same `data-target`. They will be grouped into a single marker cluster at the top-right of the target element. The dashed outline color is determined by the first annotation's category.

Multiple `<template class="ds-annotations-template">` elements can coexist on the same page (e.g. from different partials). The script collects annotations from all of them.

---

## Toggle & Persistence

A floating button at the bottom-right corner of every page lets users show or hide annotations. The preference is saved in `localStorage` so it persists across page loads and sessions.

Pages without a `<template class="ds-annotations-template">` block will not display the toggle button or any annotation UI — the script exits early.
