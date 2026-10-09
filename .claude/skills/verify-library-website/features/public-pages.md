# Public pages

Anyone can open the public site without logging in. The home page shows the library search tabs, research guides, and news, and the main navigation opens menus for each section. Content pages such as a library's page render from the CMS.

## Sub-features

- `public-home` renders the home page with the `The University of Chicago Library` heading and the search tablist.
- `public-nav` opens a main navigation menu from its button.
- `public-standard-page` renders a fixture content page by its URL.
- `public-not-found` renders the site's 404 page for an unknown path.

## How to get to it (user POV)

- Open `/` on the public site.
- Choose a button in the `main` navigation, for example `About`.
- Follow a link to a content page, or type its URL, for example `/crerar/`.

## Driving it with verify-site.sh

Preconditions:

- `$V doctor` passes.
- The fixture is loaded. Page `/crerar/` has the title `The John Crerar Library`.
- `mkdir -p "$VERIFY_EVIDENCE_DIR/public-pages"` has run.

- **Home page.** Open the home page anonymously. Run `$V browse --out public-pages --fresh goto / expect "Explore Research Guides" shot home aria home`. `actions.log` shows `status=200` and the title `The University of Chicago Library - The University of Chicago Library`. `home.aria.yml` has `heading "The University of Chicago Library" [level=1]` and `tablist "Search"` with the tabs `Catalogs`, `Articles, Journals & Databases`, and `Website Search`.
- **Main navigation.** Open the `About` menu. Run `$V browse --out public-pages goto / click button "About" shot nav-about aria nav-about`. `nav-about.aria.yml` has `button "About" [expanded]` followed by links such as `About the Library`, and the screenshot shows the open menu.
- **Content page.** Open a library page. Run `$V browse --out public-pages goto /crerar/ expect "The John Crerar Library" shot crerar`. The title starts with `The John Crerar Library`.
- **Not found.** Request a missing path. Run `$V curl public /no-such-page/ -o /dev/null -w '%{http_code}\n' > "$VERIFY_EVIDENCE_DIR/public-pages/404.txt"`. The file contains `404`.

## Gotchas

- The home page catalog and article tabs submit to `/switchboard/`, which redirects to the external catalog. Only `Website Search` stays on this site. See [site search](./site-search.md).
- The `Library hours by building` button can read `Loading...` in a snapshot taken right after the page loads. Do not assert on the hours.
- Fixture images are missing unless the checkout has the dev `media/` files, so image areas render empty.
- Anonymous pages can come from the page cache (`X-Wagtail-Cache: hit`). After an edit, run `$V manage clear_wagtail_cache`.
