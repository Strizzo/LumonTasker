# V39 — aligned rear faces

Both assembled rear faces end at Y170.75. The display bay rear extends9.75mm, including its hatch, fixed rear wall/IEC recess, roof skirt and rear screws. Both navy bases end atY168.25. Rear outer corner radii match at9.5mm; bases at7mm.

The front region throughY135 is preserved exactly, retaining the25-degree display front, screen mounts and front appearance. Pi/PSU placements are frozen at their original values; the increased legacy depth cannot move them silently. All printer-side parts, including the cradle, cover, shell and raised outlet, are unchanged.

Validation: one solid per changed part, watertight meshes, zero assembly/hardware-reference clashes, clear exhaust slots, covered joint screw lands, aligned roof/base screw axes, unobstructed rear printer-cover removal. Actual electronics dimensions and fit remain unverified; these CAD checks do not establish physical fit.

Fusion: saved and verified as **LUMON_v39_ALIGNED_REAR**,22 September19:38. Ten editable documents are now in use. The file `whole_enclosure_review.step` is the actual assembly. `aligned_rear.png` shows the corrected rear.

## Prepared Bambu plates

| Plate | Time | PLA | Layers |
|---|---:|---:|---:|
| 01_V39_printer_shell.gcode.3mf | 18h30m54s | 634.49g | 805 |
| 02_V39_printer_rear_cover.gcode.3mf | 4h04m51s | 140.90g | 231 |
| 03_V39_printer_base.gcode.3mf | 2h48m01s | 97.50g | 45 |
| 04_V39_display_body.gcode.3mf | 19h07m34s | 612.70g | 880 |
| 05_V39_display_roof.gcode.3mf | 3h02m00s | 108.80g | 105 |
| 06_V39_display_rear_hatch.gcode.3mf | 0h54m30s | 34.64g | 15 |
| 07_V39_display_base.gcode.3mf | 4h38m18s | 159.59g | 45 |

P1S0.4mm, texturedPEI,0.20mm layers,4walls. White PLA usesA2/PolyTerra; navy PLA usesA1/Bambu. Effective G-code settings verified:220C nozzle,55C bed,flow0.98,maxvol22. All plates inside the build volume and their G-code checksums valid.

The shell uses both colours only in its first4layers,6changes total. Every other prepared plate is single-colour with no prime tower. The seven plates require1528.76g white and259.86g navy; unchanged bezel/retainer/diffuser are additional parts.

The three printer-side slices are byte-identical to the reviewed V38 files because the actual printer geometry is unchanged; their embedded names may still sayV38. V39 filenames and plate_manifest.json identify this explicitly. The four display-side plates are newly sliced. Display body/roof use auto-tree supports; hatch/base need none.

Printer shell dispatched on 22 September at 21:45 local after explicit user authorization and build-plate-clear confirmation. Bambu reports successfully sent; P1S downloaded the job and is heating the bed. Navy A1 / cotton white A2; bed leveling and timelapse OFF. See print_dispatch.json. No other plate dispatched. First-layer quality and completion are not yet verified. Left hardware fitting is still pending before final display-bay production.

Regenerate:build_v39_aligned_rear.py, thenprepare_v39_projects.py in cad/review. Re-slice changed geometry through Bambu Studio; source generators do not reproduce native G-code.

## Physical build update — 23 September

Shell completed; user confirms existing V31 cradle and printer fit perfectly in the new shell. Cosmetic lower-band recess is accepted for this build, with a flush-band change recorded for the next revision in NEXT_REVISION.md. Rear cover sent to P1S at 16:36 local, cotton white A2 only, bed leveling/timelapse OFF. Device reports matching job downloading and bed heating. See rear_cover_print_dispatch.json. Cover completion and secured retention still await physical verification.
