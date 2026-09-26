# Lumon enclosure: engineering review

**Current build:** the assembled prototype was accepted on 26 September 2026.
See [CURRENT_PRINT_FILES.md](CURRENT_PRINT_FILES.md) for the parts used and
[BUILD_STATUS.md](BUILD_STATUS.md) for the physical build record. The sections
below describe the original V19 review and are historical where later revisions
supersede them. Do not treat modelled parts as printed or assembled.

The real printer, screen assembly, Pi/cooler and cable paths determine the
mechanical design. The generated reference picture is a style reference only.
Neither the old picture nor the inherited component boxes establish fit.

## Working files

- `lumon_v19.py`: portable parametric working copy of the archived v18 generator.
- `export_review.py`: colored STEP, assembly-position STLs, individually oriented
  STLs, small fit coupons, previews and independent geometry checks.
- `review/logo_v18.step`: exact logo recovered from the supplied v18 STEP recess;
  six disconnected artwork regions, deliberately preserved.
- `review/audit_v18.py`: baseline STEP/mesh audit.
- `review/prepare_v19.py`: one-time migration recipe, not the normal build command.
- `output/v19/`: generated review artifacts. **Not a print release.**

Run from the project root:

```sh
.venv/bin/python cad/export_review.py
```

Python dependencies are recorded in `requirements.txt`. Original files in
`files/` remain unchanged. Fusion imports are review copies; edits made there
must be intentionally carried back to the generator before another rebuild.

## Color and assembly intent

| Group | Color | Print/assembly decision |
| --- | --- | --- |
| Left shell | Pale grey | Floor, walls, display ribs, insert lands, partition and Pi mounts form one structural print. Supports required at some internal features and the screen-opening roof. |
| Right shell | Pale grey | Floor, walls, spine and printer support rails form one print. Rails remain provisional until the printer is measured. |
| Left top cover | Pale grey | Separate for access to display fasteners, seam screws and electronics. Four screws. |
| Printer trim | Dark charcoal | Separate, open aperture around the provisional printer envelope. Two rear screws and locating skirt. The real printer supplies its lid, paper exit and controls. |
| Screen bezel | Dark charcoal | Separate flat print; perimeter fit clearance added. A thin adhesive attachment is still to be specified; no snap attachment is claimed. |
| Base plates, left/right | Dark charcoal | Separate prints, four screws each. Preserve independent color and screw access. Left plate has through vents and underside channels. |
| Display retainer | Pale grey/internal | Separate flat print; installs after the screen and clamps it at four points. |
| Rear service panels | Pale grey | Separate flat prints, four screws each with external pan heads. |
| Logo | Blue | Optional multi-material region registered to the right shell. Six loose regions are not a sensible first manual assembly. Paint/decal is the simpler single-extruder alternative. |
| Hardware reference bodies | Visualization only | Never print these as enclosure parts. Their shapes are unverified bounding boxes. |

Do not merge lids, retainer or service panels into the shells: doing so traps
hardware or prevents servicing. Keep the two main modules independently
printable and join them at the existing spine. There is no need to introduce
more large external seams until the actual build plate is known.

## Print orientation and remaining checks

`assembly_stl/` retains registration for fit and multi-material inspection.
`oriented_stl/` places each individual part on Z=0; these coordinates no longer
assemble together. Do not mix the two sets in a multi-material object.

- Shells: floor down, open top up. Inspect supports below the screen opening,
  rear-opening roofs and sideways bosses. The old blanket “no supports” claim
  is withdrawn. Supports must be removable before fitting electronics.
- Bezel and retainer: un-tilted and laid flat, rather than printed at their
  14-degree assembly rake.
- Rear panels: exterior face down; locating step faces up.
- Covers/trim: exterior top down to avoid supporting a whole internal ceiling;
  inspect the rounded perimeter for support and bed-contact requirements.
- Base plates: bottom down. Check channels, counterbores and first-layer grip.

The first fit-test plate is configured in `output/p1s_fit_plate/LUMON_v19_fit_test.3mf`
for a Bambu P1S, 0.4mm standard nozzle and textured PEI plate: 0.20mm layers,
3 walls, 20% infill, 3mm outer brim, and automatic build-plate support for the
screen corner. Studio estimates 1h24m and 27.07g including purging.
Physical AMS A1 supplies dark Bambu PLA Matte; A2 supplies light-grey Generic
PLA, as explicitly confirmed by the user. A2 was registered as Generic PLA
in the device settings. The full enclosure has not yet been sliced or released.

General support/split/tolerance rationale follows Prusa's manufacturer guide:
https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135
A mesh that is watertight can still have unprintable bridges or unusable holes.

## Hardware information needed for a fit release

- Printer exact model; body width/depth/height; rubber feet; lid hinge/swing;
  paper path/cutter; buttons and release lever; cable exits and plug clearances.
- Display exact model and complete assembly dimensions, including driver board,
  mounting frame, connectors and cable bend space. Confirm active image area
  before accepting the 6mm edge overlap inherited from v18.
- Raspberry Pi model, cooler and connector/cable directions.
- Actual power supply and voltage architecture. The inherited internal supply,
  inlet and barrier are packaging placeholders, not an electrical design approval.
- Printing setup confirmed: P1S with AMS, standard 0.4mm nozzle and two PLA colors.

The first physical step should be small fit coupons, followed by a printer-bay
fit test after measurement. A full pair of shells should wait for these checks.
