# Photo Imprint (印痕)

> Not a filter. It keeps what your photo is, and redraws how it feels.

[English](README.md) | [中文](README.zh-CN.md)

Turn real travel photos into a consistent watercolor journal carousel for Instagram / Xiaohongshu — without losing the identity of each source image.

`locoda/photo-imprint-skill` · English skill, Chinese name 印痕

## See what it does

Direct prompting gives you a pretty picture that forgets your photo. Photo Imprint keeps the silhouette, proportions, and anchors, and only abstracts the brushwork.

| Source photo | Photo Imprint (Template B – drink-minimal-caption-above) |
|---|---|
| ![source 01](assets/samples/source-01.webp) | ![imprint 01](assets/samples/01-sjc-small-cup-paper-locked-v11.webp) |
| SJC Airport – small cup, green drink, clear lid | Same cup, same lid, same proportion. 50% paper white, caption `SJC Airport` at y=300 / y=367, diffusion ≤10% width, 2–3 edge bleeds only |
| ![source 02](assets/samples/source-02.webp) | ![imprint 02](assets/samples/02-in-flight-paper-locked-v11.webp) |
| In-flight cup in hand | Cup locked, cabin simplified to cool wash, no invented skyline |
| ![source 03](assets/samples/source-03.webp) | ![imprint 03](assets/samples/03-roppongi-paper-locked-v11.webp) |
| Roppongi street cup | Cup locked, background strongly simplified, no Tokyo Tower invented |

All samples are locally compressed to webp <100KB (`assets/samples/`). Full 1152×2048 finals are 399–430KB jpg, no EXIF.

Template A (travel-scene-caption-below) works the same — image lower, caption below — for open scenes. Share 2–3 travel photos and I will add a Template A example in the same folder.

## Install and use

```bash
npx skills add locoda/photo-imprint-skill
# or
git clone https://github.com/locoda/photo-imprint-skill.git
pip install -r requirements.txt
python3 bin/check_environment.py
```

3 steps:

```bash
# 1. EXIF order + manifest
python3 bin/preprocess.py --input /path/to/photos --output work/manifest.json --config work/resolved-config.json

# 2. Plan + sample only
python3 bin/build_production_plan.py --render-plan work/render-plan.json --output work/production-plan.md
# render page 1, discuss plan+sample together

# 3. After explicit approval → batch → QA → ZIP
python3 bin/package_verified.py package --input work/final --output dist/carousel.zip
```

`workflow.py status` / `next` never writes, it only tells you what to do next.

## How it works

This is not a prompt collection. It's a gated production workflow that keeps 5 concerns independent:

1. **Theme** – what to draw (source photo is authority)
2. **Style** – how to draw it (wash, edge, value grouping from a reference, never its subject)
3. **Layers** – what must stay separate (plate / paper / typography)
4. **Composition** – where each element goes (deterministic, 9:16, 1152×2048, paper `rgb(247,244,235)`)
5. **Unification** – how the set is normalized (same brightness, same grain, same caption y=300/367)

Principle:

```
photos → EXIF order → per-page production_brief (preserve / simplify / omit) → production-plan.md
      → render page 1 only → hash-lock sample style contract (mark, edge, negative-space, tonal, background, frame, abstraction)
      → discuss plan+sample → explicit user approval (exact message)
      → batch pages 2..N with frozen contract → clean-plate normalization (profile-driven)
      → deterministic composition (paper, placement, caption) → two-level QA
      → verified ZIP (no EXIF/GPS/XMP)
```

Why the sample gate? Direct prompting drifts: small cup becomes tall cup, bottle shoulder warps, MEGA label changes. Here shape-lock is enforced:

- Template B: cup/bottle silhouette, proportions, cap/lid, logo position locked; abstraction only in brushwork
- Diffusion is restrained: 2–3 ultra-light edge bleeds ≤10% width right / ≤8% height bottom, colors sampled from subject itself, rest is clean paper

Typed revisions after approval (`remove`, `retain_but_simplify`, `add_as_secondary`, `preserve_unchanged`) prevent “the roads feel strange” from becoming “delete every road”.

## 2 layout templates (structured)

Both are part of the plan, locked before rendering. Typography is added after plate, never generated inside artwork.

**Template A: `travel-scene-caption-below`** – image lower (vertical center 58–62%, scale 38–45%), caption below, ~50% negative space top/sides, very light wash behind subject only.

**Template B: `drink-minimal-caption-above`** – caption above at y=300/367, subject centered 60–65% (scale 32–40%, small cup stays small), same 50% paper, restrained diffusion. Current 3-page set uses this.

See `production-plan.md` for full fields: canvas, paper, placement, typography (`NotoSerifDisplay-Regular 48pt / Light 27pt`, `#403C44`), diffusion limits, forbidden elements.

## vs naive prompting

| Naive | Photo Imprint |
|---|---|
| One prompt for all pages | Per-page brief + frozen style contract |
| Invents background / landmarks | Forbidden-inventions list enforced |
| Small cup → big cup | Shape-lock, small stays small |
| 3 pages 3 different papers | Unified warm white, same grain/brightness, captions aligned |
| No review | Page-level compliance + set-level cohesion, separate gates |

## Project layout

```
SKILL.md                  # operational workflow (English)
presets/travel-food-journal.json
profiles/{themes,styles,layers,compositions,unification}/
assets/samples/           # compressed before/after (webp <100KB)
assets/style-packs/       # Smithsonian public-domain packs (blue-lavender-watercolor, highway-485-lithograph)
tests/                    # 34 gate/regression checks
```

Private reference images stay local and are never sent externally without explicit consent. Final ZIP contains only verified numbered images + release manifest.

## Validation

```bash
python3 -m unittest discover -s tests -v
python3 bin/validate_skill.py --json
```
