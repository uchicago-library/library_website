---
title: "Design Intent"
description: "These value pairs frame design conversations by anchoring each decision between two valid directions. They are not meant to produce precise formulas — a score simply captures the team's current lean on each axis, and that lean may shift depending on the audience or workflow."
---

## Rich ↔ Streamlined

{% include "design_system/includes/design-intent-scale.html" with left="Rich" right="Streamlined" value=9 %}

*Also: dense ↔ airy.*

A **rich** design surfaces more content and metadata upfront, uses harder visual groupings (higher contrast borders, panels), and keeps secondary content visible.

A **streamlined** design has fewer elements per screen, more generous spacing, progressive disclosure (filters behind toggles, secondary nav collapsed, options under a dropdown), and greater navigation depth.

This axis will shift by workflow. Dashboard and research guide home pages will lean rich — they serve frequent, task-focused users. The homepage and audience help pages will lean streamlined.

## Traditional ↔ Contemporary

{% include "design_system/includes/design-intent-scale.html" with left="Traditional" right="Contemporary" value=6 %}

*Also: calm ↔ dynamic, safe ↔ bold.*

A **traditional** design favors descriptive text over implicit UI: labeled metadata, descriptive button text, links over icon-only controls. Uses serif headings, less rounded corners (`rounded-1`, `rounded-2`), minimal hover animation, and less saturated color. Flatter designs with less shadows and gradients.

A **contemporary** design uses progressive disclosure, implicit controls, sans-serif headings, rounder corners (`rounded-3` on panels), subtle hover transitions, and more saturated color. They tend on dynamic styles like transparencies and blurred background effects, or gradients, or mesh gradient backgrounds, or stacked borders, even several of these (ex: glassmorphism).

## Institutional ↔ Approachable

{% include "design_system/includes/design-intent-scale.html" with left="Institutional" right="Approachable" value=8 %}

*Also: serious ↔ playful, formal ↔ casual, quiet ↔ expressive.*

Primarily expressed through copy and microcopy: reading level, tone, action label phrasing, empty state messaging.

More **institutional** means text-first, minimal decoration, and restrained use of primary color.

More **approachable** means icons alongside labels, illustrations in empty states and onboarding, and more prominent CTAs.
