# Fusion design reconciliation — 21 September 2026

## Evidence and current state

Inspected the two open Fusion documents visually: LUMON_TERMINAL_v18 and LUMON_v19_colored_review (both unsaved review imports). Compared their source/export notes and the exported v19 STEP against the v28 printer bay currently printing. Neither open Fusion document is the current full device; do not use its printer cavity or old print parts as a release reference.

V19 explicitly assigns dark #10161E to printer_trim, display_bezel and both feet; the body and left cover are pale #DEE9EE and the logo blue #0B4F7E. This is deliberate styling, not merely Fusion component colouring. The dark printer part is an OPEN rim around the old top-exit printer, not a solid lid for the new orientation. build_lid specifies a12mm upper fillet and a hollow locating skirt. V28 has a closed, integrated pale top, a6mm front-right corner in plan, and no equivalent rounded upper transition. Earlier explanations that the separate right top was necessary for printability were wrong.

## What must be reconciled

| Area | Finding | Next action |
| --- | --- | --- |
| Printer crown | Dark rounded rim lost when old top-exit architecture was replaced. Old part is158mm wide; current bay175mm. | Design a NEW separately printed navy cosmetic cap for the existing flat top. Do not reuse old rim/cover. Keep rear removal and LED clear. |
| Upper rounding | Thin cap can soften its own edges but cannot recreate the original12mm fillet around a square shell without added height or overhang. | Show cap section/proportions before selecting radius; do not promise identical old silhouette. Prefer modest softening for this prototype. |
| Relative heights | Old full left module reaches181mm; right bay now reaches201mm before any cap. | Treat the20mm step deliberately in whole-device review. A cap increases it. Do not blindly raise display geometry or assume a flush common top. |
| Printer base | Old right foot is sized for158mm bay and has obsolete mounting points. V28 has no matching four foot-insert bosses and its shell starts atZ9. | Design matching dark right plinth and its retention for the printed shell; preserve rocker swept channel and cable opening. Align ground plane with left foot. Do not print old foot_right. |
| Base styling | Old light lower stepped band is absent from new right shell. | Decide with cap/plinth proportions whether to echo it cosmetically; a foot alone will not recreate the old inset light band. |
| Main joint | V28 retains five seam screw locations and two alignment-dowel locations from v19. | Join through left bay before electronics obstruct access; confirm fastener lengths and real tool access. Pairwise STEP audit checks cross-module collisions, not assembly access. |
| Printer support | V26 physically mostly fits; V27/V28 carry approved8.1mm bottom rise and0.6mm narrower total guide gap. | Print refined cradle as final assembly part, not another trial. It is separate from shell by design. |
| Printer retention/service | Whole printer rear-loads; two bars and rear cover are removed for paper service. | Print bars and rear cover. Verify real plug bends, switch clearance and extraction after installation. No top opening needed. |
| LED | Separate insert trial accepted; translucent PETG available. | Print PETG insert separately after profile/slot known; flange attachment without pressing native controls. Confirm visibility behind installed front. |
| Screen bezel/corner | V19 corrected prior lower-left corner geometry; bezel coupon passed previously. | Retain correction and separate dark bezel; specify adhesive only on locating lands, after actual screen fit. Do not restore v18 corner. |
| Display retention | Source assumes192.96x110.76mm original Pi7-inch display,21mm assembly depth TBD and6mm bezel overlap. | Confirm exact actual display, active-area boundaries, PCB thickness, connector and ribbon clearance before printing left tub/retainer. Source MEASURED comments are not new verification. |
| Pi/cooler | Inherited85x56mm PCB and58x49 mounting pattern;22mm assembled height TBD. | Confirm actual Pi and cooler, port direction and cable access; update mounts/envelope. |
| Power packaging | Old left tub hardcodes LRS-100-24-size supply, IEC inlet, divider and a speculative buck envelope. | Confirm actual chosen power hardware before carrying those pockets/cutouts into the next left module. No electrical implementation inferred from CAD placeholders. |
| Cooling | V19 left foot has through slots and rear-opening underside channels. | Keep intake path open; review exhaust and cooler clearance with actual hardware, then evaluate temperatures in assembled prototype. |
| Colours and print split | Current A2 light grey/A1 navy differ from exact historical render swatches. | Keep bezel/cap/plinth navy as separate jobs; pale structural parts separately; six shell colour changes only for logo. PETG insert separate. |
| Fastener schedule | Old31-insert count included obsolete right foot/top details. | Recount after plinth and left bay are final. Tested4.2mm insert bores remain; no two top-cover screws in V28. |

## Execution order

1. Allow current integrated-top shell print to continue. Review does not require cancellation.
2. Design and render the new rounded dark cap and matching right plinth around the ACTUAL v28 shell; these are not yet print-ready parts. Preserve LED and rear service clearances.
3. Prepare final refined cradle, retaining bars, rear cover and PETG diffuser. Verify Bambu settings natively: previous imports did not honor every programmatic setting. Slice each and request print launch as instructed.
4. Confirm display/Pi/cooler/power hardware (question sent to user), then finalize left bay, bezel, retainer, left cover, rear panel and feet together.
5. Recheck seam assembly, wiring, supports and whole-device appearance before releasing left structural print.

