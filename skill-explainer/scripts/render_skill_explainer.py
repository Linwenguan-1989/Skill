#!/usr/bin/env python3
"""Render a concise Skill explainer HTML page from structured JSON."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from string import Template


REQUIRED_KEYS = [
    "skill_name",
    "one_liner",
    "audience",
    "workflow",
    "inputs",
    "outputs",
    "scenarios",
]


def as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def render_items(items: list[str], ordered: bool = False) -> str:
    tag = "ol" if ordered else "ul"
    body = "\n".join(f"<li>{html.escape(item)}</li>" for item in items)
    return f"<{tag}>{body}</{tag}>"


def render_cards(items: list[str]) -> str:
    return "\n".join(f'<div class="mini-card">{html.escape(item)}</div>' for item in items)


def render_flow(items: list[str]) -> str:
    return "\n".join(
        '<div class="flow-step">'
        f'<span class="flow-index">{index:02d}</span>'
        f'<p>{html.escape(item)}</p>'
        '</div>'
        for index, item in enumerate(items, start=1)
    )


def load_template() -> Template:
    template_path = Path(__file__).resolve().parents[1] / "assets" / "template.html"
    return Template(template_path.read_text(encoding="utf-8"))


def validate(data: dict[str, object]) -> None:
    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise SystemExit(f"Missing required JSON keys: {', '.join(missing)}")


def render(data: dict[str, object]) -> str:
    validate(data)
    skill_name = str(data["skill_name"]).strip() or "Unnamed Skill"
    metaphor = str(data.get("metaphor", "")).strip()
    key_points = as_list(data.get("key_points"))
    template = load_template()
    return template.safe_substitute(
        title=html.escape(skill_name),
        one_liner=html.escape(str(data["one_liner"]).strip()),
        metaphor=html.escape(metaphor),
        key_points=render_cards(key_points),
        audience=render_cards(as_list(data["audience"])),
        workflow=render_flow(as_list(data["workflow"])),
        inputs=render_cards(as_list(data["inputs"])),
        outputs=render_cards(as_list(data["outputs"])),
        scenarios=render_cards(as_list(data["scenarios"])),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a Skill explainer HTML page.")
    parser.add_argument("--data", required=True, help="Path to explainer content JSON.")
    parser.add_argument("--output", required=True, help="Path for the generated HTML file.")
    args = parser.parse_args()

    data_path = Path(args.data).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    data = json.loads(data_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render(data), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
