# Admin edit and publish

Editors sign in to the Wagtail admin at `/admin/`, edit a page and publish it. The new content then appears on the live site. This is the path for proving changes to page models, StreamField blocks, admin panels or hooks.

## Sub-features

- `admin-login` signs in through the `/admin/login/` form.
- `admin-edit` opens a page's edit view and changes a field.
- `admin-publish` publishes from the `More actions` menu and shows a success message.
- `admin-live` shows the published content to anonymous visitors once the page cache is cleared.
- `admin-revision` records a new revision row with the page's title updated.

## How to get to it (user POV)

- Open `/admin/`, sign in, then go to Pages, the page, and `Edit`.
- Open `/admin/pages/<id>/edit/` directly.
- Use the userbar `View Wagtail quick actions` on a live page, then `Edit this page`.

## Driving it with lwv

Preconditions:

- `lwv doctor` is all `ok`.
- The target is page `3007` (`Borrowing`, a `StandardPage` at `/borrow/borrowing/`). Pick a different page if it was already edited in this run.

- **Whole flow.** Run `lwv node .claude/skills/verify-library-website/lib/flows/admin-edit-publish.mjs 3007 /borrow/borrowing/ "Borrowing LWV-<run>"`. Exit code `0`. `$ARTIFACTS/admin-edit-publish/3007/report.json` records `oldTitle: "Borrowing"`, `adminMessage` starting with `Page 'Borrowing LWV-<run>' has been published.`, `public-before.h1: "Borrowing"` and `public-after-clear.h1` equal to the new title.
- **Login.** The flow fills `#id_username` and `#id_password` and clicks `button "Sign in"`, then waits until the URL leaves `/admin/login`.
- **Edit and publish.** The flow fills `#id_title` on `/admin/pages/3007/edit/`, clicks `button "More actions"`, then `button "Publish"`. The browser lands on the parent's listing `/admin/pages/1668/` with the success message.
- **Live check.** The flow loads the page anonymously right after publishing (`public-after`) and records `staleAfterPublish`. It then runs `lwv manage clear_wagtail_cache` and loads the page again (`public-after-clear`), whose H1 must be the new title.
- **DB side effect.** Run `lwv sql "select p.title, p.live, p.has_unpublished_changes, r.created_at from wagtailcore_page p join wagtailcore_revision r on r.id = p.latest_revision_id where p.id = 3007"`. The title is the new one, `live = t`, `has_unpublished_changes = f`, and `created_at` is within the run.
- **Proof.** Keep the `admin-edit-publish/3007/` directory (`public-before`, `admin-edited`, `admin-published`, `public-after`, `public-after-clear` captures and `report.json`) plus the SQL output.

## Gotchas

- Publishing does not purge wagtail-cache. If the page was cached before the edit, anonymous visitors keep the old version (`X-Wagtail-Cache: hit`) until `clear_wagtail_cache` runs or the 6-hour timeout passes. The flow reports this as `staleAfterPublish: true`, which is current behavior and not a failure. Report it only if your change is about cache invalidation.
- Admin pages are never cached for logged-in users, so the admin "View live" link can show the new title while anonymous visitors still get the old page.
- Mutations persist for the rest of the run. Run this recipe last, or use a fresh `lwv up` for a clean baseline.
- When editing StreamField content, wait for the block chooser to render before filling fields. Assert on the success message, not the button click.
