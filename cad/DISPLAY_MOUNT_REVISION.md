# Display mounting revision — actual hardware photos, 23 September 2026

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
- New prints not dispatched; fresh plate-clear confirmation is still needed.
  CAD: output/v49_measured_display_depth. Fusion stays savedV39; not synced.
- Earlier2.5 mm maximum-thread-depth claim is not explicitly verified in the
  manufacturer drawing. Do not force a screw that stops before its head seats.
- Full display case still needs cable/power and full-body print/access review.

**Latest width change, 24 September: V45 uses a 3 mm bearing ledge.** The user
requested the wider seat and confirms the black band stays clear of the outer
3 mm rear glass border. The whole ledge remains 2.3 mm thick; 0.8 mm glass,
1 mm front recess, accepted outer opening, and four integral retention arms
remain unchanged. No band notch is needed. V44's 2 mm width below is history.
The nominal chassis is only 0.35 mm away from the wider seat at its lower edge;
the actual seating and metal mount stack still require the physical trial.
See output/v45_display_seat_3mm. Full-case release and Fusion sync remain pending.

**Latest correction, 24 September: the user's recessed seat is load-bearing.**
The glass must rest on its rear perimeter and be stopped from moving inward
without screws. Four screws through integral case arms into the metal lugs
prevent front withdrawal. V41/V43's deliberate gap under the glass was incorrect
for this request. V44 supersedes that load path; historical proposals below are
retained as history, not current instructions.

V44 provides a 2 mm bearing width and keeps the accepted glass opening and 1 mm
recess. The user now measures mostly 0.8 mm glass, and 1.3 mm at a local black
band (possibly a data connection, not identified). The measured baseline seat
is y1.8; historical 0.7 and 1.1 mm variants remain references. The user confirms
the band does not reach the outermost 2 mm rear bearing border, so no seat relief
is needed. The 2 mm dimension is the inward support width, not soft padding
thickness. Glass_0p8 is the selected seat. An interior envelope conservatively
checks band clearance without inventing its exact location or identity. This
does not release the full case for printing. The seat and four rear metal-lug lands must match
the freely seated assembly simultaneously. Check for printing tolerances/high
spots and correct any rear lug gap with measured rigid shims or revised pads;
never use the screws to pull the glass across that gap. No bedding layer is
assumed; any later bedding thickness must be included in the mounting stack.
The old V40 contour test does not validate this new bearing seat. See
output/v44_bearing_seat/README.md and per-variant audits. Fusion and printing
are unchanged by this revision.

The photos show a Pi already attached to the display controller standoffs, four unused outer mounting lugs on the metal back, a thin glass overhang, an orange flex and a DSI cable. Treat the display and Pi as one serviceable assembly. The loose wires were unplugged accidentally; the user confirms no physical pins/connector were reported broken. Their original pin mapping has not been verified, so do not infer connections from wire colours alone.

## Why the V39 display-side mount must change

The inherited CAD represents the display as a192.96×110.76×21 mm box. Its21 mm depth is explicitly a placeholder. The generic4 mm thick rear retainer sits21 mm behind the inner front panel, with long side ribs. Pi references and mounts are separate on the enclosure wall. Photo evidence makes those representations incomplete for this assembled hardware. Previous placeholder collision checks do not establish clearance for the attached Pi or plugs.

## Selected mounting direction

Keep the25-degree sloping face. The latest user requirement removes the separate navy surround and uses the glass border in an integral white recessed seat. Use the four OUTER threaded lugs in the display's metal chassis, on a lightweight removable carrier or local brackets. The official drawing labels these M3, nominal126.2×65.6 mm pitch. Do not confuse them with the inner M2.5 controller/Pi mounting pattern58×49 mm. Verify the hardware variant and fastener engagement before selecting screw length.

Locate the glass within a shallow opening with clearance. A soft anti-rattle gasket can be added, but mounting screws must seat against properly sized rigid spacers/bearing pads, never pull the glass tightly against a rigid lip. The original corner coupon is useful for contour/clearance comparison only and cannot validate the entire mounting stack.

The manufacturer enclosure whitepaper documents0.7 and1.1 mm glass variants with the same front-to-rear-mount datum, and warns that hard contact against the glass during tightening can detach or crack it. A lipless glass opening supported from the metal rear mount is the preferred starting point here; retain the option of soft pads after actual stack measurement. Do not glue only the glass corners. The guide also permits an appropriately designed perimeter tape mount as an alternative; we prefer screw-removable retention for this build.

