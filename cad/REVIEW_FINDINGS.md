# v19 enclosure review

## Scope and status

This revision keeps the overall 376.96 × 161 × 181 mm envelope and repairs
mechanical details independent of the hardware measurements. It is a review
candidate, not a production or slicer-approved print release. The generated
reference image provides styling only. Actual hardware takes precedence.

The original archive is preserved. v19 is generated from `lumon_v19.py` and
exported by `export_review.py`; the imported Fusion document is a review copy.

## Findings and changes

| Finding in v18 | v19 change |
| --- | --- |
| Uneven transition beside the lower-left screen corner: rake cut through a previously rounded upright edge | Construct the sloping shell first, then round its actual front edge. Retain the deliberate base-band step. |
| Rear service rebate reached into the rounded rear-left corner; inset base reduced cavity-wall thickness | Move/narrow the left service panel and preserve 3mm walls around the inset base cavity. |
| Display bezel and pocket had identical perimeter size | Add 0.3mm clearance per side to the separate bezel. Adhesive attachment remains to be specified. |
| Forward alignment dowel at Y=15, Z=118 lay in front of the raked left wall | Move it to Y=35 and relocate the nearby upper screw to Y=50. Check hole and surrounding material on both mating walls. |
| Seam counterbore left only 0.8mm of the 3mm wall under the head | Use a full-thickness clearance hole with the screw head accessible inside the left bay. |
| Magnet pockets lacked reliable open seats/lands; some generated enclosed void shells | Replace the speculative magnetic retention with six screw locations: four left, two at the rear of the printer trim. Add connected insert lands and compression sleeves under the covers. |
| Foot inserts were deeper than the tub floor; some locations conflicted with internal packaging | Add raised insert bosses and relocate the eight mounting points into clear regions. |
| 2.2mm rear-panel counterbores cut through the 1.8mm outer skin | Keep the skin and use external screw heads. |
| Solid dark base plate blocked the floor intake slots | Add matching through slots and channels opening at the back of the base. |
| Chamfer along both sides of the base seam produced a V notch | Chamfer the outside perimeter while leaving the mating seam square. |
| Cover imposed an unmeasured paper slot and hid the real printer's top | Replace it with a separate dark, open trim. Its aperture remains provisional; real lid swing, controls and cable access still need checking. |
| Old STEP omitted the blue logo fill and had no useful color separation | Export named, colored bodies, including all six logo regions. Keep hardware references in a separate STEP. |

## Verification and limits

- Independent baseline audit: archived STEP solids were geometrically valid;
  that did not establish good fasteners, assembly access or print orientation.
- v19 checks each main part for one solid, CAD validity and watertight STL.
- All-pairs volume intersections include the case parts, logo, and inherited
  display/printer/Pi/PSU/inlet/buck boxes. See `output/v19/geometry_review.json`.
- Local material probes check insert bores, blind-hole floors, screw passages,
  compression sleeves, rear-panel head bearing and seam fastener surrounds.
- A radial sample of the rear-left corner at seven heights and seven angles,
  sampled every 0.05mm, measured about 1.25mm minimum in v18 and about 3mm in
  v19. This is a targeted check, not a complete minimum-thickness certification.
  See `output/v19/rear_corner_wall_check.json`.
- Three small coupons are extracted from actual geometry: left/right rear seam
  and the screen corner. Each is a valid single solid. They still need slicing
  with the actual printer profile.
- No lid-swing simulation, cable routing validation, physical fit test, thermal
  test or slicer toolpath review has been completed. Hardware boxes are not
  accurate representations of connectors, levers, feet or moving lids.

## Assembly and fastener plan

Keep ribs, lands and floor united with their corresponding shell. Keep covers,
rear panels, feet, screen retainer and dark bezel separate for access and color.
Use the two-module spine joint rather than adding another large visible seam
before knowing the print bed size.

Current geometry has 31 M3 insert locations: spine 5, retainer 4, rear panels 8,
base plates 8, covers 6. Pi pilot holes are separate and are not included in that
count. Two 4mm alignment dowels are provided. These counts are design inventory,
not a finalized shopping list: insert body size, screw engagement and head
geometry need confirmation with the chosen hardware and fit coupons.

Suggested order: test coupons; install accessible inserts in empty shells;
mount display/retainer and required wiring; join the spine while screw access
is clear; fit electronics and printer; attach separate base plates, rear panels,
bezel and covers. Recheck this order with the actual connectors and tools.
The rear lower spine screw is close to the power-supply region: join the modules
before fitting that supply. A removable electronics tray is a sensible later
revision if the confirmed hardware makes service access awkward.

## Remaining design decisions before full-shell printing

1. Confirm actual printer, display assembly, Pi/cooler, power architecture and
   connector dimensions. The printer trim may require a front relief for its
   lid release or controls; do not infer that relief from the generated image.
2. Confirm printer bed, nozzle, filament and multicolor capability.
3. Inspect support paths and removal in a slicer. The upright left shell has a
   roughly 181mm-wide screen opening; “vertical opening” does not make its roof
   self-supporting. If supports prove excessive, separate the front carrier
   with designed screw lands rather than simply cutting the shell in two.
4. Test inserts, dowel fit and bezel rebate. A successful mesh check cannot
   establish real extrusion tolerances.
5. Choose logo method: registered multicolor region, paint, or decal. The small
   disconnected blue islands are not recommended as loose hand-assembled prints.

Print orientations and the part/color table are in `README.md`.
