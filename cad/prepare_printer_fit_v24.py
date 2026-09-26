"""Small single-colour printer fit samples; preparation only, no print dispatch."""
from pathlib import Path
import sys,json
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'files'))
from render3d import Scene
OUT=ROOT/'cad/output/v24_printer_fit';OUT.mkdir(exist_ok=True)
def box(x,y,z,w,d,h):return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
# Front template in flat printing coordinates: y=0 is printer upper edge.
# 56mm provisionally denotes upper edge of aperture; centre interpretation is 49mm.
def template(offset):
 s=box(0,0,0,131,6,3)+box(0,0,0,6,offset+20,3)+box(125,0,0,6,offset+20,3)
 s+=box(0,offset-5,0,131,24,3)
 s-=box(20.5,offset,-1,90,14,5)
 # Centre V at datum edge is away from rounded printer corners.
 notch=b.extrude(b.Polygon((63.5,0),(67.5,0),(65.5,2),align=None),amount=4)
 return s-notch
# Actual cross-section of existing tray, not a guessed tolerance sample.
assy=b.import_step(ROOT/'cad/output/v23_upper_output/printer_bay.step')
tray=next(s for s in assy.children if s.label=='cradle_tray')
gauge=b.Compound(children=list(tray.intersect(box(0,30,0,158,16,40))));bb=gauge.bounding_box();gauge=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*gauge
parts={'front_template_upper_edge_56':template(56),'front_template_centre_56_ALTERNATIVE':template(49),'cradle_width_sample':gauge}
report={'status':'PREPARATION ONLY — no print dispatch','offset_datum':'awaiting upper-edge vs centre clarification','parts':{}}
for name,s in parts.items():
 assert s.is_valid and len(s.solids())==1,name
 b.export_stl(s,OUT/(name+'.stl'),tolerance=.03);b.export_step(s,OUT/(name+'.step'))
 m=trimesh.load_mesh(OUT/(name+'.stl'));assert m.is_watertight
 report['parts'][name]={'watertight':True,'solids':1,'bounds_mm':m.extents.tolist(),'solid_volume_cm3':round(s.volume/1000,2)}
# Nominal aperture and guide clearance checks.
assert abs(gauge.volume- (141*16*3+2*16*17*2))<.01
report['cradle_guide_gap_mm']=133;report['printer_width_mm']=131
report['template_aperture_mm']=[90,14];report['template_thickness_mm']=3
(OUT/'checks.json').write_text(json.dumps(report,indent=2))
sc=Scene(1100,760,ss=1)
sc.add(parts['front_template_upper_edge_56'],'#DEE9EE');sc.add(b.Pos(0,95,0)*gauge,'#DEE9EE')
sc.look_at((200,-200,310),(65,52,0),fov=33);sc.save(str(OUT/'samples.png'))
print(json.dumps(report,indent=2))
