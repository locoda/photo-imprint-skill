# Quality checks

## Blocking checks

Every page must pass before delivery.

1. **Dimensions**: identical requested dimensions and aspect ratio.
2. **Subject integrity**: no missing identity-critical object, clipped vessel/building/landmark, accidental duplication, or distorted relationship.
3. **Theme fidelity**: preserved elements match the selected theme profile; forbidden inventions are absent.
4. **Subject/caption clearance**: no overlap; preserve the composition profile's minimum clearance.
5. **Edge integration**: no unintended rectangular crop, mask edge, white fringe, or compositing seam.
6. **Layer separation**: no generated typography, route, marker, watermark, border, or numbering in the clean subject plate.
7. **Paper consistency**: the same paper master, color, texture scale, and finish across all pages.
8. **Style consistency**: comparable line weight, edge treatment, detail density, and color behavior defined by the style profile.
9. **Color consistency**: no unexplained outlier in brightness, black point, contrast, saturation, or color temperature.
10. **Typography**: identical approved font, size, tracking, leading, color, alignment, coordinates, and line count.
11. **Optional route**: exactly one line layer; no shadow, duplicate, branch, leftover segment, or jagged edge.
12. **Route continuity**: adjacent boundaries match exactly; the line avoids every subject and caption.
13. **Endpoints**: first page starts at its marker and last page ends at its marker; no line outside those nodes.
14. **Watermark/disclosure**: exact approved text, consistent placement, and no accidental extra copy.

## Series-level review

Create and inspect:
- color contact sheet;
- grayscale contact sheet;
- long-strip preview in final order;
- enlarged boundary crops when a cross-slide element is enabled;
- resolved config and source metadata for the active style.

Automated metric flags are leads, not proof. A legitimate dark dish, night landscape, or bright facade may differ from the median. Correct style drift, not the identity of the photographed subject.

## Repair rule

Fix the source layer that caused the defect. Re-render the subject plate or rebuild the deterministic overlay, then rerun the full check. Do not cover a defect with a patch that introduces a new seam, double line, or inconsistent paper area.
