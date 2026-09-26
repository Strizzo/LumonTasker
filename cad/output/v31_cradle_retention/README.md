# V31 — printer cradle and retention fit test

The v28 shell finished on 22 September. User substituted yellow when the light-grey filament ran out; treat the shell as a mechanical prototype, not a final appearance print. The photo does not establish dimensional accuracy, adhesion at the colour transition, or the inside/support condition. User confirms they do everything through the assistant and have done no unreported steps. User has ONLY the earlier v26 test cradle; do not assume inserts, bars, cradle installation, or other assembly has happened. New white/navy filament expected this afternoon.

## Next print

`02_cradle_and_bars_reviewed.3mf` is the native Bambu project; `02_cradle_and_bars_reviewed.gcode.3mf` is its exported sliced plate. It contains the approved refined cradle, revised lower retaining bar, and unchanged upper bar. All three use one PLA colour, with no repeated colour changes or prime tower.

Native Bambu Studio slice verified 22 September: **3h 6m 28s total (2h 59m 15s model), 108.54 g, 212 layers at 0.20 mm**, P1S / 0.4 mm / textured PEI. Four walls, five top and bottom layers, 15% gyroid, 3 mm outer brim, supports off. Saved native settings and exported G-code were checked. Slicer reports no object outside the plate. Its standard PLA bed-temperature warning is recorded in `slice_review.json` (55 C bed versus profile's 45 C vitrification field); nozzle 220 C. Current physical PLA must still be identified before launch.

**Dispatched.** User clicked Send after CUA controls failed. Verified matching V31 job in Bambu Studio, heating bed, 0/212 layers, estimated finish 15:32. AMS A2 yellow Generic PLA, bed leveling and timelapse off. Completion and physical fit remain unconfirmed. Earlier app-control timeout was recovered without asking the user to operate Bambu. The generic generator project remains `02_cradle_and_bars.3mf`; its override metadata is fixed so intended settings survive import. Use the reviewed project for this release.

The cradle's support rise is 8.1 mm, 2.7 mm taller at the front than the v26 test cradle. Its total lateral gap is 0.6 mm narrower. The old cradle is useful for gross shell clearance but NOT for final outlet/LED alignment; do not alter the shell to compensate for its lower support pose.

## Mechanical retention

The lower bar now has two downward legs at local x20–30 and x140–150, with forward lips overlapping the tray's rear edge by 4 mm. Both rear and vertical clearance are 0.5 mm. The bar uses the same two M3x12 screws and shell inserts as before. The upper bar uses two more M3x12 screws. No holes, glue or snap-fit are added to the printed shell or cradle. This retains the tray without preloading the tapered printer case. Remove the lower bar before withdrawing the cradle.

CAD checks pass: one valid/watertight bar, no installed-part collisions, existing screw bores retained, no new intrusion into the rocker/cable channels, rear installation path checked. Translated-tray checks show freedom within 0.45 mm and capture at 0.75 mm. These checks do not replace physical trial assembly or validate unknown real cable bends.

## Physical sequence

1. Remove loose brim/supports from the shell. Check that the narrow LED opening, paper opening, rear mounting rails and underside relief channels are clear. Identify supports before cutting; the photo alone cannot establish whether the pale material in the LED opening is support or an inserted part. Check flatness and the colour-transition bond by gentle handling.
2. Slide in the revised cradle from the rear, narrower guide spacing and taller support ends toward the paper outlet. It should sit flat on the floor. Align the open switch/cable channels. Do not force it or glue it.
3. With power disconnected, insert the intact printer in the already-tested upper-output orientation. Check that its body sits on the sloped lands, the rocker never touches the floor/table during insertion or when seated, and native buttons/lid are not loaded.
4. Check the paper outlet is centred in the 90 x 14 mm front opening and the LED aligns with its upper opening. Record any offset with the revised cradle fully seated. Do not reduce the paper slot or choose a cosmetic surround until feed/cut clearance is established.
5. Install four M3 inserts in the rear rails for the two bars (z58 and z137 screw positions). Fit the revised lower and original upper bar using four M3x12 screws. Verify actual screw/insert engagement and bottoming; tighten gently without pulling the printer casing into a wedge. The lower lips should clear the tray top rather than bend it down. Check movement by gentle handling with both hands, not shaking the enclosure.
6. Connect power/USB with the rear still open and check real plug bends. Feed/print a short receipt and then a longer one; confirm that paper exits freely and cutting/tearing is accessible without dragging on the shell. Check that the status LED can be seen. The final translucent PETG diffuser remains a separately printed and fitted part.
7. Remove the bars and withdraw the printer; open its own lid and change/reseat the roll outside the shell. Verify the intended service route. A full rear cover test follows using `rear_cover.stl`, four further rear-rail inserts and four M3x14 screws. Rear-cover closure and ventilation/temperature testing remain pending.

Until the dark base is fitted, the photo's shell rests on its own bottom face rather than the eventual z0 ground plane. Confirm that neither the rocker nor cables reach the table through the underside openings; do not assume the missing base provides clearance.

## Appearance direction — pending design and hardware fit

User finds the printed printer bay too like a donation box and explicitly allows redesign before the final print. Do not freeze the current square shell as final solely because it has been printed. Review the COMPLETE device, not this isolated bay: the current matching dark plinth is modelled, but a rounded dark crown is still missing. Develop coordinated upper-edge rounding, a modest navy paper-outlet surround (clear of paper/cutter) and consistent base/bezel proportions. Avoid decorative elements or labels without a purpose.

For the final shell, a rounded shoulder can be designed into the structural geometry rather than relying on a tall cap to hide the prototype's square edge. Preserve the closed rigid front/top, rear paper service and all validated hardware datums. Review actual CAD in Fusion before any final-colour shell print. Display/Pi/cooler/power dimensions remain unconfirmed.

Regenerate geometry: `.venv/bin/python cad/review/build_v31_cradle_retention.py`.
Prepare plate: `.venv/bin/python cad/review/pack_cradle_v31.py`.
Fusion review export: `whole_enclosure_review.step`. Imported and saved in project `lumon` as `LUMON_v31_CRADLE_RETENTION_REVIEW`; complete assembly visually checked. Fusion reported the 10-editable-document limit after saving; the named document remains present with no unsaved marker. Existing review documents were left intact.
