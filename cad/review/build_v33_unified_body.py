"""Cohesive exterior study: one envelope split into printable modules.

Retains V32 hardware datums. Review only; left hardware and print supports
remain unverified. The already printed V28 shell is a mechanical prototype.
"""
from pathlib import Path
import copy
import itertools
import json
import math
import sys

import build123d as b
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'files')]
from render3d import Scene

OUT = ROOT / 'cad/output/v33_unified_body'
OUT.mkdir(parents=True, exist_ok=True)
W, SPLIT, D, H = 393.96, 218.96, 161., 201.
BASE_Z, BAND_TOP = 9., 33.
R_PLAN, R_TOP, BAND_INSET = 14., 12., .8
PALE, NAVY = '#F0F1EB', '#173B53'
NAVY_PARTS = {'foot_left', 'foot_right_bonded', 'display_bezel', 'logo'}


def box(x, y, z, w, d, h):
    return b.Pos(x+w/2, y+d/2, z+h/2) * b.Box(w, d, h)


def cz(x, y, z, diameter, height):
    return b.Pos(x, y, z+height/2) * b.Cylinder(diameter/2, height)


def volume(shape):
    return sum(s.volume for s in shape.solids()) if shape else 0.


def envelope(inset, bottom, top, plan_radius, top_radius=0.):
    s = box(inset, inset, bottom, W-2*inset, D-2*inset, top-bottom)
    s = b.fillet(s.edges().filter_by(b.Axis.Z), plan_radius)
    if top_radius:
        # Only the front roof edge is rounded. A rolled rear edge would lower
        # the printer extraction opening and foul its upper rear corner.
        corner = box(-1, inset, top-top_radius, W+2, top_radius, top_radius)
        barrel = (b.Pos(W/2, inset+top_radius, top-top_radius) *
                  b.Rot(0,90,0) * b.Cylinder(top_radius,W+4))
        s -= corner-barrel
    assert s.is_valid and len(s.solids()) == 1
    return s


def round_front_rect(width, height, radius, y, depth, cx=109.48, z=109.):
    # Positive extrusion on this rotated XY plane points toward -Y.
    return (b.Pos(cx, y+depth, z) * b.Rot(90, 0, 0) *
            b.extrude(b.RectangleRounded(width, height, radius), amount=depth))


def front_halfspace(local_y):
    # Same pivot and 14 degree screen rake as V32.
    slab = (b.Pos(0, 0, BAND_TOP) * b.Rot(-14, 0, 0) *
            b.Pos(0, 0, -BAND_TOP) * box(-10, -500, 0, W+20, 500+local_y, 400))
    return slab


old = b.import_step(ROOT / 'cad/output/v32_equal_height/whole_enclosure_review.step')
before = {s.label: s for s in old.children}
parts = {k: copy.deepcopy(s) for k, s in before.items()}
display = b.import_step(ROOT / 'cad/output/v32_equal_height/display_reference.step')
printer = b.Pos(SPLIT, 0, 0) * b.import_step(ROOT / 'cad/output/v28_integrated_top/printer_reference.step')

# Build the outer shape ONCE, then divide it. No independent radii at the
# module seam, so its front, top and lower profiles share exact datums.
outer = envelope(0., BAND_TOP, H, R_PLAN, R_TOP)
inner = envelope(3., BAND_TOP-1, H-3.5, R_PLAN-3, R_TOP-3)
band = envelope(BAND_INSET, BASE_Z, BAND_TOP, R_PLAN-BAND_INSET)
left = box(-1, -1, -1, SPLIT+1, D+3, H+3)
right = box(SPLIT, -1, -1, W-SPLIT+1, D+3, H+3)
low = box(-1, -1, BASE_Z, W+2, D+3, BAND_TOP-BASE_Z)
upper_tub = box(-1, -1, BAND_TOP, W+2, D+3, 185-BAND_TOP)

# Recess the tilted display inside a new upright perimeter. This is a hollow
# outer frame; the old angled display mounts stay behind it at the same angle.
well_outer = round_front_rect(203., 132., 11., -.4, 60.)
well_inner = round_front_rect(190., 116., 5.5, -2., 65.)
well = (well_outer - well_inner) & front_halfspace(.8)
bezel = parts['display_bezel'] + well
well_clearance = (round_front_rect(203.6, 132.6, 11.3, -1., 62.) &
                  front_halfspace(1.1))
