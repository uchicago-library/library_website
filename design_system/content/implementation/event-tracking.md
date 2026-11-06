---
title: "Event Tracking"
description: "Custom event labeling schema for GA4 analytics using data attributes."
---

## Overview

A centralized [JavaScript](https://www.lib.uchicago.edu/static/base/js/jquery.track-everything.js) reads `data-ga-*` attributes from the DOM and sends structured events to Google Analytics 4. The DOM is the source of truth — templates set the attributes, and the script reads them at interaction time.

Visual documentation of how key screens are tracked is available in [this Figma file](https://www.figma.com/design/I546YaJgcD4JR1agVR2rxD/Custom-events-documentation?node-id=0-1&t=Y11QGiBVbdz5x0ze-1). The canonical reference is the [wiki page](https://github.com/uchicago-library/library_website/wiki/Custom-Event-labeling).

---

## HTML Attributes

These `data-ga-*` attributes are set directly in HTML templates. Values can be defined on the interactive element itself or inherited from a parent container.

| Attribute | Scope | Description |
| --- | --- | --- |
| `data-ga-category` | Parent or element | The page region. Can be set on a parent container and inherited by all links inside. |
| `data-ga-subcategory` | Parent or element | The content block or component name. Also inheritable from a parent. |
| `data-ga-label` | Element | The specific link text or role. Set on the interactive element. |
| `data-ga-position` | Element | The item's index in a list or table. Useful for tracking click depth. |

---

## Event Schema

Adopted September 2025. Each tracked interaction produces an event with these fields.

### Action (`name`)

- `click` — most interactive elements (links, buttons)
- `tab` — elements with `role="tab"`, accordion toggles, and navbar dropdowns
- `dropdown` — elements with `data-toggle="dropdown"`

The event name is determined automatically by the tracking script based on CSS selector matching — there is no HTML attribute for it. Accordion buttons and tabs are detected by their Bootstrap selectors and fire as `tab`; dropdown toggles fire as `dropdown`; everything else fires as `click`.

### Category (`event_category`)

The broad page region the interaction belongs to.

- **Navigation** — header, breadcrumbs
- **Main** — primary content area
- **Sidebar** — left or right sidebar
- **Footer**
- **Floating** — alert banners, feedback button
- **Main Search Widget** — the homepage search (has its own category)
- **Global Navbar** — the global navigation bar (has its own category)

### Subcategory (`event_subcategory`)

A recognizable content block or component within the category. Typically a conceptual term: List, Widget, Table, Form, Toolbar, Pagination.

When not explicitly set, the script falls back to:

1. The `aria-labelledby` value of the nearest labeled region
2. The `id` of the closest ancestor with an `id`

### Label (`event_label`)

Identifies the specific element that was clicked. Resolution order:

1. `aria-label`
2. `textContent`
3. `title`
4. `alt` (for images)
5. `"Unknown"`

For highly dynamic content (search results, catalog records), the role of the link is preferred over the dynamic text. Domain-specific overrides exist for VuFind (Title, Author, Holding, Save Record) and LibGuides (Guide Name, Guide Author, Guide Subject).

### Position (`click_position`)

The index of the clicked item within a list. Tracked for search results, news listings, and tabular data. Can be based on `<li>` index, a `<div>` container index, or a table row.

### Indecision count (`event_indecision_count`)

Counts how many times a user clicks on tabs or dropdowns before making a final selection. Helps identify confusing navigation patterns.

### Options (`event_option`)

Records checkbox or radio button state when paired with a primary action (e.g., the search type selector in the homepage search widget). Only applied to the main search widget.

---

## Attribute Inheritance

`data-ga-category` and `data-ga-subcategory` can be set on any ancestor element. All interactive elements inside inherit those values unless they define their own. This avoids repetitive markup.

For example, setting `data-ga-category="Main"` and `data-ga-subcategory="Card"` on a `.row` container means every `<a>` inside the cards inherits both values. Each link only needs its own `data-ga-label` to identify the specific action.

---

## Fallback Behavior

When `data-ga-*` attributes are not present in the HTML, the tracking script deduces values from DOM context. Explicitly setting the attributes in templates is preferred — it makes tracking deterministic and avoids fragile CSS-class-based heuristics.

The script also has a function that pre-populates HTML with attributes at runtime when template changes are impractical or when context is too ambiguous for automatic deduction.

---

## Websites Using This System

- [lib.uchicago.edu](https://www.lib.uchicago.edu) — Library Website
- [catalog.lib.uchicago.edu](https://catalog.lib.uchicago.edu) — Catalog
- [guides.lib.uchicago.edu](https://guides.lib.uchicago.edu) — LibGuides
- [rooms.lib.uchicago.edu](https://rooms.lib.uchicago.edu) — Rooms
- [sfx.lib.uchicago.edu](https://sfx.lib.uchicago.edu/sfx_local) — FindIt!

---

## Special Cases

- **Main Search Widget** — has its own category, not "Main". Tracks `event_option` for radio/checkbox state.
- **Global Navbar** — has its own category, not "Navigation".
- **Left Sidebar** — on LibGuides, the sidebar contains both navigation and "secondary content" blocks, so the subcategory differentiates them.
- **Pagination** — category: Main, subcategory: Pagination.
