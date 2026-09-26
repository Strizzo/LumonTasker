# Receipt-printer identification and orientation review

User product link: https://amzn.eu/d/0i2RsHIF
Resolved listing: https://www.amazon.it/dp/B0CNYYWVCS
Read 20 September 2026. Listing brand Sunydog, model POS 8370, black & grey, USB+LAN, 80mm thermal receipt printer with automatic cutter. Listing explicitly advertises wall mounting with two underside hanging holes. User photo 3 confirms two keyhole mounts and a recessed cable bay with connected power and USB.

User subsequently supplied physical dimensions: width 13.1cm, depth 17.5cm, height 12cm. Use 131mm W × 175mm D × 120mm H in the normal desktop orientation. These supersede the listing axis labels and inherited CAD dimensions (142 × 122 × 122mm). External plug/cable clearance and lid sweep are additional to this body envelope.

For the proposed 90-degree rotation about the left/right axis, the body envelope becomes 131mm W × 120mm D × 175mm H. This is a body-envelope transform only, not final enclosure dimensions. The old 55mm vertical plinth budget must be reconsidered; do not reuse it blindly with the taller rotated printer.

## Confirmed orientation and service choice

User confirmed feeding and cutting work with the printer rotated for front output. User prefers a robust integral enclosure front and accepts removing the whole printer to change paper. Native casing, cutter and lid remain intact. The original detachable-front proposal is superseded.

## Rear-loading mounting decision

Native keyholes: 61mm centre-to-centre, larger-hole centre line 132mm from the original rear/cable edge. These are recorded but not used for the current cradle mounting. No corner-radius measurement is needed.

Active source is `printer_bay_v23.py`. A removable tray and side guides allow nominal 1mm lateral clearance to the full measured rectangular body. Two screw-fastened retaining bars have nominal 0.5mm rear clearance. Front clearance is 1mm. Optional removable shims can take up play after trial fitting; do not rely on an interference fit. Contact-pad positions and actual cable bends still need physical confirmation.

Selected orientation puts native buttons above and original rear/cable edge below. The integral front exposes a 127 × 88mm upper opening for controls and output; exact outlet/control positions are not measured. The printer is represented in CAD by its measured box envelope, not a detailed model. Keep the native cutter unobstructed and verify the output path during the prototype trial.

Paper replacement: disconnect cables, remove enclosure rear cover and two retaining bars, slide the complete printer out, then open its native lid. CAD rear-removal sweep is clear with the top fitted; native lid movement inside the enclosure is not required for this service method.

See `output/v23_upper_output/README.md` for assembly, fasteners and prepared plates. Mesh and nominal collision checks pass. Slicer/preview checks remain blocked by unavailable Bambu UI and command-line crashes; no new print is released or sent. Overall display-side hardware fit and final cosmetic integration remain unfinished.

21 September update: user corrected outlet position to upper half. V23 relocates front opening and logo, and provides lower floor/tray/rear cable relief. The outlet is now measured at 90 × 14mm, centred horizontally and 56mm from upper edge (distance datum pending); connector positions still require physical confirmation; upper-output feed/cut test is already confirmed. Print hold remains in force.

21 September measurement correction: upper-output operation is already tested. Outlet 90mm wide × 14mm high, horizontally centred; 56mm from upper edge, with upper-edge/centre datum clarification pending. Plug measurements supplied: power 15mm, square USB 12mm. Small fit samples prepared in `cad/output/v24_printer_fit`; broad v23 front aperture remains provisional and has NOT yet been replaced by an unvalidated narrow slit. No print dispatch.

Confirmed 21 September: 56mm is to outlet VERTICAL CENTRE; upper/lower edges 49/63mm below printer top. V24 centre-version samples sliced 45m42s, 15.37g, A2 only. User conditionally authorized this sample plate before 11:30 if under an hour; full-case hold remains.

## Physical sample result, 21 September 2026

User confirms cradle fit is fine; retain 133mm guide gap. Printed centre-56mm template fits acceptably, but moving its opening DOWN 4mm aligns it perfectly: use centre 60mm below printer upper edge, edges 53/67mm below top, unchanged 90 × 14mm size. This supersedes the earlier 56mm value. No repeat sample print requested or sent. Corrected reference geometry is in `cad/output/v24_printer_fit_refined`; preserve this printed job as history. Paper feed/cut through template was not explicitly reported, so do not mark that test passed.

