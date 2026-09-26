# V48 print-quality feedback — 24 September 2026

User sees continuing fraying on the opposite side after the frame was flipped,
and suggests filament calibration or excessive separation from support. This
must be resolved or deliberately avoided before final enclosure printing.

Photo:
`/tmp/codex-remote-attachments/01a0bf3e-2220-7252-adef-d07f9ff37b1f/E4D6E3C7-4DCB-467E-A393-EA903649E511/1-Foto-1.jpg`

## Evidence and uncertainty

- Photo shows loose perimeter strands and exposed internal/support structures.
  Do not classify all exposed infill as a defect or judge unfinished top layers
  as completed surface finish.
- Read-only Bambu check during this report: matching V48 job printing at
  58%, layer103/121,1h16m remaining, ETA16:13. Completion not verified.
- Moving the rough area when reversing orientation is consistent with a
  support-contact/bridging problem. This is a hypothesis, not a proven cause;
  exact contact face and damage after support removal still need inspection.
- V48's upward-facing glass seat is not yet confirmed clean, flat or sound.
  Do not mark the orientation change as a validated quality fix.
- Original mount hole alignment remains physically confirmed and unshifted.

## Actual saved toolpath settings

- PolyTerra Cotton White PLA, A2, nozzle220 C.
- Same PLA for model and supports; normal snug supports.
- Support top Z gap **0.2 mm**, unchanged from V46.
- Three top interface layers, interface spacing0.15 mm; support/model XY0.3 mm.
- Support scaffold spacing4 mm; bridge speed30 mm/s; interface speed40 mm/s.
- Saved project filament2 flow ratio0.985, maximum volumetric speed29 mm³/s,
  part fan100%, auxiliary fan70%. These are extracted settings, not measured
  calibration results. Check effective settings after GUI profile resolution;
  do not claim the intended template values are necessarily the saved values.
- The maximum flow setting alone does not establish actual extrusion demand
  or prove under-extrusion in these low-speed bridge/support paths.

The 0.2 mm same-material gap is Bambu's general starting recommendation.
A smaller gap trades easier removal for better support-contact finish; it is
not automatically better for this thin ledge. Reference:
[Bambu user manual, support settings pages65–66](https://csm.bblcdn.com/hub/4668d0ca43994ff3bff4b37f1a65c2e7.pdf#page=66).

## Before the final case

1. Inspect the completed part after support removal: distinguish sacrificial
   support strands from model damage; check upward glass bearing, lug lands,
   reverse face, ordinary walls and top surfaces separately.
2. Prefer a production orientation or local printable geometry that avoids
   support contact on visible and glass-bearing faces. This is a full-case
   orientation decision; a successful small fixture is not proof for the shell.
3. Use a small representative corner/ledge coupon, with comparable unsupported
   spans and support height, to compare current0.2 mm contact gap with a closer
   candidate (e.g.0.12 mm). Keep other variables fixed first; retain the dense
   interface and verify effective sliced gap. Do not make PLA-to-PLA gap zero.
   Check surface, removal effort, ledge damage and dimensional accuracy.
4. Include a directly supported/bed-printed reference to distinguish local
   support-contact failure from general extrusion quality. If supported walls
   or top surfaces also show gaps/poor bonding, verify the saved filament
   profile and run targeted flow/temperature checks before more surface tests.
5. Tune speed/cooling only against observations, rather than changing all
   variables together. Preserve the user's preference to minimize filament
   waste; do not use another full frame just to calibrate support finish.

No new calibration print was prepared or dispatched by this note. The active
job was not changed. This records a final-print quality check, not a confirmed
diagnosis or a reason to change the accepted hole pattern.
