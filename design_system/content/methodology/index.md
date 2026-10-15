---
title: "Project Methodology"
order: 5
description: "How this project is built and documented: the goals behind the design system, and where each kind of documentation lives."
---

## Goals

- Consistency and modularity across platforms — Wagtail, VuFind, SpringShare, Aeon, FindIt! and others. The same tabs, search buttons and thumbnails should behave the same everywhere.
- Maintainable by a small team. The system cannot be demanding to keep current.
- Approachable for new or temporary contributors — fellows, new staff, and AI agents — so that questions like "should I make a new class, or is there one already?" have clear answers.
- Built on the latest Bootstrap and Font Awesome, customised through SCSS variables.
- Atomic and cumulative, so the system keeps growing rather than being redesigned from scratch every decade.

## How This Project Is Documented

Documentation drifts when two places can hold the same fact. The rule here is that **a fact lives at the lowest layer that can hold it, and the build distributes it upward.**

| Layer | Where | Who reads it |
| --- | --- | --- |
| **Code and annotations** | `_variables.scss`, `base/`, `components/` | The source of truth. Travels with the change. |
| **Generated output** | Token Tables, `tokens.json`, `/design/llms.txt`, the Markdown source of each page | Anyone consuming the system, including agents |
| **Design system pages** | `design_system/content/foundation/`, `guidelines/`, `implementation/` | Designers and developers using the system |
| **Methodology** | `design_system/content/methodology/` (this section) | People working *on* this project |
| **Contributor checklist** | `design_system/README.md` in the library website repository | People opening a pull request. Links here, states nothing of its own |
| **Agent instructions** | `CLAUDE.md` in the library website repository root | AI agents working on this project |

Three rules follow from it:

1. **If it can be generated, it must be.** Token values, class lists, page indexes and navigation are all derived from the source. None of them is maintained by hand.
2. **If it is in the code, annotate the code.** A note beside a token or a class cannot be separated from the thing it describes. A paragraph on another page can.
3. **These pages hold only what cannot be derived** — the reasoning, the conventions, and the process. Where an agent and a person need the same fact, it is written here once and `CLAUDE.md` points at it.

Standards that constrain the design itself, rather than the process of working on the repository, live with the system they constrain: see [Design Standards](/design/foundation/design-standards/).