For the current v23 body placement (X16.5..147.5, Z16..191), the fitted outlet rectangle maps to X37..127 and Z124..138, centre X82/Z131. This is centred on the printer, not shell X79. The v23 broad opening remains provisional; carry these coordinates into the detailed front while resolving button access.

## Hardware correction: tapered casing, downward rocker and LED

User photos, 21 September 2026, show original front/rear walls are not parallel. In the chosen orientation these become upper/lower faces. The prior 131 × 120 × 175mm reference remains only a maximum envelope; it cannot validate support contact, printer tilt or actual outlet alignment when installed. The width coupon passed, not the full cradle. Do not print the full v23 tray/shell as a validated mount.

Original rear power rocker becomes downward-facing. Provide a clearance pocket or through-opening in BOTH tray and any shell floor beneath it, including both switch positions, assembly tolerances and insertion/removal path. The table or eventual foot/base structure must not reach the rocker through that opening. Switch width/height, position and protrusion are pending; no precise hole is guessed from photographs. Define structural support pads on verified casing lands clear of switch and connectors; shim/pad heights may differ to keep the paper-output face aligned. Retainers must secure without wedging tapered casing or loading buttons/lid.

User does not require external feed/lid-release button access; those become available after removing the intact printer for paper service. Conceal with internal noncontact clearance, not a wall resting on controls. LED should remain visible. Preferred proposal: a small separate translucent/off-white insert, supported by a concealed shoulder in the shell, with a light-collection cavity accommodating the sloped native face. Do not claim a fixed matte-PLA wall thickness will transmit enough light; test an optical sample with the actual filament. No direct loading of the native LED lens. Exact LED position and angle pending.

Required measurements: rocker outline, protrusion in both positions and distances to two adjacent edges; original front-to-rear length at lid and bottom (taper); LED outline and centre relative to upper edge in chosen orientation. Photographs establish features but not precise dimensions. The fitted outlet centre remains 60mm from printer top, but its absolute CAD height depends on corrected support placement. No printing authorized for this redesign.

## Additional measurements — 21 September

Original top length 166mm becomes front vertical span; original bottom length175mm becomes rear vertical span. Difference9mm over approximately120mm new front/back depth. This constrains overall taper but does not establish how the9mm is divided between upper and lower faces. Do not assume a9mm wedge under the printer or move the fitted outlet until support pose is determined. Keep175mm as conservative height envelope.

Downward switch outline23×16mm; distance65mm from original top/new front edge and16mm from closest side edge. Edge-versus-centre datum, side in installed coordinates and protrusion remain unconfirmed. Store measurements without silently locating a precision hole. Prefer open relief beneath rocker with support lands outside its full travel; table/base and insertion path clearance still required. No print sent.

## Confirmed rocker clearance

User confirms offsets65mm from new front and16mm from nearest side are to NEAREST EDGES. Rocker protrudes4.5mm. With provisional23mm across-width and16mm front/back axis assignment, rocker spans65–81mm from front and16–39mm from nearest side. Proposed relief27×20mm gives2mm margin on each side:63–83mm from front,14–41mm from nearest side. Reserve at least6.5mm free depth normal to the casing (4.5mm rocker +2mm margin), in both switch positions. These are design allowances, not a validated installed cutout.

Any tray/floor/base structure must clear this volume. A closed pocket under the final position alone is insufficient if the downward rocker crosses solid supports while sliding in; use an open insertion channel or a removable support arrangement. Resolve actual taper/support pose and transverse-side mapping before committing support geometry. No print sent.

Active revision: v25_tapered_printer, source printer_bay_v25.py. User-authorized60/40 taper implemented with bearing rails, rear-open switch channel, fitted90×14 paper slot and separate hollow0.8mm LED insert. LED40×4.5 projected, upper edge2mm down (interpretation); switch mapped left in top plan with FRONT at top. See v25 README for assumptions and checks. Printing requires explicit user confirmation.
