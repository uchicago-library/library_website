---
name: create-template
description: Write or migrate a Django/Wagtail template for the public site on the design system (Bootstrap 5). Use when creating any public template, page, partial or StreamField block template, or when moving a page type from base/public_base.html to base/public_base_bs5.html (#1109).
---

# Create a template

For any public-site template, new or migrated. Rules that hold for any
Library site live in the design system; this skill links to them by path and
adds only what is specific to this site.

Read first:
- `design_system/content/implementation/components.md`: the rules this
  system adds to Bootstrap's components.
- `design_system/content/implementation/layouts.md`: the page layouts.
- `design_system/content/implementation/event-tracking.md`: the `data-ga-*`
  attributes.
- `design_system/content/implementation/site-chrome.md`: header and footer.

## Building it

1. **Use what exists, in this order:** a design system or Bootstrap 5.3
   component, then Bootstrap utilities, then a new component only when
   neither can do it. A new component goes in `design_system/scss/components/`
   and gets documented there; say why in the PR.
2. **No Bootstrap 3 or Font Awesome 4 classes** (`col-xs-*`, `hidden-*`,
   `img-responsive`, `pull-*`, `btn-morelink`, `glyphicon`, `fa fa-*-o`).
3. **Images:** `{% picture %}` or `{% srcset_image %}` with a few widths and
   a `sizes` that matches the column, not `{% image %}` at one size.
   Decorative images take `alt=""`.
4. **Ids only where a script or an ARIA relationship needs one.**
5. **Tracking:** keep the `data-ga-*` attributes of the markup you replace.
6. **Indent with 2 spaces;** CI runs `djhtml --check`.

## Site specifics

- **Base:** `base/public_base_bs5.html`. It only arranges partials; the
  partials live in `base/includes/bs5/`, the sidebar widgets in `sidebar/`
  and the widgets below the content in `below_content/`.
- **Partials are included with `only`** and list their context in a comment
  at the top. Pass `page=self` rather than reading `self` inside.
- **Columns come from `{% block layout %}`**, which picks them from
  `has_left_sidebar` and `self.has_right_sidebar`. The home page and
  full-width pages override the block; other pages fill `content`.
- **Other blocks:** `title`, `meta`, `styles`, `banner`, `breadcrumbs`,
  `above_main_content`, `page_heading`, `under_h1`, `content`,
  `left_sidebar_extras`, `right_sidebar`, `btm_content`, `optional_footer`,
  `extra_scripts`, `js`.
- **Containers:** the site's chrome and sidebar layouts use `container-lg`;
  a single column uses `container-md` with `col-lg-10 mx-auto`.
- **Sidebar widgets** are `<section>`s with an `<h2 class="h5">`.
- **StreamField block templates** are rewritten in place, Bootstrap 5 only.
  A block renders on both bases until #1128, so check it on each.

## Migrating a page type

Until #1128 removes the old base.

1. Point the template at `base/public_base_bs5.html` and keep only the blocks
   it fills. Move anything it still draws itself onto a partial if another
   page type needs it too.
2. Grep the template, its includes and its blocks for the Bootstrap 3
   classes above, inline jQuery and `|safe` / `autoescape off` markup built
   in Python.
3. Look at the page in the browser at 390, 1024 and 1280 px, after
   `./manage.py clear_wagtail_cache`. Open what opens, and walk it with the
   keyboard.

## Tests

- One render test per page type.
- One test per data-dependent branch (a widget that shows only when a field
  is set, a variant chosen from a value).
- One test per hook something else relies on (an id a script uses, the skip
  link target).
- One regression test per bug.
- None for classes, wording or static markup, and none for reports.

Partials included with `only` can be tested with `render_to_string` and a
plain dict. Tests for the base are in `base/tests.py` (`TestDesignSystemBase`).
