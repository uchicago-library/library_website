---
title: "Setup & Installation"
description: "Run the design system documentation locally and rebuild its stylesheets after changing the SCSS."
---

## Prerequisites

The design system is part of the [library website](https://github.com/uchicago-library/library_website). Set up that project first, following its README; the Docker setup installs Node and the npm packages the design system needs.

## Building the Stylesheets

After any change under `design_system/scss/`, rebuild and commit the output:

```bash
npm run build:design-system
```

This compiles `main.css`, `main-libapps.css` and `meta.css` into `design_system/static/design_system/css/`, copies Bootstrap's JavaScript beside them, and regenerates `design_system/data/tokens.json` for the tokens page. `npm run build` runs it too, after the webpack build.

While editing SCSS, recompile on every save instead:

```bash
npm run watch:design-system
```

The watcher compiles the stylesheets only. Run `npm run build:design-system` before committing, so `tokens.json` is regenerated as well.

## Viewing the Documentation

Start the library website's development server and open `http://localhost:8000/design/`. Pages under `design_system/content/` and their templates are re-read on every request in development, so edits show on reload.

## Available npm Scripts

| Command | Description |
| --- | --- |
| `npm run build` | The webpack build, then `build:design-system` |
| `npm run build:design-system` | Compile the stylesheets, copy Bootstrap's JavaScript, regenerate `tokens.json` |
| `npm run build:design-system:css` | Compile the stylesheets only |
| `npm run build:design-system:tokens` | Regenerate `tokens.json` only |
| `npm run watch:design-system` | Recompile the stylesheets on every change |

## Checking a Change

```bash
./manage.py test design_system
```

The tests render every page under `/design/` and fail on an error or a broken internal link. CI also rebuilds the stylesheets and `tokens.json` and fails if the committed copies are out of date.

## Next Steps

- **[System architecture: structure, tokens, and what is generated](/design/contributing/architecture/)**
- **[Conventions and the definition of done](/design/contributing/conventions/)**
