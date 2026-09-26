# Next shell revision — physical feedback, 23 September 2026

## Exposed unused insert hole — 26 September feedback

Remove the unused screw-insert bore exposed on the printer-bay edge beside
the display glass in the user's photo:
`/tmp/codex-remote-attachments/01a0bf3e-2220-7252-adef-d07f9ff37b1f/491BE101-4384-473F-91DF-DCE7AA8ACD06/1-Foto-1.jpg`.
The next revision should have a continuous finished surface there. Identify
the exact source feature against this photo before modifying CAD; remove any
corresponding unused mating bore, while preserving the other functioning
inter-bay joints and display mounts. This is future-revision feedback, not
a request to reprint or alter the currently printing inlet panel.

User accepts the current V39 shell and confirms the existing V31 cradle and printer fit perfectly inside it. Do not reprint this shell now. User authorizes the next piece (the compatible V39 rear cover) and confirms the build plate is clear.

The lower light-coloured band is recessed 0.8 mm on the exterior, Z9–33 mm. This is deliberate styling geometry inherited from V33 and retained through V39, not evidence of filament shrinkage. With the shell printed front-face down, the recessed front strip needs support; user photographs show the navy support interface still present in the first photo and the stepped side outline in the second.

For the next shell revision, make this light-coloured lower band flush with the main exterior on front and sides. Preserve the tested inner floor, cradle datums, switch/cable relief, insert positions and retention interfaces. Coordinate the matching rear-cover lower band and display-bay exterior so the assembly remains cohesive. Keep the separate navy foot as a separate design decision; do not silently remove its base functions. Review the revised print orientation and support preview to eliminate this unnecessary exterior support strip.

Source anchors: build_v33_unified_body.py BAND_INSET=.8; V38 rear cap repeats the .8 mm lower band; V39 retains the printer-side geometry. No geometry or current prepared slice has been changed by this note.

## Weight reduction — additional user feedback

User reports that the shell feels too heavy and asks for a better balance of robustness and filament use. Treat this as a design requirement for the next shell revision and a reason to review the remaining unprinted parts before release. The already printed shell is accepted; do not scrap it. The rear cover is already printing and was not stopped or modified.

Evidence from the actual V39 shell G-code (see weight_audit.json): 4 wall loops, 5 top / 5 bottom layers, 15% gyroid. Slicer model mass approximately 593.16 g; total with support/purge/tower 634.49 g. Summed XY deposition by feature gives 415.39 g of inner+outer wall paths, 72.52 g sparse infill, 54.42 g internal solid infill, 39.54 g support/interface. These are toolpath estimates, not a physical weighing. The feature sums match the slicer total after excluding stationary purge. Existing CAD includes 3 mm front/outer wall, 4 mm roof/floor, a continuous 9 mm inter-bay wall, and thick rear mounting rails.

Reducing sparse infill from15% to10% would, under a simple proportional estimate, save only about24 g on this shell (approximately4% of model mass); actual reslicing is required. Geometry and perimeter allocation offer the larger opportunity. The unprinted display body has only23.26 g of sparse infill in612.70 g total, making infill-only changes particularly ineffective there.

Candidate design, requiring slicing and physical stiffness/retention checks before release:
- Broad non-load-bearing skins: start at2.4 mm; preserve overall outside dimensions and tested internal bearing/locating datums. Expand selected cavities to thin panels without moving the printer, cradle or screw axes. Use short local ribs where large panels flex.
- Inter-bay wall and full-height rear rails: replace excess bulk with a thinner web plus local mounting bosses/gussets. Preserve the complete insert engagement depth and surrounding material at each screw. Do not merely change the9 mm wall globally, since it locates and joins the bays.
- Printer-bearing floor: preserve cradle seats and load paths; consider pockets between them rather than blanket thinning.
- Initial slicer candidate:3 wall loops,4 top/bottom layers,8–10% gyroid in remaining thick regions. Keep local reinforcement around inserts, inter-bay joints and retaining contacts. Thin skins may remain effectively solid; fewer loops alone is not a guaranteed mass saving.
- Unprinted navy feet: investigate a ribbed underside retaining the existing outer appearance, bearing/bonding pads, cable/switch openings and rear-cover clearance. Review the unprinted display body/roof before using current heavyweight slices.
- Coordinate with the flush lower-band correction. Keep the current V39 cover compatible with the accepted shell; future matching pieces must be versioned separately.

Before any revised print: compare model/support mass and time against V39 in Bambu; inspect unsupported roofs, panel skins and reinforced fasteners. Validate with a representative panel/corner sample using the actual filament and orientation if needed. Do not claim a final percentage saving or validated strength until those checks are complete. No revised lightweight CAD or G-code has yet been released.

## Closed navy underside — 24 September feedback

The V42 lean slice of the original V39 navy base is printed and the user confirms it fits; they will glue it later. Keep this accepted part. For the next base revision, the user prefers a closed flat underside instead of openings copying the shell-floor reliefs. This supersedes the open/ribbed underside suggestion above.

V30 and V38 conservatively extended rocker and cable service volumes through the complete base to ground level. A matching through-cut below every shell-floor aperture is not intrinsically required. Develop a thin continuous bottom skin below internal clearance recesses, with necessary rear/side exits, rather than filling the base solid. Verify rocker clearance in both positions, plugs/cable bends and rear insertion/removal against actual hardware; the old ground-reaching keepout boxes do not establish the minimum physical clearance. Preserve the accepted outer fit and adhesive lands and review weight/time after slicing. No closed-floor geometry or print is released yet.
