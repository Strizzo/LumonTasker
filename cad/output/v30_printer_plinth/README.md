# V30 — matching printer base

The new navy `foot_right_bonded` fills the missing z0–9 mm beneath the exact v28 shell. It shares the left foot's ground plane, 2.5 mm inset and 5 mm lower bevel. The outside corners have an 11.5 mm radius. The v29 rear-hatch correction is retained.

Print `foot_right_navy.stl` as a separate single-colour PLA part, underside flat on the bed. Proposed filament: existing A1 navy PLA. Bounds: 172.5 × 156 × 9 mm. Slicer setup and print approval are still required; no print was launched.

Assembly: dry-fit under the joined enclosure first, front edge aligned and feet on a flat surface. The shell rests on the top lands; five 0.3 mm-deep recessed beds provide room for adhesive. Apply adhesive only within those beds and seat the lands fully against the shell. Do not use thick foam tape that raises the shell. This bonded retention avoids drilling or revising the shell already being printed. Rear withdrawal of the native printer remains available without removing the base.

The switch relief, rear cable channel and inter-bay cable notch remain open through the base. No new screw holes or assumed fasteners have been added. Physical fit and adhesive retention have not yet been tested.

Checks in `audit.json`: one valid watertight solid, common ground plane, every bonding bed backed by the shell floor, zero interference with all existing assembly parts, and zero intrusion into the three relief volumes.

Regenerate: `.venv/bin/python cad/review/build_v30_plinth.py` from the project root. Fusion project `lumon`: `LUMON_v30_MATCHING_BASE_REVIEW`.
