---
name: meeting-minutes
description: Generate a complete, polished, responsive Chinese HTML meeting-minutes document from pasted text, transcripts, chat logs, notes, or attachments. Use when the user asks to整理会议纪要, 生成会议纪要, summarize meeting notes/transcripts, or convert meeting material into a business meeting-minutes HTML artifact.
---

# Meeting Minutes

## Non-Negotiable Output

Always produce one deliverable: a standalone responsive `.html` file.

Do not generate PDF, PNG, long image, DOCX, or other derivative formats unless the user explicitly requests them.

## Role And Standard

Act as a professional meeting-summary expert. Transform meeting material into a clear, beautiful, easy-to-read business meeting record.

The output must satisfy the user's original prompt:

- Complete: do not omit important information from the source.
- Structured: organize by logical topic so information is easy to locate.
- Highlighted: use icons, color, labels, and visual hierarchy to surface core ideas.
- Actionable: extract decisions, next steps, owners, deadlines, key numbers, and execution risks.
- Professional: rewrite oral or fragmented speech into polished written Chinese without changing factual meaning.
- Mobile-friendly: optimize for one-handed mobile reading.

## Required Processing Flow

1. Extract information from the user's text and attachments. Use appropriate file readers for `.txt`, `.md`, `.docx`, `.pdf`, spreadsheets, or transcript-like files when present.
2. Identify meeting topic, time, participants, background, key viewpoints, important data, decisions, action items, risks, and unresolved questions.
3. Reorganize content by topic, not by raw speaking order, unless chronology is essential.
4. Rewrite into concise professional Chinese. Preserve names, numbers, dates, commitments, disagreements, and causal relationships.
5. Generate the HTML with the required sections below.
6. Verify the HTML file exists, is non-empty, and contains the required sections. Return its absolute path.

## Required HTML Sections

Use these sections in this order unless the source material clearly makes a section impossible:

1. Hero cover: meeting theme, time, speaker/participants, source, content type, and one compact tag.
2. Core insights: 3-5 card-style key points, each written as a conclusion, not a vague label.
3. Detailed minutes: topic-based card blocks covering the important discussion content.
4. Data summary: prominent metric cards plus a table explaining key numbers and business meaning.
5. Action items: owner/role, concrete task, deadline or timing, status/priority when available.
6. Quotes or highlights: valuable original statements, if present.
7. Follow-up plan, risks, or open issues: unresolved items that affect execution.
8. Final conclusion: one concise paragraph stating the main judgment and implications.

If information is missing from the provided complete record, write `未提供` for essential metadata and avoid inventing facts. For empty nonessential sections, include a short note such as `原始材料未明确提及。` Do not ask the user to provide more material unless the user explicitly requests an interactive clarification pass.

## Accuracy Rules

- Never invent participants, deadlines, decisions, metrics, or owners.
- Distinguish confirmed decisions from proposals, opinions, and pending questions.
- If a speaker expresses disagreement, preserve the disagreement rather than smoothing it into false consensus.
- If action ownership is unclear, write `待明确` instead of assigning an owner.
- If the meeting contains sensitive client, revenue, hiring, or legal information, keep it factual and avoid adding speculative interpretation.
- Prefer direct, decision-useful wording. Avoid generic phrases such as `进行了深入讨论` unless the source only supports that level of detail.

## HTML Visual Requirements

Use `assets/meeting-minutes-template.html` as the baseline and keep these rules:

- Theme color: `#BC1F1A`.
- Typography: `Microsoft YaHei`, `PingFang SC`, `Noto Sans CJK SC`, `Arial`, sans-serif.
- Layout: mobile-first, responsive, single-column on phones, centered readable layout on desktop.
- Visual tone: polished business document with a strong first screen: red gradient hero, rounded cards, subtle shadows, clean whitespace, and clear hierarchy.
- Core points: use card-style blocks with numbered headings such as `01｜...`.
- Detailed content: use repeated topic cards with compact red badges.
- Data: use metric cards for big numbers and a table for explanation/business meaning.
- Action items: use bordered action blocks or tables with owner/role clearly separated from the task.
- Escape source text before inserting it into HTML. Do not include untrusted raw HTML from user material.

## Quality Checklist

Before finishing, check:

- HTML exists and is non-empty.
- The HTML contains the required sections.
- The title and first screen immediately show the meeting topic, time, and 3-5 core conclusions.
- Core insights are conclusions, not generic headings.
- Action items are concrete and include owner/deadline/status when available.
- Important names, numbers, dates, and decisions match the source.
- The document uses `#BC1F1A` and is readable on mobile.
