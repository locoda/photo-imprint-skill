#!/usr/bin/env python3
"""Shared schema checks for carousel planning, revisions, QA, and release gates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

BRIEF_STRING_FIELDS = ("subject_priority", "thumbnail_read")
BRIEF_LIST_FIELDS = (
    "preserve_anchors", "abstract_or_omit", "material_depth_cues", "forbidden_inventions"
)
STYLE_CONTRACT_FIELDS = (
    "mark_edge_quality", "negative_space_rules", "fill_tonal_rules",
    "background_cleanliness", "frame_border_policy", "abstraction_level",
)
REVISION_OPERATIONS = {"remove", "retain_but_simplify", "add_as_secondary", "preserve_unchanged"}
REVISION_DOMAINS = {"page-content", "page-overlay", "sample", "style-reference", "shared-system", "source-order"}
LOCAL_REVISION_DOMAINS = {"page-content", "page-overlay"}
QA_PAGE_CHECKS = (
    "production_plan_compliance", "subject_integrity", "thumbnail_read", "material_depth_cues",
    "structural_lines", "forbidden_inventions", "background_uniformity", "rectangular_seam_risk",
    "border_frame_risk", "subject_to_paper_compositing", "full_size_viewed", "phone_scale_viewed",
)
QA_SET_CHECKS = (
    "visual_cohesion", "paper_consistency", "style_consistency", "typography_consistency",
    "order_and_dimensions", "cross_page_rhythm", "route_or_module_integrity",
)


def load_object(path: Path, label: str = "JSON") -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object: {path}")
    return value


def write_object(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(nonempty_string(item) for item in value)


def validate_production_brief(brief: object, prefix: str = "production_brief") -> list[str]:
    errors: list[str] = []
    if not isinstance(brief, dict):
        return [f"{prefix} is required"]
    for field in BRIEF_STRING_FIELDS:
        if not nonempty_string(brief.get(field)):
            errors.append(f"{prefix}.{field} is required")
    for field in BRIEF_LIST_FIELDS:
        if not string_list(brief.get(field)):
            errors.append(f"{prefix}.{field} requires one or more strings")
    lines = brief.get("structural_lines")
    if not isinstance(lines, list) or not lines:
        errors.append(f"{prefix}.structural_lines requires one or more objects")
    else:
        for index, item in enumerate(lines, start=1):
            if not isinstance(item, dict) or not nonempty_string(item.get("element")):
                errors.append(f"{prefix}.structural_lines[{index}] requires element")
                continue
            if item.get("operation") not in {"retain", "retain_but_simplify"}:
                errors.append(f"{prefix}.structural_lines[{index}].operation must be retain or retain_but_simplify")
    return errors


def validate_style_contract(contract: object, prefix: str = "sample_style_contract") -> list[str]:
    errors: list[str] = []
    if not isinstance(contract, dict):
        return [f"{prefix} is required"]
    for field in STYLE_CONTRACT_FIELDS:
        value = contract.get(field)
        if field in {"mark_edge_quality", "negative_space_rules", "fill_tonal_rules", "background_cleanliness"}:
            if not string_list(value):
                errors.append(f"{prefix}.{field} requires one or more strings")
        elif not nonempty_string(value):
            errors.append(f"{prefix}.{field} is required")
    if contract.get("generated_page_is_style_reference") is not False:
        errors.append(f"{prefix}.generated_page_is_style_reference must be false")
    return errors


def validate_revision_changes(changes: object, valid_pages: set[int]) -> list[str]:
    errors: list[str] = []
    if not isinstance(changes, list) or not changes:
        return ["changes requires one or more revision operations"]
    for index, item in enumerate(changes, start=1):
        if not isinstance(item, dict):
            errors.append(f"changes[{index}] must be an object")
            continue
        if item.get("page") not in valid_pages:
            errors.append(f"changes[{index}].page is not in the render plan")
        if item.get("operation") not in REVISION_OPERATIONS:
            errors.append(f"changes[{index}].operation must be one of {sorted(REVISION_OPERATIONS)}")
        if item.get("domain") not in REVISION_DOMAINS:
            errors.append(f"changes[{index}].domain must be one of {sorted(REVISION_DOMAINS)}")
        if not nonempty_string(item.get("target")) or not nonempty_string(item.get("instruction")):
            errors.append(f"changes[{index}] requires target and instruction")
    return errors
