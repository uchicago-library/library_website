---
title: "UChicago Library Design System"
description: "Design tokens, components and guidelines for University of Chicago Library websites. Built on Bootstrap 5 with the Library's brand colours and typeface, and held to WCAG 2.1 Level AA."
---

## Where to Start

- **Building a page or a product with the system?** [Start with Implementation](/design/implementation/).
- **Reviewing the decisions behind it?** [Start with the Foundations](/design/foundations/).
- **Changing the design system itself?** [Start with Contributing](/design/contributing/).
- **Pointing an AI agent at it?** [Give it /design/llms.txt](/design/llms.txt).

## About

### Goals

- Consistency and modularity across platforms — Wagtail, VuFind, Springshare, Aeon, FindIt! and others. The same tabs, search buttons and thumbnails should behave the same everywhere.
- Maintainable by a small team. The system cannot be demanding to keep current.
- Approachable for new or temporary contributors — fellows, new staff, and AI agents — so that questions like "should I make a new class, or is there one already?" have clear answers.
- Built on the latest Bootstrap and Font Awesome, customised through SCSS variables.
- Atomic and cumulative, so the system keeps growing rather than being redesigned from scratch every decade.

### Priorities

- Our most important users are from our academia, but the website needs to be usable by non-experts, new students, potential donors, and community members (neighborhood residents, high school teachers and students, etc).
- We would like to provide customization where possible.
- Ensure that Library sites are accessible and follow practices of universal design.

### How It Fits Together

The system has three layers, each built on the one before it. The [Foundations](/design/foundations/) are what every decision answers to: the accessibility and usability standards, the writing rules, the research, and where the design leans between competing values. The [Guidelines](/design/guidelines/) turn them into choices that hold on any page, such as how much of each [colour](/design/guidelines/color/) to use. [Implementation](/design/implementation/) is the code: the stylesheet to load, the components and layouts, and the rules for building on top of them.

Implementation's reference is the [tokens page](/design/tokens/), with every token and class and its value, and the [demos](/design/demos/) show the system in place on complete pages.

## Status

**In progress:** this design system is a stabilization effort aimed for completion by **November 2026**. It is based on a [planning document on Box](https://uchicago.app.box.com/file/2095747484682?s=jf05ybrn63rgky5f66j8uhms6ljr26ez).

The [systems using it](/design/contributing/#published-files-and-who-uses-them) are listed under Contributing, beside the files each one loads.

### Roadmap

- Finalize the initial set of components and design tokens based on the most common patterns across the library's websites.
- Test it by implementing it in the main Library website.
- Check the mechanical accessibility criteria on every build, and fail it on a miss: landmarks, skip links, missing `alt` attributes, duplicate IDs, skipped heading levels, and unnamed form controls. Today they are checked by hand.
- Add a utility to easily copy any `<pre>` or `<code>` content.