Use the lighter enclosure design direction: broad skins around2.4 mm initially, with reinforcement local to the carrier mounts. Remove unused separate Pi mounts and bulky generic display ribs only when the new full assembly is represented. Check PSU/divider/buck clearances, airflow, ribbon bends, GPIO jumpers, USB/printer cable, power plug and SD access. No final electrical or thermal layout is implied by this mechanical proposal.

## Confirmed glass outline and provisional corner radius

User measured the glass as **193 × 111 mm** on 23 September, consistent with the nominal 192.96 × 110.76 mm reference. The official drawing shows rounded corners but does not dimension their radius. Scaling its vector outline gives tangent offsets of approximately 7.9 mm; use **R8 provisionally**, not as a manufacturer-certified dimension. Reproducible values are saved in references/display_glass_corner_inference.json. Provide perimeter clearance/corner relief and verify a small fit sample so a minor corner variation cannot load the glass. No additional manual radius measurement is required at this stage. These are reference data and mounting requirements; production CAD has not yet been revised.

## Depth confirmed and V40 fit test

The user confirms **40 mm** total depth with the Pi attached. The user also explicitly requests a precise visual fit. V40 targets a 193.4 × 111.4 mm opening: 0.2 mm clearance per side, provisional R8.2 opening around an R8 glass contour. The rear metal lugs carry the assembly. The glass sits 1 mm behind the navy frame's face; it is not squeezed against a rigid lip.

A small full-outline frame and four brackets have been generated and independently checked in output/v40_display_mount/fit_audit.json. This fit-kit release is separate from the full-enclosure audit: the provisional rear cable allowance overlaps the inherited divider by 188.72 mm³. Do not erase or waive that full-enclosure check. Resolve actual cable routing/power layout before printing the large left body. The nominal 126.2 × 65.65 mm outer M3 lug pattern and glass-to-lug plane must be physically checked using the kit. The earlier 65.6 mm pitch was a rounded reading; the drawing says65.65.

Fusion remains closed at the user's request after Mac performance problems. V40 is not yet synchronized there. The separate fit-kit STEP and mesh files are local and reviewable; keep V39 Fusion clearly distinguished.

Existing V39 display-side projects are review-only and are not released for printing under these new facts. Current printer shell remains accepted. The rear cover was verified finished at231/231 layers before the V40 fit kit was dispatched at21:39 local; both physical checks remain pending.

Sources: see display_hardware.json. The unchanged official drawing is saved at references/original_touch_display_mechanical.pdf.

## Physical contour accepted; integral recessed seat — 24 September

The user reports the V40 frame fits perfectly and shows it around the glass. Preserve the printed193.4×111.4 mm,R8.2 pocket contour. This confirms the practical opening, not the precise glass radius, rear bracket fit, or final retention stack. Rear-bracket clarification is pending.

The user explicitly clarified that there should be **no final navy bezel and no navy lip**. The existing black glass border is the visible surround. The intended geometry is an integral recessed seat in the white sloped panel, with a step behind the glass, not a separate piece overlapping its front. The assistant's earlier interpretation about restoring the original6 mm front overlap was incorrect and must not be implemented.

V41 retains the accepted outline and unchanged V40 bracket shapes, moving the glass and complete relative mounting stack rearward together to recess the glass below the white panel. Fill the old bezel rebate flush with the white face, remove the separate bezel component, and keep the glass free of rigid clamping pressure. Actual body/recess fit and cable/power clearances still require review before a large print.

## Four integral mounts — latest user direction,24 September

V43 merges the four arms into the case and closes the obsolete case-side screw/insert holes. Front-insert the unplugged display and attached Pi; four rear M3×6 screws fasten into the original metal lugs. The integral mounts remain during front removal. Exact nominal swept-envelope checks now include those fixed arms and pass; the earlier V41 check removed the detachable brackets. Existing V40 test pieces are still useful for measuring the same mounting pattern and bearing depth. The final assembly will not need them as loose parts.

Four bearing pads retain3.9 mm thickness and nominal2.1 mm screw engagement. The large case print may need local support beneath integral arms; slicing and real screwdriver/cable access remain to be checked. Unconfirmed actual power architecture and the237.48 mm³ cable/divider clash still hold full-case release. No new print dispatched; Fusion remainsV39.
