#!/usr/bin/env python3
"""
FamilySearch API CLI — read-only access to the FamilySearch Family Tree.

Usage:
    python3 scripts/familysearch.py <command> [options]

Commands:
    config             Store app key and environment settings
    auth               Authenticate via OAuth2 (opens browser)
    verify             Confirm authentication works
    get-person         Fetch a person by PID
    get-current-user   Fetch the authenticated user's tree person
    ancestry           Ascending pedigree (ancestors)
    descendancy        Descending pedigree (descendants)
    search             Search persons in the Family Tree
    search-records     Search historical record collections
    match              Get research hints for a person
    parents            List a person's parents
    spouses            List a person's spouses
    children           List a person's children
    relationship-path  Find the relationship path between two persons
    sources            List sources attached to a person
    memories           List memories attached to a person
    download-memory    Download a memory artifact to local filesystem
    export-person      Export a person and their network as JSON

Requires: httpx (pip install httpx)
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import subprocess
import sys
import time
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Any

try:
    import httpx
except ImportError:
    sys.exit(
        "httpx is required: pip install httpx\n"
        "  or: pip install --break-system-packages httpx"
    )

# ── Constants ─────────────────────────────────────────────────────────

CONFIG_DIR = Path.home() / ".familysearch"
CONFIG_FILE = CONFIG_DIR / "config.json"
TOKEN_FILE = CONFIG_DIR / "token.json"

# Pre-registered client ID from getmyancestors — no developer account needed
DEFAULT_CLIENT_ID = "a02j000000KTRjpAAH"
DEFAULT_REDIRECT_URI = "https://misbach.github.io/fs-auth/index_raw.html"

BASE_URLS = {
    "integration": "https://integration.familysearch.org",
    "production": "https://api.familysearch.org",
}

# Auth endpoints always use ident.familysearch.org
AUTH_BASE = "https://ident.familysearch.org"
LOGIN_BASE = "https://www.familysearch.org"
SEARCH_BASE = "https://www.familysearch.org"

GEDCOMX_JSON = "application/x-gedcomx-v1+json"
GEDCOMX_ATOM = "application/x-gedcomx-atom+json"

MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, doubled each retry


# ── Config helpers ────────────────────────────────────────────────────


def load_config() -> dict[str, Any]:
    """Load config from ~/.familysearch/config.json."""
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text())


def save_config(cfg: dict[str, Any]) -> None:
    """Persist config to ~/.familysearch/config.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def load_token() -> dict[str, Any]:
    """Load stored OAuth2 token."""
    if not TOKEN_FILE.exists():
        return {}
    return json.loads(TOKEN_FILE.read_text())


