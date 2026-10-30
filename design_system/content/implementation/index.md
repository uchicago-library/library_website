---
title: "Implementation"
order: 3
description: "Everything needed to build with the design system: the stylesheet to load, the components and layouts, and the rules for styling on top of it."
# The introduction of /design/llms.txt, after the home page's title and
# description. Agents building with the system are this page's readers too.
llms: |
  Built with Bootstrap 5 and Font Awesome 6. Every page below is linked as
  Markdown. Prefer Bootstrap's own classes and the documented component
  classes over bespoke CSS.

  Before producing any interface, read these three:
  [Getting Started](/design/implementation/getting-started.md) for the files
  to load and the checklist before shipping,
  [Design Standards](/design/foundations/design-standards.md) for the
  accessibility requirements, and
  [Writing](/design/foundations/writing.md) for the copy.

  Every token and documented class, with its value and the guidance on when to
  use it, is published as JSON at [/design/tokens.json](/design/tokens.json).
  Read it rather than the HTML tokens page.
---

## Start Here

- [Getting Started](/design/implementation/getting-started/) — the stylesheet to load, the files it comes with, and the checklist before you ship. Start here the first time.
- [Tokens and Classes](/design/tokens/) — every token and documented class, with its CSS variable, SCSS variable and value. The search box in the header goes straight to it from any page.
- [Components](/design/implementation/components/) — the rules for each component.

## Read Before Designing

The rules a design has to meet, wherever it is built:

- [Design Standards](/design/foundations/design-standards/) — the accessibility and usability requirements.
- [Writing](/design/foundations/writing/) — voice, naming and mechanics, for every label and message.
- [Guidelines](/design/guidelines/) — colour, typography and grouping content.

## See It in Place

- [Demos](/design/demos/) — complete pages built with the system.
- [Playground](https://uchicago-library.github.io/ucld/) — mockups and experiments, outside this site.
