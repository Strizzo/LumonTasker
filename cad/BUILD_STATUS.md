# Current physical build status — 26 September 2026

## Assembled device accepted; software phase started — 26 September

User reports “It's great and it works” after assembling the two bays, including
the translucent PETG insert. The supplied photo shows the assembled device with
the blue indicator illuminated. This supersedes the insert's pending completion,
fit and transmission checks below. No further enclosure print is requested at
this point; the next task is Trello verification and the Lumon terminal UI.
Software deployment and live checks are documented in `../software/README.md`.
Photo reference:
`/tmp/codex-remote-attachments/01a0bf3e-2220-7252-adef-d07f9ff37b1f/0633AA76-1ED7-49BC-8ACD-53273498E6D4/1-Foto-1.jpg`.

## Translucent PETG LED insert — 26 September

User confirms translucent PETG is loaded in AMS slot **3**. Prepared the current
assembly's existing insert, unchanged from the accepted earlier PLA fit trial.
One valid watertight solid, 44 × 8.5 × 3.4 mm in flange-down print orientation,
zero clashes with the current assembly. The saved Fusion assembly already
contains this geometry; no new Fusion document is needed.

Native Bambu slice: **11m30s, 0.61 g, 17 layers at 0.2 mm**, Generic PETG
255 C nozzle / 70 C textured PEI bed, no supports or prime tower. Continuous
first-layer flange and layer 14 short face bridge visually checked. Native
export verifies the PETG preset and temperatures. A3 PETG K0.040 registration
confirmed in Device; project filament 1 must map to physical **A3** at launch.
Prepared project/toolpath: `output/v51_petg_led_insert`.

**Dispatched** after fresh user confirmation that the plate is cleared.
Send dialog mapping verified PETG **A3**, timelapse OFF, auto bed levelling OFF.
Device confirms active preparation of the matching LED job at 0/17 layers,
waiting for heatbed; nozzle target 255 C / bed target 70 C. Estimated finish
22:25 local.
Completion, physical PETG fit and optical transmission are still pending.
After printing,
fit the insert from behind the light opening, flange inside; test the blue light
before small flange adhesive points. PETG optical performance remains untested.

White DC inlet panel is **Finished 100%, 40/40 layers** in Bambu Device.
Removal is confirmed by the user clearing the plate; actual socket/panel fit
is not yet confirmed. This supersedes
older inlet-panel "active preparation" statements below.

## Exposed unused insert hole — next revision feedback, 26 September

User identifies the visible screw-insert hole on the printer-bay edge beside
the display glass as useless and requests removal in a future revision.
Photo reference:
`/tmp/codex-remote-attachments/01a0bf3e-2220-7252-adef-d07f9ff37b1f/491BE101-4384-473F-91DF-DCE7AA8ACD06/1-Foto-1.jpg`.
Omit that exposed unused bore and any associated unused mating feature in the
next revision, leaving a continuous finished surface beside the screen.
Map this photo to the exact CAD bore before editing; do not remove the other
working inter-bay joints or display mounts as a blanket change. Current
printed parts and the active inlet-panel job are unchanged.

## Remaining-print and batching review — 26 September

User is away and cannot clear the build plate between jobs. Bambu Device was
checked again: the V51 navy display base is Finished 100%, 45/45 layers; the
white DC inlet panel was initially prepared but not dispatched. User subsequently
confirms the plate was left cleared and authorizes printing. The inlet panel
was sent to P1S using cotton white A2 with bed levelling and timelapse off;
Device confirms active preparation at 0/40 layers, filament loading and
heating to 55 C bed / 220 C nozzle; estimated finish 17:26 local.
Completion and physical fit remain pending.

There are no other specified, unprinted PLA enclosure parts to add to the
inlet-panel plate. The printer shell/cradle, printer rear cover, both navy
bases, display body, rounded roof and rear hatch have already been printed.
Printed does not mean physically fitted: printer rear-cover fit and display
base fit still need user confirmation. Old loose display brackets and navy
screen bezel are superseded and must not be printed. Inter-bay joining uses
fasteners and the existing rear metal alignment-dowel provision, not a new
printed joining block.

The LED insert was only trial-printed in light-grey PLA (see V25
`led_trial_slice.json`, finished and accepted). The final translucent PETG
insert is prepared with Generic PETG and user-confirmed AMS A3; its printing
and optical check are pending (see current section above). Keep this as a separate PETG job rather than adding it to
the cotton-white PLA inlet panel. Any converter mount or harness restraint
requires the actual selected converter and wiring layout. Future lighter
shells, improved display roof supports and larger glass seat are revision
requests, not additional parts needed for this physical assembly.

## Rear 24 V inlet glue panel — 26 September

User chooses to glue the female DC socket and requests a cylindrical sleeve
extending **5 mm inward** for adhesive contact. Prepared the V51 accessory with
10.2 mm bore for the requested nominal 10 mm neck, 14.2 mm sleeve outer diameter
and 2 mm radial wall. Outer face remains 56 × 37.1 mm, locating shoulder
46.9 × 28 mm, preserving the already printed case. It is one valid watertight
solid with zero CAD assembly clashes. Actual socket neck/body clearance must
be dry-fitted before glue. The separate rear clamp and black-body measurement
request are superseded by the user's glue choice.

Bambu Studio native slice of `02_DC_inlet_glue_panel.3mf`: **20m27s, 5.62 g,
40 layers at 0.2 mm**, cotton-white PolyTerra PLA on project filament 2 / AMS
slot 2. Outside face on bed; no supports/prime tower. First layer and complete
sleeve toolpaths visually checked. Saved native project and exported native
G-code 3MF in `output/v51_dc_inlet_panel`. Stock PolyTerra profile uses 220°C
nozzle, 55°C textured bed and carries the generic PLA chamber/bed heat advisory;
do not alter profile glass-transition fields simply to suppress that warning.
**Dispatched 26 September, approximately 17:05 local, after explicit plate-clear
confirmation.** Cotton white A2, bed levelling and timelapse OFF. Device
confirms active preparation of the inlet panel at 0/40 layers, filament
loading and heating; estimated finish 17:26 local.
Completion and physical socket/panel fit are pending.

