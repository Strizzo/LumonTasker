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
OUT=ROOT/'cad/output/v26_double_taper_printer';OUT.mkdir(exist_ok=True)
W,D,H=175.,161.,201.
CENTER_X=90.5
FRONT_WIDTH,REAR_WIDTH=132.,143.
# User-authorized taper approximation: 60% lower/switch face, 40% upper.
LOWER_DELTA,UPPER_DELTA=5.4,3.6
FRONT_TOP=191-UPPER_DELTA
OUTLET_Z=FRONT_TOP-60
LED_TOP=FRONT_TOP-2
# Profile points are (new front/back Y, height Z), extruded along width.
def prism(x,width,points):
 return b.Pos(x,0,0)*b.extrude(b.Plane.YZ*b.Polygon(*points,align=None),amount=width)

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
shell += b.Pos(0,0,9)*b.extrude(b.Polygon((W-9,141),(W-3,135),(W-3,141),align=None),amount=H-13)
# Tray floor provides a continuous loading surface. Side guides leave 1mm
# clearance on each side of the estimated tapered envelope.
tray=box(9.5,3.5,13,W-19,157,3)
tray-=box(W-9.5,3,12.9,10,9.5,3.2)
# Symmetric lateral taper is provisional: 5.5mm per side over 120mm.
# 1mm side clearance; guides widen toward the rear for straight withdrawal.
for poly in [((21.5,4),(23.5,4),(18,124),(16,124)),
             ((157.5,4),(159.5,4),(165,124),(163,124))]:
 tray+=b.Pos(0,0,13)*b.extrude(b.Polygon(*poly,align=None),amount=20)
# Open-ended cable relief beneath the native rear/connector edge.
# Side strips support the casing, leaving the unknown connector bay unobstructed.
tray-=box(40,95,12,78,67,5)
shell-=box(40,95,8,78,67,6)
# Shallow longitudinal rails follow the estimated lower slope. Narrow lands
# avoid the switch, cable bay and reliance on a full flat contact surface.
for x in (25,148):
 tray+=prism(x,8,[(4,15.9),(124,15.9),(124,16),(4,21.4)])
# Rocker no-contact channel: 2mm lateral margins, open to rear insertion.
# x is interpreted from user's above-view with the enclosure front at page top.
rocker_channel=box(35,67,0,31,100,24)
tray-=rocker_channel
shell-=rocker_channel
# Rear guides end before the rear fastening rails.
# Captive rear bars prevent withdrawal without depending on friction.
bars={}
for z in (58,137):
 bar=box(0,D,z-7,W,6,14)
 for x in rear_x:bar-=cy(x,D-.1,z,3.4,6.2)
 for x in (33.5,130.5):bar+=box(x,124.5,z-7,11,D-124.5+.1,14)
 bars['retaining_bar_'+str(z)]=bar
# Integral front: no front fasteners or parting seam. Service from top/rear.
# Upper-face opening reflects the previous opening about the printer body mid-height.
# Original front/buttons are now above; original rear/cable edge below.
# It intentionally exposes a generous region, not a precision guessed paper slot.
front=box(0,0,9,W,3,H-13)-box(45.5,-1,OUTLET_Z-7,90,5,14)
# Separate translucent insert: clearance around tongue, rear flange for bonding.
front-=box(70.3,-1,LED_TOP-4.7,40.4,5,4.9)
diffuser=box(70.5,0.2,LED_TOP-4.5,40,2.9,4.5)+box(68.5,3.05,LED_TOP-6.5,44,.55,8.5)
# Hollow light cavity leaves a 0.8mm front membrane; rear remains open.
diffuser-=box(71.3,1,LED_TOP-3.7,38.4,4,2.9)
shell += front
# Soften exposed outer-right corners while preserving the flat seam interface.
corner=box(W-6,0,8,6,6,H)-cz(W-6,6,8,12,H)
shell-=corner
# Registered artwork, flush 0.8mm inlay, prints in the first four 0.2mm layers.
logo=b.Pos(W/2-297.96,0,57-62)*b.import_step(ROOT/'cad/review/logo_v18.step')
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
def section(y,width,bottom,top):
 left=CENTER_X-width/2;right=CENTER_X+width/2
 return b.Pos(0,y,0)*(b.Plane.XZ*b.Polygon((left,bottom),(right,bottom),(right,top),(left,top),align=None))
