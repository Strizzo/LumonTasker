> SUPERSEDED: user rejected the detachable front. Use ../v20_integral_front/ for the current mechanical study.

# Front-output v20 mechanical study

This is a new printer-module study, not the completed styled enclosure or a released print job. Do not print the old v19 printer housing: its hardware dimensions are obsolete.

Confirmed inputs:
- User measured desktop body: 131 W × 175 D × 120 H mm.
- User successfully tested feed/cut with the native output face forward.
- Rotated body envelope: 131 W × 120 D × 175 H mm.
- Seam, bezel and insert coupons passed; retain 4.2mm insert bores.

The prototype keeps the existing 158mm right-module width and spine screw positions. It has a 201mm overall design height, 20mm taller than v19, so the complete enclosure silhouette is not yet resolved. The STEP uses local right-module coordinates; translate X by 218.96mm to inspect against the v19 left module. The printer reference is a rectangular measured envelope, not a model of its native face, lid or connectors.

Six separate solids: grey shell, cradle tray, tray stop, top cover, rear cover; dark front surround. The shell floor and walls are united. Tray, stop and covers remain removable. The full native face is exposed by the surround so a guessed small paper slot does not constrain the lid. The rear cable opening is open to the panel bottom. The mounting bracket using the printer's two native keyholes is not yet modeled: its hole spacing and offset have been requested. Without that bracket, the printer is not positively retained and this design is not ready to use.

All six solids are valid and watertight; pairwise intersections and intersections with the measured printer box have no volume overlap above 0.05mm³. This checks nominal geometry only. It does not verify real case curvature, lid sweep, buttons, cable bending, retention or sliced supports. Single-part STL orientations are normalized to the bed. Separate colors onto separate plates. No new job has been sent to the P1S.

Assembly and exploded PNGs visualize the mechanical layout only. The blank grey rectangle in the assembly image represents the purchased printer envelope. Cosmetic radii, logo placement, shared silhouette with the display module, and printer mounting bracket remain to be resolved before releasing a full print.

Rebuild: `.venv/bin/python cad/front_output_v20.py`.
