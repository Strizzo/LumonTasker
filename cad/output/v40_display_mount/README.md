# V40 — close-fitting display mount test

This is a mechanical test for the user's 193 × 111 mm glass and 40 mm total attached-Pi depth. It is not the final display enclosure.

## Parts and assembly

The large thin ring reproduces the proposed close-fitting opening and four case mounting points. The four small brackets support the display's rear metal lugs. No glue or force fit is used. The complete measured assembly is supported from metal, not from pressure on the glass corners.

1. With the display safely aside, install four tested M3 heat-set inserts into the frame's 4.2 mm bores. Let the plastic and inserts cool completely.
2. Dry-fit the glass in the opening without screws. Target a narrow, even gap around all four edges and rounded corners. It should enter freely; do not force or flex it. Report any corner or straight edge that touches.
3. Support the display face on a clean soft surface and position the frame around it. The intended glass face is 1 mm behind the front of the surrounding ring, not hard against a lip.
4. Fit the two longer brackets (38.97 mm overall) to the lower mounting points and the two shorter ones (37.38 mm) to the upper points, relative to the drawing orientation. Left/right copies are identical. The deep recessed hole goes to the display's metal lug; the plain hole goes to the frame boss. All holes should line up without pulling the glass sideways.
5. Intended hardware: four M3×6 screws into the metal lugs and four M3×8 into the frame inserts. The lug pad is3.9 mm thick, leaving nominal2.1 mm thread engagement against a manufacturer2.5 mm maximum. Check actual screw protrusion/length before fitting; do not use a longer screw in the display lugs. Tighten only gently after confirming both bracket ends seat naturally.
6. Check that the Pi, ribbon and loose wire plugs are clear of the brackets. This test does not determine the loose wires' electrical pin mapping.

If the glass fit or lug pattern differs, report where; modify this inexpensive test before releasing the large display shell. R8 glass corners are inferred from the drawing, not physically confirmed.

## Files and verification

- `01_V40_display_fit_kit.3mf`: one-colour A2 PolyTerra cotton-white project.
- `display_fit_kit_assembled.step`: test components in assembly coordinates.
- `fit_audit.json`: passed solids, meshes, print orientation and collision checks for the test kit.
- `audit.json`: larger candidate audit, still blocked by a provisional rear cable/divider clash. Large case not released.

The unprinted display foot has underside pockets retaining a2.4 mm upper skin, rim, ribs and screw columns. CAD solid volume is44.3% lower; sliced mass and physical stiffness are not yet checked. No accepted printer-side geometry changed.

Fusion was intentionally left closed after the user's performance interruption. The latest saved Fusion assembly remains V39. No V40 Fusion synchronization should be claimed.

## Print status — 23 September, 21:39 local

Dispatched and verified heating on P1S 3DP-01P-994: 60 layers,26.74 g, estimated1h11m26s (finish around22:50). All five parts use cotton-white PLA in AMS A2. No supports or colour swaps; bed leveling and timelapse off. Physical completion and fit remain unverified. See slice_review.json and print_dispatch.json.
