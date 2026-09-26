## Physical result — 24 September 2026

Both corner samples passed seating without bending and gentle tightening of
the actual 4 mm screws. User measured to identify the mixed samples and selects
0.12 mm support gap as better. See physical_test.json. Historical CAD and slice
audit below precede this result; full enclosure still needs final preparation.

# V49 — measured display mounting depth

The actual glass-front-to-metal mounting plane is 8.4 mm, not the inherited
5.96 mm. The four pads now start 2.44 mm farther behind the glass. The glass
itself stays in its 1 mm recess, on the existing 3 mm-wide bearing seat.

The user's screws measure 4 mm underneath their heads. Reducing the plastic
grip from 3.9 to 2.0 mm leaves 2.0 mm nominal thread engagement. The 6.5 mm
head recess diameter stays unchanged: the user confirms the heads fit.
Use these measured screws, not the previously assumed M3x6 screws.

All four hole axes and the original arm roots/beams are unchanged. The
193.6 x111.4 mm/R8.2 glass pocket and 3 mm bearing width are unchanged.
The production left bay, assembly STEP, and full fixture are updated together.
Fusion has not been synchronized; its last saved version remains V39.

## Small test plate

The prepared plate contains two identical upper-right glass corners, each
with one complete integral mounting arm. Both print front-face down again.
The LEFT sample uses a 0.20 mm top support gap; the RIGHT uses 0.12 mm.
All other settings match. Keep track of the samples while removing them.
This compares support release/finish while testing the measured depth and
screw reach, without printing another whole frame.

1. Remove supports and loose strands, without shaving away bearing material.
2. Fit one sample to the upper-right glass corner, looking at the display from
   the front in its correctly aligned landscape orientation. The glass rests
   on the short 3 mm ledge; the arm sits behind the matching metal lug.
3. With no screw, the glass and metal should both meet their supports without
   pushing the arm backwards. Report a gap or bending instead of forcing it.
4. Try one measured 4 mm screw gently. Its head should reach the recess floor
   while the mounting face remains relaxed. Stop if it resists before seating.
5. Compare the two support-contact surfaces and how cleanly support released.

## Verification and limits

CAD checks verify valid single solids, watertight meshes, full 3 mm seat width,
glass inward stop/outward clearance, clear screw/head passages, 2 mm plastic
grip, and unchanged geometry outside four pad masks. Nominal front insertion
also passes with the conservative metal envelope extended to the measured
mounting plane. Chassis XY and Pi references remain provisional.

The manufacturer's drawing does not explicitly establish the previously
claimed universal 2.5 mm thread-depth limit. Its handling guide requires screws
to avoid pressing into the backlight. The actual 2 mm engagement and simultaneous
glass/lug bearing remain physical checks, not CAD-established facts.

The inherited full-case cable/divider clash and power/access review are still
outstanding. This is a small test release, not a full display-case release.
Bambu slice reviewed and saved: **50m14s, 14.30 g total**, white A2 only, no
colour swaps. Both support-gap overrides survive the saved project and produce
different interface heights in the toolpath. User confirmed plate clear; Send
clicked with A2 white, bed leveling/timelapseOFF. P1S accepted the matching
V49 job and reports0/152,startup/heating,ETA18:14 local. First layer and
completion are not yet verified. See print_dispatch.json.
