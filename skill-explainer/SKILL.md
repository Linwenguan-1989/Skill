---
name: skill-explainer
description: Explain an existing Codex Skill as a concise human-readable HTML page. Use when the user has a Skill folder, SKILL.md, or skill name and wants to understand what it does, who it is for, its workflow, required inputs, outputs, and typical application scenarios; also use when asked to generate a lightweight webpage that explains a Skill.
---

# Skill Explainer

## Purpose

Turn a Codex Skill into a lightweight "read-this-first" HTML page for beginners. The page must help a person who has never used the Skill quickly understand what it is, who should use it, what it can do, what to give it, and what they get back.

Do not produce a comprehensive product manual by default. Prioritize plain language, strong summarization, and a memorable metaphor. Assume the reader does not know what a Skill is.

## Required Output Sections

Generate exactly these sections in this order unless the user explicitly asks for more:

1. **一句话说明** - Explain what the Skill is in one beginner-friendly sentence.
2. **适合谁用** - Say which ordinary person or role would use it.
3. **工作流程** - Show the process in 3-5 short, visualizable steps.
4. **输入信息** - Say what the user needs to give it, in normal words.
5. **输出成果** - Say what the user gets back, in normal words.
6. **典型应用场景** - Give 2-4 familiar situations where someone would naturally use it.

At the top of the page, also include:

- **形象比喻** - Explain the Skill with one concrete metaphor.
- **关键判断** - 2-3 very short cards that front-load the most important facts.

Avoid default sections such as "使用边界", "不适合场景", "文件结构解释", "风险提示", or "完整输出示例" unless the user asks for them.

## Workflow

1. Locate the target Skill:
   - If the user gives a folder path, use that folder.
   - If the user gives a `SKILL.md` path, use its parent folder.
   - If the user gives only a skill name, search likely skill roots such as the current workspace, `~/.codex/skills`, and `~/.agents/skills`.
2. Read the target `SKILL.md` completely.
3. Inspect only the immediately relevant bundled resources:
   - List `scripts/`, `references/`, and `assets/` when present.
   - Read small reference files only if needed to understand the Skill's real workflow.
   - Do not load large resources just to be exhaustive.
4. Extract the human-facing meaning:
   - What problem does this Skill solve?
   - Who would naturally use it?
   - What inputs does it expect?
   - What does it actually do step by step?
   - What does it produce?
5. Create a concise content JSON matching the six required sections.
6. Run `scripts/render_skill_explainer.py` to generate the final HTML page.
7. Return the absolute output path to the user and briefly summarize the generated page.

## Content Style

- Write in Chinese by default unless the user requests another language.
- Lead with judgment, not background.
- Use plain, specific language. Prefer everyday words over internal Skill terminology.
- Explain technical terms only when unavoidable. Prefer "小工具/助手" over "工作流/系统/产物".
- Avoid assuming the reader understands Codex, agents, frontmatter, assets, scripts, or HTML implementation details.
- Keep each card short. One card should usually be one sentence.
- Use a concrete metaphor when it makes the Skill easier to understand.
- Prefer short lists over long paragraphs.
- Explain the Skill as a usable capability, not as internal implementation trivia.
- If the Skill is vague or poorly written, say so in the page by making the description appropriately cautious instead of inventing certainty.

## Rendering

Use the bundled renderer:

```bash
python3 scripts/render_skill_explainer.py --data /path/to/content.json --output /path/to/output.html
```

The JSON must use this shape:

```json
{
  "skill_name": "skill-name",
  "one_liner": "一句话说明。",
  "metaphor": "你可以把它理解成...",
  "key_points": ["关键判断 1", "关键判断 2", "关键判断 3"],
  "audience": ["适合谁用 1", "适合谁用 2"],
  "workflow": ["步骤 1", "步骤 2", "步骤 3"],
  "inputs": ["输入信息 1", "输入信息 2"],
  "outputs": ["输出成果 1", "输出成果 2"],
  "scenarios": ["典型应用场景 1", "典型应用场景 2"]
}
```

Name the output file `<skill-name>-explainer.html` unless the user specifies another name.
