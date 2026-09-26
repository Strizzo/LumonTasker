# V32 — equal-height bay study

The user confirmed that both bays should have the same overall height with
their tops aligned, and the display moved upward. This is a CAD design option,
not a new print release. Existing V28 printed shell and V31 fit kit are retained.

## Geometry

- Display bay grows from 181 to **201 mm**, matching the printer bay.
- Both navy feet stay on the same z=0 ground plane; the floor does not float.
- Screen, bezel, rebate, support ribs and retainer rise **10 mm vertically**
  to stay centred within the taller usable front face. The unchanged 14-degree
  rake moves them about 2.49 mm rearward too.
- Front cover screw centres move about 4.99 mm rearward together with the tub
  insert lands and cover sleeves, following the taller sloped wall.
- Rear vents move 20 mm upward; the smaller V29 service hatch stays in place.
  Clear vertical gap from hatch to first vent is now 26 mm.
- Existing bay-joining screw/dowel positions, foot, hatch, lower cable passage,
  Pi mounts and power placeholders retain their original positions.
- Every printer-side solid is copied unchanged from V31, including the printed
  shell and the revised cradle-retaining bar. The prepared fit-kit print remains
  compatible and is still awaiting approval, bed clearance and current PLA slot.

## Checks and limits

All four changed parts are valid single solids and their meshes are watertight.
The complete assembly has no volumetric part clashes; joining bores, cover
passages and all five vents pass obstruction checks. The inherited display
envelope does not intersect the assembly. See `audit.json`.

These are geometry checks, not verification of actual display, Pi/cooler,
power hardware, screw tool access, print supports or thermal performance.
The screen dimensions and left-side hardware remain unconfirmed. STL files
here are in assembly coordinates and must not be treated as oriented print files.

This study establishes the heights only. Coordinated top rounding/navy trim
and the paper-outlet surround still need the separate appearance review; they
are not silently included in these previews. Any future crown must preserve
the agreed common finished height across both bays.

## Review files

- `whole_enclosure_review.step`: complete coloured assembly.
- `before_front.png`: exact previous assembly at the same camera position.
- `equal_height_front.png`: equal-height option.
- `equal_height_rear.png`: rear view and ventilation separation.
- `display_reference.step`: unverified reference envelope; never print.

The PNGs are actual CAD renders. A dark display reference is included only in
the front previews so the window is readable; it is not a verified device model.
Rebuild with `.venv/bin/python cad/review/build_v32_equal_height.py`.

Fusion import completed. The user confirms they set older versions read-only
and saved this review on 22 September, resolving the editable-document limit.
Local STEP and previews are also saved.
