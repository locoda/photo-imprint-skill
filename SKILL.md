---
name: "photo_to_illustration_carousel"
description: "Turn user photos into a consistent illustrated social-media carousel with EXIF ordering, source-specific visual briefs, a plan+sample approval gate, clean-plate normalization, deterministic overlays, typed revisions, two-level visual QA, and verified packaging."
---

# Photo-to-Illustration Carousel

## Purpose
Convert photos into one coherent illustrated carousel while keeping five controls independent: theme, style, layers, composition, and unification. `presets/travel-food-journal.json` is the complete executable default; see `references/configuration.md` for defaults and overrides.

## Workflow

### 1. Resolve and preprocess

```bash
python3 bin/resolve_config.py --preset presets/travel-food-journal.json --output work/resolved-config.json
python3 bin/preprocess.py --input <photos> --output work/manifest.json --config work/resolved-config.json
```

Order by EXIF. Stop on missing factual metadata unless the user explicitly authorizes draft mode. Never invent captions, dates, locations, or page-specific subject decisions.

### 2. Complete the plan inputs

For every page, fill the required `production_brief`: subject priority, phone-thumbnail read, identifying anchors, abstraction/omission, material/depth cues, source-grounded structural lines (`retain` or `retain_but_simplify`), and forbidden inventions. Confirm the project `sample_style_contract`: mark/edge quality, negative-space rules, fill/tonal rules, background cleanliness, frame/border policy, and abstraction level. The generated sample must never become a style reference.

```bash
python3 bin/build_render_plan.py --config work/resolved-config.json --manifest work/manifest.json --output work/render-plan.json
python3 bin/build_production_plan.py --render-plan work/render-plan.json --output work/production-plan.md --state-output work/approval-state.json
python3 bin/render_scope.py --render-plan work/render-plan.json --state work/approval-state.json --mode sample --output work/sample-scope.json
```

### 3. Render, normalize, and discuss only page one

Render only the first EXIF page. Normalize/validate its clean plate with `clean_plate.py`, compose deterministic paper/text/modules, then register both the normalized plate and composed sample.

The Markdown plan must exist. It may be sent as an artifact or faithfully summarized, but all plan decisions and the sample must be discussed together. Record the mode with `review_gate.py mark-shown`. See `references/review-gate.md`.

### 4. Record explicit approval and batch

Copy the user's exact approval message into `review_gate.py approve`, then generate `render_scope.py --mode batch`. Batch scope contains pages 2..N only. Propagate the frozen sample style contract into every page prompt. Use only original approved references; never use page one as a style reference.

### 5. Normalize plates and compose deterministically

Use the active style's profile-driven cleanup policy. Watercolor/pale media and opaque collage must not be treated like line art. Apply shared paper, placement, typography, route, markers, watermark, and disclosure only after clean plates pass. Optional modules must remain removable.

### 6. Review two independent acceptance dimensions

Run `qa_images.py` with the render plan and config. Open every final page at full size and phone scale, not only the contact sheet.

- **Page-level compliance:** each page satisfies its own production brief, source fidelity, material/depth cues, structural-line operations, background cleanliness, and border/seam policy.
- **Set-level cohesion:** the ordered set passes shared paper, style, typography, rhythm, dimensions, and overall visual unity.

Record evidence and validate `review-checklist.json`. Packaging is blocked unless both dimensions pass. See `references/quality-checks.md`.

### 7. Handle post-approval feedback without overcorrection

For non-sample page-local corrections, create `revision_scope.py` changes using only: `remove`, `retain_but_simplify`, `add_as_secondary`, and `preserve_unchanged`. The scope marks only affected pages stale and hash-locks unchanged approved pages.

Any change to page one, the style contract/reference, source/order, shared layout, or system plan invalidates batch approval and returns to the plan+sample gate.

### 8. Stage, package, and deliver

Lock staged numbered images with `package_verified.py stage`; rerun QA against that stage; package only after checklist validation; then run `package_verified.py verify`. Artifact delivery copies verified staged outputs and must not regenerate images.

## Output Contract
- `production-plan.md` always exists before the first render.
- Before explicit approval, only the first EXIF page is renderable.
- The approved visual method is structured, hash-locked, and propagated to batch prompts.
- Plates are normalized/validated under the active style policy.
- Every page and the set pass separate evidence-bearing QA gates.
- Page-local revisions preserve unchanged approved pages.
- The ZIP contains only verified staged files plus its release manifest.

## Operating Rules
1. Keep style separate from subject; reference images contribute techniques, never objects.
2. Keep private references local and out of delivery/version control unless rights permit.
3. Do not claim consistency, transparency, or QA success without opening the actual outputs.
4. Fix the causal layer, not a cosmetic patch.
5. Preserve user authority over plan, sample, revisions, and approval.
