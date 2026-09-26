"""Full-case preparation audit; does not authorize or dispatch a print."""
from pathlib import Path
import json, math, sys
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/output/v50_full_display_preflight';OUT.mkdir(exist_ok=True)
PREV=ROOT/'cad/output/v49_measured_display_depth'
parts={s.label:s for s in b.import_step(PREV/'whole_enclosure_review.step').children}
BASE=33.
def box(x,y,z,w,d,h):return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
def cy(x,y,z,d,h):return b.Pos(x,y+h/2,z)*b.Rot(-90,0,0)*b.Cylinder(d/2,h)
def unrake(s):return b.Pos(0,0,BASE)*b.Rot(25,0,0)*b.Pos(0,0,-BASE)*s
def rake(s):return b.Pos(0,0,BASE)*b.Rot(-25,0,0)*b.Pos(0,0,-BASE)*s
def vol(s):return sum(t.volume for t in s.solids()) if s else 0.
def bounds(s):
 q=s.bounding_box();return {'min':[q.min.X,q.min.Y,q.min.Z],'max':[q.max.X,q.max.Y,q.max.Z],'size':[q.size.X,q.size.Y,q.size.Z]}
report={'parts':{n:{'volume_mm3':vol(s),'bounds_mm':bounds(s)} for n,s in parts.items()},'support_gap_selected_mm':.12,'full_display_mount_physical_test':'V49 corners pass; original full-frame hole XY confirmed separately'}
print(json.dumps(report['parts'],indent=2),flush=True)
body=parts['tub_left'];local=unrake(body)
front_down=b.Rot(90,0,0)*local
bb=front_down.bounding_box()
front_down=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*front_down
report['front_down_orientation']={'bounds_mm':bounds(front_down),'front_panel_height_above_bed_mm':-bb.min.Z,'note':'Tested fixture front-down does not imply the full shell face can lie on the bed. Check lower-front projection.'}
print('Front-down valid:',front_down.is_valid, 'bounds:',bounds(front_down),flush=True)
b.export_stl(front_down,OUT/'display_body_front_down_review.stl',tolerance=.035)
mesh=trimesh.load_mesh(OUT/'display_body_front_down_review.stl');assert mesh.is_watertight
# Straight driver shank follows each screw axis from the existing head recess,
# beyond the shell; roof and rear hatch removed, body remains intact.
centres=json.loads((PREV/'audit.json').read_text())['lug_centres_local_xz']
report['straight_driver_access']={}
for x,z in centres:
 shaft=rake(cy(x,11.401,z,5.5,250))
 hit=body&shaft
 report['straight_driver_access'][f'{x:.2f},{z:.2f}']={'body_obstruction_mm3':vol(hit),'hit_bounds':bounds(hit) if vol(hit)>.01 else None}
# Compact tool can be placed through open roof even where a long external
# rear approach is obstructed. Hardware wiring follows mount fastening.
compact={}
for x,z in centres:
    tool=rake(cy(x,11.401,z,5.5,55)+cy(x,66.4,z,25,45))
    compact[f'{x:.2f},{z:.2f}']={n:vol(tool&p) for n,p in parts.items()
        if n not in ('top_plate_left','rear_panel_left') and vol(tool&p)>.01}
assert not any(compact.values()),compact
report['compact_driver_access']={'shank_length_mm':55,'shank_diameter_mm':5.5,
    'handle_length_mm':45,'handle_diameter_mm':25,'clashes_mm3':compact,
    'scope':'Working position fits, roof removed. Insert compact driver through roof before cabling.'}

# Review view without lid/hatch, inherited PSU/divider kept pending user choice.
sys.path.insert(0,str(ROOT/'files'))
from render3d import Scene
sc=Scene(1100,820,ss=1);sc.add(body,'#EEEEE4');sc.look_at((340,510,330),(109,83,101),fov=31);sc.save(str(OUT/'body_rear_audit.png'))
sc=Scene(1100,820,ss=1);sc.add(front_down,'#EEEEE4');sc.look_at((390,-450,300),(109,120,80),fov=35);sc.save(str(OUT/'body_front_down_audit.png'))
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='parts'},indent=2),flush=True)
