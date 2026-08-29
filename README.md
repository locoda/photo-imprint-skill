# Photo Imprint (印痕)

> Keep the photo, remember it in a different stroke. 留住那张照片，只换一种笔触去记。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Version](https://img.shields.io/badge/version-1.2.0-blue)](SKILL.md) [![Skill](https://img.shields.io/badge/skill-photo__imprint-teal)](#)

`locoda/photo-imprint-skill` · English-first skill, Chinese name 印痕 · 9:16 vertical carousel, EXIF order, gated production

---

## An empowering moment

You took twelve photos — SJC small cup, tray table in flight, Roppongi at night. They sit in your camera roll, too personal to post raw, too scattered to be a story.

You run Photo Imprint. It orders them by EXIF capture time, locks the cup you actually held — silhouette, lid, proportion, logo position — and writes a one-page production brief for each. It renders only page one.

You look at page one and say: "this stroke, keep the lid exactly like that, simplify the cabin to a cool wash." That exact sentence is recorded as approval.

Batch runs with the frozen style contract. Plates are normalized under the active style policy, composed deterministically to 1152×2048 on warm paper `rgb(247,244,235)`, ~50% paper-white breathing room, captions at y=300 / y=367, diffusion restrained to 2–3 edge bleeds ≤10% width. Two-level QA opens every page at full size and 360×640 phone size. The ZIP contains no EXIF, GPS, or XMP.

The first time you post the carousel to IG / Xiaohongshu, it still feels like your trip — just remembered in watercolor. You feel in control, not edited out. That feeling of being remembered, on your own terms, is what this skill is built for.

---

## How it keeps the photo

Not a prompt collection. A gated workflow that keeps five concerns independent, so the stroke changes and the photo stays.

### 1. Theme — what to draw, source is authority
The source photo is authority. Every page gets a rich `production_brief`: subject priority, phone-thumbnail read, identifying anchors, abstraction/omission, material/depth cues, source-grounded `structural_lines` (`retain` or `retain_but_simplify`), and `forbidden_inventions`. No location, date, or caption is invented unless you supply it or explicitly allow draft mode.

### 2. Style — how to draw, techniques only
Style contributes technique, never subject. The bundled opt-in Smithsonian packs `blue-lavender-watercolor` and `highway-485-lithograph` (Allen Tucker, public domain) each declare `technique_roles` and `subject_exclusions`; only the former may influence rendering. The reusable preset defaults to `watercolor-journal` unless your project preset explicitly names another. The generated sample never becomes a style reference.

Shape-lock is why it stays yours: Template B locks cup/bottle silhouette, proportions, cap/lid, logo position; abstraction only in brushwork, colors sampled from the subject itself.

### 3. Layers, composition, unification — where it goes and how the set stays one
- **Layers** owns plate / paper / typography separation and who renders what.
- **Composition** owns deterministic 9:16, 1152×2048, warm paper, placement (Template A `travel-scene-caption-below` image lower 58–62%, Template B `drink-minimal-caption-above` caption above), typography `NotoSerifDisplay-Regular 48pt / Light 27pt #403C44`, diffusion limits, forbidden elements.
- **Unification** owns shared paper, brightness, grain, caption y, rhythm.

`presets/travel-food-journal.json` supplies complete workflow defaults. Actual plates still require a configured renderer and a validated receipt (`renderer_receipt.py`) recording model/version/seed/settings and source/reference/output hashes. A `not-configured` receipt is an honest blocker, not permission to continue.

### 4. Gated production — plan + sample, then explicit approval
```
photos → EXIF order → per-page brief + sample_style_contract → production-plan.md
      → render page 1 only → hash-lock sample style contract
      → discuss plan+sample together (artifact or faithful summary) → record mode
      → explicit approval with your exact message → batch 2..N with frozen contract
      → clean-plate normalization (profile-driven) → deterministic composition
      → two-level QA → verified ZIP + release manifest
```
`workflow.py status` / `next` never writes; it only tells you what to do next. Private references stay local unless you give separate explicit consent for external image-service processing.

### 5. Two independent QA gates and verified packaging
- **Page-level compliance:** subject priority, thumbnail read, anchors, material/depth cues, structural-line operations, no forbidden inventions, background cleanliness, no rectangular seam or forbidden frame.
- **Set-level cohesion:** overall visual unity, shared paper, style/mark consistency, typography, order/dimensions, cross-page rhythm, optional-module integrity.

Packaging is blocked unless both pass. `package_verified.py stage` hash-locks numbered images, QA runs against that exact stage, `package` revalidates sources, captions, renderer/plate provenance, QA locks, review evidence, and exact staged bytes. Delivery copies verified staged outputs and must not regenerate images. Final outputs contain no EXIF, GPS, or XMP.

### 6. Post-approval revisions without overcorrection
Non-sample page-local fixes use only four typed operations: `remove`, `retain_but_simplify`, `add_as_secondary`, `preserve_unchanged`. Scope marks only affected pages stale and hash-locks unchanged approved pages. Any change to page one, style contract, source/order, shared layout, or system plan invalidates batch approval and returns to plan+sample.

---

## What remains open

Honest limits in 1.2.0:

- No image-generation backend is bundled. You must configure a renderer and supply a validated receipt; without it the skill stops at render scope.
- Typography requires an explicit readable font file; no silent substitution.
- Template A (open travel scenes) is implemented but has no locked sample set in this repo — share 2–3 scene photos to add a Template A example in `assets/samples/`.
- Three text-only style profiles remain `reference_status: pending-selection`: `watercolor-journal`, `botanical-watercolor`, `paper-collage`. They render from text rules until an approved reference set is added with full source metadata.
- Private references require two separate consents: local storage vs. external processing. Local presence never implies upload permission.
- Contact-sheet alone is insufficient for QA — full-size and phone evidence must exist for every page.

## Where this could go

Not promises, just directions:

- Additional layout templates for city maps and food journals, keeping 9:16 and 50% paper-white.
- More Smithsonian public-domain packs after item-level rights verification and derivative optimization (long edge 1600px, WebP 82–88, ≤750KB).
- Optional modules (route line with hand-drawn markers, watermark as project override, disclosure) staying removable and off by default.
- Phone-thumbnail tuning helpers and preflight caption verification against EXIF.
- Evaluation set for source fidelity, style boundary, layout compliance, and set cohesion, shared across 对坐 and 牌间 showcase.

---

## License

MIT License — Copyright (c) 2026 locoda. See [LICENSE](LICENSE). Code and docs are MIT; bundled style-pack derivatives are public domain with separate provenance in `assets/style-packs/*/source.json`.

## References and credits

- **Style references (bundled, opt-in):**
  - Allen Tucker *Watercolor no. 73, Blue and Lavender* (1928, watercolor, Smithsonian American Art Museum 1966.34.7) — technique roles: transparent wash, soft-to-controlled edge, cool blue/lavender value grouping, selective dark anchors. Subject exclusions: seascape, shoreline, water horizon, landscape subject, composition. Derivative: 1600×1107 WebP, 242KB, SHA256 `2eaaba...1b10`, stripped EXIF/GPS/XMP. Source TIFF 149MB. Rights: public domain, free to use. [Record](https://americanart.si.edu/artwork/watercolor-no-73-blue-and-lavender-24276)
  - Allen Tucker *Highway 485* (lithograph, SAAM 1966.34.9) — technique roles: sparse broken dry-crayon/contour, paper-white negative space, restrained dark accents, radical simplification, limited hatching. Subject exclusions: road, road sign, utility poles, wires, landscape subject, composition. Derivative: 1600×1113 WebP, 83KB. Rights: public domain. [Record](https://americanart.si.edu/artwork/highway-485-24266)
  - Both stored under `assets/style-packs/*/reference.webp` with full `source.json` provenance (institution, object number, license URL, retrieval date, derivative settings).

- **Preset & profiles:** `presets/travel-food-journal.json` composing five concerns (theme/style/layers/composition/unification) with `workflow_defaults` for EXIF ordering, mandatory production-plan, first-page-only sample, explicit approval, deterministic composition, typed revisions, hash-locked staging.

- **Fonts / typography:** Default composition expects `NotoSerifDisplay-Regular` / Light (SIL OFL). You must supply the actual font file; the skill validates readability and records it in the composition manifest.

- **Validation:** 34 gate/regression checks in `tests/`, `bin/validate_skill.py`, `bin/check_environment.py`.

Private user-supplied references stay out of version control and delivery unless rights permit and explicit external-processing consent is given.

---

## Made by

Made by [1mether](https://1mether.me).

---

If this skill is useful to you, consider starring the repository.

[English](README.md) | [中文](README.zh-CN.md)