Bambu Device reports the navy display base **Finished 100%, 45/45 layers**.
User confirms the plate is clear, so removal is confirmed; base fit is still
unconfirmed. The revised full assembly STEP is
`LUMON_v51_GLUE_DC_INLET_ASSEMBLY.step`. Imported and saved the full assembly
in Fusion project `lumon` as `LUMON_v51_GLUE_DC_INLET_ASSEMBLY`. Confirmed saved
(no asterisk), with only that document left open. V30 review was made read-only
to free one editable slot; it is preserved.

Incoming regulated 5 V can use Pi **physical pin 2**, and incoming ground
**physical pin 9**; the display remains on pin 4 (red 5 V) and pin 6 (black GND).
On a component-side view with the header along the top and USB/Ethernet to the
right, the outside row is even-numbered left to right, and the inside row is odd.
GPIO input bypasses the Pi 3 micro-USB input protection: final protected converter
and secure harness are still pending. No physical power wiring is inferred.

## V51 display-body fit and support feedback — 26 September

The user reports that several of the automatic tree supports inside the upright
white body broke during printing. The roof bridge still printed, but left loose
strands that the user removed. This is a support failure, not evidence that the
body geometry or filament calibration alone is at fault. For the next full body,
replace the current default `tree(auto)` strategy at that roof span with a
stable, deliberately placed support arrangement and inspect its footprint,
branch/trunk stability, interface and bridge layers in Bambu Studio before
printing. Consider a self-supporting roof detail if it preserves the accepted
external shape and roof interface. Do not reuse the V51 support plan unchanged.

The V51 recessed glass seat was too tight in the full body: fitting required
substantial sanding despite the earlier small fit coupons. On the next body
revision, enlarge the seat **2.0 mm overall in width and 2.0 mm overall in
height**, centred on the existing glass/lug datums (nominal current opening
193.6 × 111.4 mm; proposed 195.6 × 113.4 mm, subject to checking the actual
V51 source). Keep the accepted four mounting-hole axes and screw-contact depth.
Retain an effective 3 mm load-bearing ledge under the actual glass perimeter;
do not simply move the inner ledge edge outward with the new pocket. Check
glass retention, visible edge gap, corner profile and front removal with the
real display before another full print. The current sanded white body remains
the physical test part; no reprint is requested now.

The navy base was still printing when this feedback was reported. Bambu now
reports completion; physical fit is not yet confirmed.

The user does the project through the assistant and has done no unreported work.
Keep CAD, sliced, printed, and physically fitted states separate. Update physical
state only from explicit user confirmation or direct evidence; never infer that
an instruction has been carried out.

## Power requirement clarified — one external cable

User confirms **Raspberry Pi 3 Model B**. Printer adapter label is 24 V DC,
1.5 A, 36 W (adapter rating, not measured printer load). Plan: one external
24 V enclosed brick, internal regulated 5 V converter feeding Pi micro-USB,
and a separate 24 V printer branch. The user is willing to reuse the original
printer DC cable/three-contact plug; pinout and polarity still need verification.

Recommended adapter: **Mean Well GST90A24-P1M, 24 V / 3.75 A / 90 W**.
Amazon.de listing https://www.amazon.de/dp/B0131V8XWQ verified 24 September:
IT-Tronics GmbH €32.91 + €8 shipping = €40.91, estimated 30 September–5 October.
Cheapest offer €37.78 delivered, estimated 8–12 October. No purchase made.
C14 mains inlet needs a grounded C13 mains lead; listing only states one adapter.
DC output is 5.5 × 2.5 mm centre-positive barrel, not the printer's connector.
Converter and enclosure DC inlet are still to finalize. See power_architecture.json.

This direction supersedes the old unconfirmed internal LRS supply, IEC inlet
and divider. No electrical connections or full-body release yet. Active V50
roof/rear-panel print remains compatible and unchanged.

## V51 display body preparation — 25 September

Follow-up: user reports the V51 white display body has finished and the plate
is clear. The bottom edge and four roof mounts look intact; user says roof and
rear-hatch fits look fine. No detailed mounted-screen test has been reported.
The navy display base is printing on P1S 3DP-01P-994. The inherited V40
underside-pocket base was rejected after native slice preview (124.03 g,
4h38m, cantilever warning). V51 uses the closed-surface V39 outer profile
with old power-vent slots filled. CAD probes confirm continuous top/bottom
material across the interior and preserve the four fastening holes. Six small
tabs introduced by the slot plugs were trimmed to the chamfered outer profile
before the final slice. The top-face-down plate sliced with no support at
3h23m17s, 114.16 g, 45 layers, 3 walls, 4 top/bottom layers and 8% gyroid.
Bambu Studio reported successfully sent with navy PLA A1, timelapse off and
auto bed levelling off; Device subsequently showed active printing at 6%,
layer 1/45, with nozzle and bed at printing temperature. Completion and
physical fit are pending. After it cools, check the closed underside/edge,
dry-fit it to the white body and compare the back edge with the printer bay
base before any permanent assembly.

V50 rounded white roof and 132 × 94 mm white rear hatch completed. Bambu shows
Finished 114/114; user confirms both intact and build plate clear. They do not
assemble until the full display bay body is printed. Roof fastens from above;
rear hatch closes the lower rear service opening. Remove supports gently and
store both parts. No need for glue.

