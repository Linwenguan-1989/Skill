---
name: dedao-sync
description: Time-scoped fetch from 得到大脑/Get笔记 to a local "Dedao Brain" folder. Use when the user mentions "得到大脑" or "Get笔记" together with "同步" and a specific day, exact time, or time range, such as "帮我同步得到大脑7月1号的笔记", "同步得到大脑7月1号上午9:17的笔记", "把得到大脑上周的笔记同步到本地"; fetch only complete original records/transcripts into local original.md files without loading note bodies into the model context.
---

# Dedao Sync

## Purpose

Use this skill as a fast, low-cost, explicit-command fetch worker from 得到大脑/Get笔记 to local files.

Primary trigger pattern: the user says "得到大脑" or "Get笔记" plus "同步" plus a time expression.

Do not use the model to read note bodies during sync. Run the bundled script, let the script call the API, find notes by time, and save only the original record file as `original.md`. Do not rewrite, reformat, summarize, or add metadata into the file. Report only a short summary unless the user explicitly asks to inspect a specific local file.

Do not run open-ended or daily automatic sync by default. The user must provide a time scope:

- a specific day, such as "7月1号"
- a specific time, such as "7月1号上午9:17"
- a specific time range, such as "7月1号到7月3号" or "昨天上午"

If the user says only "同步一下" or "同步最新笔记" without a time scope, ask for the day, exact time, or time range before running the script.

The user usually will not provide note IDs. Convert natural Chinese time expressions into script parameters before running the script. Use the current year unless the user states another year.

## Default Local Archive

Default root folder is inside the current project where the command is run:

```text
./Dedao Brain
```

This matters: if the user is working in a "会议纪要" project folder, sync into that project folder's `Dedao Brain/`, not a global Documents folder.

Override with either:

```bash
DEDAO_BRAIN_DIR="/path/to/Dedao Brain"
```

or:

```bash
python3 scripts/sync_dedao.py --root "/path/to/Dedao Brain"
```

Each synced note is written as:

```text
Dedao Brain/
  notes/
    YYYY-MM-DD_HHMM_title/
      original.md
```

Do not create `summary.md`, `meta.json`, sync logs, or state files in the fast path.

## Workflow

1. Run `scripts/sync_dedao.py`.
2. The script reads credentials from `~/.openclaw/openclaw.json` first, then falls back to `GETNOTE_API_KEY` and `GETNOTE_CLIENT_ID`.
3. The script lists notes only inside the requested `--date`, `--at`, or `--start`/`--end` time scope.
4. The script fetches details for matching notes.
5. For each matching note, the script writes only `original.md`: the complete original transcript/content already provided by 得到大脑, preferring `audio.original`, then `audio.transcript`, then webpage original content, then plain note content.
6. If the same folder already exists, overwrite `original.md` with the latest fetched original content.

## Commands

Sync one whole day:

```bash
python3 /Users/gavenlin/.codex/skills/dedao-sync/scripts/sync_dedao.py --date 2026-07-01
```

Sync notes at a specific minute:

```bash
python3 /Users/gavenlin/.codex/skills/dedao-sync/scripts/sync_dedao.py --at "2026-07-01 09:17"
```

Sync a specific time range:

```bash
python3 /Users/gavenlin/.codex/skills/dedao-sync/scripts/sync_dedao.py --start 2026-06-27 --end 2026-06-28
```

Date-only `--end` values include that full day. Exact datetime `--end` values are treated as the exclusive boundary.

Dry run without writing note files:

```bash
python3 /Users/gavenlin/.codex/skills/dedao-sync/scripts/sync_dedao.py --date 2026-07-01 --dry-run
```

Limit one run to a small batch:

```bash
python3 /Users/gavenlin/.codex/skills/dedao-sync/scripts/sync_dedao.py --date 2026-07-01 --max-new 5
```

Use a custom archive folder:

```bash
python3 /Users/gavenlin/.codex/skills/dedao-sync/scripts/sync_dedao.py --date 2026-07-01 --root "/path/to/Dedao Brain"
```

Print full details only when explicitly useful:

```bash
python3 /Users/gavenlin/.codex/skills/dedao-sync/scripts/sync_dedao.py --date 2026-07-01 --verbose
```

Only restrict to recording/audio/meeting notes when explicitly requested:

```bash
python3 /Users/gavenlin/.codex/skills/dedao-sync/scripts/sync_dedao.py --date 2026-07-01 --recordings-only
```

## Natural Language Mapping

- "帮我同步得到大脑7月1号的笔记" -> `--date 2026-07-01`
- "同步得到大脑7月1号所有笔记内容" -> `--date 2026-07-01`
- "帮我同步得到大脑7月1号上午9:17的那篇笔记" -> `--at "2026-07-01 09:17"`
- "把得到大脑7月1号到7月3号的笔记同步到本地" -> `--start 2026-07-01 --end 2026-07-03`
- "同步得到大脑昨天上午的笔记" -> convert to exact local date and time range before running.

## Speed And Token Rules

- Treat sync as mechanical IO; prefer a cheap/lightweight model.
- Do not check whether notes were previously synced.
- Do not create summary files, metadata files, state files, or sync logs.
- Do not add headers, note IDs, timestamps, or explanations into `original.md`; save the fetched original text itself.
- Do not paste complete transcripts into chat during routine sync.
- Do not paste long note IDs into routine chat output or folder names.
- Do not re-transcribe audio.
- Only use a stronger model when the user asks for analysis, extraction, rewriting, or decisions based on synced content.

## Reporting

After sync, report only:

- number of original records fetched
- archive root
- the compact preview shown by the script, usually title and local folder only
- any errors or skipped notes

Keep private note contents out of the response unless explicitly requested.