The current combined review is output/v28_integrated_top/whole_enclosure_review.step and PNG, generated from retained v19 left parts plus v28 right parts. It is a REVIEW with unverified left hardware, not a complete print release. Cross-module interference audit is context_audit.json. Existing Fusion tabs remain untouched as reference.


## Fusion synchronized — 21 September

Imported the coloured whole_enclosure_review.step into a new Fusion document and saved in the existing lumon project as LUMON_v28_CURRENT_ASSEMBLY_REVIEW. Verified current integrated-top right shell and dark left bezel/foot visible. Original v18/v19 tabs preserved. The new cap/right plinth are still unmodelled, not silently represented by obsolete parts. Left hardware remains unverified.

Standing workflow: refresh the complete coloured assembly in Fusion BEFORE asking for future print approval. Match reviewed right-shell geometry to the actual release revision, retain clear part names and label unverified/concept parts. Keep source generators and review STEP reproducible; save an explicitly versioned Fusion review and visually verify it. Do not use stale Fusion tabs to describe the currently printing design.


## V29 — rear service hatch / ventilation correction (2026-09-21)

The v19 electronics hatch overlapped the lower four rear exhaust slots.
V29 reduces its opening from 112 × 94 to 112 × 74 mm and the cover from
132 × 114 to 132 × 94 mm. Lower datum is retained; upper screw centres move
from z132 to z112. The rear wall and rebate change together, leaving 6 mm
between the cover top and the first exhaust slot. All five vents pass solid
intersection checks, the two changed meshes are watertight, and assembly
pair checks report no interference. This verifies geometry, not cooling performance.

Source: `cad/lumon_v29.py`; regenerate with `.venv/bin/python cad/review/build_v29_review.py`.
Only `tub_left` and `rear_panel_left` are replaced in the exact v28 combined STEP.
The actively printing v28 printer shell is unaffected. Left-side hardware
measurements and print release remain pending.

Complete coloured assembly: `cad/output/v29_rear_vent_fix/whole_enclosure_review.step`.
Saved and opened in Fusion, project `lumon`, as `LUMON_v29_REAR_VENT_REVIEW`.
Audit and rear view are in the same output directory. No new print dispatched.

## V30 — matching printer plinth added (2026-09-21)

Supersedes the printer-base omission above. `cad/review/build_v30_plinth.py`
adds a new navy bonded foot around the exact v28 printed shell, retaining
all v29 geometry. The foot is 9 mm high with 2.5 mm inset and 5 mm lower
bevel matching the left foot. Ground planes agree. Open cutouts preserve
the rocker, rear cables and inter-bay cable route. Five 0.3 mm recessed
adhesive beds retain the foot; unrecessed top lands carry compression.
This avoids new holes in the already printing shell. Physical fit and
bonding remain untested; do not present it as a screw-mounted base.

Valid single-solid watertight mesh, all adhesive beds backed by shell floor,
zero base/assembly intersections and clear relief volumes verified.
Files and assembly notes: `cad/output/v30_printer_plinth/`.
Opened and saved in Fusion project `lumon` as `LUMON_v30_MATCHING_BASE_REVIEW`.
Separate navy print only; not sliced or dispatched. Dark rounded top cap
remains outstanding. No other geometry was changed.

## V31 — prototype complete, cradle retention and next physical checks (2026-09-22)

The v28 shell is now printed (grey/yellow substitution), explicitly a test shell.
The user has only the earlier v26 cradle. V31 retains the exact v28 shell and
approved refined cradle, and adds two tray-capturing legs/lips to the lower rear
bar using its existing screws. Rear/upward nominal play is 0.5 mm. Geometry,
clearance and tray-motion checks pass; physical fit remains pending. The kit
has now been sliced and verified in Bambu Studio: 3 h 6 m 28 s, 108.54 g PLA,
212 layers, one colour. Use `02_cradle_and_bars_reviewed.3mf` and its matching
G-code export. Launch approval, clear bed and current PLA slot remain pending.
See `output/v31_cradle_retention/README.md` for the fitting sequence and prepared
single-colour kit. Imported into Fusion and saved in the existing `lumon`
project as `LUMON_v31_CRADLE_RETENTION_REVIEW`; the complete assembly was
visually checked. A 10-editable-document-limit notification appeared after
saving, but the named v31 document is present without an unsaved marker. No
older document was deleted or changed to read-only during this update.

The user wants the final enclosure less box-like. Keep rear service and a rigid
front/top, but revisit the final structural shoulder rounding and coordinated
navy crown/outlet surround/base using the full assembly. The grey/yellow shell
does not constrain the final styling. Do not start another large shell or final
colour print before hardware fit and actual-CAD appearance review.

