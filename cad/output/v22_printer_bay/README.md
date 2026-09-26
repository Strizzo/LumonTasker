# V22 rear-loading printer bay — prototype, not print-released

**USER HOLD: preparation only; do not print until renewed user authorization.**

Source: `cad/printer_bay_v22.py`. Bambu project packer: `cad/review/pack_printer_projects.py`.

## Design

The intact printer slides in from the rear onto a removable tray. Two rear bars retain it; a separate rear cover conceals them. The front is part of the main shell and has no removable panel or front screws. Side guides have 1mm nominal clearance to the measured 131mm body width, so its corner radius is not needed. The native keyholes (61mm centres, 132mm from large-hole centres to original rear/cable edge) are recorded but unused.

Rotated printer envelope: 131 W × 120 D × 175 H mm. Controls face forward near the bottom, original rear/cable edge is above. Front clearance is 1mm, rear retaining-pad clearance 0.5mm. Optional removable shims can take up play after trial fitting. Never force the body into place.

The front aperture is 127 W × 88 H mm, exposing a generous lower region for the native cutter and buttons. Their exact locations and paper trajectory are not measured; this aperture requires physical verification. The grey block in renders represents the printer envelope, not a second panel to print. Native printer casing, lid and mechanism stay intact.

## Assembly and paper changes

1. Fit M3 heat-set inserts in the tested 4.2mm bores, flush and square. Keep bores clear.
2. Place the tray on the shell floor and slide the printer in from the rear.
3. Confirm the front opening clears the cutter, paper and buttons, and pads contact solid casing. Route cables through the upper rear opening without pinching or tight bends.
4. Attach two retaining bars with four M3×12 screws (6mm bar thickness, nominal 6mm thread engagement).
5. Attach the rear cover with four M3×14 screws (9.5mm cover/spacer stack, nominal 4.5mm engagement).
6. Attach the top using two M3×8 screws (4mm cover, nominal 4mm engagement). Check screws do not bottom out; tighten gently.

For paper changes: disconnect cables, remove rear cover and both bars, slide the whole printer rearward, then open its native lid outside the enclosure. The top may remain fitted according to the rectangular-body removal check. Reinstall in reverse. Spine attachment to the display module uses the inherited interface and is separate from these ten screws.

## Prepared plates

| File | Parts | Physical AMS slot | Nominal layers at 0.2mm |
|---|---|---|---|
| 01_shell_with_logo.3mf | Integral-front shell and registered flush logo | A2 shell, A1 logo | 805; both colours only in first 4 |
| 02_cradle_and_bars.3mf | Tray and two retaining bars | A2 | about 213 |
| 03_top_cover.3mf | Top cover | A2 | 20 |
| 04_rear_cover.3mf | Rear cover including integral spacers | A2 | about 48 |

Layer counts above are geometric estimates, not slicer results. A2 is light-grey Generic PLA, A1 dark Bambu PLA Matte. Only the shell plate requires colour changes. Shell prints front-face down, with the 0.8mm logo against the plate; all other parts are single colour. Never independently centre the shell and logo STLs: the registered files share the same transform and are assembled in the prepared 3MF.

Proposed settings: P1S 0.4mm, 0.2mm layers, four walls, five top/bottom layers, 15% gyroid, 5mm outer brim. Supports currently disabled for inspection, not yet validated. Slicer must confirm bed/exclusion-area and prime-tower clearances, bridging/overhangs, correct filament allocation and time/material totals before sending.

## Verification and remaining work

`checks.json`: six individual structural solids plus six-region logo; all meshes watertight, no significant pairwise/body-envelope collisions, rear-removal sweep clear with top fitted. This validates nominal CAD geometry, not physical hardware fit or print success.

`whole_enclosure_study.png` / `.step` combines the new bay with the existing display module for proportions. The new bay is 20mm taller than the old 181mm design height. The right plinth/feet and final cosmetic integration are unfinished; this is a printer-bay prototype, not the full case release. Display/Pi/cooler and power/cable fit remain unverified.

Bambu Studio 02.05.00.66 command-line slicing crashed before output on both this project and the previously printed fit-test project. Explicit settings loading also failed profile compatibility. Native UI returned no accessible window. No valid sliced G-code, print-time estimate or waste total was produced, and no print was sent. Resume via Bambu UI when the Mac/window is accessible. Prepared archives still require successful Bambu import and preview validation.
