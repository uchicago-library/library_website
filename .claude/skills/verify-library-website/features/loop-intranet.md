# Loop intranet

Loop is the staff intranet, served on its own hostname (`loopdev`). Every page under the Loop root requires membership in the `Library` group. Anyone else is redirected to the public no-permission page. Signed-in staff see a news feed home, primary navigation, and a Loop search.

## Sub-features

- `loop-gate` redirects anonymous users to `https://www.lib.uchicago.edu/no-permission/`.
- `loop-home` shows the news feed with author links and the primary navigation.
- `loop-search` shows a result count, a document-library hint, and results with breadcrumbs.
- `loop-nav` links Human Resources, Departments, Committees & Groups, Documents & Policies, Technical Support.

## How to get to it (user POV)

- Open `loop:/` (`$LOOP_URL/`). Production signs in with Shibboleth. The verification run signs in through `loop:/admin/login/` as `lwv_admin`, who is in `Library`.
- Use the `Search Loop` textbox and the `Find` button in the header, or open `loop:/loop-search/?query=<terms>`.

## Driving it with lwv

Preconditions:

- `lwv doctor` is all `ok` (it already checks the anonymous gate).

- **Gate.** Run `curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' "$LOOP_URL/"`. The output is `302 https://www.lib.uchicago.edu/no-permission/`.
- **Home.** Run `lwv browse loop:/ --login --shot loop/home.png --aria loop/home.aria.txt`. The status is `200`. There is `navigation "Primary"` with `link "Human Resources"` and `link "Committees & Groups"`, `heading "News" [level=1]`, and news posts like `heading "Energy discharge in six seconds" [level=2]`.
- **Search.** In a `lwv node` script: `await adminLogin(page, { loop: true }); await page.goto(url("loop:/"));`, fill `getByRole("textbox", { name: "Search Loop" })` with `triolic`, then click `getByRole("button", { name: "Find" })`. The URL is `/loop-search/?query=triolic` and `main` shows `There are 13 Results`, an `alert` linking `Wagtail document library`, and `heading "Triolic waves" [level=2]`.
- **Proof.** Keep the gate curl output plus the home and search captures.

## Gotchas

- Sessions are per hostname. A public-host login (`adminLogin(page)`) does not authenticate `loopdev`. Use `{ loop: true }` or `lwv browse loop:/... --login`.
- `lwv_admin` is a superuser, so the Wagtail userbar (`View Wagtail quick actions`) shows on every page. Don't mistake it for page content.
- The gate is a `before_serve_page` hook plus checks in the Loop search and staff views. Pages outside the Loop tree are not gated, so test the specific page your change touches.
- `/staff/` and `/loop-search/` are routed on both hosts. Run them on `loop:` to exercise the intranet context.
