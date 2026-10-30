---
title: "Components"
description: "The rules this system adds to Bootstrap's components: which variants to use and which to avoid, and what each needs for accessibility and tracking."
---

Every component is Bootstrap 5.3's, styled by the system's tokens, and [Bootstrap's documentation](https://getbootstrap.com/docs/5.3/components/) covers its markup. This page holds only the rules this system adds. The classes the system defines itself, such as `.btn-default` and `.panel`, are listed with their notes on the [tokens page](/design/tokens/) and in [tokens.json](/design/tokens.json). The [Components demo](/design/demos/components/) shows them in place.

## Buttons

- **One `.btn-primary` per view**, for its single main action. Every other action is `.btn-default`, which is complete on its own: do not add `.btn-outline-secondary` beside it.
- **On a dark or image background**, use `.btn-outline-white`.
- **An action that loses data** is `.btn-danger-x`, with `<i class="fa-solid fa-exclamation me-2" aria-hidden="true"></i>` before its label. Do not use a filled `.btn-danger`.
- **Size.** The default size suits every standard context: forms, modals, cards, toolbars. `.btn-sm` is for dense UI where space is short, such as tables and inline actions, and never for emphasis. `.btn-lg` is only for the main call to action in a hero or an empty state.
- **Not used:** `.btn-secondary`. `.btn-info` is the active state built into tabs and navigation, so do not put it on a standalone button. Avoid `.btn-link`: if the action navigates, use an `<a>`.
- **Elements.** `.btn` works on `<button>`, `<a>` and `<input>`. An `<a>` styled as a button that acts on the page rather than navigating takes `role="button"`.

## Forms

- Every control has a `<label>` tied to it by `for` and `id`. A placeholder is not a label.
- A group of radio buttons or checkboxes sits in a `<fieldset>` with a `<legend>`.

## Cards

- A card is the grouping unit for repeated content: thumbnails, and links to pages with a featured image, such as news. See [Grouping Content](/design/guidelines/grouping-content/).
- Set `data-ga-category` and `data-ga-subcategory` once, on the row holding the cards, and `data-ga-label` on each link. See [Event Tracking](/design/implementation/event-tracking/).

## Accordions

- When an accordion's labels act as section titles, make each `.accordion-header` a heading one level below the section it sits in.
- For a long set of items, `.accordion-two-column` lays them in two columns from the `md` breakpoint. Wrap the items in a `.row`, and each `.accordion-item` in a `.col-md-6`.
- The tracking script recognises accordion buttons and sends a `tab` event, so they need no tracking attribute.

## List Groups

- `.active` is visual only. Add `aria-current` to the active item, so assistive technology conveys it too.
- In a list of results, `data-ga-position` on each link records how far down readers click.

## Tables

- Wrap a table in `.table-responsive`, so it scrolls sideways on a narrow screen instead of overflowing the layout.
- Which table to use is in [Typography](/design/guidelines/typography/#tables).

## Icons

- The icon set is Font Awesome 6.5.2.
- A decorative icon takes `aria-hidden="true"`. An icon that carries meaning on its own needs a text alternative, such as a `.visually-hidden` span.

## Alerts

- Each variant keeps its Bootstrap meaning.
- A link inside an alert takes the alert's own colour, so it stays legible on every variant. Add `.alert-link` only if you also want it bold.

## Badges

- A badge's colour only repeats what its text, or the text around it, already says.

## Navigation

- Navs, tabs, pills and breadcrumbs are Bootstrap's, used unmodified. Keep the ARIA attributes Bootstrap's examples carry.
- Give every `<nav>` its own `aria-label`, since a page usually has several.
- End a breadcrumb on the current page, unlinked.
- The site's own header and footer are in [Site Chrome](/design/implementation/site-chrome/).

## Pagination

- Wrap it in a `<nav>` with its own `aria-label`, and mark the current page with `aria-current="page"`.
- Put `data-ga-label` on Previous and Next, and `data-ga-position` on the numbered pages.
