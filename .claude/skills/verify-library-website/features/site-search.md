# Site search

Website search finds CMS pages by text. On the public site, a visitor searches from the `Website Search` tab on the home page and gets a `Search Results` page. On Loop, a logged-in staff member searches from the `Search Loop` box in the header.

## Sub-features

- `search-public-tab` submits a query from the home page `Website Search` tab and lands on `/results/?query=<query>`.
- `search-public-results` lists matching public pages, for example `Crerar Lounge` for `Crerar`.
- `search-loop` submits a query from the Loop header and lands on `/loop-search/?query=<query>` with a result count.
- `search-public-empty` and `search-loop-empty` show `No results found` for a query with no matches.

## How to get to it (user POV)

- On the public home page, choose the `Website Search` tab, type in `Search the Library website`, and press Enter.
- Open `/results/?query=<query>` on the public site.
- On any Loop page, type in `Search Loop` and choose `Find`.
- Open `/loop-search/?query=<query>` on Loop.

## Driving it with verify-site.sh

Preconditions:

- `$V doctor` passes.
- For Loop steps, the browser is logged in to Loop. See [Loop intranet](./loop-intranet.md).

- **Public search from the home tab.** Search for `Crerar`. Run `$V browse --out site-search goto / click tab "Website Search" fill "Search the Library website" "Crerar" press Enter expect-url "/results/?query=Crerar" expect "Crerar Lounge" shot public-results aria public-results`. `actions.log` shows the title `Search - The University of Chicago Library`. `public-results.aria.yml` has `heading "Search Results" [level=1]` and `link "Crerar Lounge"`.
- **Public search by URL.** Open the results page directly. Run `$V browse --out site-search goto "/results/?query=Crerar" expect "Crerar Lounge"`. The page shows the same result.
- **Public empty result.** Search for `zzzz`. Run `$V browse --out site-search goto "/results/?query=zzzz" expect "No results found" shot public-empty`.
- **Loop search.** Search Loop for `triolic`. Run `$V browse --site loop --out site-search goto / fill "Search Loop" "triolic" click button "Find" expect-url "/loop-search/?query=triolic" expect "There are 13 Results" shot loop-results aria loop-results`. The results include `heading "Triolic waves" [level=2]`.
- **Loop empty result.** Search Loop for `koala`. Run `$V browse --site loop --out site-search goto "/loop-search/?query=koala" expect "No results found" shot loop-empty`.

## Gotchas

- The home page tab panel needs a click on `Website Search` before its field is visible. A `fill` without that click fails after 30 seconds.
- The public form posts to `/switchboard/`, which redirects to `/results/`. A direct GET of `/switchboard/` returns 500, so do not use that as a check.
- The search uses Wagtail's database backend and the index that `up` builds. A page you publish during a run appears in results only after `$V manage update_index`.
- `/loop-search/` without a Loop login redirects to the live no-permission page.
