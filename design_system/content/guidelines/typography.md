---
title: "Typography"
description: "Which heading, text style, link and table to use, and what the system changes from Bootstrap's defaults."
---

The typeface is **UChicago Sans Serif**. `main.css` declares it in four weights — Light 300, Regular 400, SemiBold 600 and Bold 700, each with an italic — so no font stylesheet needs loading beside it. The font files are served by UChicago Creative. The full stack, with its system fallbacks, is `$font-family-sans-serif` on the [tokens page](/design/tokens/).

Everything else is Bootstrap 5.3's typography, except where this page says so. [A History of the Book](/design/demos/typography/) shows every element in continuous prose.

## Headings

- Use `<h1>` to `<h6>` in order: one `<h1>` per page, and no level skipped to get a smaller size.
- The system sets their sizes and weights. `<h1>` is maroon, and `<h6>` is uppercase and muted.
- Display headings, `.display-1` to `.display-4`, are for a hero only, and still go on the heading level the outline needs.

## Body Text

- `.lead` is for the introductory paragraph under a page title, once per page.
- `.text-muted` is for secondary information, such as captions, metadata and helper text, and never for anything a reader needs.
- `<small>` is for fine print and legal notices.

## Inline Elements

- `<strong>` marks importance and `<em>` marks stress or a term. Use neither for decoration.
- `<mark>` highlights a match, such as a search term in a result.
- `<del>` and `<ins>` show an edit the reader needs to see. `<s>` marks something no longer accurate, such as a superseded date.
- Avoid `<u>`: underlined text reads as a link.
- `<code>` is for code and `<kbd>` for a key to press. The system gives `<code>` and `<pre>` a tinted background.

## Links

- Links are Lake, from `$link-color`, and never maroon, which is reserved for calls to action. See [Color](/design/guidelines/color/).
- Leave links in the default colour. Of Bootstrap's `.link-*` classes, only `.link-info` matches the interactive role; the others would make a link read as a status.

## Tables

Lists, description lists, code blocks, tables and blockquotes are Bootstrap's, unchanged, and [Bootstrap's documentation](https://getbootstrap.com/docs/5.3/content/tables/) covers their markup. Which table to use:

- `.table` for any data table, inside `.table-responsive`, with a `<caption>` or a heading naming it, and `scope` on the header cells.
- Add `.table-striped` when the rows are long or many, so the eye keeps its line.
- Add `.table-sm` in dense UI, such as a dashboard.
- Add `.table-hover` only when a whole row is a link or an action.
- Avoid `.table-bordered`. Borders group content, and [Grouping Content](/design/guidelines/grouping-content/) keeps them for components.
