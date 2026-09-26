# V38 — straight rear lands, rounded retaining cover

User requests straight rear shell edges with the curvature in the removable panel. This revision replaces the separate bars and cover with one reinforced cover, preserving the tested printer pose, cradle, retention clearances, raised paper opening and corrected logo spacing.

The structural rear edge now ends square and flat at Y161. The cover forms the outer rear radius (9.5 mm) beyond a 0.25 mm cosmetic seam. Its back face is Y170.75 versus Y170.5 for the former cover, so overall closed depth grows only 0.25 mm. A thin deliberate seam remains; this is not a seamless monolithic print.

Four M3x14 screws secure the cover: local X4.5 and X161, Z40 and Z180. The outer screw pair moves inward 9.5 mm to keep screw heads and mounting posts on flat lands. Grip is 9.75 mm and nominal engagement 4.25 mm into the existing 4.2 mm insert bore design. Actual hardware bottoming and secure engagement require a physical trial. The old prototype's outer screw holes do not match this revised cover.

The lower and upper retaining ribs and lower cradle-capture lips are integral. Their printer-facing and tray-facing positions are retained. The lower cable opening widens 5 mm toward the switch side (X35–118) to preserve the complete switch/service clearance. The navy base extends under the new cover and keeps the front bevel and adhesive beds.

CAD checks: each changed component valid, one solid and watertight; zero cover collisions against shell/cradle/printer reference/base; tested 0.45 mm tray freedom and capture at 0.75 mm; straight rear cover removal clear; all four insert lands supported around full screw annulus; original front geometry unchanged. Hardware references do not substitute for physical checks. No electronics-side hardware release is made.

Files: `whole_enclosure_review.step` is the real full assembly. `V38_REAR_INSPECTION.step` is a rotated side-by-side viewing aid only. `*_assembly.stl` use local printer-bay coordinates; `*_print.stl` are oriented for slicing. The Fusion assembly is saved as **LUMON_v38_INTEGRATED_REAR**, verified with no unsaved marker.

## Reviewed print plates

| Part | Selected sliced file | Estimate | PLA | Layers |
|---|---|---:|---:|---:|
| Shell and logo | V38_final_shell_tree.gcode.3mf | 18h30m54s | 634.49g | 805 |
| Integrated rear cover | V38_rear_cover.gcode.3mf | 4h04m51s | 140.90g | 231 |
| Navy base | V38_navy_base.gcode.3mf | 2h48m01s | 97.50g | 45 |

Shell uses cotton-whiteA2 and navyA1; only the first4 layers use both,6 changes total. Cover is all white; base is all navy. Shell tree supports use39.54g and save46.77g/1h20m53s against normal supports. Shell editable project is `01_V38_shell_reviewed.3mf`. G-code was exported from Bambu Studio and checked for correct effective settings and build-volume fit.

No V38 print started. Send dialog is prepared for the shell, mappingA1/A2 verified, bed leveling and timelapse OFF. Printing is authorized; a pending build-plate-clear question is the only launch dependency because camera coverage is partial. Do not send superseded V37 G-code or V38 normal-support comparison file.

Regenerate CAD with `.venv/bin/python cad/review/build_v38_integrated_rear.py`. Running the generator resets its audit status, so preserve the physical/slice ledger separately. The selected tree project differs from the original project only in support type/style.
