#!/usr/bin/env bash
# Launch, check, drive, and tear down a throwaway copy of the library website
# for verification. Run with no arguments for usage.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
COMPOSE_FILE="$SKILL_DIR/compose.yml"

PROJECT="${VERIFY_PROJECT:-lw-verify}"
export VERIFY_HTTP_PORT="${VERIFY_HTTP_PORT:-18000}"
RUN_ROOT="${TMPDIR:-/tmp}/verify-library-website/$PROJECT"
STATE_DIR="${VERIFY_STATE_DIR:-$RUN_ROOT/state}"
EVIDENCE_DIR="${VERIFY_EVIDENCE_DIR:-$RUN_ROOT/evidence}"
TOOLS_DIR="${VERIFY_TOOLS_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/verify-library-website}"
LABEL="verify-library-website"
FIXTURE_USERS="darthvader skywalker jyn zoran"

usage() {
	cat <<EOF
Usage: $(basename "$0") <command> [args]

  up                 Build the image, start db/redis/web, load the fixture, wait
                     until the public home page answers.
  doctor             Read-only health check. Exit 0 only if every check passes.
  url SITE [PATH]    Print the URL for SITE (public or loop).
  curl SITE PATH [CURL_ARGS...]
                     curl a path on SITE, resolving its host name to 127.0.0.1.
  browse [OPTIONS] STEP...
                     Drive headless Chrome. See scripts/browse.cjs for steps.
  manage ARGS...     Run manage.py ARGS inside the web container.
  logs               Save web container logs into the evidence directory.
  creds              Print the fixture user names and the run's password.
  down               Save logs, then remove this project's containers, network,
                     and volumes. Keeps the evidence directory.
  tools              Install playwright-core into the tools directory.

Environment:
  VERIFY_PROJECT      Compose project name        (now: $PROJECT)
  VERIFY_HTTP_PORT    Host port for the web server (now: $VERIFY_HTTP_PORT)
  VERIFY_EVIDENCE_DIR Evidence directory           (now: $EVIDENCE_DIR)
  VERIFY_STATE_DIR    Scratch state, removed by down (now: $STATE_DIR)
  VERIFY_TOOLS_DIR    playwright-core install dir  (now: $TOOLS_DIR)
  VERIFY_CHROME       Chrome or Chromium binary    (default: first found on PATH)
EOF
}

compose() {
	docker compose -p "$PROJECT" -f "$COMPOSE_FILE" "$@"
}

say() { printf '%s\n' "$*" >&2; }
die() {
	say "ERROR: $*"
	exit 1
}

# Each fixture site needs its own host name. Both resolve to 127.0.0.1.
site_host() {
	case "$1" in
	public) echo wwwdev ;;
	loop) echo loopdev ;;
	*) die "unknown site '$1' (use public or loop)" ;;
	esac
}

site_url() {
	echo "http://$(site_host "$1"):$VERIFY_HTTP_PORT${2:-/}"
}