def save_token(tok: dict[str, Any]) -> None:
    """Persist OAuth2 token."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(tok, indent=2))


def get_base_url(cfg: dict[str, Any]) -> str:
    """Resolve the base URL for the active environment."""
    env = cfg.get("environment", "production")
    return BASE_URLS.get(env, BASE_URLS["production"])


def get_client_id(cfg: dict[str, Any]) -> str:
    """Get the OAuth2 client ID, falling back to the pre-registered default."""
    return cfg.get("app_key", DEFAULT_CLIENT_ID)


def get_redirect_uri(cfg: dict[str, Any]) -> str:
    """Get the OAuth2 redirect URI, falling back to the default."""
    return cfg.get("redirect_uri", DEFAULT_REDIRECT_URI)


def require_config() -> dict[str, Any]:
    """Load config, using defaults if no config file exists."""
    cfg = load_config()
    # No longer require explicit app_key — we have a default
    return cfg


def require_token() -> dict[str, Any]:
    """Load token or exit with auth instructions."""
    tok = load_token()
    if not tok.get("access_token"):
        sys.exit(
            "Not authenticated. Run:\n"
            "  python3 scripts/familysearch.py auth"
        )
    return tok


# ── HTTP client ───────────────────────────────────────────────────────


def make_client(cfg: dict[str, Any], tok: dict[str, Any]) -> httpx.Client:
    """Create an httpx client with auth headers for API requests."""
    base = get_base_url(cfg)
    return httpx.Client(
        base_url=base,
        headers={
            "Authorization": f"Bearer {tok['access_token']}",
            "Accept": GEDCOMX_JSON,
        },
        timeout=30.0,
        follow_redirects=True,
    )


def refresh_token_if_needed(cfg: dict[str, Any], tok: dict[str, Any]) -> dict[str, Any]:
    """Refresh the access token if it's expired or about to expire."""
    expires_at = tok.get("expires_at", 0)
    if time.time() < expires_at - 60:
        return tok  # still valid

    refresh = tok.get("refresh_token")
    if not refresh:
        sys.exit("Token expired and no refresh token available. Re-run: python3 scripts/familysearch.py auth")

    client_id = get_client_id(cfg)
    resp = httpx.post(
        f"{AUTH_BASE}/cis-web/oauth2/v3/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "client_id": client_id,
        },
    )

    if resp.status_code != 200:
        sys.exit(f"Token refresh failed ({resp.status_code}): {resp.text}\nRe-run: python3 scripts/familysearch.py auth")

    data = resp.json()
    tok["access_token"] = data["access_token"]
    tok["expires_at"] = time.time() + data.get("expires_in", 7200)
    if "refresh_token" in data:
        tok["refresh_token"] = data["refresh_token"]
    save_token(tok)
    return tok


def api_get(
    client: httpx.Client,
    path: str,
    params: dict[str, Any] | None = None,
    accept: str | None = None,
) -> dict[str, Any]:
    """GET request with retry and backoff."""
    headers = {}
    if accept:
        headers["Accept"] = accept

    backoff = RETRY_BACKOFF
    for attempt in range(MAX_RETRIES):
        resp = client.get(path, params=params, headers=headers)

        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 204:
            return {"status": "no_content"}
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", backoff))
            time.sleep(retry_after)
            backoff *= 2
            continue
        if resp.status_code == 401:
            sys.exit("Authentication expired. Re-run: python3 scripts/familysearch.py auth")
        if resp.status_code == 403:
            sys.exit(f"Forbidden (403): Your app key may not have access to this endpoint.\nURL: {resp.url}")
        if resp.status_code == 404:
            return {"error": "not_found", "url": str(resp.url)}

        # Other errors
        if attempt < MAX_RETRIES - 1:
            time.sleep(backoff)
            backoff *= 2
            continue

        sys.exit(f"API error {resp.status_code}: {resp.text}")

    sys.exit("Max retries exceeded")


# ── OAuth2 auth flow (programmatic, same as getmyancestors) ──────────


