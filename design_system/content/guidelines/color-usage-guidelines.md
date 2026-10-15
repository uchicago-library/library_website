---
title: "Color Usage Guidelines"
description: "Use color with restraint to build clear hierarchy, strong readability, and a modern, sober interface."
---

## 60-30-10 Rule

**60%** neutral foundation: use light neutrals for page or component backgrounds to keep content readable and reduce visual noise.

**30%** structural support: use a darker neutral for surfaces, dividers, and secondary UI regions that define layout.

**10%** emphasis color: use `primary` only for call-to-action elements, and use the `lake` family for active states, links, and inline code.

Visual ratio example:

{% include "design_system/includes/color-ratio.html" %}

## Page-Level Application

Start with neutral backgrounds and text contrast first, then add one emphasis color only where users need to act or orient themselves.

Keep emphasis usage consistent across the page: CTA buttons in `primary`, while links and selected states stay in the `lake` family.

## Component-Level Application

Most components should remain neutral by default and only use color for interaction or status moments.

Avoid placing multiple accent families in the same component unless they represent clear semantic states such as success or warning.

## Best Practices

- Prioritize contrast and readability first; color should support content, not compete with it.
- Use one dominant accent family per screen to keep the UI calm and coherent.
- Reserve highly saturated colors for important actions and feedback.
- Do not rely on color alone to convey meaning; pair color with text labels or icons.
- Test color combinations in context on desktop and mobile breakpoints.

## CSS Classes (Quick Reference)

Use semantic utility classes tied to the design tokens:

- `.btn-primary` and `.bg-primary` for call-to-action emphasis only.
- `.text-info`, `.link-info`, and `.bg-info` for active states and interactive emphasis.
- `.bg-secondary`, `.text-secondary`, `.border-secondary` for supporting neutral structure.
- `.bg-light` and `.text-dark` for baseline readability and page foundation.
- `.text-muted` for low-emphasis metadata and helper text.
- `.bg-success`, `.bg-warning`, `.bg-danger`, `.bg-info` only for semantic states.

For all approved color families and their values, see the [brand palette](/design/implementation/token-tables/#panel-brand-colors) in the Token Tables.

## Token Reference

Use the same role across Sass, CSS variables, and utility classes:

- **CTA:** `$primary` | `--bs-primary` | `.btn-primary`, `.bg-primary`
- **Active/Interactive:** `$info`, `$link-color` | `--bs-info`, `--bs-link-color-rgb` | `.btn-info`, `.text-info`, `.link-info`
- **Extra-subtle Active Surface:** `$ucl-info-bg-extra-subtle` | `--ucl-info-bg-extra-subtle` | `.accordion-button` active state token
- **Structure:** `$secondary`, `$light`, `$dark` | `--bs-secondary`, `--bs-light`, `--bs-dark` | `.bg-secondary`, `.bg-light`, `.text-dark`
