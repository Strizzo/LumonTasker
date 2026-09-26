"""Restore sloped display face; connect roof planes without a rounded seam valley.

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

OUT = ROOT / 'cad/output/v34_sloped_connected_roof'
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
parts = {k: copy.deepcopy(s) for k,s in before.items()}
v33 = {s.label:s for s in b.import_step(ROOT/'cad/output/v33_unified_body/whole_enclosure_review.step').children}
display = b.import_step(ROOT/'cad/output/v32_equal_height/display_reference.step')
printer = b.Pos(SPLIT,0,0)*b.import_step(ROOT/'cad/output/v28_integrated_top/printer_reference.step')
# Keep the accepted common lower band, but restore the exact sloped front,
# original bezel and all its mounts above the band. No vertical facade or well.
parts['tub_left'] = ((before['tub_left'] & box(-1,-1,33,W+2,D+3,H)) +
                     (v33['tub_left'] & box(-1,-1,9,W+2,D+3,24)))
parts['shell'] = copy.deepcopy(v33['shell'])

# Left roof is planar all the way to the printer seam. Only the exposed
# sloping front edge rolls into the top; never fillet the joining edge.
sys.path.insert(0,str(ROOT))
from cad import lumon_v29 as m
m.p.H = H
lid_outer = m.plate_region('left',0.,185.,16.,14.) - m.front_solid(0.)
# Continue the existing 3 mm sloped outer-left corner into the lid.
front_corner = [e for e in lid_outer.edges() if e.geom_type == b.GeomType.LINE
                and abs(e.center().X)<.001 and e.center().Y<60 and 15<e.length<18]
assert len(front_corner)==1, len(front_corner)
lid_outer = b.fillet(front_corner,3.)
angle = math.radians(14)
cy = (H-R_TOP-BAND_TOP)*math.tan(angle)+R_TOP/math.cos(angle)
cz_roof = H-R_TOP

def roll_front(s, radius):
    tangent_z = cz_roof+radius*math.sin(angle)
    corner = box(-1,-100,tangent_z,W+2,cy+100,H-tangent_z+1)
    cylinder = b.Pos(W/2,cy,cz_roof)*b.Rot(0,90,0)*b.Cylinder(radius,W+4)
    return s-(corner-cylinder)

lid_outer=roll_front(lid_outer,R_TOP)
hollow=(m.plate_region('left',6.,184.9,12.6,8.)-m.front_solid(6.))
hollow &= box(-1,-1,184.,SPLIT-5.,D+3,20.)
hollow=roll_front(hollow,8.5)
lid=lid_outer-hollow
# Preserve the existing rear locating skirt and screw axes.
lid += before['top_plate_left'] & box(-1,-1,179.9,W+2,D+3,5.1)
front_screw_y=46+20*math.tan(angle)
lid_screws=[(7.,front_screw_y),(SPLIT-7.,front_screw_y),(7.,D-18),(SPLIT-7.,D-18)]
for x,y in lid_screws:
    lid+=cz(x,y,185,8.,13.)
    lid-=cz(x,y,184.,3.3,19.)
    lid-=cz(x,y,199.,6.5,3.)
parts['top_plate_left']=lid
changed=['tub_left','top_plate_left','shell']
report={
 'status':'CAD form review only; not sliced or physically fitted.',
 'form':'Original sloping display face and bezel restored; planar connected roofs, no fillet along internal seam.',
 'height_mm':201., 'display_angle_deg':14., 'exposed_front_roof_radius_mm':12.,
 'roof_join':'Flat z201 surface across x218.96 behind the display front roll; fine assembly seam remains.',
 'left_roof_front_roll_ends_y_mm':cy,
 'changed_parts':changed,'parts':{},'interferences':[],
 'preserved':'V32 screen position, bezel, supports, cradle/bars and all hardware datums.',
 'limits':['Left hardware unverified','Print supports/orientation unsliced','Fine assembly seam needs finishing to become invisible'],
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

# Both roofs occupy the same plane at the join, without an inward radius.
roof_probe=box(SPLIT-.8,cy+2,H-.5,1.6,D-cy-4,.4)
roof_coverage=volume(parts['top_plate_left'].intersect(roof_probe))+volume(parts['shell'].intersect(roof_probe))
assert abs(roof_coverage-roof_probe.volume)<.01, (roof_coverage,roof_probe.volume)
report['roof_join_coverage_mm3']={'actual':roof_coverage,'expected':roof_probe.volume}
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()],
                        label='LUMON_V34_SLOPED_CONNECTED_ROOF'), OUT/'whole_enclosure_review.step')
for name,eye,target in [
 ('sloped_front',(555,-745,365),(197,67,109)),
 ('sloped_roof',(490,-550,590),(197,67,109)),
 ('sloped_rear',(550,820,410),(197,80,109)),
]:
 sc=Scene(1500,960,ss=1)
 for k,s in parts.items():
  sc.add(s,'#4E95AE' if k=='led_diffuser' else NAVY if k in NAVY_PARTS else PALE)
 sc.add(display,'#142B35');sc.add(printer,'#32383C')
 sc.look_at(eye,target,fov=32);sc.save(str(OUT/(name+'.png')))
print('V34 saved: restored sloped face, connected roof',flush=True)
