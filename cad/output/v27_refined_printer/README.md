# V27 — physical-fit refinements

V26 cradle reported mostly fine. User explicitly requests proceeding without another cradle test. Bottom support rise is increased by50% from5.4 to8.1mm above the rear bearing level; front support rises2.7mm. Lateral guide gap is reduced0.6mm total (0.3mm each side), giving133.4mm front and144.4mm rear. Side guide slope and height are unchanged.

Reference front bottomZ24.1/top190.1 preserves measured166mm front span; rear remainsZ16..191 and175mm span. Paper aperture and LED are raised2.7mm with the front datum; aperture centre remains60mm below front top. This updates the estimated casing profile to fit feedback, not a precise scan or proven rigid-body pose. Width taper remains132/143mm. Switch channel remains conservative and open rearward.

All exported solids/meshes pass validity/watertightness, pairwise collision, body rear withdrawal and switch sweep checks. No physical repeat of refinements is claimed. Whole-enclosure context STEP/PNG includes the older left module for visual review only; display/Pi fit and full base integration remain pending.

## Print preparation

Use01_shell_supported.3mf for the shell: saved by Bambu Studio with tree(auto) supports enabled,2 wall loops,15% infill. GUI slicing:8h49m,335.77g total,15.85g supports,1.96g purge,0.8g tower,6 filament changes,805layers. No cantilever warning remains. Slot2 light-grey PLA body,slot1 navy PLA logo. Shell lies front-face down; logo is confined to initial layers. Native archive contains meshes/settings, not saved G-code. No print sent.

The generated01_shell_with_logo.3mf is an intermediate, not the reviewed native variant. Programmatic settings were not fully applied by this Bambu version; verify settings in GUI for all remaining projects. Do not overwrite01_shell_supported.3mf by rerunning the packer.

Other prepared projects:02_cradle_and_bars (final refined cradle, not another trial),03_top_cover,04_rear_cover,07_retaining_bars_only (alternative if cradle handled separately). These remain unsliced; no duration claims. Use separate single-colour jobs for these parts. PETG diffuser remains a separate insert STL; profile/loaded slot not specified, so no PETG print project dispatched.

Assembly: install4.2mm heat-set inserts; seat refined cradle, load intact printer from rear, install two retaining bars (fourM3x12), rear cover (fourM3x14), top (twoM3x8). Check screw bottoming and retain the switch/cable clearances. Diffuser bonded only on its flange, no pressure on original light/buttons. Paper service via rear cover and retaining-bar removal.

Print launch requires user confirmation, consistent with standing instruction; the earlier time-window and specific cradle authorizations do not release this long shell job.


## Shell dispatched with explicit user approval

21 September approximately16:51 local:01_shell_supported sent and device confirmed active heating,805 layers,335.77g,estimated finish22 September01:39. AMS A2 light-grey body/A1 navy logo;Auto Bed Leveling off,timelapse off. Other parts remain unprinted.