def run_auth_flow(cfg: dict[str, Any], username: str | None = None, password: str | None = None) -> None:
    """Authenticate with FamilySearch using username/password.

    Uses the same programmatic login flow as getmyancestors:
    1. GET the login page to obtain XSRF token
    2. POST credentials to ident.familysearch.org/login
    3. Follow OAuth2 authorization redirect to capture the auth code
    4. Exchange the code for an access token
    """
    client_id = get_client_id(cfg)
    redirect_uri = get_redirect_uri(cfg)
    env = cfg.get("environment", "production")

    if not username:
        username = input("Enter FamilySearch username: ")
    if not password:
        password = getpass.getpass("Enter FamilySearch password: ")

    print(f"Logging in to FamilySearch ({env})...")

    # FamilySearch blocks non-browser User-Agents with 403
    browser_ua = (
        "Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0"
    )

    with httpx.Client(
        follow_redirects=True,
        timeout=60.0,
        headers={"User-Agent": browser_ua},
    ) as session:
        # Step 1: GET the login page to pick up XSRF cookie
        login_page = session.get(f"{LOGIN_BASE}/auth/familysearch/login")
        if login_page.status_code != 200:
            sys.exit(f"Failed to load login page ({login_page.status_code})")

        # Extract XSRF token from cookies
        xsrf = None
        for cookie in session.cookies.jar:
            if cookie.name == "XSRF-TOKEN":
                xsrf = cookie.value
                break

        if not xsrf:
            sys.exit("Could not find XSRF token. FamilySearch login page may have changed.")

        # Step 2: POST credentials
        print("Submitting credentials...")
        login_resp = session.post(
            f"{AUTH_BASE}/login",
            data={
                "_csrf": xsrf,
                "username": username,
                "password": password,
            },
        )

        if login_resp.status_code not in (200, 302):
            sys.exit(f"Login failed ({login_resp.status_code}). Check your username and password.")

        # Step 3: Follow OAuth2 authorization to get the code
        print("Getting authorization code...")
        auth_resp = session.get(
            f"{AUTH_BASE}/cis-web/oauth2/v3/authorization",
            params={
                "response_type": "code",
                "scope": "profile email qualifies_for_affiliate_account country",
                "client_id": client_id,
                "redirect_uri": redirect_uri,
            },
        )

        # The code should be in the final redirect URL's query params
        final_url = str(auth_resp.url)
        parsed = urllib.parse.urlparse(final_url)
        query_params = urllib.parse.parse_qs(parsed.query)
        code = query_params.get("code", [None])[0]

        if not code:
            sys.exit(
                f"Could not extract authorization code from redirect.\n"
                f"Final URL: {final_url}\n"
                f"You may need to log in via browser first: {LOGIN_BASE}"
            )

        # Step 4: Exchange code for token
        print("Exchanging authorization code for token...")
        token_resp = httpx.post(
            f"{AUTH_BASE}/cis-web/oauth2/v3/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "redirect_uri": redirect_uri,
            },
        )

        if token_resp.status_code != 200:
            sys.exit(f"Token exchange failed ({token_resp.status_code}): {token_resp.text}")

        data = token_resp.json()
        tok = {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token"),
            "expires_at": time.time() + data.get("expires_in", 7200),
            "environment": env,
        }
        save_token(tok)
        print("Authenticated successfully. Token saved to ~/.familysearch/token.json")


# ── Output helper ─────────────────────────────────────────────────────


def emit(data: Any) -> None:
    """Print JSON to stdout."""
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    print()


# ── Person helpers ────────────────────────────────────────────────────


def extract_person_summary(person: dict[str, Any]) -> dict[str, Any]:
    """Extract a human-friendly summary from a GEDCOM X person object."""
    display = person.get("display", {})
    pid = person.get("id", "")

    # Extract facts
    facts = {}
    for fact in person.get("facts", []):
        fact_type = fact.get("type", "").rsplit("/", 1)[-1]
        date_str = fact.get("date", {}).get("original")
        place_str = fact.get("place", {}).get("original")
        facts[fact_type] = {
            "date": date_str,
            "place": place_str,
        }

    return {
        "id": pid,
        "name": display.get("name"),
        "givenName": display.get("givenName", display.get("name", "").split(" ")[0] if display.get("name") else None),
        "surname": display.get("familyName"),
        "gender": display.get("gender"),
        "lifespan": display.get("lifespan"),
        "birthDate": display.get("birthDate"),
        "birthPlace": display.get("birthPlace"),
        "deathDate": display.get("deathDate"),
        "deathPlace": display.get("deathPlace"),
        "facts": facts if facts else None,
        "living": person.get("living", False),
    }


# ── Command implementations ──────────────────────────────────────────


def cmd_config(args: argparse.Namespace) -> None:
    """Store app key and environment settings."""
    cfg = load_config()

    if args.app_key:
        cfg["app_key"] = args.app_key
    if args.redirect_uri:
        cfg["redirect_uri"] = args.redirect_uri
    if args.env:
        if args.env not in BASE_URLS:
            sys.exit(f"Unknown environment: {args.env}. Use: {', '.join(BASE_URLS.keys())}")
        cfg["environment"] = args.env

    save_config(cfg)
    emit({"status": "ok", "config": cfg})