V51 CAD preserves the accepted V49 glass/metal-lug seat and V50 printed mating
interfaces. Removed old open-frame internal AC PSU divider/corner blocks and
unneeded Pi-on-side-wall standoffs; closed old floor/base cooling slots. The
old rear connector recess is retained as a modular low-voltage inlet site,
with an independent blank/pilot insert until the exact connector is selected.
Single-solid watertight STL; body front-down bounds 218.96 × 231.33 × 164.17 mm.
Bambu's selected upright, base-down plate is
`output/v51_external_power_body/02_V51_display_body_upright.3mf`.
Native tree-support slice: 20h2m, 562.20 g total (457.69 g model),
3 walls, 4 top/bottom layers, 8% gyroid, 0.12 mm support gap.
Sent to P1S 3DP-01P-994 using cotton white A2 with timelapse and auto bed
levelling off after user confirmed the roof/hatch intact and plate clear.
Bambu showed an active 0/880-layer job, cleaning nozzle tip, estimated finish
20:59 local. User subsequently confirmed this body completed, bottom and roof
mounts intact, roof and rear hatch fit, and plate clear. The corrected V51
whole-assembly STEP was uploaded to the existing Fusion `lumon` project as
`LUMON_v51_EXTERNAL_POWER_ASSEMBLY`; it appeared in the project search and
opened as a solid-design assembly. Fusion is a review copy of the generated
CAD; the project STEP remains the source for further geometry edits.

Navy display base print plate is
`output/v51_external_power_body/04_V51_closed_display_base_top_down.3mf`.
The old internal-PSU ventilation slots are closed in this version. Earlier
`03_V51_closed_display_base.3mf` is the alternate bottom-down comparison,
not the print job sent to the P1S.

User proposed Amazon Prime GPJYD 24 V / 3 A / 72 W adapter; its rating fits the
provisional power budget, but purchase/physical loaded performance are unconfirmed.
Pi needs a separate regulated 5 V converter. See power_architecture.json.

## V50 display roof and rear panel print record — 24 September

User confirms the plate is clear after V49. Sent the prepared roof and rear
panel together as V50_Display_Roof_and_Rear_Panel to P1S3DP-01P-994.
Cotton whiteA2, bed levellingOFF, timelapseOFF verified.114 heights,
3h53m40s,118.64g, no inter-colour swaps. Device later showed Finished 114/114; user confirms both pieces intact and
plate clear on 25 September. Output: v50_full_display_preflight.

The full display body/base remain unprinted. The power direction is now a
shared external 24 V supply (see above); internal converter/inlet geometry
still needs integration. Display fit tests are accepted.

## Current — V49 physical tests accepted, full bay preparation

User confirms BOTH V49 corner samples seat without bending and their 4 mm
screws reach/tighten gently. User measured the mixed samples and identifies
**0.12 mm support top gap as better**. Select that gap for supported display
bearing features. No further full-frame fit test is needed before preparing
the full display bay. The four-hole XY pattern was separately confirmed on
the earlier full-frame test; V49 tests one revised corner twice.

Full display body, roof, rear hatch and left navy base remain unprinted.
Printer shell/cradle and navy printer base fit are accepted. Printer rear
cover was printed; physical fit has not been reported. Preserve accepted
printer geometry. Power architecture is awaiting clarification: old CAD has
an unconfirmed internal PSU/divider and an interfering cable keep-out.
Full-body orientation/access and final slices still need review. Fusion V39.
Fresh plate clearance after V49 has not yet been reported.

## Full-case preflight — 24 September, after V49 acceptance

- Full body front-down bounds218.96×231.33×164.17 mm; sloped front face
  reaches the bed. Mesh watertight. Full-body slice remains outstanding.
- Four display screws have room for a compact driver envelope:55 mm shaft,
  Ø5.5 mm, plus45 mm long/Ø25 mm handle, with roof removed. Straight long
  insertion from outside the rear is obstructed at three screw axes. Use roof
  access before routing wires; exact user's screwdriver has not been measured.
- Existing rounded roof and rear hatch prepared together, sliced and previewed
  in Bambu: **3h53m40s,118.64g,whiteA2 only,114 heights**,3walls,4top/bottom,
  10%gyroid,0.12supportgap. Geometry matches savedV39. Only0.78g non-model.
  Project/toolpath in output/v50_full_display_preflight; NOT DISPATCHED.
- Awaiting user choice: existing external adapters vs specified internal PSU.
  Old divider occupies237.48mm³ of provisional Pi rear cable space; do not
  carry unconfirmed power hardware into the final full-body print.
- Fresh plate-clear question sent for roof/hatch; no answer yet. No new print.
- Remaining full body/base need power/cable and ventilation finalization;
  provide closed-looking lean left base without obstructing needed air paths.

## V49 measured bracket-depth correction — 24 September

V48 completed (Device Finished100%,121/121 and user assembly photo), but the
arms bend while seating the display and the short screws do not reach. User
measures glass FRONT to flat metal mounting face **8.4 mm**, and screws **4 mm
under the head**; heads fit the existing counterbores.

- V49 relieves all four contact pads **2.44 mm**, local y6.96 to y9.40.
- Plastic grip under screw head is **2.0 mm**, reduced from3.9; head-seat y11.40.
  The actual4 mm screws protrude2 mm nominally. Do not substitute M3x6.
- Original XY hole positions, arm roots, pocket193.6x111.4/R8.2 and3 mm ledge
  preserved; contact depth changes only. CAD single-body, watertight, bearing,
  screw passage, unchanged-region and conservative insertion checks pass.
- Return to front-face-down orientation at user request. Two small identical
  upper-right corner coupons compare support gap0.20 vs0.12 mm and test depth/
  screw reach. Full-frame geometry also updated, but no full-frame reprint queued.
- V49 small plate sliced/reviewed:50m14s,14.30 g,whiteA2 only,no colour swaps.
  Per-object0.20/0.12 gaps verified in saved project and toolpath.
- User now confirms plate clear. Sent the two V49 coupons using whiteA2,
  bed leveling/timelapseOFF. P1S shows matchingV49 job active0/152,startup,
  ETA18:14 local. First layer, completion and physical outcome pending.
  CAD: output/v49_measured_display_depth. Fusion stays savedV39; not synced.
- Earlier2.5 mm maximum-thread-depth claim is not explicitly verified in the
  manufacturer drawing. Do not force a screw that stops before its head seats.
- Full display case still needs cable/power and full-body print/access review.

## Historical quality feedback — V48 during printing

