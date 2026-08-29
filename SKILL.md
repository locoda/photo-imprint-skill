---
name: "photo_imprint"
version: "1.2.0"
description: "Photo Imprint (印痕) — 留住那张照片，只换一种笔触去记。Use when turning photos into a consistent illustrated social-media carousel (including 照片转手绘轮播): keep silhouette/proportions/anchors, redraw in watercolor. EXIF ordering, source-specific briefs, plan+sample gate, clean-plate normalization, deterministic composition, typed revisions, two-level QA, verified packaging."
---

# Photo Imprint (印痕)

## Purpose
Keep the photo, remember it in a different stroke. 留住那张照片，只换一种笔触去记。Convert photos into one coherent illustrated carousel — keep silhouette, proportions, cap/lid, logo position, only the brushwork changes. `presets/travel-food-journal.json` supplies complete workflow defaults; actual subject plates still require a configured renderer and validated receipt. Two independent, opt-in Smithsonian reference packs are bundled: `blue-lavender-watercolor` and `highway-485-lithograph`; neither replaces the preset default or may contribute its depicted subjects. See `references/configuration.md` for defaults and overrides.

## Workflow

### 0. Preflight and inspect state

Install `requirements.txt`, run `python3 bin/check_environment.py`, and after config resolution rerun it with `--config <resolved-config> --font <font-file>`. Typography requires an explicit readable font file; never substitute a font silently. `python3 bin/workflow.py --project <project-dir> status|next` reports state without writing or bypassing a gate.

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

Render only the first EXIF page. Register and validate a `renderer_receipt.py` record containing renderer kind, exact model/version, seed, settings, and source/reference/output hashes. A `not-configured` receipt is an honest blocker, not permission to continue. Normalize/validate the clean plate with `clean_plate.py`, then run `compose.py` with the explicit font and validated receipt before registering both the normalized plate and composed sample.

The Markdown plan must exist. It may be sent as an artifact or faithfully summarized, but all plan decisions and the sample must be discussed together. Record the mode with `review_gate.py mark-shown`. See `references/review-gate.md`.

### 4. Record explicit approval and batch

Copy the user's exact approval message into `review_gate.py approve`, then generate `render_scope.py --mode batch`. Batch scope contains pages 2..N only. Propagate the frozen sample style contract into every page prompt. Use only original approved references; never use page one as a style reference.

### 5. Normalize plates and compose deterministically

Use the active style's profile-driven cleanup policy. Watercolor/pale media and opaque collage must not be treated like line art. Register a full-set renderer receipt whose source/reference sets exactly match the approved plan and whose outputs hash-lock every normalized plate; record per-page seeds in settings when needed. Apply shared paper, placement, typography, route, markers, watermark, and disclosure only after clean plates pass. `compose.py` writes a composition manifest binding config, plan, renderer receipt, font, plates, and final pages. Optional modules must remain removable.

### 6. Review two independent acceptance dimensions

Run `qa_images.py` with the render plan and config. Open every final page at full size and phone scale, not only the contact sheet.

- **Page-level compliance:** each page satisfies its own production brief, source fidelity, material/depth cues, structural-line operations, background cleanliness, and border/seam policy.
- **Set-level cohesion:** the ordered set passes shared paper, style, typography, rhythm, dimensions, and overall visual unity.

Record evidence and validate `review-checklist.json`. Packaging is blocked unless both dimensions pass. See `references/quality-checks.md`.

### 7. Handle post-approval feedback without overcorrection

For non-sample page-local corrections, create `revision_scope.py` changes using only: `remove`, `retain_but_simplify`, `add_as_secondary`, and `preserve_unchanged`. The scope marks only affected pages stale and hash-locks unchanged approved pages.

Any change to page one, the style contract/reference, source/order, shared layout, or system plan invalidates batch approval and returns to the plan+sample gate.

### 8. Stage, package, and deliver

Lock staged numbered images with `package_verified.py stage`; rerun QA against that exact stage and approved config/plan; package with the composition manifest only after checklist validation; then run `package_verified.py verify`. Packaging revalidates current sources, confirmed captions, renderer/plate provenance, QA input locks, review evidence, and exact staged bytes. Artifact delivery copies verified staged outputs and must not regenerate images.

## Failure handling

Fail closed and repair the causal stage:

- environment/font failure → install the declared dependency or supply the configured font, then rerun preflight;
- missing renderer → stop at the render scope; do not fabricate a receipt or claim output exists;
- source/reference/plan hash mismatch → rebuild the plan and return to the sample gate;
- invalid plate or objective QA failure → regenerate or normalize the affected plate, then rerun composition and QA;
- QA/staging mismatch → discard the stale checklist and review the current staged bytes;
- changed shared system, sample, style, source, or order → invalidate approval and restart plan+sample review.

Manual review may decide semantic and aesthetic checks; it can never override machine-verifiable failures.

## Output Contract
- `production-plan.md` always exists before the first render.
- Before explicit approval, only the first EXIF page is renderable.
- The approved visual method is structured, hash-locked, and propagated to batch prompts.
- Plates are normalized/validated under the active style policy.
- Every page and the set pass separate evidence-bearing QA gates.
- Page-local revisions preserve unchanged approved pages.
- Objective failures such as wrong dimensions, invalid plates, severe seam/frame/background diagnostics, changed source hashes, or review/staging hash mismatches cannot be overridden by manual `pass` entries.
- Every rendered plate has a validated renderer receipt; an unconfigured renderer is reported as unavailable, never simulated.
- Deterministic outputs and packaged files contain no EXIF, GPS, or XMP metadata.
- The ZIP contains only verified staged files plus its release manifest; verification also requires the separately written trusted manifest sidecar.

## Operating Rules
1. Keep style separate from subject; reference images contribute techniques, never objects.
2. Keep private references local and out of delivery/version control unless rights permit.
3. Do not claim consistency, transparency, or QA success without opening the actual outputs.
4. Fix the causal layer, not a cosmetic patch.
5. Preserve user authority over plan, sample, revisions, and approval.
6. Keep reusable watermark defaults off; names, handles, and marks are project overrides, never universal defaults.
7. Treat local storage of a private reference and transmission to an external image service as separate permissions. Never upload a private reference without explicit external-processing consent.
