# Evaluation — results.tsv / test-prompts.json

These files document Darwin optimization (2026-08-30) that raised score 59.45 → 91.9 → 92.6.

- `test-prompts.json` — 3 scenarios used for paired comparison:
  1. typical travel-food carousel (9 photos, 9:16, whitespace, caption above)
  2. ambiguous style (user delegates — must show 8 thumbnails, default watercolor) — originally 5, updated to 8 after profile count fix
  3. failure/boundary (EXIF missing + small cup must stay small — shape-lock, freeze contract)

- `results.tsv` — timestamp, commit, old_score, new_score, status, dimension, note, eval_mode
  - baseline dry_run 100% weighted_gap max dim8=13.8
  - paired judges: dim8+dim4+dim9 (9:16 defaults, style gate, batch hash-lock, notifications, gates, blacklist)
  - dim5+dim2 (per-step Input/Output/Command, JSON schemas, last-step.md)
  - dim3+dim7 (6 layers, 6 invariants, 22-row Failure Mode Matrix)
  - 48ea3f8 → 91.9 final (JudgeA 91.4, JudgeB 92.4 avg 91.9)
  - 3b67459 → 92.6 after PR19 top-3 blockers fix (path work/root compat, subject-only contract emphasized, QA zone derived from center_y_ratio, dimension downgraded to warning, preset cwd-intuitive, version/canvas/paper/styles/7d throttle/CLI truth)

Re-run with `python3 bin/validate_skill.py` + Darwin evaluator (external LLM judges). Local simulation above approximates same rubric.

Local acceptance (2026-08-30 16:50 PDT):
- Gate A Capability Truth: PASS
- Gate B 3-way Alignment: PASS (version 1.6.0, canvas 1152×2048, paper #F1EBDD, 8 styles, 7d throttle, CLI real)
- Gate C Regression: PASS (no drop, +0.7 vs 91.9)
- Gate D Smoke: PASS (validate_skill.py PASS, workflow.py supports work/ and root)