- User photo shows continuing loose/frayed strands on the opposite side of
  the flipped frame. Orientation change is not a validated surface-quality fix.
- Device checked at58%, layer103/121,1h16m remaining, ETA16:13. Exposed infill
  and unfinished top surfaces cannot yet be judged as final finish.
- Actual support Z gap remains0.2 mm; denser3-layer/0.15 mm interface was used.
  Support contact is a plausible cause; filament calibration is not established
  as the cause from this photo. Original mounts remain unchanged/confirmed.
- Before final-case printing: inspect completed bearing and reverse faces, then
  validate contact gap/finish with a SMALL representative coupon and reference
  surface; review effective filament profile if ordinary surfaces also fail.
  Prefer orientation avoiding support contact on visible/bearing surfaces.
  No calibration job sent; existing print unchanged. Details:
  output/v48_display_original_mounts/PRINT_QUALITY_FEEDBACK.md.

## Latest correction — preserve original mount holes, V48

- User corrected display assembly orientation and confirms original holes match.
  DO NOT apply the earlier rear-view right3.6/down2 mm shift. V47 is superseded
  and was never printed; its project/toolpath are marked DO_NOT_PRINT.
- V48 retains the exact V45/V46 arms, pads, bores and counterbores. Only widen
  the pocket0.2 mm overall and retain the improved rear-down test orientation.
- Original hole alignment physically confirmed. Bearing surface quality and
  simultaneous glass/metal-lug seating are not yet accepted.
- V48 CAD checks passed, including zero mount-geometry difference fromV45.
  GUI project and toolpath saved/reviewed: 11098s, 63.32g,121 preview heights.
  User now authorizes printing and confirms plate clear. Sent V48 test to
  P1S3DP-01P-994, cotton whiteA2; leveling/timelapseOFF verified. Device
  confirms matching job active0/121, heating/loading, ETA16:15 local. Camera
  live; first layer/completion not yet verified. FusionV39.

## Historical, superseded mount shift — V46 correction to V47, 24 September

- V46 completed, confirmed by user photos and Bambu Finished100%,114/114.
- Glass almost fits; one corner tight. Increase pocket total width by0.2 mm,
  centred (+0.1 per side), to193.6×111.4 mm; R8.2 and height retained.
- Shift entire four-lug pattern and pads right3.6 mm/down2 mm viewed from rear.
  In front-based local CAD coordinates this is X−3.6/Z−2.0. Pitch unchanged.
- Loose strands/poor attachment visible along inner ledge. Do not accept the
  bearing surface or simultaneous glass/metal-lug contact as validated.
- V47 updates production tub and extracts a matching fit frame. CAD passes
  single-solid/watertight, full3 mm bearing, corrected bores/lands, nominal
  front insertion sweeps, and unchanged geometry outside interface regions.
- Revised fixture prints rear down, seat and lug lands upward. Denser three-layer
  same-PLA support interface underneath non-contact reverse faces. WhiteA2 only.
  GUI slice/preview passed:3h04m01s,63.31g,121 preview layer heights. Saved
  project/toolpath. Fresh plate-clear question pending; no dispatch yet.
- Full display enclosure not released. Actual metal/Pi offsets not inferred
  from lug-only measurement; power/cable layout and full-case access unresolved.
  Fusion remains closed/latestV39. See output/v47_display_fit_correction.

## Latest display requirement — V45 3 mm bearing seat, 24 September

- User requests 3 mm inward bearing width instead of 2 mm and explicitly
  confirms the black band clears the outermost 3 mm rear glass border.
- Widen ledge through its full 2.3 mm material thickness. Keep measured
  0.8 mm glass, 1 mm recess, accepted opening and four integral retention arms.
  No notch, front lip, soft gasket or separate navy bezel required.
- Selected candidate: output/v45_display_seat_3mm/glass_0p8. V44 2 mm geometry
  is historical. Nominal chassis clearance at lower glass border is only
  0.35 mm; actual ledge/metal-lug stack still needs a physical fit check.
- CAD passed: single valid watertight body, full-width/full-depth ledge,
  nominal hardware clearances, front sweeps with fixed arms, screw passages,
  and conservative band clearance. Bearing contact area is 1754.52 mm².
- Full-case power/cable routing, screw access and slicing remain pending;
  no display-body print released. Printer parts/job unchanged; Fusion V39.

## Completed test — V46 integral display-seat fit frame, 24 September10:39

- Exact V45 seat and four integral arms cropped into one small test frame;
  no loose brackets/case inserts. CAD interface, front passage and mesh checks
  pass. Same-colour normal supports required under ledge and mounting arms.
- GUI slice/export reviewed:2h02m04s,47.29 g (39.11 g model,8.17 g supports),
  A2 cotton white only,114 preview layer heights, no inter-colour swaps.
  3 walls/4 top-bottom layers/10% gyroid. Project/toolpath saved in
  output/v46_display_seat_fit.
- User now explicitly confirms plate clear. Sent toP1S3DP-01P-994 as
  V46_Display_3mm_Seat_Integral_Mount_Test. A2 white mapping and bed leveling/
  timelapse OFF verified before Send. Device confirms matching job active at
  0/114, waiting for heatbed55 C, nozzle220 C; estimated finish12:41 local.
  Camera enabled. Completion subsequently verified; physical test issues above.
- After print, remove supports; fit glass/Pi from front with no screws and
  check even seat plus all four lug-pad contacts, then gently secure M3×6.

## Previous display requirement — V44 bearing seat, 24 September

- User measures glass mostly 0.8 mm, with a local black band measuring 1.3 mm
  total, and confirms the band does not reach the outermost 2 mm rear border.
  Select glass_0p8 seat y1.8 for glass-front y1.0; no seat notch required.
  The 2 mm dimension is bearing width underneath glass, not padding thickness.
  The rigid integral ledge is 2.3 mm thick; there is no soft gasket/front lip.
- User explicitly requires the recessed seat to support the glass and prevent
  inward movement without screws. Four rear screws prevent front withdrawal;
  four support arms stay integral with the case. No separate bezel/front lip.