def cmd_auth(args: argparse.Namespace) -> None:
    """Run OAuth2 authentication flow."""
    cfg = require_config()
    if args.env:
        cfg["environment"] = args.env
        save_config(cfg)
    run_auth_flow(cfg, username=args.username, password=args.password)


def cmd_verify(args: argparse.Namespace) -> None:
    """Verify authentication by fetching current user."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    data = api_get(client, "/platform/tree/current-person")

    if "error" in data:
        emit({"status": "error", **data})
        return

    persons = data.get("persons", [])
    if persons:
        person = extract_person_summary(persons[0])
        emit({
            "status": "ok",
            "environment": cfg.get("environment", "integration"),
            "user": person.get("name"),
            "personId": person.get("id"),
        })
    else:
        emit({"status": "ok", "environment": cfg.get("environment", "integration"), "note": "Authenticated but no tree person found"})


def cmd_get_person(args: argparse.Namespace) -> None:
    """Fetch a person by PID."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    params = {}
    if args.relationships:
        params["relatives"] = ""

    data = api_get(client, f"/platform/tree/persons/{args.pid}", params=params if params else None)

    if "error" in data:
        emit(data)
        return

    persons = data.get("persons", [])
    result: dict[str, Any] = {}

    if persons:
        result["person"] = extract_person_summary(persons[0])

    # Include relationship data if requested
    if args.relationships and len(persons) > 1:
        result["relatedPersons"] = [extract_person_summary(p) for p in persons[1:]]

    relationships = data.get("relationships", [])
    if relationships:
        result["relationships"] = []
        for rel in relationships:
            result["relationships"].append({
                "type": rel.get("type", "").rsplit("/", 1)[-1],
                "person1": rel.get("person1", {}).get("resourceId"),
                "person2": rel.get("person2", {}).get("resourceId"),
            })

    emit(result)


def cmd_get_current_user(args: argparse.Namespace) -> None:
    """Fetch the authenticated user's tree person."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    data = api_get(client, "/platform/tree/current-person")

    if "error" in data:
        emit(data)
        return

    persons = data.get("persons", [])
    if persons:
        emit(extract_person_summary(persons[0]))
    else:
        emit({"error": "no_tree_person", "note": "Authenticated user has no tree person"})


def cmd_ancestry(args: argparse.Namespace) -> None:
    """Ascending pedigree (ancestors)."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    params: dict[str, Any] = {
        "person": args.pid,
        "generations": args.generations,
    }
    if args.details:
        params["personDetails"] = ""

    data = api_get(client, "/platform/tree/ancestry", params=params)

    if "error" in data:
        emit(data)
        return

    persons = data.get("persons", [])
    result = {
        "rootPerson": args.pid,
        "generations": args.generations,
        "totalPersons": len(persons),
        "persons": [extract_person_summary(p) for p in persons],
    }
    emit(result)