printer=b.loft([section(4,FRONT_WIDTH,21.4,FRONT_TOP),section(124,REAR_WIDTH,16,191)],ruled=True)
parts={'shell':shell,'cradle_tray':tray,**bars,'top_cover':top,'rear_cover':rear,'logo':logo,'led_diffuser':diffuser}
colors={k:'#DEE9EE' for k in parts}
colors['logo']='#173B53'
report={'status':'mechanical prototype; slicer, outlet and cable checks pending','printer_mm':[143,120,175],'front_width_mm':132,'rear_width_mm':143,'lateral_taper_assumption':'centred; 5.5mm per side','bay_width_mm':W,'orientation':'original front/buttons above; original rear/cable edge below','front_aperture_z_mm':[OUTLET_Z-7,OUTLET_Z+7],'taper_split_lower_upper_mm':[5.4,3.6],'front_body_height_mm':166,'rear_body_height_mm':175,'led_front_top_offset_mm':2,'switch_mapping':'left in above-view with front edge at top; physical confirmation required','logo_center_z_mm':57,'cable_route':'lower rear; connector geometry unmeasured','parts':{},'interferences':[]}
children=[]
for name,s in parts.items():
 assert s.is_valid and (name=='logo' or len(s.solids())==1),(name,len(s.solids()))
 c=copy.deepcopy(s);c.label=name;c.color=b.Color(colors[name]);children.append(c)
 oriented=b.Rot(90,0,0)*s if name in ('shell','logo','rear_cover') else b.Rot(-90,0,0)*s if name.startswith('retaining_bar') or name=='led_diffuser' else s
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
sweep=printer+box(CENTER_X-REAR_WIDTH/2,124,16,REAR_WIDTH,D,175)
for name in ('shell','cradle_tray','top_cover'):
 hit=parts[name].intersect(sweep)
 assert not hit or sum(s.volume for s in hit.solids())<.05,('removal blocked',name)
report['rear_removal_envelope_clear']=True
# Conservative rocker box includes 4.5mm protrusion +2mm vertical margin.
# Plane is lowest at trailing edge y85; 17.755 - 6.5 = 11.255.
rocker_sweep=box(35,67,11.255,31,D+85-67,12)
for name in ('shell','cradle_tray','top_cover'):
 hit=parts[name].intersect(rocker_sweep)
 assert not hit or sum(s.volume for s in hit.solids())<.05,('rocker path blocked',name)
report['rocker_clearance_path_clear']=True
(OUT/'checks.json').write_text(json.dumps(report,indent=2))
b.export_step(b.Compound(children=children,label='V26_DOUBLE_TAPER_PRINTER_BAY'),OUT/'printer_bay.step')
ref=copy.deepcopy(printer);ref.label='MEASURED_PRINTER_ENVELOPE_NOT_FOR_PRINT';b.export_step(ref,OUT/'printer_reference.step')
for exploded in (False,True):
 sc=Scene(1100,850,ss=1)
 for k,s in parts.items():
  if exploded:
   s=b.Pos(0,0,45)*s if k=='top_cover' else b.Pos(0,40,0)*s if k=='rear_cover' else s
  sc.add(s,colors[k])
 if not exploded:sc.add(printer,'#656A70')
 sc.look_at((410,-570,370),(W/2,65,108),fov=30);sc.save(str(OUT/('exploded.png' if exploded else 'assembly.png')))
print(json.dumps(report,indent=2),flush=True)
sc=Scene(1100,850,ss=1)
for k,s in parts.items():
 if k!='rear_cover':sc.add(s,colors[k])
sc.add(printer,'#656A70')
sc.look_at((390,590,340),(W/2,90,105),fov=30)
sc.save(str(OUT/'rear_retention.png'))
