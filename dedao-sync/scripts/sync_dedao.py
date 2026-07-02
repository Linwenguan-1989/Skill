#!/usr/bin/env python3
"""Fetch original records from Get笔记/得到大脑 into a local Dedao Brain folder."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = "https://openapi.biji.com"
AUDIO_TYPES = {
    "audio",
    "meeting",
    "local_audio",
    "internal_record",
    "class_audio",
    "recorder_audio",
    "recorder_flash_audio",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync scoped Dedao Brain notes.")
    parser.add_argument(
        "--root",
        default=os.environ.get("DEDAO_BRAIN_DIR", str(Path.cwd() / "Dedao Brain")),
        help="Local Dedao Brain archive root. Defaults to ./Dedao Brain in the current project.",
    )
    parser.add_argument("--date", help="Sync a whole day, e.g. 2026-07-01.")
    parser.add_argument("--at", help="Sync notes at a specific minute, e.g. '2026-07-01 09:17'.")
    parser.add_argument("--start", help="Inclusive start time, e.g. 2026-06-27 or '2026-06-27 09:00:00'.")
    parser.add_argument("--end", help="Inclusive end date, or exclusive exact end time, e.g. 2026-06-28 or '2026-06-29 00:00:00'.")
    parser.add_argument("--window-minutes", type=int, default=1, help="Minute window for --at. Default syncs that exact minute.")
    parser.add_argument("--max-pages", type=int, default=20, help="Maximum list pages to scan per run.")
    parser.add_argument("--max-new", type=int, default=0, help="Maximum notes to fetch this run; 0 means unlimited.")
    parser.add_argument("--page-delay", type=float, default=0.2, help="Delay between list pages.")
    parser.add_argument("--detail-delay", type=float, default=0.5, help="Delay between note detail calls.")
    parser.add_argument("--output-limit", type=int, default=10, help="Maximum synced items to print in stdout preview.")
    parser.add_argument("--verbose", action="store_true", help="Print full synced/skipped details to stdout.")
    parser.add_argument("--dry-run", action="store_true", help="Find matching notes without writing files.")
    parser.add_argument("--recordings-only", action="store_true", help="Only sync recording/audio/meeting note types.")
    args = parser.parse_args()
    scopes = int(bool(args.date)) + int(bool(args.at)) + int(bool(args.start or args.end))
    if scopes != 1:
        parser.error("Provide exactly one time scope: --date, --at, or both --start and --end.")
    if bool(args.start) != bool(args.end):
        parser.error("--start and --end must be provided together.")
    if args.window_minutes < 1:
        parser.error("--window-minutes must be >= 1.")
    return args


def load_credentials() -> tuple[str, str]:
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if config_path.exists():
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
        entry = cfg.get("skills", {}).get("entries", {}).get("getnote", {})
        api_key = entry.get("apiKey")
        client_id = entry.get("env", {}).get("GETNOTE_CLIENT_ID")
        if api_key and client_id:
            return api_key, client_id

    api_key = os.environ.get("GETNOTE_API_KEY")
    client_id = os.environ.get("GETNOTE_CLIENT_ID")
    if api_key and client_id:
        return api_key, client_id

    raise SystemExit(
        "Missing Get笔记 credentials. Configure ~/.openclaw/openclaw.json or set "
        "GETNOTE_API_KEY and GETNOTE_CLIENT_ID."
    )


def safe_json(text: str) -> Any:
    # JS callers need this for int64 precision. Python can parse big ints, but this keeps IDs string-like.
    safe = re.sub(r'"(id|note_id|parent_id|follow_id|live_id)"\s*:\s*(\d+)', r'"\1":"\2"', text)
    return json.loads(safe)


def request_json(method: str, path: str, api_key: str, client_id: str, params: dict[str, str] | None = None, body: Any = None) -> Any:
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = None
    headers = {"Authorization": api_key, "X-Client-ID": client_id}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = safe_json(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            payload = safe_json(raw) if raw else {"success": False, "error": {"message": str(exc), "code": exc.code}}
        except urllib.error.URLError as exc:
            if attempt < 2:
                time.sleep(5)
                continue
            raise RuntimeError(f"Network error: {exc}") from exc

        if payload.get("success"):
            return payload

        error = payload.get("error", {})
        if error.get("code") == 10202 and attempt < 2:
            retry_after = error.get("rate_limit", {}).get("retry_after") or 10
            time.sleep(float(retry_after))
            continue
        if error.get("code") in {30000, 50000} and attempt < 2:
            time.sleep(5)
            continue
        raise RuntimeError(json.dumps(error or payload, ensure_ascii=False))

    raise RuntimeError("Request failed after retries.")


def parse_time(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    value = value.strip()
    for fmt, size in (("%Y-%m-%d %H:%M:%S", 19), ("%Y-%m-%dT%H:%M:%S", 19), ("%Y-%m-%d %H:%M", 16), ("%Y-%m-%dT%H:%M", 16)):
        try:
            return dt.datetime.strptime(value[:size], fmt)
        except ValueError:
            pass
    return None


def parse_scope_time(value: str | None, *, is_end: bool = False) -> dt.datetime | None:
    if not value:
        return None
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        parsed = dt.datetime.strptime(value, "%Y-%m-%d")
        return parsed + dt.timedelta(days=1) if is_end else parsed
    parsed = parse_time(value)
    if not parsed:
        raise SystemExit(f"Invalid time format: {value}")
    return parsed


def resolve_scope(args: argparse.Namespace) -> tuple[dt.datetime, dt.datetime]:
    if args.date:
        start = parse_scope_time(args.date)
        end = parse_scope_time(args.date, is_end=True)
    elif args.at:
        start = parse_scope_time(args.at)
        if start and len(args.at.strip()) == 16:
            # Normalize YYYY-MM-DD HH:MM to the beginning of that minute.
            start = start.replace(second=0)
        end = start + dt.timedelta(minutes=args.window_minutes) if start else None
    else:
        start = parse_scope_time(args.start)
        end = parse_scope_time(args.end, is_end=True)
    if not start or not end or start >= end:
        raise SystemExit("Invalid time scope.")
    return start, end


def sanitize_filename(text: str, limit: int = 80) -> str:
    text = re.sub(r'[\\/:*?"<>|\n\r\t]+', "_", text).strip(" ._")
    text = re.sub(r"\s+", " ", text)
    return (text[:limit].strip() or "untitled")


def note_id(note: dict[str, Any]) -> str:
    return str(note.get("note_id") or note.get("id") or "")


def is_recording(note: dict[str, Any]) -> bool:
    joined = f"{note.get('title','')} {note.get('source','')} {note.get('note_type','')}"
    return note.get("note_type") in AUDIO_TYPES or bool(note.get("audio")) or bool(re.search(r"录音|会议|音频|录制", joined))


def list_candidates_by_range(
    api_key: str,
    client_id: str,
    start: dt.datetime,
    end: dt.datetime,
    recordings_only: bool,
    max_pages: int,
    page_delay: float,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    cursor = ""
    for _page in range(max_pages):
        params = {"cursor": cursor} if cursor else None
        payload = request_json("GET", "/open/api/v1/resource/note/list", api_key, client_id, params=params)
        data = payload.get("data", {})
        notes = data.get("notes") or []
        stop = False
        for note in notes:
            nid = note_id(note)
            created = parse_time(note.get("created_at"))
            if not nid:
                continue
            if created and start <= created < end and (not recordings_only or is_recording(note)):
                candidates.append(note)
        if stop or not data.get("has_more") or not data.get("cursor"):
            break
        cursor = str(data["cursor"])
        time.sleep(page_delay)
    return candidates


def recall_candidates_by_time(api_key: str, client_id: str, start: dt.datetime, end: dt.datetime) -> list[dict[str, Any]]:
    query = start.strftime("%Y-%m-%d %H:%M")
    payload = request_json(
        "POST",
        "/open/api/v1/resource/recall",
        api_key,
        client_id,
        body={"query": query, "top_k": 10},
    )
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for result in payload.get("data", {}).get("results") or []:
        content = str(result.get("content") or "")
        ids: list[str] = []
        created = parse_time(result.get("created_at"))
        if result.get("note_id") and created and start <= created < end:
            ids.append(str(result["note_id"]))
        if query in content or start.strftime("%Y-%m-%d %H:%M:%S") in content:
            ids.extend(re.findall(r"https://biji\.com/note/(\d+)", content))
        for nid in ids:
            if nid and nid not in seen:
                seen.add(nid)
                candidates.append({"note_id": nid, "title": result.get("title") or ""})
    return candidates


def extract_original(note: dict[str, Any]) -> tuple[str, str]:
    audio = note.get("audio") or {}
    web_page = note.get("web_page") or {}
    if audio.get("original"):
        return str(audio["original"]).strip(), "audio.original"
    if audio.get("transcript"):
        return str(audio["transcript"]).strip(), "audio.transcript"
    if web_page.get("content"):
        return str(web_page["content"]).strip(), "web_page.content"
    return str(note.get("content") or "").strip(), "note.content"


def write_note(root: Path, note: dict[str, Any], original: str, original_source: str) -> Path:
    created = parse_time(note.get("created_at")) or dt.datetime.now()
    title = note.get("title") or "未命名笔记"
    folder_name = f"{created.strftime('%Y-%m-%d_%H%M')}_{sanitize_filename(title)}"
    folder = root / "notes" / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "original.md").write_text(original.rstrip() + "\n", encoding="utf-8")
    return folder


def main() -> int:
    args = parse_args()
    api_key, client_id = load_credentials()
    root = Path(args.root).expanduser()
    if not args.dry_run:
        root.mkdir(parents=True, exist_ok=True)

    start, end = resolve_scope(args)
    candidates = list_candidates_by_range(
        api_key,
        client_id,
        start,
        end,
        args.recordings_only,
        args.max_pages,
        args.page_delay,
    )
    if not candidates and args.at:
        candidates = recall_candidates_by_time(api_key, client_id, start, end)

    candidates.sort(key=lambda n: parse_time(n.get("created_at")) or dt.datetime.min)
    if args.max_new > 0:
        candidates = candidates[: args.max_new]

    synced: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    for item in candidates:
        nid = note_id(item)
        title = item.get("title") or ""
        if args.dry_run:
            synced.append({"note_id": nid, "title": title, "folder": ""})
            continue

        time.sleep(args.detail_delay)
        try:
            detail = request_json("GET", "/open/api/v1/resource/note/detail", api_key, client_id, params={"id": nid})
        except RuntimeError as exc:
            skipped.append({"note_id": nid, "title": title, "reason": str(exc)})
            continue
        note = detail.get("data", {}).get("note") or {}
        original, source = extract_original(note)
        if not original and not note.get("content"):
            skipped.append({"note_id": nid, "title": title, "reason": "empty original"})
            continue
        folder = write_note(root, note, original, source)
        synced.append({"note_id": nid, "title": note.get("title") or title, "folder": str(folder)})

    full_result = {
        "root": str(root),
        "dry_run": args.dry_run,
        "scope": {"start": start.isoformat(sep=" "), "end": end.isoformat(sep=" ")},
        "fetched_notes": len(synced),
        "synced": synced,
        "skipped": skipped,
    }

    preview = [{"title": item.get("title", ""), "folder": item.get("folder", "")} for item in synced[: max(args.output_limit, 0)]]
    compact_result = {
        "root": str(root),
        "dry_run": args.dry_run,
        "scope": full_result["scope"],
        "fetched_notes": len(synced),
        "skipped_count": len(skipped),
        "shown": len(preview),
        "omitted": max(len(synced) - len(preview), 0),
        "synced_preview": preview,
    }
    print(json.dumps(full_result if args.verbose else compact_result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