- V41/V43 left 0.4–0.8 mm behind the glass and did not meet this requirement.
  V44 raises the continuous 2 mm bearing ring to the nominal glass-back plane.
  Accepted 193.4×111.4 mm/R8.2 opening and 1 mm recess are preserved.
- Two older nominal variants (0.7 and 1.1 mm) remain as references. The new
  glass_0p8 baseline uses the user's measurement. A conservative interior band
  envelope checks seat clearance; exact band geometry remains unknown.
  Seat geometry selected; full case not released for printing. Keep glass and rear lug
  bearing planes matched; never tighten across a lug gap.
- The measured 0.8 mm baseline and both reference variants pass valid single-body/watertight checks, all four-side bearing
  checks, glass-alone inward stop/outward clearance, and nominal front sweeps
  with integral arms in place. This verifies geometry, not physical strength
  or a physical assembly test.
- Existing V40 contour test does not validate the new seat or metal lug stack.
  Full-body power/cable, screw access and printability checks remain pending.
  Printer geometry/job unchanged; Fusion remains V39. See output/v44_bearing_seat.

## Previous display candidate — V43 integral mounts,24 September

- User proposes case-integrated mount arms because the display/Pi inserts from
  front. Implemented four integral arms, four M3×6 rear screws into metal lugs.
  Removed four separate brackets, four M3×8 case screws and four case inserts.
- White recessed seat, accepted outline/R8.2 corners and1 mm recess unchanged.
  No navy bezel/front lip. Metal pad depth and screw engagement unchanged.
- Revised body single valid/watertight solid. Four bores/head recesses/lands
  pass. Exact nominal front insertion/extraction sweeps pass with integral arms
  LEFT IN PLACE. Nominal Pi margin and component clearances pass.
- Existing V40 frame/brackets still verify hole pattern and metal bearing depth;
  only glass contour is physically confirmed. Do not require final separate
  brackets after adopting V43. Fixed-arm full-body orientation/support review,
  screwdriver/cable access, and real power architecture remain unverified.
- Cable/divider conflict237.48 mm³ retained. No full-body print released.
  Active navy base unchanged. Fusion closed/latestV39. See output/v43_integral_display_mounts.

## Completed print — navy printer base, verified 24 September morning

- User reports the previous print completed. Bambu Device confirms matching
  V42_Navy_Printer_Base_Lean, 100%, 45/45 Finished. User now explicitly confirms
  the base fits and will glue it later. Bonding remains undone.
- User dislikes the open underside and wants a closed flat bottom. The original
  conservative switch/cable clearance cuts extended through the full base.
  Next revision: thin bottom skin, internal clearance recesses and necessary
  rear/side exits; validate rocker travel, cables and printer extraction first.
  This is recorded design feedback, not a released CAD change. Keep this base.
- User subsequently cleared the plate; V46 was dispatched at10:39 as above.

- User said go on and then explicitly confirmed all five display-test pieces
  were removed and the plate completely clear.
- Compared original V39 slice97.50 g/2h48m01s, pocketed CAD89.01 g/2h38m37s,
  and original shape with lean settings75.89 g/2h05m09s. Selected the last:
 22.2% less filament and42m52s faster than V39, with intact outer/bond surfaces.
- Dispatched02_V42_printer_base_lean toP1S3DP-01P-994. Device shows job
  V42_Navy_Printer_Base_Lean, heating0/45 layers, estimated finish03:02.
  NavyA1 only; no supports/colour swaps; bed leveling/timelapseOFF.
  Completion and physical fit now verified as above. See output/v42_light_printer_base.
- Pocketed candidate NOT selected. Current V42 review STEP retains the V41
  assembly with original printer-base geometry; no Fusion changes.
- V41 exact nominal front-service sweeps pass after bracket removal.
  Full display print waits for rear bracket seating confirmation and actual
  power/cable plan. Asked user about retaining existing external adapters;
  answer pending. Fusion remains closed/latestV39.

## Latest physical feedback — 24 September, V40 display frame

- User reports perfect fit and supplies a photo of the full-outline frame on the
  real glass. Preserve the193.4×111.4 mm opening withR8.2 corners as physically
  accepted. The exact glass radius itself remains inferred, not measured.
- Printed frame completion confirmed. Four rear bracket seating/alignment,
  fastener stack and retention are NOT yet confirmed; clarification requested.
- User explicitly corrects the appearance: **no separate navy bezel and no lip
  over the glass**. The existing black glass border stays visible, fitted into a
  recessed seat in the white sloped front. The assistant's preceding overlap
  interpretation was wrong and is superseded.
- Preserve the accepted pocket contour and the rear metal-lug support. Fill
  the obsolete decorative bezel rebate into the white panel and provide a
  shallow step behind the glass, without a front clamp.
- V41 candidate generated and visually checked: integrated white seat,
  glass recessed1 mm, no front overlap and no separate display_bezel component.
  Body is valid/watertight; checked part pairs and nominal hardware clear.
- Printed bracket shapes unchanged; entire glass/anchor stack moves2 mm
  rearwards together. Rear screws release the screen for extraction from front.
- No new print dispatched. Rear bracket fit remains unconfirmed; provisional
  cable keepout still overlaps divider237.48 mm³. Full-body release held.
  Fusion remains atV39. See output/v41_recessed_glass/{README.md,audit.json}.

## V40 display fit kit — 23 September evening

- User confirms attached display/Pi depth **40 mm**; glass **193 × 111 mm**.
  No outstanding glass or total-depth measurement request.
- User wants the glass to fit precisely into the frame. Candidate opening is
  **193.4 × 111.4 mm**, 0.2 mm nominal per-side gap, R8.2 from provisional R8
  glass. Physical fit test determines the final curve and allowance.
- Small five-part kit: full-outline frame and four separate metal-lug brackets.
  Geometry, connected solids, watertight meshes, assembled pair collisions,
  glass clearance, and print orientations passed independent fit-kit audit.
