# V33 — unified outer body study

**Rejected by the user.** The sloped front plane around the display must stay
at the screen angle. V34 restores it and addresses roof/base continuity without
an upright facade or deep recess. Do not use V33 as the current design direction.

The user wants one cohesive device: matching lower profiles, matching rounded
front roof edges and less of a two-box appearance. This option is built from a
single exterior envelope and split at the existing internal bay joint.

## Visible changes

- Both bays remain 201 mm high on the same ground plane, 393.96 mm overall width.
- A common upright outer face surrounds the screen and printer. The screen
  itself remains at its original 14-degree angle, recessed in a deeper navy bezel.
- Both sides have the same 12 mm front roof radius and 14 mm outside plan corners.
- A common 24 mm-high light lower band, from z9 to z33, steps inward by 0.8 mm.
  The two existing navy feet remain 9 mm high on the same plane.
- The left rounded front brow is integral with its tub. Its service-lid joint
  moves onto the roof, 26 mm behind the face, with 0.25 mm nominal clearance.
- The right roof remains integral. Printer insertion and roll service remain
  through the rear. No fragile detachable front panel is introduced.

This direction uses the structural white shoulder to create the rounding;
the previously discussed add-on navy crown is not included in this study.

## Printing and joining

The structural left and right sections remain separate prints. Their bounds
are approximately 219 × 161 × 192 mm and 175 × 161 × 192 mm, respectively.
Both fit within the P1S build envelope; orientations, supports, brim and slicing
have not been released. The left lid is separate, with its existing four screws.
The deeper navy display bezel and both navy feet are separate single-colour
parts. The translucent PETG diffuser remains separate from PLA.

The five existing inter-bay M3 axes and two alignment dowels are retained.
The geometry aligns to one contour with no decorative step at the central
join. A fine physical seam will remain when assembled dry. An invisible joint
would require bonding, filling and finishing; it is not promised by a CAD render.
The rear-loading printer can still be serviced if the main shells are bonded,
but reversible screw assembly is preferable while validating the design.

The grey/yellow V28 shell remains useful for mechanical fitting. This revised
exterior needs a new shell print for the final build. V31 cradle and retaining
bars remain unchanged and compatible; their launch approval is still pending.

## Checks

- All four changed parts are valid single solids with watertight exported meshes.
- Complete assembly reports no volumetric part clashes.
- The measured tapered printer envelope and the inherited, unverified display
  envelope do not intersect the changed geometry.
- The rear printer extraction volume remains clear.
- All five rear vents, seven inter-bay bores, and four lid passages remain clear.
- The 0.8 mm lower step leaves 2.2 mm of the original printer front wall.
- The curved roof has an inner shoulder, rather than simply shaving through
  the old square shell. Its LED-flange relief preserves the existing diffuser.

See `audit.json` for values. These checks do not establish the exact real
display/active area, Pi/cooler or power hardware fit, touch accessibility inside
the recess, thermal performance or sliced print quality. This is a CAD form
review, not permission or a release to print the final enclosure.

## Review

- `whole_enclosure_review.step`: complete coloured assembly.
- `before_front.png`: V32 at the same camera position.
- `unified_front.png` and `unified_straight_front.png`: actual new CAD geometry.
- `unified_rear.png`: rear service arrangement.
- `split_assembly.png`: separated bays and lifted left lid, illustrating assembly.
- `*_assembly.stl`: assembly-coordinate meshes, not oriented slicer releases.

Front previews include a dark unverified display reference and the measured
printer envelope for visual context; these reference blocks are not print parts.
LED colouring is illustrative, not an optical transmission simulation.

Imported, visually checked and saved in Fusion project `lumon` as
`LUMON_v33_UNIFIED_BODY_STUDY` on 22 September 2026. V32 was preserved.
No print dispatched. Rebuild with:

```
.venv/bin/python cad/review/build_v33_unified_body.py
```
