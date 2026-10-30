# Collections & Exhibits

`/collex/` is the browse interface for collection and exhibit pages. Users switch between Collections, Exhibits and Subjects, search, filter by subject, format or location, and limit to digital collections or web exhibits. Results are a table with a thumbnail, title, formats or locations, and subjects.

## Sub-features

- `collex-collections` lists collections (the default view).
- `collex-exhibits` lists current exhibits, with sort and location filters.
- `collex-subjects` lists subjects.
- `collex-search` searches within the current view, with an empty-result row.
- `collex-digital` limits collections to digital materials, and `collex-web` limits exhibits to web exhibits.

## How to get to it (user POV)

- Mega-menu `Collections & Exhibits`.
- Open `/collex/` directly. `/collex/collections/` redirects to `/collex/` and `/collex/exhibits/` redirects to `/collex/?view=exhibits`.
- Use the `Switch to Exhibits`/`Switch to Subjects` links, the `search collections` box with `Submit`, and the `limit to digital collections` checkbox.

## Driving it with lwv

Preconditions:

- `lwv doctor` is all `ok`.

- **Collections.** Run `lwv browse /collex/ --shot collex/collections.png --aria collex/collections.aria.txt`. The status is `200`, there is `heading "Collections & Exhibits" [level=1]`, and `link "Currently viewing Collections"`.
- **Search match.** In a `lwv node` script: open `/collex/`, fill `getByRole("searchbox", { name: "search collections" })` with `chicago`, then click `getByRole("button", { name: "Submit" })`. The URL has `search=chicago` and the table has many rows (60 in the fixture), including `Zines`.
- **Search miss.** Search `star` the same way. The table has the row `There were no results for your search.`
- **Digital limit.** Check `getByRole("checkbox", { name: "limit to digital collections" })`. The URL gains `digital=on`, and the first row is `19th-Century Maps of the Middle East, North Africa, and Central Asia`.
- **Exhibits.** Click `getByRole("link", { name: "Switch to Exhibits" })`. The link becomes `Currently viewing Exhibits` and there is a `searchbox "search exhibits"`, a `Sort by Title` button, and a `limit to web exhibits` checkbox. The table header reads `Current Exhibits`.
- **Proof.** Capture before and after each search or limit, and keep the row counts from `page.getByRole("table").getByRole("row").count()`.

## Gotchas

- The row count includes two header rows. Subtract 2 to get the number of results.
- Checking `limit to digital collections` submits the form immediately (no `Submit` click). Wait for `digital=on` in the URL before you assert on the table.
- Collection thumbnails come from `media/`. Missing local media files show as broken images. Report that as an environment limit unless your change touches images.
