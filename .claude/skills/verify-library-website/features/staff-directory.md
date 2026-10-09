# Staff directory

The public library directory lists staff with title, contact details, and subject specialties. Visitors can search it by staff name or department, and switch between the staff and departments views. The list comes from staff pages in the CMS.

## Sub-features

- `directory-staff` lists all staff under `All Staff` at `/about/directory/?view=staff`.
- `directory-search` finds staff and departments that match a query, under `Matching Staff` and `Matching Departments`.
- `directory-empty` shows `Sorry, no matches found` in both result sections.
- `directory-departments` switches to the departments view.

## How to get to it (user POV)

- Open `/about/directory/?view=staff` on the public site. `/about/directory/staff/` redirects there.
- Type in `search by department or staff name` and choose `submit search`.
- Choose the `Staff` or `Departments` link above the list.

## Driving it with verify-site.sh

Preconditions:

- `$V doctor` passes.
- The fixture is loaded. It has a staff page for `Julian Bashir`.

- **Staff list.** Open the directory. Run `$V browse --out staff-directory goto "/about/directory/?view=staff" expect "All Staff" shot staff-list aria staff-list`. The title is `Library Directory: Staff - The University of Chicago Library`. `staff-list.aria.yml` has an `article` for each person, with headings such as `About Julian Bashir`.
- **Search by name.** Search for `Bashir`. Run `$V browse --out staff-directory goto "/about/directory/?view=staff" fill "search by department or staff name" "Bashir" click button "submit search" expect-url "query=Bashir" expect "About Julian Bashir" shot search-bashir aria search-bashir`. The page has `heading "Matching Staff"` with one article, `Director of Budget & Facilities`.
- **No matches.** Search for `zzzz`. Run `$V browse --out staff-directory goto "/about/directory/?view=staff&query=zzzz" expect "Sorry, no matches found" shot search-empty`. Both `Matching Departments` and `Matching Staff` show the message.
- **Departments view.** Switch views. Run `$V browse --out staff-directory goto "/about/directory/?view=staff" click link "Departments" expect-url "view=department" shot departments aria departments`. The title is `Library Directory: Departments - The University of Chicago Library`, and the page lists departments such as `Administration` and `Collections & Access`.

## Gotchas

- The staff and departments views read from the CMS, so they work without `DIRECTORY_USERNAME` and `DIRECTORY_PASSWORD`. Sync commands such as `sync_staff_with_directory` and `staff/test_integration.py` need those secrets.
- This page loads jQuery from `//ajax.googleapis.com`. `browse` fetches it over HTTPS. A plain Chrome session on a network that blocks port 80 stays blank until the script times out.
- Staff photos are missing without the dev `media/` files.
- Staff profile pages such as `/staff/wesley-crusher/` live on Loop, not on the public site. See [Loop intranet](./loop-intranet.md).
