# Support and indicator revision

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


## Translucent PETG available — 21 September

User has translucent PETG. Preferred final LED diffuser is the existing separate insert printed in PETG and assembled into the PLA shell. Do not combine the materials as a bonded multi-material print. Existing light-grey PLA trial is still useful for geometry/fit. PETG brand/profile and loaded slot are not specified; do not send PETG using the current A2 PLA profile. Keep the recessed flange and noncontact cavity; verify optical transmission before final installation.


## V26: lateral taper correction

User confirms final front/outlet width132mm and rear/cable-face width143mm; switch remains underneath. V25 constant-width cradle invalid. Revised source cad/printer_bay_v26.py and output/v26_double_taper_printer accommodate both tapers, with provisional symmetric lateral split. Cradle guide gaps134/145mm; bay width175mm. Geometry audits pass for estimated envelope. Replacement cradle project prepared but not sliced/sent. Full shell remains pending physical fit and full-device integration.


## V27 physical-fit acceptance and refinement

V26 mostly fits; user waives repeat cradle trial. Increase bottom support rise5.4 to8.1mm, reduce total lateral gap0.6mm. Aperture/LED front datum rises2.7mm while retaining166mm front span. Updated CAD audits pass; final cradle included with assembly parts. Shell native supported project sliced8h49m/335.77g/six filament changes,not sent. Remaining parts prepared but not sliced. See output/v27_refined_printer/README.md; native Bambu settings must be verified because imported packer settings were not fully honored.


## V28 integrated top — user-requested cancellation

V27 shell cancelled at layer1/805. V28 merges4mm top into shell, removes both top fasteners and insert bores, retains201mm external height and rear extraction. Front-down orientation prints top as upright wall; separate cover was not required for printability. Geometry audits pass; no replacement dispatched. Bed must be cleared after cooling. See output/v28_integrated_top.
