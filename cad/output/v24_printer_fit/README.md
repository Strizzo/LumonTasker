# Printer fit samples — centre datum confirmed

User confirmed 56mm from printer upper edge to outlet vertical centre. Aperture upper edge is 49mm down, lower edge 63mm down; width 90mm, height 14mm, horizontally centred. Selected file: `front_template_centre_56_ALTERNATIVE.stl` (historical filename; this is now the confirmed version). Upper-edge-56 template is obsolete and not on the plate.

Two pieces: centre-datum front template (131 × 69 × 3mm) and actual cradle cross-section (141 × 16 × 20mm, 133mm guide gap for 131mm printer). Hold the template notch/top edge level with printer top and centre it; verify paper alignment, feed/cut and absence of rubbing. Place cradle gauge under the printer to check free fit and resting contact. Neither sample validates full connector routing or retaining pads.

P1S 0.4mm / Textured PEI / 0.2mm / four walls / 15% gyroid / 5mm brim / no supports or prime tower. Both pieces physical AMS A2 light-grey Generic PLA. Bambu GUI estimate 45m42s including preparation, 15.37g, 100 layers. No within-print colour swaps. User authorized starting if under one hour and finished before 11:30 meeting. Send initiated 21 September 10:32 local, printer accepted job and entered preparation, 0/100 layers; device estimated finish 11:18. Full-case printing remains on hold.

Plug measurements: power15mm, square USB12mm, recorded provisionally as protrusion allowances; locations and bend space remain unmeasured. Upper-output orientation is already user-tested.

## Physical sample result, 21 September 2026

User confirms cradle fit is fine; retain 133mm guide gap. Printed centre-56mm template fits acceptably, but moving its opening DOWN 4mm aligns it perfectly: use centre 60mm below printer upper edge, edges 53/67mm below top, unchanged 90 × 14mm size. This supersedes the earlier 56mm value. No repeat sample print requested or sent. Corrected reference geometry is in `cad/output/v24_printer_fit_refined`; preserve this printed job as history. Paper feed/cut through template was not explicitly reported, so do not mark that test passed.

For the current v23 body placement (X16.5..147.5, Z16..191), the fitted outlet rectangle maps to X37..127 and Z124..138, centre X82/Z131. This is centred on the printer, not shell X79. The v23 broad opening remains provisional; carry these coordinates into the detailed front while resolving button access.
