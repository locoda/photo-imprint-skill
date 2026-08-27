# Style packs

A style pack changes only rendering language. It must not change subject semantics, layer separation, composition, or final QA policy. The subject comes from the source photo and theme, never from a style reference.

## Current profiles

The repository currently contains text-only style specifications while replacement references are reviewed:

- `watercolor-journal` — loose observational line, transparent low-saturation watercolor, warm paper influence, and soft natural edges.
- `botanical-watercolor` — controlled graphite, translucent watercolor, delicate organic edges, sparse paper, and observational detail.
- `paper-collage` — cut or torn matte-paper layering, warm archival color, shallow depth, and intentional negative space.

Each profile is marked `reference_status: pending-selection`. Rendering can resolve from the text rules, but the warning must remain visible until an approved reference set is added.

## Reference sets

A style may use multiple references. Each reference must have a named technique role, such as:

- contour construction;
- paint or material application;
- edge control;
- value grouping;
- surface texture;
- simplification.

Use the same approved set across a series. Do not copy the reference's subject, text, seals, ornaments, or page content into the output.

## Storage and rights policy

Reference binaries stay out of version control until both conditions are approved:

1. item-level redistribution rights are verified through an authoritative institution or library page;
2. the image clearly demonstrates a reusable drawing method rather than only subject matter, historical atmosphere, or composition.

After approval, optimize each distributable derivative to:

- maximum long edge: 1600 px;
- preferred format: WebP;
- quality: 82–88;
- target size: 750 KB or less;
- enough retained detail to inspect line, edge, value, and texture behavior.

Record separate source metadata for every approved reference: title, creator, institution, source image URL, authoritative item record URL, exact item-level rights statement, license URL, download date, redistribution flag, derivative settings, and technique role.

Do not treat “free to view” as permission. Public references require an explicit CC0, Public Domain Mark, or equivalent item-level reuse grant. Private user-supplied references remain local and non-redistributable.

## Adding a style pack

1. Add `profiles/styles/<id>.json` with style rules independent of subject matter.
2. Add zero or more approved entries to its `references` array.
3. Store each approved binary and its source metadata under `assets/style-packs/<id>/`.
4. Run `python3 bin/validate_skill.py`.
