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
OUT=ROOT/'cad/output/v23_upper_output';OUT.mkdir(exist_ok=True)
W,D,H=158.,161.,201.
def box(x,y,z,w,d,h):return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
def cy(x,y,z,d,l):return b.Pos(x,y+l/2,z)*b.Rot(-90,0,0)*b.Cylinder(d/2,l)
def cx(x,y,z,d,l):return b.Pos(x+l/2,y,z)*b.Rot(0,90,0)*b.Cylinder(d/2,l)
def cz(x,y,z,d,l):return b.Pos(x,y,z+l/2)*b.Cylinder(d/2,l)
# Floor + uninterrupted seam wall + outer side. Rear open above low sill.
shell=box(0,3,9,W,D-3,4)+box(0,3,9,9,D-3,H-13)+box(W-3,3,9,3,D-3,H-13)
# Continuous front reinforcement, united with the integral surround.
shell += box(W-9,3,9,9,9,H-13)
# Existing v19 spine interface retained, independent of printer body.
for y,z in [(25,22),(50,118),(76,70),(140,45),(140,118)]:shell-=cx(-.1,y,z,4.2,6.3)
for y,z in [(35,118),(140,70)]:shell-=cx(-.1,y,z,4.3,8.7)
# Floor-level inter-bay cable opening, open from below to avoid a bridge.
shell-=box(-1,126,8,11,20,22)
# Rear rails lie outside the full straight insertion envelope.
rear_x=(4.5,W-4.5)
for x in rear_x:
 shell+=box(x-4.5,D-20,9,9,20,H-13)
 shell-=cz(x,D-8,190.7,4.2,6.4)
 for z in (40,180):shell-=cy(x,D-6.3,z,4.2,6.4)
 for z in (58,137):shell-=cy(x,D-6.3,z,4.2,6.4)
# 45-degree ramp into the thicker right rear rail for front-face-down printing.
shell += b.Pos(0,0,9)*b.extrude(b.Polygon((149,141),(155,135),(155,141),align=None),amount=H-13)
# Tray floor provides a continuous loading surface. Side guides leave 1mm
# clearance to the widest rectangular body envelope, so corner radii need not match.
tray=box(9.5,3.5,13,139,157,3)
tray-=box(W-9.5,3,12.9,10,9.5,3.2)
for x in (13.5,148.5):tray+=box(x,12.5,13,2,112,20)
# Open-ended cable relief beneath the native rear/connector edge.
# Side strips support the casing, leaving the unknown connector bay unobstructed.
tray-=box(40,95,12,78,67,5)
shell-=box(40,95,8,78,67,6)
# Right guide extends to 150.5, so it stops before the rear fastening rail.
# Captive rear bars prevent withdrawal without depending on friction.
bars={}
for z in (58,137):
 bar=box(0,D,z-7,W,6,14)
 for x in rear_x:bar-=cy(x,D-.1,z,3.4,6.2)
 for x in (25,122):bar+=box(x,124.5,z-7,11,D-124.5+.1,14)
 bars['retaining_bar_'+str(z)]=bar
# Integral front: no front fasteners or parting seam. Service from top/rear.
# Upper-face opening reflects the previous opening about the printer body mid-height.
# Original front/buttons are now above; original rear/cable edge below.
# It intentionally exposes a generous region, not a precision guessed paper slot.
front=box(0,0,9,W,3,H-13)-box(18.5,-1,101,127,5,88)
shell += front
# Soften exposed outer-right corners while preserving the flat seam interface.
corner=box(W-6,0,8,6,6,H)-cz(W-6,6,8,12,H)
shell-=corner
# Registered artwork, flush 0.8mm inlay, prints in the first four 0.2mm layers.
logo=b.Pos(79-297.96,0,57-62)*b.import_step(ROOT/'cad/review/logo_v18.step')
shell-=logo
top=box(0,0,H-4,W,D,4)
top-=corner
for x in rear_x:top-=cz(x,D-8,H-4.1,3.4,4.2)
# Rear cover has a bottom-open cable exit, below the lower retaining bar.
# Native rear/cable edge is now below; actual connector bends need a fit trial.
rear=box(0,D+6.5,9,W,3,H-13)-box(40,D+6,8,78,5,39)
for x in rear_x:
 for z in (40,180):rear-=cy(x,D-.1,z,3.4,3.2)
 for z in (40,180):
  rear+=box(x-4,D,z-4,8,6.6,8)
  rear-=cy(x,D-.1,z,3.4,10)
printer=box(16.5,4,16,131,120,175)
parts={'shell':shell,'cradle_tray':tray,**bars,'top_cover':top,'rear_cover':rear,'logo':logo}
colors={k:'#DEE9EE' for k in parts}
colors['logo']='#173B53'
report={'status':'mechanical prototype; slicer, outlet and cable checks pending','printer_mm':[131,120,175],'orientation':'original front/buttons above; original rear/cable edge below','front_aperture_z_mm':[101,189],'logo_center_z_mm':57,'cable_route':'lower rear; connector geometry unmeasured','parts':{},'interferences':[]}
children=[]
for name,s in parts.items():
 assert s.is_valid and (name=='logo' or len(s.solids())==1),(name,len(s.solids()))
 c=copy.deepcopy(s);c.label=name;c.color=b.Color(colors[name]);children.append(c)
 oriented=b.Rot(90,0,0)*s if name in ('shell','logo','rear_cover') else b.Rot(-90,0,0)*s if name.startswith('retaining_bar') else s
 bb=oriented.bounding_box();oriented=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*oriented
 path=OUT/(name+'.stl');b.export_stl(oriented,path,tolerance=.03)
 if name in ('shell','logo'):
  # Common transform, preserving registration for the multi-material shell.
  b.export_stl(b.Pos(0,H-4,0)*b.Rot(90,0,0)*s,OUT/(name+'_registered.stl'),tolerance=.03)
 mesh=trimesh.load_mesh(path);assert mesh.is_watertight,name
 report['parts'][name]={'solids':len(s.solids()),'watertight':True,'print_bounds_mm':mesh.extents.tolist(),'volume_mm3':s.volume}
for i,(an,a) in enumerate(list(parts.items())):
 for bn,v in list(parts.items())[i+1:]+[('printer_reference',printer)]:
  intersection=a.intersect(v);vol=sum(s.volume for s in intersection.solids()) if intersection else 0
  if vol>.05:report['interferences'].append({'a':an,'b':bn,'mm3':vol})
(OUT/'checks.json').write_text(json.dumps(report,indent=2))
assert not report['interferences'],report['interferences']
# Full rearward swept body, with rear cover and retaining bars removed.
# Top remains fitted; no corner-radius matching or interference fit is used.
sweep=box(16.5,4,16,131,120+D,175)
for name in ('shell','cradle_tray','top_cover'):
 hit=parts[name].intersect(sweep)
 assert not hit or sum(s.volume for s in hit.solids())<.05,('removal blocked',name)
report['rear_removal_envelope_clear']=True
(OUT/'checks.json').write_text(json.dumps(report,indent=2))
b.export_step(b.Compound(children=children,label='V23_UPPER_FRONT_OUTPUT_PRINTER_BAY'),OUT/'printer_bay.step')
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
sc=Scene(1100,850,ss=1)
for k,s in parts.items():
 if k!='rear_cover':sc.add(s,colors[k])
sc.add(printer,'#656A70')
sc.look_at((390,590,340),(79,90,105),fov=30)
sc.save(str(OUT/'rear_retention.png'))
