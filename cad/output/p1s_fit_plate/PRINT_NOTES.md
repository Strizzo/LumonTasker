# First physical fit test — 20 September 2026

Bambu Studio project: `LUMON_v19_fit_test.3mf`.

Sent through Bambu Studio to P1S `3DP-01P-994`; device acknowledged the matching job name and completed downloading. Bed seen clear in camera before sending. Auto bed leveling enabled; timelapse disabled.

- A1 / physical AMS slot 1: dark Bambu PLA Matte; bezel corner.
- A2 / physical AMS slot 2: user-confirmed light-grey Generic PLA; screen corner and both seam samples.
- Slot 4 orange was explicitly excluded from final mapping.
- 0.4mm standard nozzle, textured PEI, 0.20mm layers, 3 walls, 20% infill, 3mm outer brims.
- Automatic support from build plate enabled for screen-corner sample.
- Slice estimate: 1h24m, 27.07g total, 16 filament changes.

After cooling, remove brims/support carefully. Check the bezel against the opening, inspect the revised lower-left corner, and test mating seam alignment and M3 holes/inserts. These samples check local geometry and tolerances; they do not establish that the real display or receipt printer fits. Actual device measurements remain required before full-shell release.

`LUMON_v19_fit_test_setup.3mf` is the unarranged intermediate used by `cad/review/configure_fit_project.py`; print the final project above, not that intermediate.

## User-reported fit results

Both grey seam samples match, and the dark bezel corner matches the grey screen corner (confirmed 20 September 2026). Insert installation and screw retention remain untested.

Hardware photo shows M3 screws in lengths 6/10/14/20mm in the silver kit and 8/12/16/20mm in the black kit, plus assorted brass inserts whose dimensions are not identifiable from the photo. Current insert bores are nominally 4.2mm diameter and 6mm deep; intended insert OD in source is 4.6mm. Obtain actual M3 insert outside diameter and length before installation or changing bore dimensions.

User printing preference: group separate parts onto single-color plates to reduce purge waste. Use multicolor printing when required within one part, such as the logo wall. User accepted the first coupon plate's 16 changes.

User subsequently confirmed the insert test is fine and requested proceeding. Retain the tested 4.2mm insert bore; no bore enlargement is justified by the approximate caliper photos. This confirms the seam coupon fit, not every blind-hole installation in the enclosure.
