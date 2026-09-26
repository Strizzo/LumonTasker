# V44 — glass-bearing recessed seat

The user clarified the load path: the glass must rest on a step within the white
front panel and be unable to move inward even before screws are installed. Four
rear screws into the display's metal lugs prevent withdrawal through the front.
The four supports remain integral with the case. There is no separate bezel and
no lip overlapping the front of the glass.

V41/V43 did **not** implement this: their shoulder was 0.4–0.8 mm behind the glass,
and the metal lugs carried inward loads. V44 replaces that clearance with a
continuous 2 mm bearing width under the glass's rear border. The previously
accepted 193.4 × 111.4 mm, R8.2 opening and 1 mm front recess are preserved.

## Selected measured glass seat

The user subsequently measured mostly **0.8 mm glass**, and **1.3 mm total** at
a local black band, possibly a data connection. Use 0.8 mm as the working glass
thickness. The local feature is approximately 0.5 mm thicker. The user confirms
it does **not** reach the outermost 2 mm of the rear glass border, so no notch is
needed in the supporting ledge. Exact band identity and position remain unknown;
do not interpret the confirmation as a detailed model of the flex or its route.

The `glass_0p8` seat is selected. Its **2 mm** dimension is the bearing width
extending inward beneath the glass border, not padding thickness. The integral
rigid ledge is 2.3 mm thick; the glass front recess is 1 mm. No soft gasket or
front overlap is included. The 0.7 and 1.1 mm variants are historical nominal
references from the official Raspberry Pi enclosure guide; they are not the
selected hardware. All share a nominal glass-front-to-metal-lug datum.

| Folder | Glass assumption | Glass front | Bearing seat | Rear lug plane |
| --- | --- | --- | --- | --- |
| glass_0p8 | 0.8 mm measured baseline | y=1.0 | y=1.8 | y=6.96 |
| glass_0p7 | 0.7 mm | y=1.0 | y=1.7 | y=6.96 |
| glass_1p1 | 1.1 mm | y=1.0 | y=2.1 | y=6.96 |

Coordinates are in the display's local frame, positive y inward. Each variant
has a STEP body, whole assembly, assembly with nominal hardware, STL and audit.
STLs are assembly-oriented CAD exports, not sliced or approved print jobs.
`variants.json` selects `glass_0p8` for the seat geometry. Full-case release still
requires the physical mounting stack and other outstanding checks. Reproduce it
with:

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python cad/review/build_v44_bearing_seat.py --glass-mm 0.8 --measured --local-band-total-mm 1.3 --band-clear-of-seat
```

## Mechanical checks and limits

The generator checks each variant for a valid single body and watertight mesh,
nominal hardware clearances, four retention holes/head recesses, and exact front
insertion sweeps with the integral supports left in place. It checks glass
contact along all four sides and the complete nominal bearing ring. A 0.05 mm
inward displacement of the glass alone collides with the seat; a 0.05 mm outward
displacement is clear. This verifies geometric stopping, not structural strength.
For the band, a separate conservative envelope covers the entire glass area
inset by 2 mm, from the glass back to the band's reported back plus 0.3 mm
rearward clearance. Both its seated position and front-insertion sweep are
checked against the case components. This does not model the band's exact shape.

In the nominal CAD, the glass rests on the seat while all four metal lugs touch
their support lands. Tightening must not pull the display across a gap. Actual
lug positions/depth and FDM tolerances still need a physical check. Inspect the
bearing surface for high spots or warping. If there is a rear lug gap, correct it
with measured rigid shims or revised pad depths and recalculate screw engagement;
do not tighten the screws to force the glass into position. No gasket is assumed.
Adding soft bedding requires updating the seat and rear mount stack together.

M3×6 remains nominal: 3.9 mm bearing pads and 2.1 mm engagement before any shims,
against the manufacturer's 2.5 mm maximum thread depth. The already printed V40
fixture confirms the opening contour only and has the old non-bearing shoulder;
it cannot prove the new load path. Existing loose brackets remain useful for lug
pattern checks but are not final assembly parts.

The inherited cable/divider clash, real power layout, rear screw/tool access and
full-body orientation/support review remain unresolved. Printer parts and the
active navy-base job are unchanged. Fusion remains closed with V39 last saved.

Source for variant/stack considerations:
`cad/references/touch_display_enclosure_mechanical_design.pdf`, pages 4–5 of
the document (PDF pages 5–6). The guide specifically discusses damage from a
mismatch between glass bearing and rear mount depths.
