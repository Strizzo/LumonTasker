# V46 — one-piece display seat and retention test

**Dispatched 24 September around10:39 local.** The user explicitly confirmed the
plate is now clear. P1S3DP-01P-994 shows matching job
`V46_Display_3mm_Seat_Integral_Mount_Test` active/heating at0/114 layers,
waiting for the bed to reach55 C, nozzle target220 C. Estimated finish12:41.
First-layer quality, completion and physical fit are not yet verified.

**2h02m04s, 47.29 g, white PLA from AMS A2 only.** GUI reports39.11 g model and
8.17 g supports (rounding differs by0.01 g). One initial filament load, no
inter-colour swaps or prime tower. Preview has114 layer heights including
independent support heights; nominal object layer height0.2 mm, maxZ15.8 mm.
Three walls, four top/bottom layers,10% gyroid. Normal supports use the same
white PLA, with0.2 mm contact gap. A2 white PLA mapping, bed leveling OFF and
timelapse OFF were verified in the Send dialog. See `print_dispatch.json`.

The test is cropped from the actual V45 body and retains the whole3 mm seat,
2.3 mm seat thickness,1 mm glass recess and all four integral mounting arms.
It is **one part**, with four screws into the display's metal lugs and no loose
brackets or case-side heat-set inserts. The print lies front-face-down; supports
under the ledge and arms must be removed before fitting the display.

The crop preserves the actual mounting regions and the full seat material.
CAD checks passed for one valid solid, watertight mesh, nominal glass/chassis/Pi
front passage, the conservative black-band envelope, and clear screw bores/head
recesses. This tests the newly chosen mounting stack, which the earlier V40
glass-outline frame did not validate. It does not validate final cable/power
routing or screwdriver access in the closed large enclosure.

## After this test prints

1. Remove supports and check the ledge, four mount pads and screw holes for
   residue or raised spots. Do not seat the glass on support remnants.
2. With the display/Pi unplugged and screws absent, insert it from the front.
   The glass should rest evenly on the ledge without rocking or being forced.
3. Check the four outer metal lugs meet the printed pads and their holes align.
   If a pad holds the glass away from the seat or a lug leaves a gap, report it;
   do not pull the display into place with screws.
4. If both seat and pads meet, gently secure four M3×6 screws from the rear.
   Nominal thread engagement is2.1 mm; confirm length before tightening.
   The screws should prevent withdrawal through the front.

The nominal chassis-to-seat clearance is only0.35 mm at the lower border, so
the real check matters. The band was confirmed by the user to clear the outer
3 mm. Keep electrical reconnection separate until the unplugged wires' mapping
has been verified; no assumption from wire colours is made.

The completed navy printer base can meanwhile be dry-fitted beneath the accepted
printer shell: check flat seating, matching outline and clear switch/cable
channels. Keep it unglued until rear-cover and full assembly fit are checked.

Files: `01_V46_display_seat_fit.3mf`, `01_V46_display_seat_fit.gcode.3mf`,
`display_seat_fit_local.step`, `display_seat_fit_print.stl`, `audit.json`,
`slice_review.json`, `plate_manifest.json`, `integral_fit_frame.png`.
