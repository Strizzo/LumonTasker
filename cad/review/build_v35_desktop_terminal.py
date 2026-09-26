"""25-degree desktop terminal study with connected roofs and shared base.

Printer geometry stays at V34; display and front lid lands move. Left hardware and print supports
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

OUT = ROOT / 'cad/output/v35_desktop_terminal'
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


old = b.import_step(ROOT / 'cad/output/v34_sloped_connected_roof/whole_enclosure_review.step')
before = {s.label:s for s in old.children}
parts = {k:copy.deepcopy(s) for k,s in before.items()}
old_display = b.import_step(ROOT/'cad/output/v32_equal_height/display_reference.step')
printer = b.Pos(SPLIT,0,0)*b.import_step(ROOT/'cad/output/v28_integrated_top/printer_reference.step')
sys.path.insert(0,str(ROOT))
from cad import lumon_v29 as m
m.p.H=H
m.p.rake_deg=25.
m.CR=math.cos(math.radians(m.p.rake_deg))
m.SR=math.sin(math.radians(m.p.rake_deg))
m.FACE_LEN=(m.p.H-m.p.lid_t-m.p.skirt_h)/m.CR
m.DZL=m.p.skirt_h+(m.FACE_LEN-m.p.display_h)/2
m.BEZ_CZ=m.DZL+m.p.display_h/2
# Move the front lands with the upper raked wall; retain their previous
# distance behind that wall. Rear screw axes and all printer parts stay put.
front_screw_y=46+20*math.tan(math.radians(14))+(H-16-BAND_TOP)*(math.tan(math.radians(25))-math.tan(math.radians(14)))
original_add_lands=m.add_lid_lands
def add_lands(tub,side):
    m.LID_SCREWS_L=[(x,front_screw_y if y==46 else y) for x,y in m.LID_SCREWS_L]
    return original_add_lands(tub,side)
m.add_lid_lands=add_lands
tub=m.build_tub_left()
# Retain the V34 band and V32 raised exhaust positions.
tub += m.box_at(30,m.p.D-m.p.wall,120,m.p.x_split-60,m.p.wall,18)
for i in range(5):
    tub -= m.box_at(30,m.p.D-m.p.wall-1,140+i*4,m.p.x_split-60,m.p.wall+2,2)
parts['tub_left']=(tub & box(-1,-1,33,W+2,D+3,H))+(before['tub_left'] & box(-1,-1,9,W+2,D+3,24))
parts['display_bezel']=m.build_display_bezel()
parts['display_retainer']=m.build_retainer()
# Small clearance notch at the front corner of the inherited PSU divider.
# Relieve the retainer, not the divider; no change to the hardware layout.
# The contact was x76.96..79.96, y40..40.79, z52.53..54.60 at 25 degrees.
parts['display_retainer'] -= box(m.p.partition_x-.6,39.4,51.9,m.p.partition_t+1.2,2.,3.3)
display=m.raked(m.box_at(m.p.display_x,m.p.wall,m.DZL,m.p.display_w,m.p.display_t,m.p.display_h))

lid_outer = m.plate_region('left',0.,185.,16.,14.) - m.front_solid(0.)
# Continue the existing 3 mm sloped outer-left corner into the lid.
front_corner = [e for e in lid_outer.edges() if e.geom_type == b.GeomType.LINE
                and abs(e.center().X)<.001 and e.center().Y<110 and 15<e.length<18]
assert len(front_corner)==1, len(front_corner)
lid_outer = b.fillet(front_corner,3.)
angle = math.radians(25)
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
lid_screws=[(7.,front_screw_y),(SPLIT-7.,front_screw_y),(7.,D-18),(SPLIT-7.,D-18)]
for x,y in lid_screws:
    lid+=cz(x,y,185,8.,13.)
    lid-=cz(x,y,184.,3.3,19.)
    lid-=cz(x,y,199.,6.5,3.)
parts['top_plate_left']=lid
changed=['tub_left','top_plate_left','display_bezel','display_retainer']
report={
 'status':'CAD form review only; not sliced or physically fitted.',
 'form':'Desktop terminal: screen and surrounding face at 25 degrees; connected planar roofs and common base.',
 'height_mm':201., 'display_angle_deg':25., 'exposed_front_roof_radius_mm':12.,
 'roof_join':'Flat z201 surface across x218.96 behind the display front roll; fine assembly seam remains.',
 'left_roof_front_roll_ends_y_mm':cy,
 'changed_parts':changed,'parts':{},'interferences':[],
 'preserved':'Exact V34 printer assembly and base; display and its mounts regenerated together.',
 'front_lid_screw_y_mm':front_screw_y,
 'screen_centre_displacement_mm':list(display.center()-old_display.center()),
 'front_alignment_dowel':'The former y35,z118 pin lies ahead of the steeper left wall. Omit this pin; five M3 axes and rear alignment dowel remain.',
 'retainer_relief_mm':{'x':76.36,'y':39.4,'z':51.9,'width':4.2,'depth':2.,'height':3.3},
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
# Hardware layout is inherited and unverified: report the actual envelope
# checks, without turning them into a physical-fit claim.
report['display_to_electronics_clearance_mm']={}
for name,ref in [('Pi',m.PI_REFERENCE),('PSU',m.PSU_REFERENCE),('buck',m.BUCK_REFERENCE),('IEC',m.IEC_REFERENCE)]:
    hit=volume(display.intersect(ref))+volume(parts['display_retainer'].intersect(ref))
    report['display_to_electronics_clearance_mm'][name]={'intersection_mm3':hit,'display_distance_mm':display.distance_to(ref),'retainer_distance_mm':parts['display_retainer'].distance_to(ref)}
    assert hit<.1,(name,hit)
# The five screw axes must still have a complete supporting annulus, rather
# than merely passing a bore-clearance check in empty space.
report['joint_screw_land_fraction']=[]
for y,z in [(25,22),(50,118),(76,70),(140,45),(140,118)]:
    outer=b.Pos(SPLIT-1.5,y,z)*b.Rot(0,90,0)*b.Cylinder(3.,2.8)
    hole=b.Pos(SPLIT-1.5,y,z)*b.Rot(0,90,0)*b.Cylinder(1.7,3.)
    ring=outer-hole
    fraction=volume(parts['tub_left'].intersect(ring))/ring.volume
    report['joint_screw_land_fraction'].append(fraction)
    assert fraction>.99,(y,z,fraction)
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
                        label='LUMON_V35_DESKTOP_TERMINAL_25DEG'), OUT/'whole_enclosure_review.step')
display.label='REFERENCE_ONLY_unverified_display_25deg'
b.export_step(display,OUT/'display_reference.step')
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
print('V35 desktop terminal 25 degree CAD ready',flush=True)