## V32 — equal-height study (2026-09-22)

The user explicitly confirmed equal overall heights, tops aligned. This
supersedes the earlier relative-height direction: the left bay grows from
181 to 201 mm, matching the printer bay, with both bases on z=0. The display,
bezel, supports and retainer move up 10 mm to remain centred on the taller
face. Front lid fasteners follow the taller sloped wall and rear vents move
up 20 mm, leaving 26 mm above the service hatch. Bay joining holes retain
their coordinates. All printer-side parts are exact V31 solids, preserving
compatibility with the printed shell and prepared cradle kit.

Changed solids and meshes pass validity/watertightness checks. Complete
assembly intersection checks find no clashes; joining bores, lid fastener
passages and rear vents are unobstructed. Actual left-side hardware remains
unverified, so this is a proportions study, not a left-bay print release.
Coordinated crown rounding and navy trim are still outstanding and must
preserve the common finished height.

Source: `cad/review/build_v32_equal_height.py`. Complete STEP, audit, and
before/after actual-CAD previews: `cad/output/v32_equal_height/`.
The V32 STEP is imported and visible in Fusion as `whole_enclosure_review*`.
Cloud save is blocked by the personal-use 10-editable-document limit;
repeated CUA coordinate actions on the older V28 Editable control failed
with `windowNotFoundAtPosition`, including after resetting the tool session.
No older document was deleted or made read-only. Local STEP and previews are
saved. The design browser was restored. No print was dispatched.


V32 save blocker resolved: the user confirms on 22 September that they made
older Fusion versions read-only and saved the latest equal-height review.

## V33 — cohesive exterior study (2026-09-22)

User explicitly requested matching lower profiles and top-front rounding, with
one continuous shape split for printing rather than two visibly independent
bays. V33 uses a common upright outer envelope with a recessed 14-degree
display. The band has one height and setback across the face; both bays share
a 12 mm front roof radius. The left front brow is now integral, with the
removable lid joint on the roof behind it. The screen and printer datums,
cradle/bars, bay joining axes and service access remain unchanged.

This is a form option, not a final print release. Its four changed solids and
meshes pass checks, all assembly/hardware-envelope and rear-extraction checks
are clear, and vents/joining bores/lid bores are unobstructed. Actual left
hardware and slicer validation remain pending. An assembled seam remains;
do not promise an invisible joint without finishing.

Complete CAD and notes: `cad/output/v33_unified_body/`. Source generator:
`cad/review/build_v33_unified_body.py`. Imported, visually verified and saved
in Fusion project `lumon` as `LUMON_v33_UNIFIED_BODY_STUDY`, without an unsaved
marker. Older V32 saved by the user is preserved. No print dispatched.

## V34 — correction: preserve the sloped display surround (2026-09-22)

The user rejected V33's upright facade and deep screen recess. The original
sloped plane around the display is required. V34 restores the exact V32 face,
bezel and screen position, retaining the common base profile. The display
cover is rebuilt with no fillet along the joining edge: both roof surfaces
meet flat at z201. Exposed front edges have matching 12 mm radii tangent to
their respective faces. The existing front setback from the display rake
remains; no canopy fills it. Roof joint coverage and all assembly, reference,
extraction, vent and bore checks pass. Left hardware and slicing remain pending.

Saved and visually checked in Fusion `lumon` as
`LUMON_v34_SLOPED_CONNECTED_ROOF`. V33 remains only as a rejected alternative.
Files: `cad/output/v34_sloped_connected_roof/`. No print dispatched.

## V35 — desktop-terminal angle (2026-09-22)

User liked the desktop-terminal direction after discussing 20 vs 25 degrees.
V35 models 25 degrees for the entire sloped display face and screen assembly,
retaining the connected roofs and common base. The printer side is exact V34.
Front lid lands/screws move rearward with the panel. A small retainer relief
clears the existing power divider without cutting it. Five screw lands remain
fully supported; use only the rear alignment dowel because the old front pin
now lies ahead of the left wall. All assembly, reference-envelope, extraction,
vent and bore checks pass. Actual electronics remain unverified, with a tight
1.29 mm retainer-to-buck placeholder clearance. No print released/dispatched.

Saved and visually checked in Fusion `lumon` as
`LUMON_v35_DESKTOP_TERMINAL_25DEG`. V34 remains for 14-degree comparison.
Source: `cad/review/build_v35_desktop_terminal.py`.
Files and assembly notes: `cad/output/v35_desktop_terminal/`.


## V39 rear alignment —22 September2026

Full assembly saved in Fusion as LUMON_v39_ALIGNED_REAR at19:38 and verified.
Display-side rear wall/hatch/roof/base extend9.75mm to the printer cap datum.
Front throughY135,25-degree display,Pi/PSU and all printer-side parts unchanged.
Rear corners and base radii matched; CAD/mesh/clearance checks pass.
Seven Bambu bay plates prepared, no dispatch; see output/v39_aligned_rear.
