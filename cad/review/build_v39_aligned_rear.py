"""Align both assembled rear faces, roofs and bases; preserve the fitted printer.

Regenerate only the display bay's rear region from its existing parametric CAD.
The retained prefix makes the 25-degree front and its hardware datums exact.
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
from cad import lumon_v29 as m

OUT = ROOT / 'cad/output/v39_aligned_rear'
OUT.mkdir(parents=True, exist_ok=True)
D, OLD_D, CUT, SPLIT, H = 170.75, 161., 135., 218.96, 201.
REAR_R = 9.5
PALE, NAVY = '#F0F1EB', '#173B53'
NAVY_PARTS = {'foot_left', 'foot_right_bonded', 'display_bezel', 'logo'}

def box(x, y, z, w, d, h):
    return b.Pos(x+w/2, y+d/2, z+h/2) * b.Box(w, d, h)

def vol(s):
    return sum(v.volume for v in s.solids()) if s else 0.

def difference(a, c):
    return vol(a-c) + vol(c-a)

def cz(x, y, z, diameter, h):
    return b.Pos(x,y,z+h/2)*b.Cylinder(diameter/2,h)

assembly = b.import_step(ROOT/'cad/output/v38_integrated_rear/whole_enclosure_review.step')
before = {s.label: s for s in assembly.children}
parts = {k: copy.deepcopy(s) for k,s in before.items()}
prefix = box(-1,-10,-1,SPLIT+2,CUT+10,H+3)
suffix = box(-1,CUT,-1,SPLIT+2,D-CUT+2,H+3)

# Keep electronics in their existing locations. Increasing D must not silently
# move the Pi or PSU because their legacy placement properties depend on D.
old_pi_y, old_psu_y = m.p.pi_y, m.p.psu_y
m.P.pi_y = property(lambda self: old_pi_y)
m.P.psu_y = property(lambda self: old_psu_y)
m.p.D, m.p.H, m.p.rake_deg = D, H, 25.
m.p.fillet_main, m.p.band_inset = REAR_R, .8
m.CR, m.SR = math.cos(math.radians(25)), math.sin(math.radians(25))
m.FACE_LEN = (H-m.p.lid_t-m.p.skirt_h)/m.CR
m.DZL = m.p.skirt_h+(m.FACE_LEN-m.p.display_h)/2
m.BEZ_CZ = m.DZL+m.p.display_h/2

tub = m.build_tub_left()
# Preserve the raised exhaust slots, separate from the lower service hatch.
tub += m.box_at(30,D-3,120,SPLIT-60,3,18)
for i in range(5):
    tub -= m.box_at(30,D-4,140+i*4,SPLIT-60,5,2)
parts['tub_left'] = (before['tub_left'] & prefix) + (tub & suffix)

# Flat rear roof, with the same 9.5mm outer rear radius as the printer cap.
# The existing rounded/sloped front is retained verbatim up to Y135.
outer = m.plate_region('left',0,185,16,REAR_R)
inner = m.plate_region('left',6,184.9,12.6,REAR_R-6)
inner &= box(-1,-1,184,SPLIT-5,D+3,20)
lid = outer-inner
o = m.p.wall+m.p.fit_clear
lid += box(m.p.wall+REAR_R,D-o-2.4,180,
           SPLIT-m.p.wall-m.p.fit_clear-(m.p.wall+REAR_R),2.4,5)
rear_roof_axes = [(7,D-18),(SPLIT-7,D-18)]
for x,y in rear_roof_axes:
    lid += cz(x,y,185,8,13)
    lid -= cz(x,y,184,3.3,19)
    lid -= cz(x,y,199,6.5,3)
parts['top_plate_left'] = (before['top_plate_left'] & prefix) + (lid & suffix)
parts['rear_panel_left'] = b.Pos(0,D-OLD_D,0)*before['rear_panel_left']
foot = m.build_foot('left')
parts['foot_left'] = (before['foot_left'] & prefix) + (foot & suffix)
changed = ['tub_left','top_plate_left','rear_panel_left','foot_left']

report = {'status':'CAD verification underway; not printed',
          'common_rear_y_mm':D,'extension_mm':D-OLD_D,
          'common_base_rear_y_mm':D-2.5,'rear_corner_radius_mm':REAR_R,
          'base_rear_corner_radius_mm':REAR_R-2.5,
          'display_angle_deg':25,'changed_parts':changed,
          'pi_psu_positions':'unchanged; depth-derived placement frozen',
          'rear_hatch_iec_roof_mounts':'moved back9.75mm together',
          'interferences':[],'parts':{},'prefix_difference_mm3':{}}
for name,s in parts.items():
    s.label=name
    s.color=b.Color(NAVY if name in NAVY_PARTS else PALE)
    assert s.is_valid and len(s.solids())==len(before[name].solids()), name
    if name in changed:
        path=OUT/(name+'_assembly.stl')
        b.export_stl(s,path,tolerance=.035)
        assert trimesh.load_mesh(path).is_watertight,name
        if name!='rear_panel_left':
            delta=difference(s & prefix,before[name] & prefix)
            report['prefix_difference_mm3'][name]=delta
            assert delta<.01,(name,delta)
    else:
        assert difference(s,before[name])<.01,name
    bb=s.bounding_box()
    report['parts'][name]={'valid':True,'solids':len(s.solids()),
                          'bounds_mm':[list(bb.min),list(bb.max)]}

for (an,a),(cn,c) in itertools.combinations(parts.items(),2):
    ab,cb=a.bounding_box(),c.bounding_box()
    if any(min(getattr(ab.max,k),getattr(cb.max,k))-
           max(getattr(ab.min,k),getattr(cb.min,k))<.001 for k in ('X','Y','Z')):
        continue
    hit=vol(a & c)
    if hit>.1:report['interferences'].append([an,cn,hit])

display=b.import_step(ROOT/'cad/output/v35_desktop_terminal/display_reference.step')
printer=b.Pos(SPLIT,0,0)*b.import_step(ROOT/'cad/output/v28_integrated_top/printer_reference.step')
refs={'display':display,'printer':printer,'Pi':m.PI_REFERENCE,
      'PSU':m.PSU_REFERENCE,'buck':m.BUCK_REFERENCE,
      'IEC':b.Pos(0,D-OLD_D,0)*m.IEC_REFERENCE}
report['hardware_clashes_mm3']={name:{part:vol(ref & s) for part,s in parts.items()}
                                for name,ref in refs.items()}
report['vent_obstructions_mm3']=[]
for i in range(5):
    probe=box(30.01,D-13,140+4*i+.01,SPLIT-60.02,14,1.98)
    report['vent_obstructions_mm3'].append(sum(vol(probe&s) for s in parts.values()))
report['joint_land_fractions']=[]
for y,z in [(25,22),(50,118),(76,70),(140,45),(140,118)]:
    ring=b.Pos(SPLIT-1.5,y,z)*b.Rot(0,90,0)*(b.Cylinder(3,2.8)-b.Cylinder(1.7,3))
    fraction=vol(parts['tub_left']&ring)/ring.volume
    report['joint_land_fractions'].append(fraction)
    assert fraction>.99,(y,z,fraction)
for x,y in rear_roof_axes:
    assert vol(parts['top_plate_left'] & cz(x,y,185,3.29,17))<.01
    ring=cz(x,y,184.5,8,.4)-cz(x,y,184.49,4.21,.42)
    assert vol(parts['tub_left']&ring)/ring.volume>.999
for x in (55,SPLIT-28):
    y=D-9
    assert vol(parts['foot_left']&cz(x,y,0,3.39,9))<.01
    assert vol(parts['tub_left']&cz(x,y,9.01,4.19,5.98))<.01
for name in ['tub_left','top_plate_left','rear_panel_left','rear_cover_integrated']:
    assert abs(parts[name].bounding_box().max.Y-D)<.001,name
for name in ['foot_left','foot_right_bonded']:
    assert abs(parts[name].bounding_box().max.Y-(D-2.5))<.001,name
# Rear removal of printer cover remains unobstructed by the extended left bay.
for dy in (.1,1,10,50,100):
    shifted=b.Pos(0,dy,0)*parts['rear_cover_integrated']
    for name in ['tub_left','top_plate_left','foot_left']:
        assert vol(shifted & parts[name])<.01,(dy,name)
report['printer_components_unchanged']=True
report['rear_roof_axes_xy_mm']=rear_roof_axes
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['interferences','hardware_clashes_mm3','vent_obstructions_mm3']},indent=2),flush=True)
assert not report['interferences'],report['interferences']
assert max(v for group in report['hardware_clashes_mm3'].values() for v in group.values())<.1
assert max(report['vent_obstructions_mm3'])<.01
report['status']='CAD checks passed; left physical hardware fit unverified; Fusion update and Bambu preparation pending'
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
b.export_step(b.Compound(children=list(parts.values()),label='LUMON_V39_ALIGNED_REAR'),OUT/'whole_enclosure_review.step')
for name in changed:
    standalone=copy.deepcopy(parts[name])
    standalone.parent=None
    b.export_step(standalone,OUT/(name+'.step'))
for name,eye in [('aligned_rear',(520,840,400)),('aligned_front',(550,-745,360)),('aligned_roof',(450,480,780))]:
    sc=Scene(1500,1000,ss=1)
    for k,s in parts.items():sc.add(s,NAVY if k in NAVY_PARTS else PALE)
    sc.add(display,'#142B35')
    sc.look_at(eye,(197,80,108),fov=32)
    sc.save(str(OUT/(name+'.png')))
print('V39 aligned rear ready',flush=True)
