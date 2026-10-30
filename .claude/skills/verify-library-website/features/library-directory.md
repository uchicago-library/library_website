# Library directory

The directory at `/about/directory/` lets visitors find staff and departments. It has three views (Staff, Departments, Org Chart), a search box for department or staff names, and department links that filter the staff list.

## Sub-features

- `dir-staff` lists staff (the default view).
- `dir-department` lists departments as a hierarchy, with phone and building.
- `dir-org` shows the org chart view.
- `dir-search` searches by staff or department name and shows "Matching Departments" and "Matching Staff".
- `dir-filter` filters staff by department from a department link.

## How to get to it (user POV)

- Mega-menu `About`, then `Departments & Staff`.
- Open `/about/directory/` directly, then use the `Staff`, `Departments` and `Org Chart` links.
- `/about/directory/staff/` redirects to `/about/directory/?view=staff`.

## Driving it with lwv

Preconditions:

- `lwv doctor` is all `ok`.

- **Default view.** Run `lwv browse /about/directory/ --shot dir/staff.png --aria dir/staff.aria.txt`. The status is `200`. `main` has `searchbox "search by department or staff name"` and the links `Staff`, `Departments`, `Org Chart`.
- **Departments.** Run `lwv browse "/about/directory/?view=department" --aria dir/dept.aria.txt`. There is `heading "Library Directory: Departments" [level=1]`, `heading "Administration" [level=2]` and `heading "Collections & Access" [level=2]`.
- **Search.** In a `lwv node` script: open `/about/directory/`, fill `getByRole("searchbox", { name: "search by department or staff name" })` with `picard`, then click `getByRole("button", { name: "submit search" })`. The URL contains `query=picard`, `heading "Matching Staff" [level=2]` lists an article `About Jean-Luc Picard`, and "Matching Departments" says `Sorry, no matches found`.
- **Department filter.** From the departments view, click `getByRole("link", { name: "View all Administration staff" })`. The URL is `?view=staff&department=Administration` and only Administration staff are listed.
- **Org chart.** Run `lwv browse "/about/directory/?view=org" --shot dir/org.png`. The status is `200`.
- **Proof.** Capture each view, plus the search before and after submitting.

## Gotchas

- Anonymous directory responses are cached by wagtail-cache like any other page (`X-Wagtail-Cache: hit` on repeat loads). Clear the cache after editing staff or units.
- The fixture's staff are fictional (Star Trek names). Assert on names that are in the fixture, such as `Jean-Luc Picard` and `Wesley Crusher`.
- The first load takes about 2 s because the full staff list is rendered.
