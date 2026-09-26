# V45 — 3 mm display bearing ledge

The user requested a wider ledge and explicitly confirmed the local 1.3 mm black
band stays clear of the outermost **3 mm** of the glass's back surface. The
selected seat is therefore widened from 2 to **3 mm inward beneath the glass**,
with no local band notch. This is bearing width, not a soft padding thickness.

The full 3 mm width has **2.3 mm plastic thickness**, from local y1.8 to y4.1.
The added inner strip is not a thin shelf. The measured 0.8 mm glass sits with
its front at y1.0, still recessed 1 mm behind the white face. The accepted
193.4 × 111.4 mm opening and R8.2 corners, four integral retention arms and
four nominal M3×6 screws are unchanged. There is no front-overlapping lip or
separate navy bezel. The glass rests on the ledge without screws; screws retain
against front withdrawal and must not draw the glass across a mounting gap.

The generator checks the complete bearing area at the glass back and throughout
the 2.3 mm ledge thickness, hardware clearances, front insertion/extraction with
fixed arms, and the four screw bores/head recesses. The band is checked using
the entire glass area inset by 3 mm, with its reported 0.5 mm extra thickness
plus 0.3 mm rearward margin. This is a conservative clearance envelope, not a
claim about its exact shape or identity. Geometry is a single valid solid with
a watertight mesh; detailed results are in `glass_0p8/audit.json`.

The nominal metal chassis starts 3.35 mm in from the lower glass edge, leaving
only **0.35 mm nominal lateral clearance** from the wider ledge there. This
passes the CAD envelope check but still requires the real seating/mounting test.
The front contour alone has been physically tested; the new ledge and integral
mounting stack have not. Full-case power/cable routing, screw access and slicer
support review remain pending. Selecting this seat does not release the full
display case for printing.

The printer parts/job are unchanged. Fusion has not been updated and remains at
the previously saved V39 assembly. The 2 mm V44 exports remain historical.

Reproduce:

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python cad/review/build_v44_bearing_seat.py --glass-mm 0.8 --measured --local-band-total-mm 1.3 --seat-width-mm 3 --band-clear-border-mm 3 --output cad/output/v45_display_seat_3mm
```

`glass_0p8/whole_enclosure_with_hardware.step` is the assembly review with nominal
hardware. `tub_left.step` and `tub_left_assembly.stl` are the revised body; the STL
is assembly-oriented, not an approved print file. `variants.json` records the
selected 0.8 mm glass / 3 mm seat configuration.
