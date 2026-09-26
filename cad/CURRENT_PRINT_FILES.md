# Parts used in the accepted prototype

The user accepted the assembled device on 26 September 2026. Its parts come
from several revisions; old fit coupons, superseded display brackets and navy
screen bezels are preserved in the archive but are not part of this build.

| Part | Existing print project / geometry |
| --- | --- |
| Printer shell with navy logo | [V39 printer shell](output/v39_aligned_rear/01_V39_printer_shell.3mf) |
| Printer cradle | [V31 reviewed cradle plate](output/v31_cradle_retention/02_cradle_and_bars_reviewed.3mf); [cradle STL](output/v31_cradle_retention/cradle_tray.stl) |
| Printer rear cover and integrated retention | [V39 rear cover](output/v39_aligned_rear/02_V39_printer_rear_cover.3mf) |
| Navy printer base | [V42 selected lean base](output/v42_light_printer_base/02_V42_printer_base_lean.3mf), retaining the original V39 shape; the pocketed V42 candidate was rejected. |
| Display body with recessed glass seat | [V51 upright display body](output/v51_external_power_body/02_V51_display_body_upright.3mf); [STEP](output/v51_external_power_body/display_body.step) |
| Rounded display roof and rear hatch | [V50 roof/hatch plate](output/v50_full_display_preflight/02_V50_display_roof_and_hatch.3mf) |
| Navy display base with closed surfaces | [V51 top-down base](output/v51_external_power_body/04_V51_closed_display_base_top_down.3mf); [STEP](output/v51_external_power_body/display_base.step) |
| Glued rear DC inlet panel | [V51 inlet panel](output/v51_dc_inlet_panel/02_DC_inlet_glue_panel.3mf); [STL](output/v51_dc_inlet_panel/dc_inlet_glue_panel_print.stl) |
| Translucent PETG indicator insert | [V51 PETG insert](output/v51_petg_led_insert/01_LED_insert_PETG.3mf); [STL](output/v51_petg_led_insert/led_insert_print.stl) |

Current complete geometry:
[LUMON_v51_GLUE_DC_INLET_ASSEMBLY.step](output/v51_dc_inlet_panel/LUMON_v51_GLUE_DC_INLET_ASSEMBLY.step).
The cloud Fusion review with the same name is a separate saved document; no
native Fusion `.f3d` archive has been exported into this project.

Projects were prepared for a Bambu P1S, 0.4 mm nozzle and textured PEI plate.
The final colour mapping was navy PLA in AMS slot 1, cotton-white PolyTerra PLA
in slot 2 and translucent PETG in slot 3. Slice and inspect the projects for
your own printer and mapping. Existing `.gcode.3mf` exports document past jobs;
their existence does not mean a historical part should be printed again.

For the next revision, retain the accepted working assembly while addressing
the recorded weight, supports, glass-pocket clearance, unused insert bore and
open printer-base underside feedback. See [BUILD_STATUS.md](BUILD_STATUS.md),
[V39 next-revision notes](output/v39_aligned_rear/NEXT_REVISION.md) and the
[V42 base feedback](output/v42_light_printer_base/README.md).
