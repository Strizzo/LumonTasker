# Full-case print preparation

**USER HOLD: prepare only. Do not send or start any print until the user authorizes printing again (20 September 2026).**

Fit coupons passed: shell seam, bezel corner and heat-set insert fit. Keep 4.2mm insert bores. Physical AMS: A2 light-grey Generic PLA, A1 dark Bambu PLA Matte. Separate independent colours onto separate plates; multicolour only for a part requiring both colours.

## Active printer bay

Current source: `printer_bay_v23.py`; instructions and prepared projects: `output/v23_upper_output/README.md`. Supersedes all v19 right-shell, trim, rear and foot parts and v20/v21/v22 printer studies. Do not print those older right-module files.

V23 uses a rear-loading guided cradle, two retaining bars and an integral front with a flush logo. User measurements are 131 W × 175 D × 120 H mm in desktop orientation; rotated envelope is 131 W × 120 D × 175 H. Front-output feeding/cutting is user-confirmed. Native keyhole measurements are recorded but unnecessary to this mounting method; no corner-radius measurement is required.

CAD checks pass for solids, watertight meshes, nominal collisions and rear-removal envelope. Four proposed plate projects are saved, but Bambu import/slicing/preview are not verified. No new print has been sent. Slicer CLI crashes on the previously printed project too; native UI currently inaccessible. The next action is successful GUI import and slice, overhang/bed/filament checks, then await renewed user authorization before printing the printer-bay prototype.

## Remaining full-device work

The combined context study exposes a 20mm rise in printer-bay height compared with the display housing. Complete final cosmetic integration and right plinth/feet before releasing the entire device. The printer opening, cable routing and contact pads need physical trial. Paper changes require removing the printer through the rear; native lid sweep inside the enclosure is therefore unnecessary.

The v19 left tub, bezel, display retainer, top, rear and left foot remain review parts. Confirm real display mounting/thickness/active area, Pi/cooler envelope and power/cable layout before printing the whole left module. Do not describe hardware-reference boxes as verified installed components.

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

21 September12:51: user authorizes useful prints until15:30, meeting15:30–16:00. Must finish with margin before15:30; do not launch a job likely to overlap. LED trial sent usingA2. Between jobs, verify plate cleared before sending; no automatic stacked jobs. This time-limited authorization supersedes earlier ask-before-every-print instruction only within this window.


## V26: lateral taper correction

User confirms final front/outlet width132mm and rear/cable-face width143mm; switch remains underneath. V25 constant-width cradle invalid. Revised source cad/printer_bay_v26.py and output/v26_double_taper_printer accommodate both tapers, with provisional symmetric lateral split. Cradle guide gaps134/145mm; bay width175mm. Geometry audits pass for estimated envelope. Replacement cradle project prepared but not sliced/sent. Full shell remains pending physical fit and full-device integration.


## V27 physical-fit acceptance and refinement

V26 mostly fits; user waives repeat cradle trial. Increase bottom support rise5.4 to8.1mm, reduce total lateral gap0.6mm. Aperture/LED front datum rises2.7mm while retaining166mm front span. Updated CAD audits pass; final cradle included with assembly parts. Shell native supported project sliced8h49m/335.77g/six filament changes,not sent. Remaining parts prepared but not sliced. See output/v27_refined_printer/README.md; native Bambu settings must be verified because imported packer settings were not fully honored.


## V28 integrated top — user-requested cancellation

V27 shell cancelled at layer1/805. V28 merges4mm top into shell, removes both top fasteners and insert bores, retains201mm external height and rear extraction. Front-down orientation prints top as upright wall; separate cover was not required for printability. Geometry audits pass; no replacement dispatched. Bed must be cleared after cooling. See output/v28_integrated_top.