def cmd_descendancy(args: argparse.Namespace) -> None:
    """Descending pedigree (descendants)."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    params: dict[str, Any] = {
        "person": args.pid,
        "generations": args.generations,
    }

    data = api_get(client, "/platform/tree/descendancy", params=params)

    if "error" in data:
        emit(data)
        return

    persons = data.get("persons", [])
    result = {
        "rootPerson": args.pid,
        "generations": args.generations,
        "totalPersons": len(persons),
        "persons": [extract_person_summary(p) for p in persons],
    }
    emit(result)


def _search_via_curl(url: str, params: dict[str, Any], token: str) -> dict[str, Any]:
    """Call FamilySearch search service via curl.

    httpx and urllib.request both hang on FamilySearch's /service/search/
    endpoints due to TLS/connection issues. curl works reliably.
    """
    qs = urllib.parse.urlencode(params)
    full_url = f"{url}?{qs}"
    result = subprocess.run(
        [
            "curl", "-s", "--max-time", "30",
            "-H", f"Authorization: Bearer {token}",
            "-H", "Accept: application/json",
            "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
            full_url,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit(f"Search request failed: {result.stderr}")
    if not result.stdout.strip():
        sys.exit("Search returned empty response")
    return json.loads(result.stdout)


def cmd_search(args: argparse.Namespace) -> None:
    """Search persons in the Family Tree."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    # Build q.-prefixed params for the search service
    params: dict[str, Any] = {
        "count": args.limit or 20,
        "offset": 0,
        "m.defaultFacets": "on",
    }
    if args.name:
        parts = args.name.strip().split(None, 1)
        if len(parts) == 2:
            params["q.givenName"] = parts[0]
            params["q.surname"] = parts[1]
        else:
            params["q.surname"] = args.name

    if args.given_name:
        params["q.givenName"] = args.given_name
    if args.surname:
        params["q.surname"] = args.surname
    if args.birth_year:
        yr = int(args.birth_year)
        params["q.anyDate.from"] = str(yr)
        params["q.anyDate.to"] = str(yr + 5)
    if args.birth_place:
        params["q.anyPlace"] = args.birth_place
    if args.death_year:
        yr = int(args.death_year)
        params["q.anyDate.from"] = str(yr)
        params["q.anyDate.to"] = str(yr + 5)
    if args.death_place:
        params["q.anyPlace"] = args.death_place
    if args.sex:
        params["q.sex"] = args.sex

    has_query = any(k.startswith("q.") for k in params)
    if not has_query:
        sys.exit("At least one search parameter is required (--name, --surname, --birth-year, etc.)")

    data = _search_via_curl(
        f"{SEARCH_BASE}/service/search/tree/v2/personas",
        params,
        tok["access_token"],
    )

    results = []
    for entry in data.get("entries", data.get("results", [])):
        person_data = entry.get("content", entry)
        persons = person_data.get("gedcomx", {}).get("persons", []) if "content" in entry else []
        if persons:
            summary = extract_person_summary(persons[0])
            summary["score"] = entry.get("score")
            results.append(summary)
        elif "display" in entry:
            results.append({
                "id": entry.get("id"),
                "name": entry.get("display", {}).get("name"),
                "lifespan": entry.get("display", {}).get("lifespan"),
                "birthPlace": entry.get("display", {}).get("birthPlace"),
                "score": entry.get("score"),
            })

    emit({
        "totalResults": data.get("totalCount", data.get("results", len(results))),
        "returned": len(results),
        "persons": results,
    })


def cmd_search_records(args: argparse.Namespace) -> None:
    """Search historical record collections."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    # Build q.-prefixed params for the historical records search service
    params: dict[str, Any] = {
        "count": args.limit or 20,
        "offset": 0,
        "m.queryRequireDefault": "on",
    }
    if args.name:
        parts = args.name.strip().split(None, 1)
        if len(parts) == 2:
            params["q.givenName"] = parts[0]
            params["q.surname"] = parts[1]
        else:
            params["q.surname"] = args.name
    if args.birth_year:
        yr = int(args.birth_year)
        params["q.birthLikeDate.from"] = str(yr)
        params["q.birthLikeDate.to"] = str(yr + 5)
    if args.death_year:
        yr = int(args.death_year)
        params["q.deathLikeDate.from"] = str(yr)
        params["q.deathLikeDate.to"] = str(yr + 5)

    has_query = any(k.startswith("q.") for k in params)
    if not has_query:
        sys.exit("At least one search parameter is required")

    data = _search_via_curl(
        f"{SEARCH_BASE}/service/search/hr/v2/personas",
        params,
        tok["access_token"],
    )

    results = []
    for entry in data.get("entries", data.get("results", [])):
        content = entry.get("content", {}).get("gedcomx", {})
        persons = content.get("persons", [])
        sources = content.get("sourceDescriptions", [])
        result: dict[str, Any] = {}
        if persons:
            result["person"] = extract_person_summary(persons[0])
        if sources:
            result["source"] = {
                "title": sources[0].get("titles", [{}])[0].get("value"),
                "about": sources[0].get("about"),
            }
        result["score"] = entry.get("score")
        results.append(result)

    emit({
        "totalResults": data.get("totalCount", data.get("results", len(results))),
        "returned": len(results),
        "records": results,
    })


def cmd_match(args: argparse.Namespace) -> None:
    """Get research hints (matches) for a person."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    data = api_get(
        client,
        f"/platform/tree/persons/{args.pid}/matches",
        accept=GEDCOMX_ATOM,
    )

    if "error" in data:
        emit(data)
        return

    entries = data.get("entries", [])
    results = []
    for entry in entries:
        content = entry.get("content", {}).get("gedcomx", {})
        persons = content.get("persons", [])
        if persons:
            summary = extract_person_summary(persons[0])
            summary["score"] = entry.get("score")
            results.append(summary)

    emit({
        "personId": args.pid,
        "totalMatches": len(results),
        "matches": results,
    })


