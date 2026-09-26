# First enclosure prototype — exploration, 20 September 2026

> Follow-up: the working v19 engineering review and revised geometry are in
> `cad/REVIEW_FINDINGS.md` and `cad/output/v19/`. The notes below describe the
> original archive before that review, not the current working candidate.

## Starting point

This workspace is an archive of parametric CAD, STEP assemblies, STL exports,
renders, and reference photographs. No application/firmware project or Git
repository was found at the workspace root. CAD generators use build123d/OCCT.

Use `files/mnt/user-data/outputs/lumon_terminal_v18/` as a **candidate baseline
for review**, alongside `files/lumon_v18.py` and `files/LUMON_TERMINAL_v18.step`.
It includes the raked display module, printer cover with paper slot, separate
feet, rear panels, and display bezel. Its report gives an assembled envelope
of 376.96 × 161 × 181 mm. This is not a print-approved release.

Do not combine the loose STLs in `files/` into an assembly: they include older
geometry. For example, the loose left tub is 227.46 × 160 × 151.97 mm while
the archived v18 left tub is 218.96 × 161 × 156 mm. The loose top plate is
3 mm tall; the v18 cover is 21 mm tall. Selected loose STL/report hashes do
not match their archived counterparts. Names such as v51/v52/v53 should not
alone establish chronological order; source headers and timestamps are unreliable.

## Measured STL bounds for the v18 candidate

Dimensions below were read directly from binary STL vertices, in the model's
millimetre convention. These are assembly-axis bounds, not chosen print orientations.

| Part | X × Y × Z (mm) |
| --- | --- |
| tub_left | 218.96 × 161.00 × 156.00 |
| tub_right | 158.00 × 161.00 × 156.00 |
| top_plate_left | 218.96 × 128.09 × 21.00 |
| printer_lid | 158.00 × 161.00 × 21.00 |
| display_retainer | 194.36 × 36.85 × 133.18 |
| display_bezel | 212.96 × 34.06 × 125.66 |
| rear_panel_left | 140.00 × 3.00 × 114.00 |
| rear_panel_right | 110.00 × 3.00 × 90.00 |
| foot_left | 216.46 × 156.00 × 9.00 |
| foot_right | 155.50 × 156.00 × 9.00 |

`ref_*.stl` represents purchased hardware, not enclosure parts to print.
STLs retain assembly offsets: e.g. tub bottoms are at Z=9 and the printer
cover starts at Z=160. Each part needs deliberate orientation and placement
on the slicer's bed. Bounding-box fit alone does not account for brims or supports.

## Issues to resolve before full-size case prints

1. The archived v18 validation report flags a **1.7 mm rear-left wall FAIL**.
   Reproduce and inspect this before releasing the left tub.
2. Printer dimensions remain explicitly UNVERIFIED: 142 × 122 × 122 mm.
   Confirm the actual unit, connectors, lid opening sweep, controls, and paper
   exit. `paper_slot_y=45` is still TBD. Display thickness is also TBD at 21 mm.
3. The report contains stale statements: it describes both modules as raked
   and also describes the printer block as upright; it calls the printer well
   open although a cover is exported. Its 21-insert schedule omits separate
   foot fastening and the source now includes lid magnets. Recalculate hardware
   from the chosen geometry rather than shopping from the old report.
4. Existing zero-interference results cover selected pairs only. They do not
   establish cover clearance, paper travel, lid servicing, or full assembly fit.
5. Regeneration needs environment repair: build123d is absent from the default
   Python; source uses `/home/claude/out_v18`, `/home/claude/logo_src.png`, and
   `/mnt/user-data/uploads`. The exact logo source is not present under that
   filename. Export code also retains a v2 STEP filename. Preserve the archive
   and make a portable working copy before regenerating.

## Next prototype sequence

1. Record printer model/build volume/nozzle/material and actual component measurements.
2. Confirm the v18 appearance as the desired baseline and repair/revalidate
   the working CAD, including the thin wall and complete mating-part checks.
3. Generate small fit fragments for the seam joint, display rebate, and printer
   support before committing to full tubs (also proposed in BUILD_PLAN_v2.md).
4. Slice and inspect those fragments using the actual printer profile.
5. After fit checks, print the right tub and trial-fit the receipt printer;
   then release the left tub, covers, bezel, retainers, and feet.

An appearance-only mockup can use provisional component dimensions, but should
be labelled accordingly. A functional fit prototype needs measured hardware.

## Verification performed

Read the existing build plans, v18 source and report, inspected the v18 render,
compared selected loose/archive hashes, and independently measured STL bounds.
No CAD regeneration, mesh-manifold validation, slicing, or physical fit test
has been performed. Original design files have not been modified.
