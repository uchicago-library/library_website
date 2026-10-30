# Public pages and navigation

Visitors see Wagtail pages on the public site. Every page shares a header with quick links and today's hours, a mega-menu of seven sections, breadcrumbs, a site-wide alert banner and a footer. Page bodies are StreamField content rendered from `PublicBasePage` subclasses.

## Sub-features

- `pages-home` renders the homepage with catalog search tabs, guides, news and quick links.
- `pages-standard` renders a standard page with its H1, breadcrumb and sidebar.
- `pages-megamenu` opens a mega-menu section and lists its links.
- `pages-alert` shows the site-wide alert banner with a "More info..." link.
- `pages-404` returns a styled 404 for an unknown path.

## How to get to it (user POV)

- Open `/` (the homepage).
- Follow any link in the page body or the mega-menu, for example `/borrow/` or `/borrow/borrowing/`.
- Press one of the mega-menu buttons: `Search`, `Borrow & Request`, `Research & Teaching`, `Collections & Exhibits`, `Visit & Study`, `Libraries`, `About`.
- Type a URL directly.

## Driving it with lwv

Preconditions:

- `lwv doctor` is all `ok`.

- **Homepage.** Load `/`. Run `lwv browse / --shot pages/home.png --aria pages/home.aria.txt`. The status is `200` and the title is `The University of Chicago Library - The University of Chicago Library`. The ARIA snapshot has `heading "The University of Chicago Library" [level=1]`, a `tablist "Search"` with `tab "Catalogs" [selected]`, and `navigation "main"`.
- **Alert banner.** Use the same snapshot. An `alert` contains `The Library is online` and `link "More info..."` pointing at `/alerts/alert/`.
- **Standard page.** Load `/borrow/borrowing/`. Run `lwv browse /borrow/borrowing/ --shot pages/borrowing.png --aria pages/borrowing.aria.txt`. The status is `200`, there is a `heading "Borrowing" [level=1]`, and `navigation "breadcrumb"` is present.
- **Mega-menu.** In a `lwv node` script: `await page.goto(url("/"), {waitUntil:"networkidle"}); await page.getByRole("button", { name: "About", exact: true }).click();`. The button gets `[expanded]` in `page.getByRole("navigation", { name: "main" }).ariaSnapshot()`, and the links `About the Library`, `Departments & Staff` and `Library Policies` appear under it.
- **404.** Run `curl -s -o /dev/null -w '%{http_code}' "$PUBLIC_URL/no-such-page-lwv/"`. The output is `404`.
- **Proof.** Keep the home and standard-page `.png` and `.aria.txt` files, plus a capture taken after the mega-menu click (`capture(page, "pages/megamenu-about")`).

## Gotchas

- The page scrolls `<body>`, not the document, so Playwright's `fullPage: true` leaves everything below 900 px blank. Use `fullShot()`/`capture()`/`lwv browse --shot`, which resize the viewport.
- The header hours widget calls LibCal. Offline it may stay `Loading...` or show cached hours. That is not a page failure.
- `/results/` logs `$(...).validateFormBeforeSubmit is not a function` as a page error. It already happens on a clean checkout, so do not attribute it to your change.
- Names like `Search` match both a mega-menu button and form buttons. Pass `exact: true` and scope to `navigation "main"`.
- Anonymous loads can be wagtail-cache hits (`X-Wagtail-Cache: hit`). Clear the cache after changing content.