def cmd_parents(args: argparse.Namespace) -> None:
    """List a person's parents."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    data = api_get(client, f"/platform/tree/persons/{args.pid}/parents")

    if "error" in data:
        emit(data)
        return

    persons = data.get("persons", [])
    emit({
        "personId": args.pid,
        "parents": [extract_person_summary(p) for p in persons],
    })


def cmd_spouses(args: argparse.Namespace) -> None:
    """List a person's spouses."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    data = api_get(client, f"/platform/tree/persons/{args.pid}/spouses")

    if "error" in data:
        emit(data)
        return

    persons = data.get("persons", [])
    emit({
        "personId": args.pid,
        "spouses": [extract_person_summary(p) for p in persons],
    })


def cmd_children(args: argparse.Namespace) -> None:
    """List a person's children."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    data = api_get(client, f"/platform/tree/persons/{args.pid}/children")

    if "error" in data:
        emit(data)
        return

    persons = data.get("persons", [])
    emit({
        "personId": args.pid,
        "children": [extract_person_summary(p) for p in persons],
    })


def cmd_relationship_path(args: argparse.Namespace) -> None:
    """Find the relationship path between two persons."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    params = {"from": args.from_pid, "to": args.to_pid}
    data = api_get(client, "/platform/tree/path", params=params)

    if "error" in data:
        emit(data)
        return

    persons = data.get("persons", [])
    emit({
        "from": args.from_pid,
        "to": args.to_pid,
        "pathLength": len(persons),
        "path": [extract_person_summary(p) for p in persons],
    })


def cmd_sources(args: argparse.Namespace) -> None:
    """List sources attached to a person."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    data = api_get(client, f"/platform/tree/persons/{args.pid}/sources")

    if "error" in data:
        emit(data)
        return

    source_descs = data.get("sourceDescriptions", [])
    results = []
    for sd in source_descs:
        results.append({
            "id": sd.get("id"),
            "title": (sd.get("titles") or [{}])[0].get("value"),
            "about": sd.get("about"),
            "citations": [c.get("value") for c in sd.get("citations", [])],
            "notes": [n.get("text") for n in sd.get("notes", [])],
        })

    emit({
        "personId": args.pid,
        "totalSources": len(results),
        "sources": results,
    })


def cmd_memories(args: argparse.Namespace) -> None:
    """List memories attached to a person."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    data = api_get(client, f"/platform/tree/persons/{args.pid}/memories")

    if "error" in data:
        emit(data)
        return

    source_descs = data.get("sourceDescriptions", [])
    results = []
    for sd in source_descs:
        media_type = sd.get("mediaType")
        results.append({
            "id": sd.get("id"),
            "title": (sd.get("titles") or [{}])[0].get("value"),
            "about": sd.get("about"),
            "mediaType": media_type,
            "description": (sd.get("description") or [{}])[0].get("value") if sd.get("description") else None,
        })

    emit({
        "personId": args.pid,
        "totalMemories": len(results),
        "memories": results,
    })