front_skin = (outer-inner) & left & upper_tub & box(-1,-1,0,W+2,61,H+2)
tub = ((parts['tub_left'] + front_skin) - well_clearance)
bezel_clearance = b.offset(before['display_bezel'], amount=.25)
tub -= bezel_clearance
# Match the shallower band step while retaining the original inner floor,
# screw lands, cooling passages and rear service opening.
band_inner = envelope(3., BASE_Z, BAND_TOP, R_PLAN-3)
band_skin = (band-band_inner) & left & box(-1,-1,0,W+2,142,H+2)
tub += band_skin
tub = (tub & low & band) + (tub & upper_tub & outer)
parts['tub_left'] = tub
parts['display_bezel'] = bezel

# One common roof profile. Keep the removable LEFT electronics lid and its
# four existing fastener axes; the printer retains its integral closed roof.
lid_region = outer & left & box(-1, -1, 185, W+2, D+3, 17)
lid_hollow = inner & box(6, -1, 184.9, SPLIT-12, D-5, 20)
lid = lid_region - lid_hollow
lid += before['top_plate_left'] & box(-1, -1, 179.9, W+2, D+3, 5.1)
front_screw_y = 46. + 20*math.tan(math.radians(14))
lid_screws = [(7., front_screw_y), (SPLIT-7., front_screw_y),
              (7., D-18), (SPLIT-7., D-18)]
for x, y in lid_screws:
    lid += cz(x, y, 185., 8., 13.)
    lid -= cz(x, y, 184., 3.3, 19.)
    lid -= cz(x, y, H-2, 6.5, 3.)
# Keep the rounded front brow integral with the tub. The service-lid front
# joint is now on the flat roof, 26 mm behind the front, with 0.25 mm clearance.
fixed_brow = lid & box(-1, -1, 179, W+2, 27., 24.)
parts['tub_left'] += fixed_brow
lid -= box(-1, -1, 179, W+2, 27.25, 24.)
parts['top_plate_left'] = lid

# Add a curved inner shoulder before trimming the old printer roof to the
# shared envelope; merely shaving the square corner would puncture its skin.
shoulder = (outer-inner) & right & box(-1, -1, 185, W+2, 37, 17)
shell = before['shell'] + shoulder
shell = (shell & upper_tub & outer) + (shell & box(-1, -1, 185, W+2, D+3, 17) & outer) + (shell & low & band)
# The 0.8 mm step leaves 2.2 mm from the original 3 mm front wall, without
# intruding into the already approved cradle or changing hardware datums.
# Re-open the LED aperture in the new front shoulder.
shell -= box(SPLIT+70.3,-1,183.4,40.4,5.,4.9)
shell -= box(SPLIT+68.3,3.02,181.4,44.4,.83,8.9)
parts['shell'] = shell

# The existing rear bars/cover remain mechanically identical. Round the outer
# plan corners of the new shell only; the rear closing panel stays serviceable.
changed = ['tub_left', 'top_plate_left', 'display_bezel', 'shell']
report = {
    'status': 'Actual CAD exterior study, not a print release; no print dispatched.',
    'form': 'Common upright envelope; tilted screen recessed inside; exact shared band and roof datums.',
    'overall_height_mm': H, 'width_mm': W, 'depth_mm': D,
    'outer_plan_radius_mm': R_PLAN, 'top_edge_radius_mm': R_TOP,
    'lower_light_band_z_mm': [BASE_Z, BAND_TOP], 'band_inset_mm': BAND_INSET,
    'module_split_x_mm': SPLIT,
    'assembly': 'Five existing inter-bay M3 fasteners plus two dowels. Fine dry-assembly seam remains; invisible seam needs bonding/filling/finishing.',
    'screen_angle_deg': 14, 'screen_and_printer_positions': 'unchanged from V32',
    'left_lid_joint': {'front_y_mm': 26., 'gap_mm': .25, 'front_brow': 'integral with tub'},
    'parts': {}, 'interferences': [], 'changed_parts': changed,
    'limits': ['Actual display/Pi/cooler/power unverified', 'Print orientations/supports unsliced',
               'Revised shell is for final redesign, not a retrofit to the grey/yellow prototype',
               'Bezel recess requires physical sightline/touch-access assessment'],
}

