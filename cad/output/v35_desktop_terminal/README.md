# V35 — 25-degree desktop terminal

After comparing the idea of 20 and 25 degrees, the user liked the desktop-terminal
direction. V35 models 25 degrees back from vertical for the display AND its
surrounding front plane, bezel and mounting structure. It retains the V34
connected planar roofs, 12 mm exposed front rounding, 201 mm height and common
lower band. V34 remains available as the 14-degree alternative.

The complete printer side is copied unchanged from V34. The display centre
moves 15.63 mm rearward and 2.44 mm downward as the face is recentered at the
new angle. The front lid screws and supporting lands move to y83.97 mm; the
rear screws stay put. The display roof roll ends at y85.98 mm; beyond that the
two roof planes meet flat with no rounded valley at the module seam.

The deeper screen assembly caught 2.46 cubic mm at the front corner of the
inherited PSU divider. A small clearance notch was added to the retainer;
the divider was left intact. No hardware is moved to obtain the clearance.

## Joint and assembly change

All five existing M3 inter-bay axes retain fully supported lands and clear
bores. Use the existing REAR alignment dowel at y140,z70. **Omit the old front
dowel at y35,z118:** that position is ahead of the 25-degree left wall, so it
no longer provides alignment. The corresponding printer-side bore is left
unchanged. No added visible rib or peg protrudes beside the sloped face.

## Checks and limits

The four changed parts are valid single solids and watertight meshes. Complete
assembly, display reference and measured printer envelope have no clashes.
Rear printer extraction, five vents, lid passages and joining screw bores are
clear. A solid strip spans the common roof plane at the joint.

Against inherited, UNVERIFIED electronics envelopes, retainer clearances are
18.73 mm to the Pi reference, 11.28 mm to the PSU, 1.29 mm to the buck reference,
and 70.31 mm to the IEC reference. The buck gap is tight; actual hardware,
cooler and wiring must be checked before releasing the left bay to print.
These are CAD clearances, not physical fit or thermal validation.

This is an unsliced form review. No print dispatched. V31 cradle/bar print
approval, clear bed and current PLA slot remain pending. Its geometry is
unchanged and it remains compatible with the printer bay.

## Files and Fusion

Saved and visually verified in Fusion project `lumon` as
`LUMON_v35_DESKTOP_TERMINAL_25DEG` on 22 September 2026.

- `whole_enclosure_review.step`: complete coloured assembly.
- `display_reference.step`: unverified display reference; not a print part.
- `sloped_front.png`, `sloped_roof.png`, `sloped_rear.png`: actual CAD previews.
- `*_assembly.stl`: assembly-coordinate meshes, not print-oriented releases.
- `audit.json`: geometry/clearance evidence.

Rebuild with `.venv/bin/python cad/review/build_v35_desktop_terminal.py`.