def cmd_download_memory(args: argparse.Namespace) -> None:
    """Download a memory artifact to local filesystem."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with httpx.Client(
        headers={"Authorization": f"Bearer {tok['access_token']}"},
        timeout=60.0,
        follow_redirects=True,
    ) as client:
        resp = client.get(args.url)
        if resp.status_code != 200:
            sys.exit(f"Download failed ({resp.status_code}): {resp.text[:200]}")

        output_path.write_bytes(resp.content)
        emit({
            "status": "ok",
            "url": args.url,
            "output": str(output_path),
            "size_bytes": len(resp.content),
        })


def cmd_export_person(args: argparse.Namespace) -> None:
    """Export a person and their network as structured JSON."""
    cfg = require_config()
    tok = require_token()
    tok = refresh_token_if_needed(cfg, tok)

    client = make_client(cfg, tok)
    collected: dict[str, Any] = {}

    # Fetch the root person
    data = api_get(client, f"/platform/tree/persons/{args.pid}")
    if "error" in data:
        emit(data)
        return

    for p in data.get("persons", []):
        collected[p["id"]] = extract_person_summary(p)

    # Fetch ancestors if requested
    if args.ancestors and args.ancestors > 0:
        anc_data = api_get(
            client,
            "/platform/tree/ancestry",
            params={"person": args.pid, "generations": args.ancestors},
        )
        for p in anc_data.get("persons", []):
            collected[p["id"]] = extract_person_summary(p)

    # Fetch immediate family (parents, spouses, children)
    for rel_type in ["parents", "spouses", "children"]:
        rel_data = api_get(client, f"/platform/tree/persons/{args.pid}/{rel_type}")
        for p in rel_data.get("persons", []):
            if p["id"] not in collected:
                collected[p["id"]] = extract_person_summary(p)

    # Fetch sources
    sources_data = api_get(client, f"/platform/tree/persons/{args.pid}/sources")
    sources = []
    for sd in sources_data.get("sourceDescriptions", []):
        sources.append({
            "id": sd.get("id"),
            "title": (sd.get("titles") or [{}])[0].get("value"),
            "about": sd.get("about"),
        })

    result = {
        "meta": {
            "rootPerson": args.pid,
            "exportedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "environment": cfg.get("environment", "integration"),
            "totalPersons": len(collected),
            "totalSources": len(sources),
        },
        "persons": collected,
        "sources": sources,
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        emit({"status": "ok", "output": str(output_path), "totalPersons": len(collected)})
    else:
        emit(result)


# ── CLI argument parser ───────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="familysearch.py",
        description="FamilySearch API CLI — read-only access to the Family Tree.",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # config
    p = sub.add_parser("config", help="Store app key and environment settings")
    p.add_argument("--app-key", help="FamilySearch app key (optional, has built-in default)")
    p.add_argument("--redirect-uri", help="OAuth2 redirect URI (default: GitHub Pages callback)")
    p.add_argument("--env", choices=list(BASE_URLS.keys()), help="Active environment (default: production)")

    # auth
    p = sub.add_parser("auth", help="Authenticate with FamilySearch username/password")
    p.add_argument("-u", "--username", help="FamilySearch username (prompts if omitted)")
    p.add_argument("-p", "--password", help="FamilySearch password (prompts securely if omitted)")
    p.add_argument("--env", choices=list(BASE_URLS.keys()), help="Environment to authenticate against")

    # verify
    sub.add_parser("verify", help="Verify authentication works")

    # get-person
    p = sub.add_parser("get-person", help="Fetch a person by PID")
    p.add_argument("--pid", required=True, help="Person ID (e.g., KWCJ-RN4)")
    p.add_argument("--relationships", action="store_true", help="Include immediate family")

    # get-current-user
    sub.add_parser("get-current-user", help="Fetch the authenticated user's tree person")

    # ancestry
    p = sub.add_parser("ancestry", help="Ascending pedigree (ancestors)")
    p.add_argument("--pid", required=True, help="Person ID")
    p.add_argument("--generations", type=int, default=4, help="Number of generations (default: 4, max: 8)")
    p.add_argument("--details", action="store_true", help="Include full person details")

    # descendancy
    p = sub.add_parser("descendancy", help="Descending pedigree (descendants)")
    p.add_argument("--pid", required=True, help="Person ID")
    p.add_argument("--generations", type=int, default=2, help="Number of generations (default: 2)")

    # search
    p = sub.add_parser("search", help="Search persons in the Family Tree")
    p.add_argument("--name", help="Full name (given + surname, space-separated)")
    p.add_argument("--given-name", help="Given name only")
    p.add_argument("--surname", help="Surname only")
    p.add_argument("--birth-year", help="Birth year (approximate)")
    p.add_argument("--birth-place", help="Birth place")
    p.add_argument("--death-year", help="Death year (approximate)")
    p.add_argument("--death-place", help="Death place")
    p.add_argument("--sex", choices=["M", "F"], help="Sex filter")
    p.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")

    # search-records
    p = sub.add_parser("search-records", help="Search historical record collections")
    p.add_argument("--name", help="Full name")
    p.add_argument("--birth-year", help="Birth year")
    p.add_argument("--death-year", help="Death year")
    p.add_argument("--limit", type=int, default=10, help="Max results")

    # match
    p = sub.add_parser("match", help="Get research hints for a person")
    p.add_argument("--pid", required=True, help="Person ID")

    # parents
    p = sub.add_parser("parents", help="List a person's parents")
    p.add_argument("--pid", required=True, help="Person ID")

    # spouses
    p = sub.add_parser("spouses", help="List a person's spouses")
    p.add_argument("--pid", required=True, help="Person ID")

    # children
    p = sub.add_parser("children", help="List a person's children")
    p.add_argument("--pid", required=True, help="Person ID")

    # relationship-path
    p = sub.add_parser("relationship-path", help="Find the relationship path between two persons")
    p.add_argument("--from", dest="from_pid", required=True, help="Source person ID")
    p.add_argument("--to", dest="to_pid", required=True, help="Target person ID")

    # sources
    p = sub.add_parser("sources", help="List sources attached to a person")
    p.add_argument("--pid", required=True, help="Person ID")

    # memories
    p = sub.add_parser("memories", help="List memories attached to a person")
    p.add_argument("--pid", required=True, help="Person ID")

    # download-memory
    p = sub.add_parser("download-memory", help="Download a memory artifact")
    p.add_argument("--url", required=True, help="Memory URL from API response")
    p.add_argument("--output", required=True, help="Local file path to save to")

    # export-person
    p = sub.add_parser("export-person", help="Export a person and their network as JSON")
    p.add_argument("--pid", required=True, help="Root person ID")
    p.add_argument("--ancestors", type=int, default=0, help="Include N generations of ancestors")
    p.add_argument("--output", help="Output file path (emits to stdout if omitted)")

    return parser


# ── Main ──────────────────────────────────────────────────────────────

COMMAND_MAP = {
    "config": cmd_config,
    "auth": cmd_auth,
    "verify": cmd_verify,
    "get-person": cmd_get_person,
    "get-current-user": cmd_get_current_user,
    "ancestry": cmd_ancestry,
    "descendancy": cmd_descendancy,
    "search": cmd_search,
    "search-records": cmd_search_records,
    "match": cmd_match,
    "parents": cmd_parents,
    "spouses": cmd_spouses,
    "children": cmd_children,
    "relationship-path": cmd_relationship_path,
    "sources": cmd_sources,
    "memories": cmd_memories,
    "download-memory": cmd_download_memory,
    "export-person": cmd_export_person,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    handler = COMMAND_MAP.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
