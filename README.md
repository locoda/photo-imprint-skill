# Photo-to-Illustration Carousel

Turn a set of real photos into a consistent illustrated social-media carousel without losing the identity of each source image.

This project is not just a prompt collection. It is a gated production workflow for:

- ordering photos from EXIF metadata;
- deciding what each page must preserve, simplify, or omit;
- separating subject rendering from typography and layout;
- reviewing a production plan and one sample before batch rendering;
- checking every page against its own brief;
- checking the carousel as one visual system;
- revising only the affected pages; and
- packaging only verified final files.

## Core model

Five concerns stay independent:

1. **Theme** — what to draw.
2. **Style** — how to draw it.
3. **Layers** — what must remain separate.
4. **Composition** — where each element goes.
5. **Unification** — how the finished set is normalized and reviewed.

A style reference teaches mark-making, edge behavior, value grouping, texture, or simplification. It does **not** supply subject matter. The source photo remains the authority for the scene.

## Workflow

```text
photos
  ↓
resolve config + EXIF order
  ↓
write per-page production briefs
  ↓
production-plan.md
  ↓
render first EXIF page only
  ↓
discuss plan decisions + sample
  ↓
explicit approval
  ↓
render remaining pages
  ↓
clean plates + deterministic composition
  ↓
page-level QA + set-level QA
  ↓
verified staging + ZIP
```

The production-plan Markdown must always exist. It does not always need to be sent as a file, but its decisions must be communicated and discussed with the sample.

## Default configuration

`presets/travel-food-journal.json` provides a complete executable default once factual captions and source-specific page decisions are supplied.

Defaults include:

- EXIF capture-time ordering;
- a mandatory production plan;
- the first EXIF page as the only pre-approval sample;
- explicit user approval before pages 2..N;
- profile-driven plate cleanup;
- full-size and 360×640 phone review for every page;
- separate page-compliance and set-cohesion gates;
- typed post-approval revisions; and
- hash-locked staging and verified ZIP packaging.

The workflow never invents missing dates, locations, caption facts, subject priorities, identifying anchors, material cues, structural lines, or forbidden elements.

## Quick start

Run commands from the repository root.

### 1. Resolve the preset

```bash
mkdir -p work
python3 bin/resolve_config.py \
  --preset presets/travel-food-journal.json \
  --output work/resolved-config.json
```

### 2. Preprocess and EXIF-order the photos

```bash
python3 bin/preprocess.py \
  --input /path/to/photos \
  --output work/manifest.json \
  --config work/resolved-config.json
```

If capture dates are missing or invalid, the workflow stops unless draft mode is explicitly authorized.

### 3. Complete each page brief

Every manifest item needs a `production_brief`:

```json
{
  "subject_priority": "what must read first",
  "thumbnail_read": "what must remain legible at phone size",
  "preserve_anchors": ["identity-critical anchor"],
  "abstract_or_omit": ["detail to summarize or remove"],
  "material_depth_cues": ["glass transparency", "bird's-eye compression"],
  "structural_lines": [
    {
      "element": "major road direction",
      "operation": "retain_but_simplify"
    }
  ],
  "forbidden_inventions": ["transport lines absent from the source"]
}
```

### 4. Build the render plan and production plan

```bash
python3 bin/build_render_plan.py \
  --config work/resolved-config.json \
  --manifest work/manifest.json \
  --output work/render-plan.json

python3 bin/build_production_plan.py \
  --render-plan work/render-plan.json \
  --output work/production-plan.md \
  --state-output work/approval-state.json
```

### 5. Render only the sample page

```bash
python3 bin/render_scope.py \
  --render-plan work/render-plan.json \
  --state work/approval-state.json \
  --mode sample \
  --output work/sample-render-plan.json
```

Render the clean subject plate from this one-page scope. Do not generate typography, watermark, route, markers, border, or numbering inside the artwork.

Normalize and validate the plate according to the active style profile:

```bash
python3 bin/clean_plate.py normalize \
  --input work/raw/01.png \
  --config work/resolved-config.json \
  --output work/plates/01.png \
  --report work/plates/01-normalization.json

python3 bin/clean_plate.py validate \
  --input work/plates/01.png \
  --config work/resolved-config.json \
  --report work/plates/01-validation.json
```

Compose the deterministic overlays, then register the clean plate and sample:

```bash
python3 bin/review_gate.py register-sample \
  --state work/approval-state.json \
  --sample-plate work/plates/01.png \
  --sample work/sample/01.webp
```

### 6. Discuss the plan and sample

The plan may be communicated as an artifact or a faithful summary. Both the plan decisions and sample must be discussed.

```bash
python3 bin/review_gate.py mark-shown \
  --state work/approval-state.json \
  --presentation-mode faithful-summary \
  --discussion-note 'Page decisions and sample reviewed together' \
  --plan-decisions-communicated \
  --sample-discussed \
  --decision-coverage ordered-page-briefs \
  --decision-coverage sample-style-contract \
  --decision-coverage sample-scope \
  --decision-coverage finish-qa-delivery
```