# Refuse to touch a Compose project whose containers or volumes were not
# created from this skill's compose.yml.
assert_project_is_ours() {
	local id foreign=""
	for id in $(docker ps -aq --filter "label=com.docker.compose.project=$PROJECT"); do
		if [ "$(docker inspect -f "{{index .Config.Labels \"$LABEL\"}}" "$id")" != "true" ]; then
			foreign="$foreign container:$id"
		fi
	done
	for id in $(docker volume ls -q --filter "label=com.docker.compose.project=$PROJECT"); do
		if [ "$(docker volume inspect -f "{{index .Labels \"$LABEL\"}}" "$id")" != "true" ]; then
			foreign="$foreign volume:$id"
		fi
	done
	for id in $(docker network ls -q --filter "label=com.docker.compose.project=$PROJECT"); do
		if [ "$(docker network inspect -f "{{index .Labels \"$LABEL\"}}" "$id")" != "true" ]; then
			foreign="$foreign network:$id"
		fi
	done
	if [ -n "$foreign" ]; then
		die "Compose project '$PROJECT' has resources this skill did not create:$foreign. Set VERIFY_PROJECT to a different name."
	fi
}

# Print the host:port that the web container publishes, or nothing.
published_port() {
	compose port web 8000 2>/dev/null || true
}

port_in_use() {
	(exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null
}

wait_for() {
	local what="$1" tries="$2"
	shift 2
	local i
	for i in $(seq "$tries"); do
		if "$@" >/dev/null 2>&1; then
			return 0
		fi
		sleep 2
	done
	die "timed out waiting for $what"
}

fingerprint() {
	cat "$REPO_ROOT/Dockerfile" "$REPO_ROOT/requirements.txt" \
		"$REPO_ROOT/requirements-dev.txt" "$COMPOSE_FILE" | sha256sum | cut -d' ' -f1
}

manage() {
	compose exec -T web /venv/bin/python manage.py "$@"
}

cmd_up() {
	assert_project_is_ours
	if [ -z "$(published_port)" ] && port_in_use "$VERIFY_HTTP_PORT"; then
		die "port $VERIFY_HTTP_PORT is taken by something outside project '$PROJECT'. Set VERIFY_HTTP_PORT."
	fi
	mkdir -p "$STATE_DIR" "$EVIDENCE_DIR"

	say "Building the web image (project $PROJECT)..."
	compose build web
	fingerprint >"$STATE_DIR/build-fingerprint"

	say "Starting db and redis..."
	compose up -d db redis
	wait_for "Postgres" 60 compose exec -T db pg_isready -U vagrant -d lib_www_dev

	say "Starting web..."
	compose up -d web
	wait_for "the web container" 30 compose exec -T web true

	say "Applying migrations..."
	manage migrate --noinput

	if [ "$(manage shell -c "from wagtail.models import Site; print(Site.objects.filter(hostname='loopdev').exists())" | tail -1)" != "True" ]; then
		say "Loading base/fixtures/test.json (takes a few minutes)..."
		manage loaddata /app/base/fixtures/test.json
		say "Rebuilding the search index..."
		manage update_index
	else
		say "Fixture already loaded; skipping loaddata."
	fi

	# Match the fixture sites to the host port, drop the default localhost site
	# (as docker-setup.sh does), and give every fixture user one password.
	local password
	password="$(od -An -N12 -tx1 /dev/urandom | tr -d ' \n')"
	manage shell -c "
from django.contrib.auth import get_user_model
from wagtail.models import Site
Site.objects.filter(hostname='localhost').delete()
Site.objects.filter(hostname__in=['wwwdev', 'loopdev']).update(port=$VERIFY_HTTP_PORT)
for user in get_user_model().objects.filter(username__in='$FIXTURE_USERS'.split()):
    user.set_password('$password')
    user.save()
"
	printf '%s\n' "$password" >"$STATE_DIR/password"
	chmod 600 "$STATE_DIR/password"

	compose exec -T web bash -c \
		"mkdir -p /app/static/lib_news/files && cp /app/base/fixtures/news-feed-test.json /app/static/lib_news/files/lib-news.json"

	say "Waiting for the public home page..."
	wait_for "the web server" 90 curl -fsS -o /dev/null \
		--resolve "wwwdev:$VERIFY_HTTP_PORT:127.0.0.1" "$(site_url public /)"
	say "Ready."
	say "  Public: $(site_url public /)"
	say "  Loop:   $(site_url loop /)"
	say "  Evidence: $EVIDENCE_DIR"
}

check() {
	local name="$1"
	shift
	if "$@"; then
		printf 'PASS  %s\n' "$name"
	else
		printf 'FAIL  %s\n' "$name"
		DOCTOR_FAILED=1
	fi
}

docker_answers() {
	docker info --format '{{.ServerVersion}}' >/dev/null 2>&1
}

container_running() {
	local id
	id="$(compose ps -q "$1" 2>/dev/null)"
	[ -n "$id" ] && [ "$(docker inspect -f '{{.State.Running}}' "$id")" = "true" ]
}

mount_is_this_checkout() {
	local id src
	id="$(compose ps -q web 2>/dev/null)"
	[ -n "$id" ] || return 1
	src="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/app"}}{{.Source}}{{end}}{{end}}' "$id")"
	[ "$src" = "$REPO_ROOT" ]
}

port_is_ours() {
	[ "$(published_port)" = "127.0.0.1:$VERIFY_HTTP_PORT" ]
}

image_is_current() {
	[ -f "$STATE_DIR/build-fingerprint" ] && [ "$(cat "$STATE_DIR/build-fingerprint")" = "$(fingerprint)" ]
}

public_home_ok() {
	curl -fsS --max-time 60 --resolve "wwwdev:$VERIFY_HTTP_PORT:127.0.0.1" \
		"$(site_url public /)" | tr -s '[:space:]' ' ' |
		grep -q "<title> The University of Chicago Library"
}

loop_requires_login() {
	local location
	location="$(curl -sS -o /dev/null --max-time 60 -w '%{redirect_url}' \
		--resolve "loopdev:$VERIFY_HTTP_PORT:127.0.0.1" "$(site_url loop /)")"
	[ "$location" = "https://www.lib.uchicago.edu/no-permission/" ]
}

sites_match_port() {
	[ "$(manage shell -c "from wagtail.models import Site; print(sorted(Site.objects.values_list('hostname', 'port')))" | tail -1)" \
		= "[('loopdev', $VERIFY_HTTP_PORT), ('wwwdev', $VERIFY_HTTP_PORT)]" ]
}

login_works() {
	[ -f "$STATE_DIR/password" ] || return 1
	[ "$(manage shell -c "
from django.contrib.auth import authenticate
print(authenticate(username='darthvader', password='$(cat "$STATE_DIR/password")') is not None)
" | tail -1)" = "True" ]
}

cmd_doctor() {
	DOCTOR_FAILED=0
	printf 'project=%s port=%s checkout=%s\n' "$PROJECT" "$VERIFY_HTTP_PORT" "$REPO_ROOT"
	printf 'revision=%s uncommitted_files=%s\n' \
		"$(git -C "$REPO_ROOT" rev-parse --short HEAD)" \
		"$(git -C "$REPO_ROOT" status --porcelain | wc -l | tr -d ' ')"
	printf 'evidence=%s\n' "$EVIDENCE_DIR"
	check "docker daemon answers" docker_answers
	check "project resources carry the skill label" assert_project_is_ours
	check "web container running" container_running web
	check "db container running" container_running db
	check "redis container running" container_running redis
	check "web container mounts this checkout at /app" mount_is_this_checkout
	check "web publishes 127.0.0.1:$VERIFY_HTTP_PORT" port_is_ours
	check "image matches Dockerfile and requirements (else rerun up)" image_is_current
	check "fixture sites use port $VERIFY_HTTP_PORT" sites_match_port
	check "public home page renders" public_home_ok
	check "anonymous Loop request redirects to no-permission" loop_requires_login
	check "darthvader can log in with the run's password" login_works
	return "$DOCTOR_FAILED"
}

cmd_curl() {
	[ $# -ge 2 ] || die "usage: curl SITE PATH [CURL_ARGS...]"
	local site="$1" path="$2"
	shift 2
	curl -sS --resolve "$(site_host "$site"):$VERIFY_HTTP_PORT:127.0.0.1" "$@" "$(site_url "$site" "$path")"
}

find_chrome() {
	if [ -n "${VERIFY_CHROME:-}" ]; then
		echo "$VERIFY_CHROME"
		return
	fi
	local candidate
	for candidate in google-chrome google-chrome-stable chromium chromium-browser; do
		if command -v "$candidate" >/dev/null; then
			command -v "$candidate"
			return
		fi
	done
}

cmd_tools() {
	if [ ! -d "$TOOLS_DIR/node_modules/playwright-core" ]; then
		mkdir -p "$TOOLS_DIR"
		npm install --silent --prefix "$TOOLS_DIR" playwright-core@1 >&2
	fi
	if [ -z "$(find_chrome)" ]; then
		say "No Chrome or Chromium on PATH; downloading Playwright's Chromium."
		"$TOOLS_DIR/node_modules/.bin/playwright-core" install chromium >&2
	fi
}

cmd_browse() {
	cmd_tools
	[ -f "$STATE_DIR/password" ] || die "no run password in $STATE_DIR; run up first"
	mkdir -p "$EVIDENCE_DIR"
	NODE_PATH="$TOOLS_DIR/node_modules" \
		VERIFY_CHROME="$(find_chrome)" \
		VERIFY_HTTP_PORT="$VERIFY_HTTP_PORT" \
		VERIFY_EVIDENCE_DIR="$EVIDENCE_DIR" \
		VERIFY_STATE_DIR="$STATE_DIR" \
		node "$SKILL_DIR/scripts/browse.cjs" "$@"
}

cmd_logs() {
	mkdir -p "$EVIDENCE_DIR"
	local out
	out="$EVIDENCE_DIR/web-$(date +%Y%m%dT%H%M%S).log"
	compose logs --no-color web >"$out" 2>&1 || true
	compose exec -T web cat /var/log/django-errors.log >>"$out" 2>/dev/null || true
	say "Saved $out"
}

cmd_down() {
	assert_project_is_ours
	if [ -n "$(compose ps -q web 2>/dev/null)" ]; then
		cmd_logs
	fi
	compose down -v --remove-orphans
	rm -rf "$STATE_DIR"
	rmdir "$RUN_ROOT" "$(dirname "$RUN_ROOT")" 2>/dev/null || true
	say "Removed project $PROJECT. Evidence kept in $EVIDENCE_DIR"
}

main() {
	local command="${1:-}"
	[ $# -gt 0 ] && shift
	case "$command" in
	up) cmd_up ;;
	doctor) cmd_doctor ;;
	url) site_url "${1:?SITE required}" "${2:-/}" ;;
	curl) cmd_curl "$@" ;;
	browse) cmd_browse "$@" ;;
	manage) manage "$@" ;;
	logs) cmd_logs ;;
	creds) printf 'users: %s\npassword: %s\n' "$FIXTURE_USERS" "$(cat "$STATE_DIR/password")" ;;
	down) cmd_down ;;
	tools) cmd_tools ;;
	*)
		usage
		[ -z "$command" ] || exit 2
		;;
	esac
}

main "$@"
