# V41 — glass in the white recessed seat

User clarification,24 September: no separate navy bezel and no lip over the glass. The glass already has the required black border and rounded shape.

This review candidate fills the old bezel pocket into the cotton-white sloped front and removes the separate display_bezel component. The visible screen border is the glass itself. The accepted193.4×111.4 mm,R8.2 pocket contour is retained. Candidate glass face is1 mm behind the white front plane, with a shallow shoulder behind its perimeter. Even the1.1 mm glass reference has0.4 mm axial clearance to that shoulder: the rear metal lugs retain the display without clamping the glass. A compliant pad can be considered if the physical stack needs it; none is assumed installed.

The four printed V40 bracket shapes are unchanged. Glass and bracket/anchor planes move2 mm rearwards together, preserving their relative stack and screw engagement. Install the display into the seat from the front and fasten the brackets from the rear. Removal reverses that sequence; the rear shoulder prevents extracting the complete glass through the smaller rear opening. Actual rear bracket fit is still awaiting confirmation.

The body is a single valid watertight solid. Checked body/component pairs and nominal glass/chassis/Pi references do not intersect. The Pi clearance allowance also passes. The provisional20 mm rear cable volume still overlaps the body/divider by237.48 mm³; this remains an explicit full-enclosure release hold along with real power/cable layout, mounting fit and slicer/orientation checks. This is not a production print release.

- whole_enclosure_review.step: actual candidate assembly, no separate display bezel.
- whole_enclosure_with_hardware.step: same plus nominal hardware references.
- recessed_glass_front.png: actual CAD view; black border belongs to the glass.
- audit.json: exact checks, dimensions and outstanding limits.

No print dispatched and Fusion intentionally left closed/latest savedV39.

Front service check24 September: exact translational sweeps of nominal unplugged glass, chassis and attached Pi pass with the four rear brackets removed. See front_service_audit.json. This does not verify real cable routing or the unconfirmed bracket seating.