- Candidate V40 removes obsolete separate Pi standoffs and generic retainer.
  Large display bay remains on hold: rear cable allowance intersects the old
  divider; resolve routing/actual power layout after the mechanical fit test.
- Candidate display foot has 44.3% less CAD solid volume; this is not a sliced
  filament-saving claim or a stiffness validation.
- User stopped work to close Fusion because Mac performance suffered, then
  authorized resuming and printing while clearing the bed. Keep Fusion closed
  for now; V40 has NOT been imported/saved there. V39 remains latest Fusion.
- User brought Bambu forward; GUI controls recovered. Fit kit sliced, saved,
  visually reviewed and dispatched at **21:39 local** to P1S 3DP-01P-994.
  Matching job verified active/heating at **0/60 layers**, estimated finish22:50.
- **1h11m26s,26.74g,60layers**; A2 cotton-white PLA only, no supports or colour
  swaps.3 walls,4 top/bottom layers,0.8 mm top minimum,10% gyroid,0.2 mm layers.
  Bed leveling and timelapse OFF. First layer/completion/physical fit unverified.
  See output/v40_display_mount/{slice_review,print_dispatch}.json.
- Earlier CLI slicing attempts failed; the saved GUI slice/export is authoritative.

## Display hardware update — 23 September

- New photos show Pi attached directly to display; four outer metal mounting
  lugs available. User confirms loose wire plugs only, not broken pins.
- Revise the display mount around metal lugs and measured spacer stack;
  glass must not be squeezed against a rigid lip. Keep25-degree facade.
- Existing21 mm display box and separate Pi mounts are unverified placeholders
  inconsistent with the complete photographed assembly; V39 display-side
  slices remain review-only. Current printer rear-cover print unaffected.
- User measured glass **193 × 111 mm**. Official drawing has no corner-radius
  callout; scaled vector outline suggests ~7.9 mm, so provisional reference R8.
  Allow clearance/corner relief and verify a small fit test; no tight glass clamp.
- Full assembly depth subsequently confirmed as40 mm; superseded by V40 fit
  kit above. See DISPLAY_MOUNT_REVISION.md and display_hardware.json.

## New design requirement — reduce enclosure weight

- User finds the printed shell too heavy; balance stiffness with material use.
- Audited actual G-code: shell ~593 g model; inner+outer wall paths~415 g,
  sparse infill~73 g. Existing broad panels3–4 mm; inter-bay wall9 mm.
- Future candidate:2.4 mm general skins, local ribs/bosses, preserve bearing
  surfaces and insert engagement;3 loops/4 skins/8–10% gyroid as a starting
  point requiring reslicing and stiffness/retention checks.
- Review remaining unprinted bases/display parts for weight before release.
  Current cover continues; existing shell accepted. Detailed measured evidence
  and candidate criteria in output/v39_aligned_rear/NEXT_REVISION.md and
  weight_audit.json. No lightweight geometry or revised print yet released.

## Completed print — V39 integrated rear cover (23 September)

- User authorized next part and confirmed bed clear after shell removal.
- Dispatched 02_V39_printer_rear_cover.gcode.3mf to P1S 3DP-01P-994.
  Device directly verified Finished,100%,231/231 layers before V40 dispatch
  at21:39 local. Physical cover fit remains unverified.
- Cotton white A2 only; auto bed leveling and timelapse OFF.
- Estimate4h04m51s,140.90g,231layers. Completion verified in Device.
  See output/v39_aligned_rear/rear_cover_print_dispatch.json.

## Latest physical confirmation — V39 shell, 23 September

- Shell finished (P1S 805/805); user supplied photos and removed the part.
- Existing V31 yellow cradle fits perfectly in this shell; printer fits perfectly
  on it inside the shell, explicitly confirmed by user.
- User accepts current shell; requests a flush lower band for next revision.
  Existing 0.8 mm decorative exterior inset causes the step and front-down
  support strip. See output/v39_aligned_rear/NEXT_REVISION.md.
- User authorizes next compatible rear-cover print and confirms bed clear.
  Rear cover, navy foot and secured closure remain untested.

## Latest check — 23 September afternoon

- P1S reports shell printing at 96%, 785/805 layers, 37 minutes remaining;
  estimated finish 16:19 local. Completion and fit are not yet confirmed.
- Next physical step: cool, remove supports/brim, dry-fit existing V31 yellow
  cradle and printer into new shell; check raised outlet, LED, switch/cables.
- Next prepared print is integrated white rear retaining cover (4h04m51s),
  then navy printer base (2h48m01s). Cover replaces old separate bars.
- Await actual shell condition and clear plate before another dispatch.

## Active print — V39 printer shell (22 September, 21:45 local)

- User explicitly authorized printing and confirmed the build plate is ready.
- Sent 01_V39_printer_shell.gcode.3mf to P1S 3DP-01P-994; Bambu confirms
  successful send. Device shows the matching job, 0/805 layers, heating.
  Estimated finish 23 September at 16:15 local.
- A1 navy / A2 cotton white; auto bed leveling and timelapse OFF.
- Estimate 18h30m54s, 634.49g, 805 layers. Only this shell dispatched.
- First-layer quality and completion not yet verified. See
  output/v39_aligned_rear/print_dispatch.json. Earlier bed-clear hold resolved.

## Current actionable state — V39 (22 September evening)

- Rear-depth mismatch fixed. Both assembled rear facesY170.75; both basesY168.25.
  Display rear extended9.75mm; matching9.5mm rear corner/7mm base radius.
- Front throughY135 exactly unchanged;25-degree display retained. Pi/PSU fixed.
  Rear hatch/IEC recess/roof skirt and rear mounts updated together. CAD audit
  passes, including clashes, vents, mounts and printer rear removal.
- Fusion saved and verified as LUMON_v39_ALIGNED_REAR at19:38;10/10 editable docs.
- Four revised display-side plates sliced plus three unchanged printer-side
  slices reused with byte-identity checks. All in output/v39_aligned_rear.
  See README.md,plate_manifest.json,slice_review.json. Shell dispatched as above.
