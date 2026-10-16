# Design system

This app documents itself. Before changing anything here, read the pages in
`content/contributing/`: `index.md`, then `architecture.md` and
`conventions.md`. They are the documentation for agents and people alike, so
this file only points at them.

- **Update the documentation in the same change as the code.** If a change
  alters a rule, a file location, a published URL, a build step or what a
  reader must know, edit the page that holds that fact. The rule for which
  page that is, is "How This Project Is Documented" in
  `content/contributing/index.md`.
- **Done means** the definition of done in `content/contributing/conventions.md`:
  `npm run build:design-system` with its output committed, then
  `./manage.py test design_system`.
