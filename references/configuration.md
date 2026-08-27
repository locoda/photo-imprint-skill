# Configuration model

A preset composes five reusable profiles. Profile JSON files live under `profiles/`.

```json
{
  "preset": "travel-food-journal",
  "version": "1.0.0",
  "profiles": {
    "theme": "food",
    "style": "watercolor-journal",
    "layers": "journal-separated",
    "composition": "vertical-journal",
    "unification": "warm-paper-journal"
  },
  "modules": {},
  "export": {},
  "overrides": {
    "composition": {},
    "unification": {}
  }
}
```

## Independence rule

- **Theme** may change subject extraction, fidelity rules, and context retention. It must not set paper, typography, or global color grading.
- **Style** may change drawing language and reference artwork. It must not change subject semantics or layout coordinates.
- **Layers** owns separation, layer order, and which components are model-rendered versus deterministic.
- **Composition** owns canvas, whitespace, scale, placement, caption zones, and cross-slide rhythm.
- **Unification** owns final paper target, palette/contrast normalization, series-level QA thresholds, and consistency checks.

## Overrides

Use `overrides.<concern>` for project-specific changes. The resolver deep-merges overrides after loading profiles, so profiles remain reusable.

## Defaults

`presets/travel-food-journal.json` is the default bundle. Its five profiles reproduce the accepted Tokyo food-journal look: food extraction, fine-line restrained watercolor, separated overlays, large top whitespace, lower-half subjects, warm matte paper, and whole-series normalization.

## Extending

1. Copy the nearest profile within the same concern.
2. Change its `id`; keep `profile_type` correct.
3. Add only concern-owned fields.
4. For a style with a reference, add `assets/style-packs/<id>/reference.webp` and `source.json`.
5. Point a preset at the new profile and run `bin/resolve_config.py`.