- Next job01_V39_printer_shell.gcode.3mf:18h30m54s,634.49g,805layers,6changes.
  Embedded name stillV38 because toolpath is unchanged. WhiteA2/navyA1.
  Bambu Send succeeded for this V39-named file; A1 navy/A2 white and
  bed leveling/timelapse OFF verified.
- Display body19h07m34s,roof3h02m,hatch54m30s,navy base4h38m.
  Seven plates total1528.76g white+259.86g navy(excludes unchanged trim/retainer).
- Older rear-depth design hold and build-plate clearance hold are resolved.
  User confirmed the plate is ready after removal request; shell dispatched.
- Left actual electronics fit unverified. Printer prototype retention/feed passed;
  new integrated rear cover/outer holes still await physical trial.

## Rear alignment review — PRINT HOLD (supersedes launch readiness below)

User identifies mismatched assembled depths in Fusion. Verified actual V38 STEP:
left rear wall/hatch/roofY161.00, printer rear coverY170.75:9.75mm step.
Left navy base endsY158.50 versus rightY168.25:also9.75mm step.
Bambu Send dialog closed without sending. Nothing started. Even a reply to the
older bed-clear question does not release this design hold.
Recommended correction: extend display-side rear envelope/roof/base to common
Y170.75 while preserving tested printer installation and25degree display front.
Dependent rear hatch/vents/IEC/roof/base mounts must be revised together. Left
Pi/PSU placements are depth-derived if regenerated and need corresponding checks.
Geometry has NOT been changed yet; this turn establishes the mismatch and cause.
See output/v38_integrated_rear/rear_alignment_review.json.

## Latest actionable state — V38 (22 September, approximately 17:49)

- Full assembly saved in Fusion as LUMON_v38_INTEGRATED_REAR (17:19 save,
  no unsaved marker, 9/10 editable documents). App-control connection recovered.
  User confirms Fusion and Bambu look fine and says proceed.
- Rear closure: flat shell lands, rounded single cover with integral retaining
  ribs/capture lips, four M3x14 screws, matching navy base. CAD audit passes.
- ALL THREE printer-bay plates sliced and exported in output/v38_integrated_rear:
  - SELECTED shell: V38_final_shell_tree.gcode.3mf, 18h30m54s, 634.49g,
    805 layers. A2 white631.72g, A1 navy2.77g. Colours coexist only layers1–4;
    six changes total. Tree supports39.54g save46.77g and1h20m53s over normal.
  - Cover: V38_rear_cover.gcode.3mf, 4h04m51s,140.90g white,231layers,
    single colour,1.33g removable support.
  - Base: V38_navy_base.gcode.3mf,2h48m01s,97.50g navy,45layers,
    single colour,no supports.
- All slices within build volume, correct P1S0.4/texturedPEI, effective G-code
  flow0.98/maxvol22/nozzle220/bed55 for the selected PLA. Native metadata
  includes per-nozzle arrays; use effective G-code settings when auditing.
- Bambu Send print job dialog OPEN for V38_final_shell_tree:634.49g/18h31m,
  P1S3DP-01P-994,navyA1/whiteA2,TimelapseOFF,AutoBedLevelingOFF verified.
  SEND NOT CLICKED. User already authorizes printing; only missing info is a
  completely clear build plate. Async question pending. Camera shows only part
  of low-positioned bed, so clearance could not be verified from it.
- Current send-dialog screenshot is700x688 with Send centre[631,644]. Refresh
  screenshot before acting. Prior V37 coordinate-mismatch rejection is historical;
  do not reuse old ungrounded coordinates.
- V37 shell G-code and V38_final_shell.gcode.3mf(normal supports) are superseded.
  Selected editable project:01_V38_shell_reviewed.3mf or tree_supports project.
- Physical prototype V28+V31 retention and feed/tear passed; new cover/outer
  screw positions not physically tested yet. Left electronics hardware fit is
  unverified; no left-bay final print released.
- Final PLA:PolyTerra CottonWhiteA2;Bambu NavyBlueA1. No V38 part dispatched.

## Confirmed (historical ledger follows)

- V28 integrated-top printer shell finished. Grey PLA ran out and the user
  continued with yellow; this shell is a mechanical prototype.
- V31 revised cradle and both retaining bars are now printed in yellow PLA.
  User reports the assembled fit is perfectly fine and provides a rear photo
  showing the printer seated and bars offered up. Screws are not installed in
  the visible holes; secured retention, outlet/LED alignment and functional
  feeding/cabling/service checks remain unconfirmed.
- User previously tested the printer in the intended upper-outlet orientation.

## Prepared, not physically completed

- V35 is the latest desktop-terminal study: display and surround at 25 degrees,
  saved in Fusion as `LUMON_v35_DESKTOP_TERMINAL_25DEG`. Printer side unchanged.
  See `output/v35_desktop_terminal/README.md`. Five joint screws and rear dowel
  remain; omit the former front dowel at y35,z118 for this angle. Current CAD
  references clear, but actual hardware remains unverified (buck gap 1.29 mm).
- V34 is the retained 14-degree exterior alternative, saved in Fusion as
  `LUMON_v34_SLOPED_CONNECTED_ROOF`. The user rejected V33's vertical display
  facade: preserve the original sloping face around the screen. V34 restores
  it and the original bezel, connects the flat roofs without a rounded valley
  at the seam, matches exposed front roof rounding and retains the common
  lower band. See `output/v34_sloped_connected_roof/README.md`.
- V33 unified-body study is geometry-checked and saved in Fusion as
  `LUMON_v33_UNIFIED_BODY_STUDY` in `lumon`. It shares the lower band and
  rounded front roof across both bays, recesses the tilted screen inside a
  common upright body, and moves the left lid joint behind the front brow.
  REJECTED by the user; retain only for reference. No new print is released/dispatched.
- V32 equal-height study is modelled and geometry-checked: both bays 201 mm
  tall, display centre 10 mm higher, bases on the same ground plane. See
  `output/v32_equal_height/README.md`. This is not a left-bay print release.
  User confirms they set older Fusion versions read-only and saved V32.
  Local STEP and previews are also saved. The previous save blocker is resolved.
