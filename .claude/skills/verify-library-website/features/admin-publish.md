# Admin edit and publish

Editors change pages in the Wagtail admin. An editor opens a page, changes a field, and publishes. The public page then shows the new content, and the page history records a new revision.

## Sub-features

- `admin-login` signs an editor in at `/admin/login/` and lands on the admin dashboard or the requested admin page.
- `admin-edit` opens the editor for a page and changes its `Title*` field.
- `admin-publish` publishes from the `More actions` menu and shows a success message.
- `admin-live` shows the published change on the public page and in the database.

## How to get to it (user POV)

- Open `/admin/` on the public site and sign in.
- Choose `Pages` in the sidebar and browse to a page, or open `/admin/pages/<id>/edit/`.
- In the editor footer, choose `More actions`, then `Publish`.

## Driving it with verify-site.sh

Preconditions:

- `$V doctor` passes.
- The fixture is loaded. Page 1755 is `Eckhart Library` at `/eck/`, and it has every required field set.
- `mkdir -p "$VERIFY_EVIDENCE_DIR/admin-publish"` has run.

- **Record the baseline.** Read the page before the edit. Run `$V manage shell -c "from wagtail.models import Page; p = Page.objects.get(id=1755); print(p.title, p.latest_revision_id)" > "$VERIFY_EVIDENCE_DIR/admin-publish/db-before.txt"`. The last line is `Eckhart Library None`. The fixture page has no revision yet.
- **Log in and open the editor.** Run `$V browse --out admin-publish goto /admin/pages/1755/edit/ login expect-url "/admin/pages/1755/edit/" shot editor`. The title is `Editing Standard page: Eckhart Library - Wagtail`.
- **Edit and publish.** Change the title and publish. Run `$V browse --out admin-publish goto /admin/pages/1755/edit/ fill "Title*" "Eckhart Library (verified)" click button "More actions" click button "Publish" expect "has been published" shot published aria published`. The browser lands on the parent page's explorer and shows the success message.
- **See it live.** Open the public page anonymously. Run `$V manage clear_wagtail_cache` and then `$V browse --out admin-publish --fresh goto /eck/ expect "Eckhart Library (verified)" shot live`. The title starts with `Eckhart Library (verified)`.
- **Confirm in the database.** Run `$V manage shell -c "from wagtail.models import Page; p = Page.objects.get(id=1755); print(p.title, p.latest_revision_id, p.live)" > "$VERIFY_EVIDENCE_DIR/admin-publish/db-after.txt"`. The last line shows the new title, a revision ID where `db-before.txt` had `None`, and `True` for `live`.

## Gotchas

- Many fixture pages fail validation on publish because required `Page maintainer` and `Editor` fields are empty. Page 1707 (`Spaces`) is one of them. The editor then shows "The page could not be saved due to validation errors". Use page 1755, or another page whose required fields are set.
- `fill "Title"` without the asterisk can match other title fields on the form. Use the full accessible name `Title*`.
- The `Publish` button is hidden in the `More actions` menu. `click button "Publish"` fails until that menu is open.
- The publish changes the throwaway database until `$V down`. Other recipes that read page 1755 then see the new title.
- Use `--fresh` for the live check, so the page renders as an anonymous visitor sees it. A logged-in session also shows the Wagtail user bar.
