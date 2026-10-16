---
title: "Design Standards"
description: "The usability heuristics and WCAG 2.1 Level AA accessibility requirements that every component in this design system is held to."
---

## Usability Heuristics

Nielsen's ten heuristics are the shared vocabulary for design review here. They are most useful as questions to ask of a component, not as a checklist to tick.

1. **Visibility of system status** — the interface says what is happening.
2. **Match between system and the real world** — "Find Resources", not "Query Database API".
3. **User control and freedom** — there is always a way out, and it is obvious.
4. **Consistency and standards** — the same thing looks and behaves the same everywhere.
5. **Error prevention** — the design makes the mistake hard to make.
6. **Recognition rather than recall** — options are visible rather than remembered.
7. **Flexibility and efficiency** — shortcuts for frequent users, without cost to newcomers.
8. **Aesthetic and minimalist design** — nothing competes with what matters.
9. **Help users recover from errors** — plain language, precise cause, a way forward.
10. **Help and documentation** — findable when needed, unnecessary the rest of the time.

The [Nielsen Norman Group's article](https://www.nngroup.com/articles/ten-usability-heuristics/) has the full treatment. The [Design Intent](/design/foundations/design-intent/) page frames the trade-offs between them for this system specifically.

## Accessibility: WCAG 2.1 Level AA

Every component and page must meet [WCAG 2.1 Level AA](https://www.w3.org/WAI/WCAG21/quickref/).

**Perceivable**

- Every image has an `alt` attribute; decorative images take `alt=""`.
- Colour contrast is at least 4.5:1 for body text and 3:1 for large text (18pt and above).
- Structure is carried by semantic HTML, not by styling alone.
- No information is conveyed by colour alone, and text can be resized.

**Operable**

- Every function is reachable and usable by keyboard.
- Focus indicators are visible on all interactive elements.
- A skip link lets keyboard users bypass the header.
- Nothing flashes more than three times a second, and motion respects `prefers-reduced-motion`.

**Understandable**

- The document language is declared.
- Navigation and component behaviour are consistent across pages.
- Every form control has an associated, descriptive label.
- Errors are identified clearly, with a constructive suggestion.

**Robust**

- Valid HTML, with ARIA used only where native semantics fall short.
- Custom controls expose a correct name, role and value.
- Dynamic updates are announced through live regions.

### How this is enforced

Every criterion is checked by hand today, against the definition of done in [Conventions](/design/contributing/conventions/). Checking the mechanical ones on every build — landmarks, skip links, missing `alt` attributes, duplicate IDs, skipped heading levels, and unnamed form controls — is on the [roadmap](/design/#roadmap). Motion respects `prefers-reduced-motion` because transitions are written through Bootstrap's mixin rather than as bare CSS properties.

The rest is judgement and will always need a person — whether alt text is *meaningful*, whether the tab order is *logical*, whether a control reads sensibly on its own.

## Design Principles

**Brand.** Designs use the UChicago palette and UChicago Sans Serif. Colour values are never transcribed by hand — the [tokens page](/design/tokens/) is generated from the stylesheets and is the reference.

**Restraint.** Uncluttered layouts, generous whitespace, and purposeful typography and imagery. Motion is used sparingly and always respects a reduced-motion preference.

**Reusability.** Components are meant to be copied into other projects. That constrains their dependencies: at runtime a component needs only Bootstrap and Font Awesome. The build tooling — Dart Sass and the token generator — never ships.

**Performance.** What ships is static: compiled stylesheets and Bootstrap's JavaScript, with no runtime of their own. New libraries are added only when there is no reasonable alternative.

## Resources

- [Nielsen Norman Group: 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [axe Accessibility Testing Tools](https://www.deque.com/axe/)
- [WebAIM: Web Accessibility In Mind](https://webaim.org/)
