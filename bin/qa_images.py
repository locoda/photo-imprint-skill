#!/usr/bin/env python3
"""Create series-level previews and consistency metrics for finished pages."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
DEFAULT_THRESHOLDS = {
    "mean_luminance": 0.12,
    "rms_contrast": 0.18,
    "mean_saturation": 0.18,
}


def metrics(image: Image.Image) -> dict:
    rgb = image.convert("RGB")
    gray = rgb.convert("L")
    hsv = rgb.convert("HSV")
    lum = ImageStat.Stat(gray)
    sat = ImageStat.Stat(hsv.getchannel("S"))
    return {
        "width": rgb.width,
        "height": rgb.height,
        "mean_luminance": round(lum.mean[0], 3),
        "rms_contrast": round(lum.stddev[0], 3),
        "mean_saturation": round(sat.mean[0], 3),
    }


def relative_delta(value: float, median: float) -> float:
    if median == 0:
        return 0.0 if value == 0 else math.inf
    return abs(value - median) / median


def load_config(path: Path | None) -> tuple[dict[str, float], bool, dict | None]:
    if path is None:
        return DEFAULT_THRESHOLDS.copy(), False, None
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or config.get("resolved") is not True:
        raise ValueError(f"not a resolved carousel config: {path}")
    raw = config.get("profiles", {}).get("unification", {}).get("qa_thresholds", {})
    thresholds = {
        "mean_luminance": float(raw.get("mean_luminance_relative_delta", DEFAULT_THRESHOLDS["mean_luminance"])),
        "rms_contrast": float(raw.get("rms_contrast_relative_delta", DEFAULT_THRESHOLDS["rms_contrast"])),
        "mean_saturation": float(raw.get("mean_saturation_relative_delta", DEFAULT_THRESHOLDS["mean_saturation"])),
    }
    route_enabled = bool(config.get("modules", {}).get("route", {}).get("enabled"))
    return thresholds, route_enabled, config


def build_sheet(images: list[tuple[Path, Image.Image]], output: Path, grayscale: bool) -> None:
    thumb_w, thumb_h, label_h = 270, 480, 34
    columns = min(5, max(1, len(images)))
    rows = math.ceil(len(images) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), "#E8E4DC")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for index, (path, source) in enumerate(images):
        row, col = divmod(index, columns)
        image = source.convert("L").convert("RGB") if grayscale else source.copy()
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = col * thumb_w + (thumb_w - image.width) // 2
        y = row * (thumb_h + label_h) + (thumb_h - image.height) // 2
        sheet.paste(image, (x, y))
        draw.text((col * thumb_w + 8, row * (thumb_h + label_h) + thumb_h + 8), path.name, fill="#3B3832", font=font)

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=94)


def build_long_strip(images: list[tuple[Path, Image.Image]], output: Path) -> None:
    max_h = max(image.height for _, image in images)
    normalized: list[Image.Image] = []
    for _, source in images:
        if source.height == max_h:
            normalized.append(source)
        else:
            width = round(source.width * max_h / source.height)
            normalized.append(source.resize((width, max_h), Image.Resampling.LANCZOS))
    strip = Image.new("RGB", (sum(image.width for image in normalized), max_h), "#E8E4DC")
    x = 0
    for image in normalized:
        strip.paste(image, (x, 0))
        x += image.width
    if strip.width > 8000:
        scale = 8000 / strip.width
        strip = strip.resize((8000, max(1, round(strip.height * scale))), Image.Resampling.LANCZOS)
    strip.save(output, quality=92)


def build_boundary_sheet(images: list[tuple[Path, Image.Image]], output: Path, crop_width: int) -> None:
    if len(images) < 2:
        return
    previews: list[tuple[str, Image.Image]] = []
    for index in range(len(images) - 1):
        left_name, left = images[index]
        right_name, right = images[index + 1]
        width = max(1, min(crop_width, left.width, right.width))
        pair = Image.new("RGB", (width * 2, max(left.height, right.height)), "#E8E4DC")
        pair.paste(left.crop((left.width - width, 0, left.width, left.height)), (0, 0))
        pair.paste(right.crop((0, 0, width, right.height)), (width, 0))
        pair.thumbnail((360, 720), Image.Resampling.LANCZOS)
        previews.append((f"{left_name.name} | {right_name.name}", pair))

    cell_w, cell_h, label_h = 380, 720, 36
    columns = min(4, len(previews))
    rows = math.ceil(len(previews) / columns)
    sheet = Image.new("RGB", (columns * cell_w, rows * (cell_h + label_h)), "#E8E4DC")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for i, (label, image) in enumerate(previews):
        row, col = divmod(i, columns)
        x = col * cell_w + (cell_w - image.width) // 2
        y = row * (cell_h + label_h) + (cell_h - image.height) // 2
        sheet.paste(image, (x, y))
        draw.text((col * cell_w + 8, row * (cell_h + label_h) + cell_h + 8), label, fill="#3B3832", font=font)
    sheet.save(output, quality=94)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path, help="Directory containing finished pages")
    parser.add_argument("--output", required=True, type=Path, help="Directory for QA outputs")
    parser.add_argument("--config", type=Path, help="Resolved config from resolve_config.py")
    parser.add_argument("--boundary-width", type=int, default=48, help="Pixels sampled from each side of a page boundary")
    args = parser.parse_args()

    paths = sorted(p for p in args.input.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED)
    if not paths:
        parser.error("No supported image files found")
    if args.boundary_width <= 0:
        parser.error("--boundary-width must be positive")
    try:
        thresholds, route_enabled, config = load_config(args.config)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    images: list[tuple[Path, Image.Image]] = []
    for path in paths:
        with Image.open(path) as image:
            images.append((path, image.convert("RGB")))
    rows = [{"filename": path.name, **metrics(image)} for path, image in images]

    medians = {key: statistics.median(row[key] for row in rows) for key in DEFAULT_THRESHOLDS}
    dimensions = {(row["width"], row["height"]) for row in rows}
    expected = None
    if config:
        canvas = config.get("profiles", {}).get("composition", {}).get("canvas", {})
        expected = (canvas.get("width"), canvas.get("height"))

    for row in rows:
        row["flags"] = [key for key, threshold in thresholds.items() if relative_delta(row[key], medians[key]) > threshold]
        if len(dimensions) > 1:
            row["flags"].append("dimensions")
        if expected and (row["width"], row["height"]) != expected:
            row["flags"].append("expected_dimensions")

    args.output.mkdir(parents=True, exist_ok=True)
    build_sheet(images, args.output / "contact-sheet-color.jpg", grayscale=False)
    build_sheet(images, args.output / "contact-sheet-grayscale.jpg", grayscale=True)
    build_long_strip(images, args.output / "long-strip.jpg")
    if route_enabled:
        build_boundary_sheet(images, args.output / "boundary-previews.jpg", args.boundary_width)

    report = {
        "schema_version": "1.0.0",
        "image_count": len(rows),
        "uniform_dimensions": len(dimensions) == 1,
        "expected_dimensions": list(expected) if expected else None,
        "matches_expected_dimensions": bool(expected and dimensions == {expected}) if expected else None,
        "route_enabled": route_enabled,
        "medians": medians,
        "thresholds": thresholds,
        "metric_flags_are_review_leads_not_failures": True,
        "manual_checks_required": ["subject_integrity", "theme_fidelity", "edge_integration", "layer_separation", "paper_consistency", "style_consistency", "typography_consistency"] + (["route_continuity", "route_endpoints", "route_avoidance"] if route_enabled else []),
        "images": rows,
    }
    (args.output / "qa-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote QA outputs to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
