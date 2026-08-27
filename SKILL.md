---
name: "photo_to_illustration_carousel"
description: "Turn one or more user photos into a visually consistent illustrated social-media carousel. Use for photo-to-illustration conversion, EXIF ordering, independently selectable theme/style/layer/composition/unification profiles, deterministic overlays, series QA, and export-ready image sets."
---

# Photo-to-Illustration Carousel

## Purpose
Convert real photos into a cohesive illustrated carousel without coupling subject choice, rendering style, layers, layout, or final color treatment.

The five independent controls are:
1. **Theme** — what to draw.
2. **Style** — how to draw it.
3. **Layers** — what must remain separate.
4. **Composition** — where each element goes.
5. **Unification** — how the set is normalized and checked.

Each concern has a default. With no overrides, resolve `presets/travel-food-journal.json`; it reproduces the August 2026 Tokyo food-journal direction.

## Workflow

### 1. Intake
Collect source photos and only decisions that change the build: preset/profile overrides, aspect ratio, ordering, caption fields, and optional modules. Never invent dates, locations, labels, or decorative copy.

### 2. Resolve configuration
Resolve and validate the preset before rendering:

```bash
python3 bin/resolve_config.py \
  --preset presets/travel-food-journal.json \
  --output work/resolved-config.json
```

A preset selects one profile from each concern. User overrides belong in the preset's `overrides` object; do not edit a reusable profile for one project. See `references/configuration.md`.

### 3. Preprocess photos

```bash
python3 bin/preprocess.py \
  --input <photo-directory> \
  --output work/manifest.json \
  --config work/resolved-config.json
```

Use EXIF `DateTimeOriginal`, then digitized/general EXIF dates. If dates are missing or invalid, stop unless the user explicitly authorizes draft mode with `--allow-missing`.

### 4. Build the render plan and render clean layers

```bash
python3 bin/build_render_plan.py \
  --config work/resolved-config.json \
  --manifest work/manifest.json \
  --output work/render-plan.json
```

For every page, use only its source photo, the selected style's approved reference set, and that page's render brief. Subject matter comes from the source photo and theme; reference subjects must never leak into the result. A style may use multiple references when each one has a clear technique role, such as line construction, watercolor handling, value grouping, texture, or simplification. Keep the same reference set across the series.

A private reference may be used only when it is present locally; never upload, commit, redistribute, or send it to an external service that the user did not authorize. Render the subject as a clean plate with no generated text, route line, marker, watermark, border, or numbering. Preserve identity-critical objects, vessels, and spatial relationships required by the theme.

Generate or assemble layers according to the resolved layer profile. Do not use earlier generated pages as style references; always return to the approved reference set.

### 5. Compose deterministically
Apply paper, placement, typography, route, markers, watermark, and disclosure after the illustration plate exists. Optional modules must be removable without changing the clean subject render.

When a cross-slide route is enabled, draw one anti-aliased path on a single long canvas, then crop it into pages. The path starts and ends at the endpoint markers and avoids subjects and caption zones.

### 6. Unify and inspect
Normalize the whole set using the resolved unification profile, then run:

```bash
python3 bin/qa_images.py \
  --input <finished-pages> \
  --output work/qa \
  --config work/resolved-config.json
```

Inspect color and grayscale contact sheets, the long-strip preview, and boundary crops when cross-slide elements are enabled. Metric flags are review leads, not automatic failures. Complete `references/quality-checks.md` before delivery.

### 7. Deliver
Preserve requested order and naming. Deliver final numbered images, manifest, resolved config, and a verified ZIP; include QA outputs when useful. Use artifact delivery for anything the user needs to keep or download.

## Output Contract
- Every page has identical requested dimensions.
- The subject remains faithful to its source photo.
- Text and modular decorations are deterministic overlays, never model-generated.
- Disabling route, captions, markers, watermark, or disclosure does not alter the subject render.
- The series reads as one visual system after unification.

## Operating Rules
1. Preserve the user's authority over wording, design, implementation, and defaults.
2. Do not guess missing factual metadata.
3. Keep the five profile concerns independent.
4. Keep style separate from subject. A style may use multiple approved references, each assigned a technique role. Every reference must visibly contribute to line construction, paint or material application, edge handling, value grouping, texture, or simplification; record item-level rights for each one.
5. Treat private references as non-redistributable unless rights are established. Keep them local and excluded from version control.
6. Do not claim licensing, consistency, or QA success without inspecting the actual files.
7. Fix the source layer that caused a defect; do not hide it with a patch.
