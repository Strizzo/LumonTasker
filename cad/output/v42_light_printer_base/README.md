# V42 — lighter printer-base print

## Selected and dispatched

**02_V42_printer_base_lean.3mf / .gcode.3mf** uses the original V39 base shape with3 walls,4 top/bottom layers,10% gyroid and0.2 mm layers. Single navy PLA fromAMS A1, no supports or colour swaps. Outer shape, original bonding pads, switch/cable channels and fit to the accepted printer shell are unchanged.

Started24 September00:57 local. On24 September morning the user reports completion and P1S3DP-01P-994 shows matching job V42_Navy_Printer_Base_Lean Finished,100%,45/45 layers. Estimated2h05m09s,75.89 g; actual finish time not retrieved. Bed leveling/timelapse off. User subsequently confirms the base fits and will glue it later; bonding remains undone. The plate was cleared and V46 display-seat test dispatched at10:39; see that job's record for the latest print state.

| Slice | Material | Time |
|---|---:|---:|
| Original V39 settings |97.50 g|2h48m01s|
| New pocketed CAD, lean settings |89.01 g|2h38m37s|
| **Selected original shape, lean settings** |**75.89 g**|**2h05m09s**|

The selected slice saves21.61 g (22.2%) and42m52s relative to V39. Pockets reduce CAD volume by29.6% but create extra perimeter paths, so they lose the actual print comparison. Do not print01_V42_light_printer_base: it is the rejected pocketed candidate. The internal plate/object names in the selected archive still mention COMPARE_ONLY because that comparison won; the dispatch job was explicitly renamed.

The current whole_enclosure_review.step copies the V41 recessed-glass candidate with the ORIGINAL printer base. whole_enclosure_pocketed_candidate.step and printer_base_local.step/printer_base_print.stl document the unselected pocket experiment. Fusion remains closed/latest savedV39.

## After printing

Dry-fit the base under the accepted printer shell. Its large rear openings must line up with the switch/cable channels and it should sit flat. Keep it unbonded until rear-cover installation and the combined-bay fit are checked. The shallow original adhesive beds remain available for final bonding; no new mounting screws or shell drilling are required.

## Underside feedback — 24 September

The user accepts the printed base's fit but prefers a closed flat bottom. V30 cut conservative rocker, rear-cable and inter-bay clearance volumes completely through the 9 mm base; V38 retained this approach in the longer base used by V39/V42. These are service-clearance openings, not ventilation requirements or a structural need to duplicate every shell-floor aperture.

For the next revision, design a thin continuous underside below internal recesses/channels, with only required rear/side cable exits and service access. Do not fill the channels solid. Check the actual rocker positions, plugged-in cables and rear extraction sweep against the proposed bottom skin rather than treating the old ground-reaching clearance boxes as measured hardware. Closed-floor clearance is not yet validated; no replacement geometry or print has been released. Keep the accepted printed base, with bonding deferred as the user plans.

## Historical V41 display progress (superseded by V45/V46)

V41 exact nominal front-extraction sweeps for glass/chassis/attached Pi passed with rear brackets removed. White recessed seat and visible glass border retained, no navy bezel. Four rear bracket seating and power hardware/layout still need confirmation. The broad cable keepout clashes with an inherited internal-PSU divider, so it has not been silently waived. User asked whether to retain existing external power adapters; answer pending. No display-body print released.
