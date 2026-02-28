#!/usr/bin/env python3
# /// script
# dependencies = [
#   "notebooklm-py>=0.3.0",
# ]
# ///

"""
NotebookLM Skill - Notebook, Source, Artifact, and Chat management for AI agents.

Commands:
  verify                 Check authentication status
  setup                  Interactively save cookie to storage state JSON
  list                   List all notebooks
  get                    Get a notebook by ID
  create                 Create a new notebook
  rename                 Rename a notebook
  delete                 Delete a notebook
  summary                Get the AI-generated summary for a notebook
  sources                List sources in a notebook
  add-url                Add a URL as a source
  add-file               Add a local file as a source
  add-text               Add raw text as a source
  add-drive              Add a Google Drive file as a source
  delete-source          Delete a source by ID
  rename-source          Rename a source
  fulltext               Get the full extracted text of a source
  chat                   Ask a question against a notebook's sources
  generate-audio         Generate an Audio Overview
  generate-report        Generate a briefing doc / study guide / report
  generate-quiz          Generate a quiz
  generate-flashcards    Generate flashcards
  list-artifacts         List generated artifacts by type
  download-audio         Download the audio overview mp3/wav
  download-report        Download a report as a file
  share                  Get a share URL for a notebook or artifact

Configuration:
  Auth uses a Playwright-format storage_state.json file.
  Default location: ~/.notebooklm/storage_state.json
  Override via env: NOTEBOOKLM_HOME=/path/to/dir
  Or inline JSON:   NOTEBOOKLM_AUTH_JSON='{...}'

  To create the storage state from a raw __Secure-1PSID cookie:
    python3 scripts/notebooklm.py setup --cookie <value>
    or set env: NOTEBOOKLM_PSID_COOKIE=<value>
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Storage state helpers
# ---------------------------------------------------------------------------

DEFAULT_NOTEBOOKLM_HOME = Path.home() / ".notebooklm"


def _get_storage_path() -> Path:
    home = Path(os.environ.get("NOTEBOOKLM_HOME", DEFAULT_NOTEBOOKLM_HOME))
    return home / "storage_state.json"


def _build_storage_state(psid_value: str) -> dict:
    """Build a minimal Playwright storage_state.json from a __Secure-1PSID cookie value."""
    # NotebookLM auth requires SID and __Secure-1PSID at minimum.
    # We only have the Secure variant; map it to both slots so the library validator is satisfied.
    cookies = [
        {
            "name": "__Secure-1PSID",
            "value": psid_value,
            "domain": ".google.com",
            "path": "/",
            "secure": True,
            "httpOnly": True,
            "sameSite": "None",
        },
        {
            "name": "SID",
            "value": psid_value,
            "domain": ".google.com",
            "path": "/",
            "secure": False,
            "httpOnly": False,
            "sameSite": "Lax",
        },
    ]
    return {"cookies": cookies, "origins": []}


# ---------------------------------------------------------------------------
# Client context manager
# ---------------------------------------------------------------------------

async def _make_client():
    """Async context manager that returns an authenticated NotebookLMClient."""
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    return NotebookLMClient(auth)


def _out(data) -> None:
    print(json.dumps(data, indent=2, default=str))


def _notebook_to_dict(nb) -> dict:
    return {
        "id": nb.id,
        "title": nb.title,
        "created_at": str(nb.created_at) if hasattr(nb, "created_at") else None,
        "updated_at": str(nb.updated_at) if hasattr(nb, "updated_at") else None,
    }


def _source_to_dict(s) -> dict:
    return {
        "id": s.id,
        "title": s.title,
        "type": str(s.type) if hasattr(s, "type") else None,
        "status": str(s.status) if hasattr(s, "status") else None,
    }


def _artifact_to_dict(a) -> dict:
    return {
        "id": a.id,
        "title": getattr(a, "title", None),
        "type": str(a.type) if hasattr(a, "type") else None,
        "status": str(a.status) if hasattr(a, "status") else None,
    }


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

async def cmd_verify(_args) -> int:
    try:
        from notebooklm.auth import AuthTokens
        auth = await AuthTokens.from_storage()
        from notebooklm.client import NotebookLMClient
        async with NotebookLMClient(auth) as client:
            notebooks = await client.notebooks.list()
            _out({"status": "ok", "notebook_count": len(notebooks)})
        return 0
    except Exception as exc:
        _out({"status": "error", "message": str(exc)})
        return 1


async def cmd_setup(args) -> int:
    psid = args.cookie or os.environ.get("NOTEBOOKLM_PSID_COOKIE", "").strip()
    if not psid:
        # Try reading from our legacy nblm_cookie.txt file
        legacy = Path.home() / ".google_workspace" / "nblm_cookie.txt"
        if legacy.exists():
            psid = legacy.read_text().strip()
    if not psid:
        print(
            "Error: provide --cookie <value> or set NOTEBOOKLM_PSID_COOKIE.",
            file=sys.stderr,
        )
        return 1

    storage_path = _get_storage_path()
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    state = _build_storage_state(psid)
    storage_path.write_text(json.dumps(state, indent=2))
    _out({"status": "ok", "storage_path": str(storage_path)})
    return 0


async def cmd_list(_args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        notebooks = await client.notebooks.list()
        _out([_notebook_to_dict(nb) for nb in notebooks])
    return 0


async def cmd_get(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        nb = await client.notebooks.get(args.id)
        _out(_notebook_to_dict(nb))
    return 0


async def cmd_create(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        nb = await client.notebooks.create(args.title)
        _out(_notebook_to_dict(nb))
    return 0


async def cmd_rename(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        nb = await client.notebooks.rename(args.id, args.title)
        _out(_notebook_to_dict(nb))
    return 0


async def cmd_delete(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        ok = await client.notebooks.delete(args.id)
        _out({"deleted": ok})
    return 0


async def cmd_summary(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        summary = await client.notebooks.get_summary(args.id)
        _out({"notebook_id": args.id, "summary": summary})
    return 0


async def cmd_sources(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        nb = await client.notebooks.get(args.id)
        sources = nb.sources if hasattr(nb, "sources") else []
        _out([_source_to_dict(s) for s in sources])
    return 0


async def cmd_add_url(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        source = await client.sources.add_url(
            args.id, args.url, wait=args.wait, wait_timeout=args.timeout
        )
        _out(_source_to_dict(source))
    return 0


async def cmd_add_file(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        source = await client.sources.add_file(
            args.id,
            Path(args.file),
            mime_type=args.mime_type or None,
            wait=args.wait,
            wait_timeout=args.timeout,
        )
        _out(_source_to_dict(source))
    return 0


async def cmd_add_text(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        body = args.body or sys.stdin.read()
        source = await client.sources.add_text(
            args.id, args.title, body, wait=args.wait, wait_timeout=args.timeout
        )
        _out(_source_to_dict(source))
    return 0


async def cmd_add_drive(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        source = await client.sources.add_drive(
            args.id,
            args.file_id,
            title=args.title,
            mime_type=args.mime_type,
            wait=args.wait,
            wait_timeout=args.timeout,
        )
        _out(_source_to_dict(source))
    return 0


async def cmd_delete_source(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        ok = await client.sources.delete(args.id, args.source_id)
        _out({"deleted": ok})
    return 0


async def cmd_rename_source(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        source = await client.sources.rename(args.id, args.source_id, args.title)
        _out(_source_to_dict(source))
    return 0


async def cmd_fulltext(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        result = await client.sources.get_fulltext(args.id, args.source_id)
        _out({"source_id": args.source_id, "text": result.text if hasattr(result, "text") else str(result)})
    return 0


async def cmd_chat(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        result = await client.chat.ask(args.id, args.query)
        if hasattr(result, "answer"):
            _out({"answer": result.answer, "references": [str(r) for r in (result.references or [])]})
        else:
            _out({"answer": str(result)})
    return 0


async def cmd_generate_audio(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        source_ids = args.source_ids.split(",") if args.source_ids else None
        status = await client.artifacts.generate_audio(
            args.id,
            source_ids=source_ids,
            language=args.language,
            instructions=args.instructions or None,
        )
        _out({"task_id": getattr(status, "task_id", None), "status": str(status)})
    return 0


async def cmd_generate_report(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient
    from notebooklm.rpc.types import ReportFormat

    auth = await AuthTokens.from_storage()
    fmt_map = {
        "briefing_doc": ReportFormat.BRIEFING_DOC,
        "study_guide": ReportFormat.STUDY_GUIDE,
    }
    report_fmt = fmt_map.get(args.format, ReportFormat.BRIEFING_DOC)

    async with NotebookLMClient(auth) as client:
        source_ids = args.source_ids.split(",") if args.source_ids else None
        status = await client.artifacts.generate_report(
            args.id,
            report_format=report_fmt,
            source_ids=source_ids,
            language=args.language,
            custom_prompt=args.prompt or None,
        )
        _out({"task_id": getattr(status, "task_id", None), "status": str(status)})
    return 0


async def cmd_generate_quiz(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        source_ids = args.source_ids.split(",") if args.source_ids else None
        status = await client.artifacts.generate_quiz(
            args.id, source_ids=source_ids, instructions=args.instructions or None
        )
        _out({"task_id": getattr(status, "task_id", None), "status": str(status)})
    return 0


async def cmd_generate_flashcards(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        source_ids = args.source_ids.split(",") if args.source_ids else None
        status = await client.artifacts.generate_flashcards(
            args.id, source_ids=source_ids, instructions=args.instructions or None
        )
        _out({"task_id": getattr(status, "task_id", None), "status": str(status)})
    return 0


async def cmd_list_artifacts(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    kind = args.type or "audio"
    async with NotebookLMClient(auth) as client:
        method_map = {
            "audio": client.artifacts.list_audio,
            "report": client.artifacts.list_reports,
            "quiz": client.artifacts.list_quizzes,
            "flashcards": client.artifacts.list_flashcards,
            "infographic": client.artifacts.list_infographics,
            "slide_deck": client.artifacts.list_slide_decks,
        }
        fn = method_map.get(kind, client.artifacts.list_audio)
        artifacts = await fn(args.id)
        _out([_artifact_to_dict(a) for a in artifacts])
    return 0


async def cmd_download_audio(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        path = await client.artifacts.download_audio(
            args.id, args.output, artifact_id=args.artifact_id or None
        )
        _out({"downloaded": path})
    return 0


async def cmd_download_report(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        path = await client.artifacts.download_report(
            args.id, args.output, artifact_id=args.artifact_id or None
        )
        _out({"downloaded": path})
    return 0


async def cmd_share(args) -> int:
    from notebooklm.auth import AuthTokens
    from notebooklm.client import NotebookLMClient

    auth = await AuthTokens.from_storage()
    async with NotebookLMClient(auth) as client:
        url = await client.notebooks.get_share_url(
            args.id, artifact_id=args.artifact_id or None
        )
        _out({"share_url": url})
    return 0


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------

def _add_notebook_id(p: argparse.ArgumentParser, name: str = "--id") -> None:
    p.add_argument(name, required=True, help="Notebook ID")


def _add_wait_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--wait", action="store_true", default=False, help="Wait until source is ready")
    p.add_argument("--timeout", type=float, default=120.0, help="Wait timeout in seconds")


def _build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="notebooklm.py",
        description="NotebookLM CLI for AI agents",
    )
    sub = root.add_subparsers(dest="command", required=True)

    # verify
    sub.add_parser("verify", help="Check authentication status")

    # setup
    p = sub.add_parser("setup", help="Save cookie to storage_state.json")
    p.add_argument("--cookie", help="Value of __Secure-1PSID cookie")

    # list
    sub.add_parser("list", help="List notebooks")

    # get
    p = sub.add_parser("get", help="Get notebook by ID")
    _add_notebook_id(p)

    # create
    p = sub.add_parser("create", help="Create a notebook")
    p.add_argument("--title", required=True, help="Notebook title")

    # rename
    p = sub.add_parser("rename", help="Rename a notebook")
    _add_notebook_id(p)
    p.add_argument("--title", required=True, help="New title")

    # delete
    p = sub.add_parser("delete", help="Delete a notebook")
    _add_notebook_id(p)

    # summary
    p = sub.add_parser("summary", help="Get AI summary for a notebook")
    _add_notebook_id(p)

    # sources
    p = sub.add_parser("sources", help="List sources in a notebook")
    _add_notebook_id(p)

    # add-url
    p = sub.add_parser("add-url", help="Add a URL as a source")
    _add_notebook_id(p)
    p.add_argument("--url", required=True, help="URL to add")
    _add_wait_args(p)

    # add-file
    p = sub.add_parser("add-file", help="Add a local file as a source")
    _add_notebook_id(p)
    p.add_argument("--file", required=True, help="Path to the file")
    p.add_argument("--mime-type", help="Override MIME type")
    _add_wait_args(p)

    # add-text
    p = sub.add_parser("add-text", help="Add raw text as a source")
    _add_notebook_id(p)
    p.add_argument("--title", required=True, help="Source title")
    p.add_argument("--body", help="Text content (omit to read from stdin)")
    _add_wait_args(p)

    # add-drive
    p = sub.add_parser("add-drive", help="Add a Google Drive file as a source")
    _add_notebook_id(p)
    p.add_argument("--file-id", required=True, help="Drive file ID")
    p.add_argument("--title", required=True, help="Source title")
    p.add_argument(
        "--mime-type",
        default="application/vnd.google-apps.document",
        help="MIME type of the Drive file",
    )
    _add_wait_args(p)

    # delete-source
    p = sub.add_parser("delete-source", help="Delete a source")
    _add_notebook_id(p)
    p.add_argument("--source-id", required=True)

    # rename-source
    p = sub.add_parser("rename-source", help="Rename a source")
    _add_notebook_id(p)
    p.add_argument("--source-id", required=True)
    p.add_argument("--title", required=True)

    # fulltext
    p = sub.add_parser("fulltext", help="Get full extracted text of a source")
    _add_notebook_id(p)
    p.add_argument("--source-id", required=True)

    # chat
    p = sub.add_parser("chat", help="Ask a question against a notebook")
    _add_notebook_id(p)
    p.add_argument("--query", required=True, help="Question to ask")

    # generate-audio
    p = sub.add_parser("generate-audio", help="Generate Audio Overview")
    _add_notebook_id(p)
    p.add_argument("--source-ids", help="Comma-separated source IDs (default: all)")
    p.add_argument("--language", default="en")
    p.add_argument("--instructions", help="Custom host instructions")

    # generate-report
    p = sub.add_parser("generate-report", help="Generate a report / briefing doc")
    _add_notebook_id(p)
    p.add_argument(
        "--format",
        choices=["briefing_doc", "study_guide"],
        default="briefing_doc",
    )
    p.add_argument("--source-ids", help="Comma-separated source IDs")
    p.add_argument("--language", default="en")
    p.add_argument("--prompt", help="Custom report prompt")

    # generate-quiz
    p = sub.add_parser("generate-quiz", help="Generate a quiz")
    _add_notebook_id(p)
    p.add_argument("--source-ids", help="Comma-separated source IDs")
    p.add_argument("--instructions", help="Custom instructions")

    # generate-flashcards
    p = sub.add_parser("generate-flashcards", help="Generate flashcards")
    _add_notebook_id(p)
    p.add_argument("--source-ids", help="Comma-separated source IDs")
    p.add_argument("--instructions", help="Custom instructions")

    # list-artifacts
    p = sub.add_parser("list-artifacts", help="List generated artifacts")
    _add_notebook_id(p)
    p.add_argument(
        "--type",
        choices=["audio", "report", "quiz", "flashcards", "infographic", "slide_deck"],
        default="audio",
    )

    # download-audio
    p = sub.add_parser("download-audio", help="Download the audio overview")
    _add_notebook_id(p)
    p.add_argument("--output", required=True, help="Output file path")
    p.add_argument("--artifact-id", help="Specific artifact ID (default: latest)")

    # download-report
    p = sub.add_parser("download-report", help="Download a report")
    _add_notebook_id(p)
    p.add_argument("--output", required=True, help="Output file path")
    p.add_argument("--artifact-id", help="Specific artifact ID (default: latest)")

    # share
    p = sub.add_parser("share", help="Get share URL for a notebook or artifact")
    _add_notebook_id(p)
    p.add_argument("--artifact-id", help="Share a specific artifact instead of the notebook")

    return root


_COMMAND_MAP = {
    "verify": cmd_verify,
    "setup": cmd_setup,
    "list": cmd_list,
    "get": cmd_get,
    "create": cmd_create,
    "rename": cmd_rename,
    "delete": cmd_delete,
    "summary": cmd_summary,
    "sources": cmd_sources,
    "add-url": cmd_add_url,
    "add-file": cmd_add_file,
    "add-text": cmd_add_text,
    "add-drive": cmd_add_drive,
    "delete-source": cmd_delete_source,
    "rename-source": cmd_rename_source,
    "fulltext": cmd_fulltext,
    "chat": cmd_chat,
    "generate-audio": cmd_generate_audio,
    "generate-report": cmd_generate_report,
    "generate-quiz": cmd_generate_quiz,
    "generate-flashcards": cmd_generate_flashcards,
    "list-artifacts": cmd_list_artifacts,
    "download-audio": cmd_download_audio,
    "download-report": cmd_download_report,
    "share": cmd_share,
}


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    handler = _COMMAND_MAP.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    try:
        sys.exit(asyncio.run(handler(args)))
    except SystemExit:
        raise
    except Exception as exc:
        import traceback
        import time

        err_msg = str(exc) or repr(exc)
        tb_str = traceback.format_exc()

        log_dir = Path.home() / ".google_workspace" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "error.log"
        with open(log_file, "a") as f:
            f.write(
                f"--- UNHANDLED EXCEPTION [google_notebooklm.py] ---\n"
                f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
                f"Command: {' '.join(sys.argv)}\n"
                f"{tb_str}\n"
            )

        _out({
            "status": "error",
            "type": "UnhandledException",
            "message": err_msg,
            "fix": (
                "AGENT DIRECTIVE: This is an internal bug in google_notebooklm.py. "
                "Document this failure in the skill's KNOWN_BUGS.md and notify the user."
            ),
            "logFile": str(log_file),
        })
        sys.exit(1)


if __name__ == "__main__":
    main()
