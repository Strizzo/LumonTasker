# V25 tapered printer bay — review, not print release

Source `cad/printer_bay_v25.py`. Supersedes v23 bay. **Current authorization (21 September): useful trial prints may proceed provided they finish with margin before 15:30. Verify the bed is clear between jobs. Later prints require renewed authorization.**

## Implemented

Approximate user-authorized60/40 taper: rear span175mm, front166mm over120mm depth; lower/switch face differs5.4mm, upper3.6mm. With reference rear bottomZ16/topZ191, front bottomZ21.4/topZ187.4. Two8mm-wide longitudinal bearing rails follow the lower slope. Original133mm side-guide gap is retained from the passed width sample. Contact lands and real casing curvature still need trial fitting; the approximation is not a scan.

Paper aperture90×14mm, centred on printer X82, not shell X79. CentreZ127.4 follows60mm below the new front topZ187.4; boundsX37..127,Z120.4..134.4. Original tested local60mm datum is retained, not the obsolete absolute height from the rectangular box. White integral front remains; logo below atZ57. Native buttons concealed with nominal front clearance; no external pushers.

Rocker23×16mm, nearest edges65mm from new front and16mm from nearest side, protrusion4.5mm. Left placement follows user's above-view description with FRONT at top of plan. Clearance channelX30.5..57.5, Y67 through rear, cuts both tray and shell floor. Its swept audit reserves2mm lateral and2mm additional depth beyond4.5mm protrusion. It is open-ended to avoid snagging during rear loading. Clear native casing pads carry load rather than rocker. Check side mapping in the top view before fabrication.

LED projected rectangle40×4.5mm, top2mm below front upper edge. Horizontal centring assumed from photographs. Separate hollow diffuser:0.8mm light-transmitting front wall, peripheral rim and rear bonding flange,0.2mm edge clearance to shell. Install from rear with small adhesive points on flange; no force or adhesive on native LED. Current material/transmission, native light angle and setback remain unverified. This is NOT a guarantee that matte light-grey PLA transmits enough blue light; translucent/white insert or thinner membrane can be substituted without reprinting the shell. Print flange-down; membrane bridges only2.9mm across the cavity. Buttons retain nominal1mm body-envelope clearance, but their actual projection is not modeled.

## Assembly

Heat-set bores remain tested4.2mm. Seat tray, slide printer from rear, route cables through lower rear relief, fit both retaining bars (fourM3×12), rear cover (fourM3×14), top (twoM3×8). Use gentle tightening and verify no bottoming. Remove rear cover and bars to withdraw intact printer for paper changes. Disconnect cables first. Body and rocker removal envelopes audited; cable plugs are not fully modeled because locations/bends remain unmeasured. Do not pull against connected cables.

## Limits and outputs

STEP, oriented STLs, registered shell/logo STLs, CAD renders, checks.json. Collision checks use an estimated tapered prism, not detailed hardware. Rear switch keepout is modeled conservatively along its path. Actual support contact, button noncontact, LED transmission and cable fit still require physical review. Full-device base/feet integration and left electronics fit remain unfinished. Print status is recorded below. Each remaining Bambu project requires successful slicing and review before dispatch.

## LED trial sliced in Bambu GUI

05_led_diffuser_trial.3mf imported and sliced successfully:10m08s total,7m13s preparation plus2m55s printing;0.61g model/material estimate,17 layers at0.2mm. Only filament2/light-grey Generic PLA used, no repeated colour changes. Trial is for checking current filament transmission before larger printing. Preview has no error. Sent at 12:51 on 21 September with user authorization; device confirmed active at 12:55. Completion is not yet confirmed.


## Cradle trial ready — not yet sent

`06_cradle_fit_only.3mf`: Bambu GUI estimate 1h23m, 48.85g / 16.38m, 100 layers, A2 light-grey PLA only. No colour swaps. Cradle plus both retaining bars would take 2h18m, so the bars were removed from this trial to leave margin before the meeting. Original combined project remains available. Await a clear bed after the LED trial before sending the cradle.

### Physical checks after cooling

- LED: hold the hollow rear toward the printer's blue LED. Check visibility from normal viewing distance without pressing either native button. No glue yet.
- Cradle: use the confirmed upper-half outlet orientation. Seat the printer gently on the two sloped rails. It should sit steadily without needing to wedge or force the housing between the guides.
- Check that the downward-facing rocker stays entirely inside the relief, with clearance in either switch position. The printer must not rest on the rocker. Check with power disconnected first.
- Slide the printer rearward out of the cradle; neither the switch nor the casing should catch. Check the cable route with the plugs attached, without bending them sharply.
- This trial checks the support geometry; the final shell, retaining bars, cover and electronics integration are not yet physically validated.


## Translucent PETG available — 21 September

User has translucent PETG. Preferred final LED diffuser is the existing separate insert printed in PETG and assembled into the PLA shell. Do not combine the materials as a bonded multi-material print. Existing light-grey PLA trial is still useful for geometry/fit. PETG brand/profile and loaded slot are not specified; do not send PETG using the current A2 PLA profile. Keep the recessed flange and noncontact cavity; verify optical transmission before final installation.


## Trial dispatch — 21 September, 13:06 local

User reports LED trial is fine and build plate is cleared. Cradle-only job sent to P1S using AMS A2 light-grey PLA. Auto Bed Leveling explicitly disabled at user request; timelapse off. Sliced estimate remains 1h23m, so expected finish around 14:30 with ample margin before 15:30 meeting. Device accepted job and began downloading; final device startup confirmation recorded in cradle_trial_slice.json.
