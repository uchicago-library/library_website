---
title: "Grouping Content"
description: "Guidelines for using surfaces, borders, and shadows to group content in the design system."
---

## Guidelines

- **Only one:** Use one grouping method per visual level. Do not combine border + shadow + surface on the same element.
- **Document layout:** Use headings, dividers, and whitespace to structure content. Do not use borders or backgrounds to group document-level content.
- **Sidebar:** Use `.sidebar` or `.bg-light` to distinguish the sidebar and other secondary interfaces. Background alone differentiates these areas, with no border, rounded corners, or shadow.
- **Primary:** Use `.panel-primary` or `.border.border-primary.rounded-3.p-3` for main components like the main search box on the homepage.
- **CTA:** Use `.bg-primary` only for small primary components like CTA buttons. Most components will have this baked into their classes like `.btn.btn-primary`. Reserve `.bg-primary` for the single primary action in a view. Custom CTA components may instead use images as background that are darkened by a minimum of 30%, like homepage banners or linked image buttons.
- **UI components:** Use `.card>.card-body` = `.border.rounded-2.p-2` or `.panel` = `.card.rounded-3.p-3` to define component boundaries in UI-driven layouts (cards, forms, panels) like dashboards. Thumbnails for images and links to pages with a featured image like news should use the `.card` component.
- Avoid boxing or over-nesting multiple levels of borders close together, like cards directly inside a panel, or bordered accordions inside a boxed tab panel. Some components may disregard the border such as `.card.border-0` in these cases. Never more than 2 borders directly nested. Components that use a border include cards, panels, forms, and accordions.
- Do not use dashed or dotted borders.
- Borders should never be touching. There should always be spacing, such as padding or margin, to distance them.
- **Shadow:** Use `.shadow` only for elevated or floating surfaces like modals and dropdowns.

### Spacing and Whitespace

Whitespace defines relationships and hierarchy. Use the scale consistently — don't skip levels or mix padding and margin for the same purpose.

#### Spacing Scale

| Level | Typical class | Use for |
| --- | --- | --- |
| 1 | `ms-1`, `me-1` | Tight inline pairings — icon + label, badge + text |
| 2 | `mb-2` | Intra-component stacking — list items, stacked inputs, card body rhythm |
| 3 | `p-3` | Component padding — cards, panels, form sections |
| 4 | `mb-4`, `g-4` | Between components; default grid gap |
| 5 | `py-5` | Section breaks and page-level structure |

#### Padding vs. Margin

Use `p-` for internal space within a component. Use `m-` only to push a component away from its siblings — prefer layout containers and gap utilities over scattered margins.

#### Asymmetric Spacing

Horizontal padding and gap is typically one step larger than vertical to improve line readability and visual flow: `px-3 py-2`, `gx-3 gy-2`.

#### Buttons

Button padding is baked in by Bootstrap (`.btn` sits between levels 1 and 2 on the scale). Do not override it with spacing utilities — use `.btn-sm` or `.btn-lg` if a size variant is needed.

---

## Visual Examples

These examples show typical grouping decisions in context.

{% include "design_system/includes/grouping-content.html" %}
