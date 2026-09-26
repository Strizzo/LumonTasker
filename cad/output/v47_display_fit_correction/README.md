# SUPERSEDED — DO NOT PRINT

User corrected the display orientation and confirmed the ORIGINAL mount holes match. The V47 mount shift is withdrawn. Use V48 original mounts instead. No V47 print was dispatched. Project/toolpath filenames have been marked SUPERSEDED_DO_NOT_PRINT. The following is historical.

# V47 — display fit corrections after physical V46 test

User feedback: the glass almost fits but one corner is tight; the four bores
need moving 3.6 mm right and 2 mm down viewed from behind; loose strands and
poor attachment are visible under the ledge. The V46 bearing surface and
glass/metal lug stack are not physically accepted.

## Geometry

- Pocket width 193.4 → 193.6 mm overall, centred (+0.1 mm each side).
  Height 111.4 mm and R8.2 corners stay unchanged. The actual measured glass
  remains 193 × 111 mm; this change is clearance only.
- All four pads, counterbores and holes move with the measured lug pattern.
  Rear-view right/down means local X−3.6/Z−2.0, because local X is right as
  viewed from the front. Pitch remains 126.2 × 65.65 mm.
- Root anchors remain outside the glass boundary; arms are rebuilt to reach
  the shifted pads. Four integral mounts, no separate brackets or inserts.
- The continuous 3 mm glass-bearing width and 2.3 mm ledge thickness remain.
  Glass front recess 1 mm, measured glass thickness 0.8 mm, no bezel/front lip.

Both the complete production tub and a matching cropped fit frame are updated.
`audit.json` records valid single solids, watertight meshes, the full bearing
ring, shifted hole/pad checks, no case-part collisions, nominal front insertion
sweeps, and no changes outside the intended interface regions.

## Printing

`01_V47_display_corrected_seat_up.3mf` is the small test only. The rear faces of
the four arms sit on the bed; the glass ledge and metal-lug contact lands face
upward. Thus neither critical bearing surface is the first layer over support.
Supports contact the reverse face of the ring. Cotton white PLA in A2 only.

Use a denser three-layer interface (0.15 mm spacing) while retaining a 0.2 mm
same-PLA separation gap for removability. The scaffold below uses 4 mm spacing;
this is separate from the dense contact layers. Settings follow the distinction
between support contact gap and its surface/removal tradeoff explained in
[Bambu's manual, pages 65–66](https://csm.bblcdn.com/hub/4668d0ca43994ff3bff4b37f1a65c2e7.pdf#page=66).
The orientation is the main bearing-surface correction; actual print quality
still needs inspection. GUI slice/support review and bed-clear confirmation
are required before dispatch.

The initial 2 mm support-scaffold spacing preview was 71.33 g / about 3h18m,
of which 32.73 g was support. This prompted a 4 mm scaffold spacing comparison
without loosening the contact interface. See `slice_review.json` for the
selected actual slice when available.

## Fit check

1. Remove temporary supports from the reverse face and holes. Keep the upward-
   printed glass seat clean and avoid scraping its bearing surface.
2. With screws absent, insert the unplugged display/Pi from the front. Check
   the tight corner now enters freely and the glass rests without rocking.
3. All four holes must line up and all four metal lugs must meet their pads
   while the glass rests naturally. Do not use screws to pull a gap closed.
4. Only after these checks, gently fit four M3×6 screws from behind.

The lug correction does not measure the entire chassis/Pi position: their
reference models remain explicitly nominal. Full-case power/cable routing,
screwdriver access and production print orientation remain unresolved; the
provisional cable/divider overlap remains 237.48 mm³. No full-case print is
released. Fusion remains closed/latest saved V39; V47 STEP is not synced there.

## Prepared slice

GUI slicing/export passed: **3h04m01s,63.31 g**, including24.72 g supports;
121 preview layer heights, A2 white only, no inter-colour changes. Final support
scaffold spacing4 mm saves8.02 g against the initial2 mm-spacing preview. The
dense contact interface is unchanged. Project and toolpath saved and checked.
**Not dispatched:** fresh plate-clear/support-debris confirmation is pending.
Bed leveling and timelapse are planned OFF, to verify in Send before dispatch.
