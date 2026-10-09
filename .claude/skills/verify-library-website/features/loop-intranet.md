# Loop intranet

Loop is the staff intranet. An anonymous visitor is sent to the live site's no-permission page. A member of the `Library` group who logs in sees the Loop home page with news items, and can browse departments, groups, and staff profiles.

## Sub-features

- `loop-denied` redirects an anonymous request for any Loop page to `https://www.lib.uchicago.edu/no-permission/`.
- `loop-login` signs a `Library` member in through the Wagtail login form and returns them to the Loop page they asked for.
- `loop-home` shows the Loop home page with the `News` heading, news items, and the primary navigation.
- `loop-departments` lists departments and units.
- `loop-groups` lists committees and groups.
- `loop-staff-page` shows a staff member's Loop profile.

## How to get to it (user POV)

- Open `/` on Loop. Anonymous visitors are redirected away.
- Open `/admin/login/` on Loop, sign in, and return to `/`.
- Choose `Departments` or `Committees & Groups` in the `Primary` navigation.
- Follow an author link from a news item to a staff profile, for example `/staff/wesley-crusher/`.

## Driving it with verify-site.sh

Preconditions:

- `$V doctor` passes, including the check `anonymous Loop request redirects to no-permission`.
- `mkdir -p "$VERIFY_EVIDENCE_DIR/loop-intranet"` has run.

- **Anonymous redirect.** Request Loop with no session. Run `$V curl loop / -o /dev/null -w '%{http_code} %{redirect_url}\n' > "$VERIFY_EVIDENCE_DIR/loop-intranet/anonymous.txt"`. The file contains `302 https://www.lib.uchicago.edu/no-permission/`.
- **Record the login baseline.** Read the user's last login before you sign in. Run `$V manage shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.get(username='darthvader').last_login)" > "$VERIFY_EVIDENCE_DIR/loop-intranet/last-login-before.txt"`. The last line shows the timestamp from the fixture.
- **Log in.** Open Loop and sign in. Run `$V browse --site loop --out loop-intranet --fresh goto / login expect-url loopdev expect "Energy discharge in six seconds" shot loop-home aria loop-home`. In `actions.log`, the `goto` line ends on the live no-permission or Turnstile page, and the `login` line ends at `http://loopdev:<port>/` with the title `Loop`. `loop-home.aria.yml` has `navigation "Primary"` with `Departments` and `Committees & Groups`, and `heading "News" [level=1]` above news items such as `Energy discharge in six seconds`.
- **Confirm the login on the server.** Read the last login again. Run `$V manage shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.get(username='darthvader').last_login)" > "$VERIFY_EVIDENCE_DIR/loop-intranet/last-login-after.txt"`. The timestamp is from this run and later than the baseline.
- **Departments.** Choose `Departments`. Run `$V browse --site loop --out loop-intranet goto / click link "Departments" expect "Departments & Units" shot departments`. The URL ends in `/departments/` and the page lists `Bridge` and `Ten Forward`.
- **Groups.** Choose `Committees & Groups`. Run `$V browse --site loop --out loop-intranet goto / click link "Committees & Groups" expect "Warp Drive Working Group (WDWG)" shot groups`. The URL ends in `/groups/`.
- **Staff profile.** Open a staff profile. Run `$V browse --site loop --out loop-intranet goto /staff/wesley-crusher/ expect "Web Developer and Graphic Design Specialist" shot staff-page`. The title is `Wesley Crusher`.

## Gotchas

- Landing on `https://www.lib.uchicago.edu/no-permission/`, or on the live Turnstile page "Site Protection - Verification Required", means the local Loop login is missing. It is not a site outage. Add the `login` step with `--site loop`. A login on `--site public` does not carry over, because the session cookie belongs to one host name.
- `--fresh` starts an anonymous browser and, when it exits, replaces the saved cookies for that site. Use it on Loop only on the first call, to prove the anonymous redirect and the login.
- `/human-resources/` returns 404 in the fixture, although the navigation links to it.
- `/mailaliases/` shows "We're having a problem with our systems" because it needs the campus directory.
- All fixture users are in `Library`. To see the denial for a logged-in user, remove that group from a user in the throwaway database first.
