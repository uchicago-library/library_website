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

## Where Each Reader Starts

Every reader has one entry point, and it must surface what that reader cannot afford to miss — stated there, or linked from it prominently, never left for them to find. When something critical changes for a reader, check that their entry point still surfaces it.

| Reader | Entry point | It must cover |
| --- | --- | --- |
| **Developer building with the system** — a new project, or a library website template | [Getting Started](/design/implementation/using-ucld/), from "Build with It" on the home page | The one stylesheet to load and its URL; that it replaces Bootstrap's own CSS; Bootstrap's JavaScript and the icon set; taking values from the [Token Tables](/design/implementation/token-tables/) rather than writing them out; the checklist before shipping |
| **Designer or project owner** reviewing decisions | [Foundation](/design/foundation/), from "Review Its Decisions" | The priorities; the palette and how much of each colour to use; the accessibility standard; where the system currently leans between competing values |
| **Contributor** changing the system | This page, from "Contribute to It" | How to build and check a change ([Setup](/design/methodology/setup/)); where every file lives ([Architecture](/design/methodology/architecture/)); the conventions and the definition of done ([Conventions](/design/methodology/conventions/)); that consumers load the stylesheet unversioned, so nothing public is renamed or removed |
| **Developer reading the code** — a reviewer or maintainer on GitHub | `design_system/README.md`, which GitHub shows when the folder is opened | The build command and committing its output; the public URLs; what the token documentation depends on; the traps that fail silently; a pointer to this section |
| **Agent building with the system** — the playground, or another project | [/design/llms.txt](/design/llms.txt) | Every page with its description, linked as Markdown; the token JSON; where to start loading the system |
| **Agent working on the library website** | `CLAUDE.md` in the repository root, which points to `design_system/README.md` | The build commands and that CI checks their output |
| **Mockup author** | The [playground](https://github.com/uchicago-library/ucld) repository and its `new-mockup` skill | Outside this site. It loads the published stylesheets and reads `llms.txt` for the rules |

## How This Project Is Documented

Documentation drifts when two places can hold the same fact. The rule here is that **a fact lives at the lowest layer that can hold it, and the build distributes it upward.**

| Layer | Where | Who reads it |
| --- | --- | --- |
| **Code and annotations** | `_variables.scss`, `base/`, `components/` | The source of truth. Travels with the change. |
| **Generated output** | Token Tables, `tokens.json`, `/design/llms.txt`, the Markdown source of each page | Anyone consuming the system, including agents |
| **Design system pages** | `design_system/content/foundation/`, `guidelines/`, `implementation/` | Designers and developers using the system |
| **Methodology** | `design_system/content/methodology/` (this section) | People working *on* this project |
| **Code entry point** | `design_system/README.md` in the library website repository | Developers reading the code. Holds the build, the public URLs and the traps; links here for everything else |
| **Agent instructions** | `CLAUDE.md` in the library website repository root | AI agents working on this project |

Three rules follow from it:

1. **If it can be generated, it must be.** Token values, class lists, page indexes and navigation are all derived from the source. None of them is maintained by hand.
2. **If it is in the code, annotate the code.** A note beside a token or a class cannot be separated from the thing it describes. A paragraph on another page can.
3. **These pages hold only what cannot be derived** — the reasoning, the conventions, and the process. Where an agent and a person need the same fact, it is written here once and `CLAUDE.md` points at it.

Standards that constrain the design itself, rather than the process of working on the repository, live with the system they constrain: see [Design Standards](/design/foundation/design-standards/).
