# Website search

The public "Website Search" finds live pages under the public homepage. It excludes unit pages and the restricted section. Results show the title link, the section and the last-updated date.

## Sub-features

- `search-match` lists matching pages for a query.
- `search-none` shows `No results found` for a query with no matches.
- `search-empty` loads the results page with no query.
- `search-home-tab` submits from the homepage `Website Search` tab.

## How to get to it (user POV)

- On the homepage, choose the `Website Search` tab in the search box and submit a query.
- Open `/results/?query=<terms>` directly. The results page also has its own textbox and `Search` button.

## Driving it with lwv

Preconditions:

- `lwv doctor` is all `ok`.

- **Match.** Search `borrow`. Run `lwv browse "/results/?query=borrow" --shot search/borrow.png --aria search/borrow.aria.txt`. Under `main` there is `heading "Search Results" [level=1]` and `textbox: borrow`, and the list contains `link "Borrowing"` (`/borrow/borrowing/`) and `link "Borrow & Request"` (`/borrow/`).
- **No match.** Search `zzqxv`. Run `lwv browse "/results/?query=zzqxv" --aria search/none.aria.txt`. `main` contains the text `No results found` and no list.
- **Empty query.** Run `lwv browse /results/ --aria search/empty.aria.txt`. The status is `200` and there is no result list.
- **Homepage tab.** In a `lwv node` script: open `/`, click `getByRole("tab", { name: "Website Search" })`, fill the now-visible input whose `aria-label` is `Search the Library website` (`page.locator('input[aria-label="Search the Library website"]')`), and press Enter. The browser lands on `/results/?query=...` with the same results as the direct URL. Capture it with `capture(page, "search/home-tab")`.
- **Proof.** Keep the match and no-match ARIA snapshots and screenshots. For the homepage tab, also keep the final URL.

## Gotchas

- With no query, the textbox shows the literal value `None`. That happens on a clean checkout, so do not report it as caused by your change.
- The run uses the database search backend, not Elasticsearch. Ranking differs from production, so assert membership in the results, not order.
- Newly published pages are only searchable once indexed. Publishing through the admin indexes them; editing data in `lwv manage shell` does not.
- `$(...).validateFormBeforeSubmit is not a function` is a known page error on this route.