for name, s in parts.items():
    s.label = name
    s.color = b.Color(NAVY if name in NAVY_PARTS else PALE)
    expected = 1 if name in changed else len(before[name].solids())
    assert s.is_valid and len(s.solids()) == expected, (name, s.is_valid, len(s.solids()))
    bb = s.bounding_box()
    report['parts'][name] = {'valid': True, 'solids': len(s.solids()),
                            'bounds_mm': [list(bb.min), list(bb.max)]}
    if name in changed:
        path = OUT / (name + '_assembly.stl')
        b.export_stl(s, path, tolerance=.035)
        mesh = trimesh.load_mesh(path)
        assert mesh.is_watertight, name
        report['parts'][name]['watertight'] = True

for (an, a), (bn, c) in itertools.combinations(parts.items(), 2):
    ba, bc = a.bounding_box(), c.bounding_box()
    if any(min(getattr(ba.max, k), getattr(bc.max, k)) -
           max(getattr(ba.min, k), getattr(bc.min, k)) < .001 for k in ('X', 'Y', 'Z')):
        continue
    overlap = volume(a.intersect(c))
    if overlap > .1:
        report['interferences'].append([an, bn, overlap])
report['hardware_envelope_clashes_mm3'] = {
    refname: {name: volume(ref.intersect(s)) for name, s in parts.items()}
    for refname, ref in [('display_unverified', display), ('printer_measured_envelope', printer)]}
report['rear_extraction_clashes_mm3'] = {}
printer_sweep = printer + box(SPLIT+19., 124., 16., 143., 161., 175.)
for name in ['shell', 'cradle_tray', 'tub_left', 'top_plate_left']:
    report['rear_extraction_clashes_mm3'][name] = volume(parts[name].intersect(printer_sweep))
report['vent_obstructions_mm3'] = []
for i in range(5):
    probe = box(30.01,148.,140.+4*i+.01,SPLIT-60.02,14.,1.98)
    report['vent_obstructions_mm3'].append(sum(volume(s.intersect(probe)) for s in parts.values()))
report['seam_bore_obstructions_mm3'] = []
for y,z,d in [(25,22,3.3),(50,118,3.3),(76,70,3.3),(140,45,3.3),(140,118,3.3),(35,118,4.2),(140,70,4.2)]:
    probe = b.Pos(SPLIT-1.5,y,z)*b.Rot(0,90,0)*b.Cylinder(d/2,3.2)
    report['seam_bore_obstructions_mm3'].append(volume(parts['tub_left'].intersect(probe)))
report['lid_bore_obstructions_mm3'] = [volume(parts['top_plate_left'].intersect(cz(x,y,185,3.3,17))) for x,y in lid_screws]
(OUT/'audit.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k: report[k] for k in ['interferences','hardware_envelope_clashes_mm3','rear_extraction_clashes_mm3']}, indent=2), flush=True)
assert not report['interferences'], report['interferences']
assert max(v for group in report['hardware_envelope_clashes_mm3'].values() for v in group.values()) < .1
assert max(report['rear_extraction_clashes_mm3'].values()) < .1
assert max(report['vent_obstructions_mm3']) < .01
assert max(report['seam_bore_obstructions_mm3']) < .01
assert max(report['lid_bore_obstructions_mm3']) < .01

b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()],
                        label='LUMON_V33_UNIFIED_BODY_STUDY'), OUT/'whole_enclosure_review.step')
for name, collection, eye, target, explode in [
    ('before_front', before, (555,-745,365), (197,67,109), False),
    ('unified_front', parts, (555,-745,365), (197,67,109), False),
    ('unified_straight_front', parts, (197,-850,170), (197,65,109), False),
    ('unified_rear', parts, (550,820,410), (197,80,109), False),
    ('split_assembly', parts, (570,-820,470), (197,65,113), True),
]:
    sc = Scene(1500, 960, ss=1)
    for part_name, s in collection.items():
        if explode:
            if part_name in {'shell','cradle_tray','retaining_bar_58','retaining_bar_137','rear_cover','logo','led_diffuser','foot_right_bonded'}:
                s = b.Pos(35,0,0)*s
            if part_name == 'top_plate_left':
                s = b.Pos(0,0,32)*s
        sc.add(s, '#4E95AE' if part_name == 'led_diffuser' else NAVY if part_name in NAVY_PARTS else PALE)
    sc.add(display, '#142B35')
    if not explode:
        sc.add(printer, '#32383C')
    sc.look_at(eye,target,fov=32)
    sc.save(str(OUT/(name+'.png')))
print('Saved V33 CAD and previews', flush=True)
