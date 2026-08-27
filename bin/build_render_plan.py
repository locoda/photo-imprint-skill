#!/usr/bin/env python3
"""Build deterministic per-page render briefs from a resolved config and manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_object(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path, help="Resolved config JSON")
    parser.add_argument("--manifest", required=True, type=Path, help="Preprocessed manifest JSON")
    parser.add_argument("--output", required=True, type=Path, help="Render plan JSON")
    parser.add_argument("--allow-unconfirmed", action="store_true", help="Build a draft plan despite unresolved metadata")
    args = parser.parse_args()

    try:
        config = load_object(args.config, "config")
        manifest = load_object(args.manifest, "manifest")
        if config.get("resolved") is not True:
            raise ValueError("config was not produced by resolve_config.py")
        if manifest.get("preset") and manifest.get("preset") != config.get("preset"):
            raise ValueError("manifest and config preset ids do not match")
        items = manifest.get("items")
        if not isinstance(items, list) or not items:
            raise ValueError("manifest.items must be a non-empty array")
    except ValueError as exc:
        print(f"Render-plan validation failed: {exc}", file=sys.stderr)
        return 2

    profiles = config["profiles"]
    theme = profiles["theme"]
    style = profiles["style"]
    layers = profiles["layers"]
    composition = profiles["composition"]
    modules = config.get("modules", {})
    canvas = composition["canvas"]
    subject = composition["subject"]
    flow = subject.get("horizontal_flow", ["center"])

    unresolved = []
    caption_fields = modules.get("caption", {}).get("lines", []) if modules.get("caption", {}).get("enabled") else []
    manifest_field = {"date": "date_label"}
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            unresolved.append(f"page {index}: item is not an object")
            continue
        if not item.get("capture_time"):
            unresolved.append(f"page {item.get('page', index)}: capture time/order is unconfirmed")
        missing = [field for field in caption_fields if not item.get(manifest_field.get(field, field))]
        if missing:
            unresolved.append(f"page {item.get('page', index)}: missing caption fields {', '.join(missing)}")
    if unresolved and not args.allow_unconfirmed:
        print("Render-plan validation failed:\n- " + "\n- ".join(unresolved), file=sys.stderr)
        return 2

    forbidden = list(dict.fromkeys(
        list(theme.get("forbid_invention", []))
        + list(layers.get("layers", {}).get("subject", {}).get("forbidden_content", []))
    ))
    negative_prompt = style.get("negative_prompt", "")
    if forbidden:
        negative_prompt = (negative_prompt.rstrip(". ") + ". Do not invent or render: " + ", ".join(forbidden) + ".").strip()

    pages = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            print(f"Render-plan validation failed: manifest item {index + 1} is not an object", file=sys.stderr)
            return 2
        placement = flow[index % len(flow)] if flow else "center"
        prompt = " ".join(
            part.strip()
            for part in (
                theme.get("prompt_fragment", ""),
                style.get("positive_prompt", ""),
                f"Render only the clean subject layer on transparency for a {canvas['width']}x{canvas['height']} composition.",
                f"Place the subject toward the {placement} in the lower portion; leave the composition profile's top whitespace empty.",
                layers.get("render_rule", ""),
            )
            if part
        )
        pages.append({
            "page": item.get("page", index + 1),
            "source_path": item.get("source_path"),
            "source_sha256": item.get("sha256"),
            "placement": placement,
            "render_prompt": prompt,
            "negative_prompt": negative_prompt,
            "plate_contract": {
                "format": "PNG",
                "width": canvas["width"],
                "height": canvas["height"],
                "transparent_background": True,
                "contains_only": "subject",
            },
            "caption_data": {
                "location": item.get("location"),
                "subject": item.get("subject"),
                "date": item.get("date_label"),
            } if modules.get("caption", {}).get("enabled") else None,
            "notes": item.get("notes"),
        })

    plan = {
        "schema_version": "1.0.0",
        "preset": config.get("preset"),
        "profile_ids": {key: value.get("id") for key, value in profiles.items()},
        "style_references": style.get("references", []),
        "layer_order": layers.get("z_order"),
        "composition": composition,
        "modules": modules,
        "deterministic_finish_contract": {
            "apply_after_subject_render": True,
            "shared_background": True,
            "typography_generated_by_model": False,
            "cross_slide_route_assembled_before_crop": bool(modules.get("route", {}).get("enabled")),
        },
        "pages": pages,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote render plan for {len(pages)} pages to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