- V31 revised cradle plus two retaining bars are sliced in Bambu Studio:
  3 h 6 m 28 s, 108.54 g PLA, 212 layers, one colour.
- Source/review: `output/v31_cradle_retention/README.md` and
  `output/v31_cradle_retention/slice_review.json`.
- Native project: `output/v31_cradle_retention/02_cradle_and_bars_reviewed.3mf`.
- Sliced plate: `output/v31_cradle_retention/02_cradle_and_bars_reviewed.gcode.3mf`.
- Fusion review saved as `LUMON_v31_CRADLE_RETENTION_REVIEW` in `lumon`.
- Inserts, bars, full printer installation, cable routing, paper feeding/cutting
  through this shell, and rear-service test are not confirmed complete.
- Right navy base and final shape refinements are not physically fitted.

## Next action

User authorizes test prints and confirms AMS slot 2 now contains yellow Generic
PLA. The send dialog maps PLA to A2; bed leveling and timelapse are off.
User clicked Send after CUA controls failed. Dispatch VERIFIED in Bambu Studio:
V31 cradle and retaining bars, 0/212 layers, heating bed to 55 C, estimated
finish 15:32. AMS A2 yellow Generic PLA; bed leveling and timelapse off.
Physical completion and fit remain unconfirmed.
Final enclosure prints wait for final filaments. Preserve these settings at launch.
If a different material/profile is selected, reslice and report any material
change to duration before dispatch.

After the kit finishes, guide the user through physical assembly one step at a
time. Do not ask them to manage Fusion, Bambu Studio, exports, or CAD files while
the assistant can do those steps. Retain the shell for mechanical checks; defer
the final-colour shell until fit and the revised appearance are approved.

The earlier Bambu app-control timeout is resolved. The project generator's
process-override metadata was corrected and the saved native settings and
exported G-code were verified.

Latest physical update: user reports V31 fit successful; photo is consistent
with lower capture bar at bottom and plain upper bar above. Hidden retaining
lip engagement cannot be established from this rear view. Next check is front
outlet/LED alignment with the printer fully seated, then secured/functional tests.

## V36 outlet correction from physical assembly

User confirms LED alignment acceptable and paper opening usable, requests opening
3 mm upward with revised cradle seated. Applied in V36 to V35 shell only:
90 x 14 mm aperture centre Z133.1 (previous130.1); LED/cradle unchanged.
Validated single-solid/watertight shell and opening clearance. STEP exported to
output/v36_outlet_alignment/whole_enclosure_review.step. Fusion import pending;
no new print. Current prototype remains usable for functional checks.

## V37 logo spacing and filament arrival

User reports final filaments arrived; brand/material/colour and loaded AMS slots
asked, not yet confirmed. V37 moves N right 0.3 mm, increasing O–N gap from
0.294 to 0.594 mm. Matching shell recess updated; V36 outlet correction preserved.
Shell and logo validated and exported; Fusion synchronization pending. No print.
Latest CAD: output/v37_logo_spacing/whole_enclosure_review.step.

## Confirmed assembly tests and final materials

User confirms BOTH secured retention and paper feed/tear through prototype pass.
PolyTerra Cotton White PLA is loaded in AMS slot 2, replacing yellow; existing
Bambu Navy Blue PLA remains in slot 1. These supersede earlier pending checks
and material questions. Rear withdrawal/roll service and rear cover remain
unconfirmed; left-bay hardware fit remains unverified. Final slicing preparation
is authorized; ask before dispatching a final print (standing instruction).

## Final shell slice ready; dispatch blocked

User explicitly authorizes proceeding, including final printing. V37 packed and
sliced in Bambu Studio using PolyTerra PLA @BBL X1C for A2 cotton white and
existing Bambu PLA Matte for A1 navy. 60924 seconds (16h55m24s),592.31g total:
589.79g white,2.51g navy;805 layers. Both colours only layers0–3;6 changes.
Support used; outside=false; standard bed-temperature metadata warning remains.
Send dialog verifies A1/A2 mapping, bed leveling/timelapse off. NOT dispatched:
automatic approval review rejected click due screenshot/coordinate mismatch.
Do not retry uncertain coordinates. Fusion V37 import also remains pending;
its native path dialog fails to resolve entered path. Local STEP correct.
Sliced file output/v37_logo_spacing/V37_final_shell.gcode.3mf.

## Rear closure review — hold final shell

User requests Fusion view and questions separate bars/cover and mismatch at
rounded rear outer corner. Source confirms V33 rounded shell but explicitly
retained square bars/cover. V37 shell slice is ON HOLD pending correction of
rear closure and mounting seating. Do not dispatch this stale slice.
Proposed final direction: one removable rear cover with integrated retaining
ribs and cradle capture; match exposed corner profile and check screw lands.

Fusion synchronization recovered: full V37 assembly imported and saved in lumon
as LUMON_v37_REAR_REVIEW. A second local inspection tab V37_REAR_INSPECTION is
open and visibly shows the rear with cover pulled out85mm and retaining bars
coloured navy for distinction. Inspection coordinates are rotated for viewing,
not print/assembly release; tab not cloud-saved. Current design flaws retained
for review, not presented as fixed. No rear geometry redesign performed yet.

## V38 rear closure redesign

User chooses straight rear shell edges and rounded removable panel. V38 built:
square rear lands, one rounded cover with integrated retaining ribs/capture,
four M3x14 screws with outer axes moved inward9.5mm, matching extended navybase.
Closed depth170.75mm (old170.5), cosmetic seam0.25, outerrear radius9.5.
Cradle/printer/front aperture/LED/logo unchanged. Geometry and removal/retention
checks pass. New cover does not use the old prototype's outer screw axes.
V37 sliced shell SUPERSEDED—do not send. V38 not yet sliced or printed.
Latest CAD: output/v38_integrated_rear/whole_enclosure_review.step.
