---
name: meeting-minutes-auto
description: "Workflow orchestrator for turning a specified 得到大脑/Get笔记 note into meeting-minutes deliverables and sending them to Feishu/Lark. Use when the user points to one specific note or gives a precise time scope and wants the current dedao-sync, meeting-minutes, and feishu-sender skills executed in sequence."
---

# Meeting Minutes Auto

## Overview

Use this skill when the user wants one concrete Get笔记/Dedao note turned into meeting-minutes deliverables and delivered to Feishu.
This skill is an orchestrator only. It must use the current instructions of these child skills at execution time:

- `dedao-sync`
- `meeting-minutes`
- `feishu-sender`

Do not copy or preserve child-skill implementation details here. If a child skill changes its commands, output files, folder layout, identity rules, or validation rules, follow the latest child-skill instructions.

## Workflow

1. Resolve the source note.
   - Read and follow the current `dedao-sync/SKILL.md`.
   - Use the user's title, date, exact time, or time range as the note clue.
   - If the note cannot be identified under the current `dedao-sync` rules, ask for one specific day, exact time, or a tighter clue.

2. Get the original material.
   - Use the source artifact produced by the current `dedao-sync` workflow.
   - Do not re-transcribe or rewrite the source before handing it to `meeting-minutes`.

3. Generate the meeting minutes.
   - Read and follow the current `meeting-minutes/SKILL.md`.
   - Use its current output, validation, and quality rules.
   - Keep facts, names, numbers, dates, and decisions exactly aligned with the source note.

4. Send the deliverables to Feishu/Lark.
   - Read and follow the current `feishu-sender/SKILL.md`.
   - Send every finished deliverable produced by `meeting-minutes`, unless the user explicitly asks to send only one format.

## Operating Rules

- If the source note is empty, ambiguous, or missing substantive content, stop and ask for the missing source instead of fabricating minutes.
- If a child skill reports an existing local artifact, reuse it according to that child skill's current rules.
- If any required output file is missing or empty, fix that before sending anything.
- If Feishu/Lark authentication or permissions fail, report the exact blocker and do not claim delivery.
- Keep the response to the user short and execution-focused: source note identified, files generated, files sent, or the exact blocker.