The approved sample freezes a structured style contract: mark and edge quality, negative-space behavior, tonal rules, background cleanliness, frame policy, and abstraction level. The generated sample is approval evidence, never a style reference.

### 7. Record explicit approval and render the batch

```bash
python3 bin/review_gate.py approve \
  --state work/approval-state.json \
  --approval-text '<exact user approval message>' \
  --explicit-user-approval

python3 bin/render_scope.py \
  --render-plan work/render-plan.json \
  --state work/approval-state.json \
  --mode batch \
  --output work/batch-render-plan.json
```

The batch scope contains pages 2..N only. A one-page carousel has an empty batch scope after approval.

## Acceptance has two independent dimensions

### Page-level compliance

Every page must satisfy its own production brief:

- subject priority and thumbnail read;
- identifying anchors;
- material and depth cues;
- retained or simplified structural lines;
- forbidden inventions;
- clean background and compositing;
- no unintended seam, frame, or border; and
- full-size and phone-scale review.

### Set-level cohesion

The ordered carousel must also work as one visual system:

- shared paper and color treatment;
- consistent mark language and density;
- consistent typography;
- correct dimensions and order;
- deliberate cross-page rhythm; and
- correct optional modules.

A unified set can still contain a wrong page. A correct page can still belong to an inconsistent set. Packaging is blocked if either gate fails.

Generate QA evidence:

```bash
python3 bin/qa_images.py \
  --input work/final \
  --plates work/plates \
  --render-plan work/render-plan.json \
  --config work/resolved-config.json \
  --output work/qa
```

Complete and validate the machine-readable review checklist:

```bash
python3 bin/review_checklist.py validate \
  --checklist work/qa/review-checklist.json
```

Automated metrics are review leads, not substitutes for visual inspection. Open every final page at full size and phone scale; a contact sheet alone is not sufficient.

## Post-approval revisions

Page-local corrections use explicit operations:

- `remove`
- `retain_but_simplify`
- `add_as_secondary`
- `preserve_unchanged`

This prevents feedback such as “the roads feel strange” from being misread as “delete every road.”

Example changes file:

```json
{
  "changes": [
    {
      "page": 4,
      "domain": "page-content",
      "operation": "retain_but_simplify",
      "target": "major roads",
      "instruction": "keep fewer, wider directional lines"
    }
  ]
}
```

Create a revision scope:

```bash
python3 bin/revision_scope.py \
  --render-plan work/render-plan.json \
  --state work/approval-state.json \
  --staging-manifest work/staging-manifest.json \
  --changes work/revision-changes.json \
  --request-text '<exact user correction>' \
  --impact page-local \
  --output work/revision-render-plan.json
```

Page-local revisions mark only affected pages stale and hash-lock unchanged pages. Changes to the sample, style references, shared system, source order, or first page return the project to the plan-and-sample gate.

## Verified packaging

```bash
python3 bin/package_verified.py stage \
  --input work/final \
  --output work/staging-manifest.json

python3 bin/package_verified.py package \
  --input work/final \
  --staging-manifest work/staging-manifest.json \
  --review-checklist work/qa/review-checklist.json \
  --state work/approval-state.json \
  --output dist/carousel.zip \
  --manifest-output dist/release-manifest.json

python3 bin/package_verified.py verify \
  --zip dist/carousel.zip
```

The ZIP contains only verified numbered images and `release-manifest.json`. Delivery should copy these staged outputs rather than regenerate artwork.

## Project layout

```text
SKILL.md                         operational workflow
presets/                         complete starting configurations
profiles/themes/                 subject-selection rules
profiles/styles/                 rendering and plate-cleanup rules
profiles/layers/                 layer-separation contracts
profiles/compositions/           canvas and placement systems
profiles/unification/            cross-page normalization
bin/                             deterministic workflow helpers
references/                      detailed configuration and QA protocols
tests/                           regression and gate tests
```

## Validation

```bash
python3 -m unittest discover -s tests -v
python3 bin/validate_skill.py --json
python3 -m py_compile bin/*.py tests/*.py
```

The regression suite includes generic, non-private cases for:

- clean cloud contours with no frame;
- a central courtyard tree with surrounding context;
- a glass facade with trees as secondary decoration; and
- a high-altitude city with summarized buildings and retained-but-simplified roads.

## References and privacy

Keep private reference images local and out of version control. A reference may be added to a reusable style pack only after its rights and instructional value are verified. Record a clear technique role for every approved reference.

See:

- [`SKILL.md`](SKILL.md)
- [`references/configuration.md`](references/configuration.md)
- [`references/review-gate.md`](references/review-gate.md)
- [`references/quality-checks.md`](references/quality-checks.md)
