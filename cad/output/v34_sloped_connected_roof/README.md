# V34 — sloped display face with connected roofs

The user rejected V33's upright display surround and deep screen recess.
The sloped front plane around the display, at the same 14-degree angle as
the screen, is a design requirement. Do not restore the V33 upright facade.

V34 retains the exact V32 sloped face, original bezel, screen position and
mounts. It keeps the matching lower band and rounded printer shell from V33.
The display cover is rebuilt so its top stays flat to the internal bay joint,
instead of rounding downward at that edge. Both roof planes meet at z201.
The exposed front roof edges have 12 mm radii, tangent to their respective
sloped and upright faces. The sloping display face naturally puts its front
roof edge farther back; the roofs connect behind that transition without
a rounded valley. No canopy or vertical wall is added around the screen.

Both structural bays remain separate prints joined with the existing internal
screw and dowel pattern. A fine physical seam remains; the CAD does not imply
an invisible manufactured joint. The display lid remains separately removable,
and the printer roof is integral with rear loading/paper service preserved.

Checks pass: valid single solids and watertight changed meshes, no assembly
clashes, no reference-envelope clashes, clear printer extraction path, five
clear vents, seven clear joining bores and four clear lid passages. A strip
across the roof joint has complete solid coverage up to the common roof plane.
See `audit.json`. Actual left-side hardware and print supports remain unverified;
this is a geometry review, not a new print release. The V31 fit kit is unchanged.

Saved and visually verified in Fusion project `lumon` as
`LUMON_v34_SLOPED_CONNECTED_ROOF` on 22 September 2026. V33 is retained only
as a rejected alternative; V34 is the current direction. No print dispatched.

- `whole_enclosure_review.step`: complete coloured assembly.
- `sloped_front.png`, `sloped_roof.png`, `sloped_rear.png`: actual CAD previews.
- `*_assembly.stl`: assembly coordinates, not oriented print releases.
- Front previews include reference hardware blocks, not printable parts.

Regenerate with `.venv/bin/python cad/review/build_v34_sloped_roof.py`.
