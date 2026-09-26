"""Front-output mechanical prototype; local right-module coordinates in mm.
Measured printer envelope, integral front surround, removable flat cradle.
Native printer is not disassembled. References are boxes, not lid-sweep models.
"""
from pathlib import Path
import sys,json,copy
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'files'))
from render3d import Scene
OUT=ROOT/'cad/output/v20_integral_front';OUT.mkdir(exist_ok=True)
W,D,H=158.,161.,201.
def box(x,y,z,w,d,h):return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
def cy(x,y,z,d,l):return b.Pos(x,y+l/2,z)*b.Rot(-90,0,0)*b.Cylinder(d/2,l)
def cx(x,y,z,d,l):return b.Pos(x+l/2,y,z)*b.Rot(0,90,0)*b.Cylinder(d/2,l)
def cz(x,y,z,d,l):return b.Pos(x,y,z+l/2)*b.Cylinder(d/2,l)
# Floor + uninterrupted seam wall + outer side. Rear open above low sill.
shell=box(0,3,9,W,D-3,4)+box(0,3,9,9,D-3,H-13)+box(W-3,3,9,3,D-3,H-13)+box(0,D-3,9,W,3,21)
# Continuous front reinforcement, united with the integral surround.
shell += box(W-9,3,9,9,9,H-13)
# Existing v19 spine interface retained, independent of printer body.
for y,z in [(25,22),(50,118),(76,70),(140,45),(140,118)]:shell-=cx(-.1,y,z,4.2,6.3)
for y,z in [(35,118),(140,70)]:shell-=cx(-.1,y,z,4.3,8.7)
# Floor-level inter-bay cable opening, open from below to avoid a bridge.
shell-=box(-1,126,8,11,20,22)
# Rear corner columns retain separate rear cover and top, clear of hardware.
for x in (9,W-12):shell+=box(x,D-12,9,3,12,H-13)
for x in (13.5,W-7.5):
 shell+=box(x-4.5,D-15,9,9,12,H-13)
 shell-=cz(x,D-8,190.7,4.2,6.4)
 for z in (40,180):shell-=cy(x,D-6.3,z,4.2,6.4)
# Sliding tray rests on floor. Four clearance holes lie outside measured body.
tray=box(9.5,3.5,13,145,134,3)
tray-=box(W-9.5,3,12.9,10,9.5,3.2)
for x in (28,W-28):
 shell+=box(x-5,129,9,10,11,7)
 shell-=cz(x,134,9.7,4.2,6.4)
 tray-=box(x-5.3,128.7,12.9,10.6,11.6,3.2)
# A rear tray crossbar screwed to floor lands holds the tray; removable.
stop=box(20,130,16,W-40,9,3)
for x in (28,W-28):stop-=cz(x,134,15.9,3.4,3.2)
# Integral front: no front fasteners or parting seam. Service from top/rear.
# Keep the large opening until the native cutter/control positions are measured.
front=box(0,0,9,W,3,H-13)-box(13.5,-1,15,137,5,178)
shell += front
top=box(0,0,H-4,W,D,4)
for x in (13.5,W-7.5):top-=cz(x,D-8,H-4.1,3.4,4.2)
# Rear cover has bottom-open cable notch; cable routing remains accessible.
rear=box(9.3,D,29.7,W-12.6,3,H-33)-box(49,D-1,29,60,5,35)
for x in (13.5,W-7.5):
 for z in (40,180):rear-=cy(x,D-.1,z,3.4,3.2)
printer=box(16.5,4,16,131,120,175)
parts={'shell':shell,'cradle_tray':tray,'tray_stop':stop,'top_cover':top,'rear_cover':rear}
colors={k:'#DEE9EE' for k in parts}
report={'status':'mechanical prototype; slicer and lid sweep checks pending','printer_mm':[131,120,175],'parts':{},'interferences':[]}
children=[]
for name,s in parts.items():
 assert s.is_valid and len(s.solids())==1,(name,len(s.solids()))
 c=copy.deepcopy(s);c.label=name;c.color=b.Color(colors[name]);children.append(c)
 oriented=b.Rot(90,0,0)*s if name=='rear_cover' else s
 bb=oriented.bounding_box();oriented=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*oriented
 path=OUT/(name+'.stl');b.export_stl(oriented,path,tolerance=.03)
 mesh=trimesh.load_mesh(path);assert mesh.is_watertight,name
 report['parts'][name]={'single_solid':True,'watertight':True,'print_bounds_mm':mesh.extents.tolist(),'volume_mm3':s.volume}
for i,(an,a) in enumerate(list(parts.items())):
 for bn,v in list(parts.items())[i+1:]+[('printer_reference',printer)]:
  intersection=a.intersect(v);vol=sum(s.volume for s in intersection.solids()) if intersection else 0
  if vol>.05:report['interferences'].append({'a':an,'b':bn,'mm3':vol})
(OUT/'checks.json').write_text(json.dumps(report,indent=2))
assert not report['interferences'],report['interferences']
# Conservative straight-up removal check using the whole measured body box.
# Top cover must be removed and cables/mounting bracket released first.
sweep=box(16.5,4,16,131,120,175+H)
for name in ('shell','cradle_tray','tray_stop','rear_cover'):
 hit=parts[name].intersect(sweep)
 assert not hit or sum(s.volume for s in hit.solids())<.05,('removal blocked',name)
report['top_removal_envelope_clear']=True
(OUT/'checks.json').write_text(json.dumps(report,indent=2))
b.export_step(b.Compound(children=children,label='V20_FRONT_MECHANICAL_PROTOTYPE'),OUT/'front_output_prototype.step')
ref=copy.deepcopy(printer);ref.label='MEASURED_PRINTER_ENVELOPE_NOT_FOR_PRINT';b.export_step(ref,OUT/'printer_reference.step')
for exploded in (False,True):
 sc=Scene(1100,850,ss=1)
 for k,s in parts.items():
  if exploded:
   s=b.Pos(0,0,45)*s if k=='top_cover' else b.Pos(0,40,0)*s if k=='rear_cover' else s
  sc.add(s,colors[k])
 if not exploded:sc.add(printer,'#656A70')
 sc.look_at((410,-570,370),(79,65,108),fov=30);sc.save(str(OUT/('exploded.png' if exploded else 'assembly.png')))
print(json.dumps(report,indent=2),flush=True)
