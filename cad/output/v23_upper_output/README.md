# V23 rear-loading printer bay — prototype, not print-released

**USER HOLD: preparation only; do not print until renewed user authorization.**

Source: `cad/printer_bay_v23.py`. Bambu project packer: `cad/review/pack_printer_projects_v23.py`.

## Design

The intact printer slides in from the rear onto a removable tray. Two rear bars retain it; a separate rear cover conceals them. The front is part of the main shell and has no removable panel or front screws. Side guides have 1mm nominal clearance to the measured 131mm body width, so its corner radius is not needed. The native keyholes (61mm centres, 132mm from large-hole centres to original rear/cable edge) are recorded but unused.

Rotated printer envelope: 131 W × 120 D × 175 H mm. Controls face forward near the top, original rear/cable edge is below. Front clearance is 1mm, rear retaining-pad clearance 0.5mm. Optional removable shims can take up play after trial fitting. Never force the body into place.

Logo centre is now at Z57mm, beneath the outlet. The front aperture is 127 W × 88 H mm, exposing a generous upper region (Z101–189mm) for the native cutter and buttons. Their exact locations and paper trajectory are not measured; this aperture requires physical verification. The grey block in renders represents the printer envelope, not a second panel to print. Native printer casing, lid and mechanism stay intact.

## Assembly and paper changes

1. Fit M3 heat-set inserts in the tested 4.2mm bores, flush and square. Keep bores clear.
2. Place the tray on the shell floor and slide the printer in from the rear.
3. Confirm the front opening clears the cutter, paper and buttons, and pads contact solid casing. Route cables through the lower rear opening without pinching or tight bends.
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

Bambu Studio 02.05.00.66 command-line slicing crashed before output on the prior v22 project and the previously printed fit-test project. Explicit settings loading also failed profile compatibility. Native UI returned no accessible window. No valid sliced G-code, print-time estimate or waste total was produced, and no print was sent. V23 has not been sliced. Resume preparation via Bambu UI when accessible; do not send a print without renewed authorization. Prepared archives still require successful Bambu import and preview validation.

## Orientation revision, 21 September 2026

Supersedes v22 lower-output layout. This is a 180-degree turn about the front/back axis relative to that orientation, preserving the body envelope and rear insertion. The front opening is reflected about the measured printer mid-height; the logo moves below. Floor and tray have an open-ended 78mm-wide relief from Y95mm rearwards for the lower connector region. Rear cable notch reaches Z47mm; lower bar begins at Z51mm. Actual plugs, bend radius, underside projections and pad contacts are unmeasured: these reliefs are provisional, not verified hardware clearances. User confirmed the upper-output orientation was the one already tested. No repeat orientation test required.

21 September measurement correction: upper-output operation is already tested. Outlet 90mm wide × 14mm high, horizontally centred; 56mm from upper edge, with upper-edge/centre datum clarification pending. Plug measurements supplied: power 15mm, square USB 12mm. Small fit samples prepared in `cad/output/v24_printer_fit`; broad v23 front aperture remains provisional and has NOT yet been replaced by an unvalidated narrow slit. No print dispatch.

## Hardware correction: tapered casing, downward rocker and LED

User photos, 21 September 2026, show original front/rear walls are not parallel. In the chosen orientation these become upper/lower faces. The prior 131 × 120 × 175mm reference remains only a maximum envelope; it cannot validate support contact, printer tilt or actual outlet alignment when installed. The width coupon passed, not the full cradle. Do not print the full v23 tray/shell as a validated mount.

Original rear power rocker becomes downward-facing. Provide a clearance pocket or through-opening in BOTH tray and any shell floor beneath it, including both switch positions, assembly tolerances and insertion/removal path. The table or eventual foot/base structure must not reach the rocker through that opening. Switch width/height, position and protrusion are pending; no precise hole is guessed from photographs. Define structural support pads on verified casing lands clear of switch and connectors; shim/pad heights may differ to keep the paper-output face aligned. Retainers must secure without wedging tapered casing or loading buttons/lid.

User does not require external feed/lid-release button access; those become available after removing the intact printer for paper service. Conceal with internal noncontact clearance, not a wall resting on controls. LED should remain visible. Preferred proposal: a small separate translucent/off-white insert, supported by a concealed shoulder in the shell, with a light-collection cavity accommodating the sloped native face. Do not claim a fixed matte-PLA wall thickness will transmit enough light; test an optical sample with the actual filament. No direct loading of the native LED lens. Exact LED position and angle pending.

Required measurements: rocker outline, protrusion in both positions and distances to two adjacent edges; original front-to-rear length at lid and bottom (taper); LED outline and centre relative to upper edge in chosen orientation. Photographs establish features but not precise dimensions. The fitted outlet centre remains 60mm from printer top, but its absolute CAD height depends on corrected support placement. No printing authorized for this redesign.
