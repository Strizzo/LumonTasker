"""Flat rear screw lands; a rounded removable cover carries the tested retainers.

Preserve printer pose, cradle, V36 outlet and V37 logo. Review before printing.
"""
from pathlib import Path
import copy,json,sys,math
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'files'))
from render3d import Scene
OUT=ROOT/'cad/output/v38_integrated_rear';OUT.mkdir(parents=True,exist_ok=True)
SHIFT=218.96;W=175.;H=201.;D=161.;GAP=.25;CAP_Y=D+GAP;BACK=170.75;R=9.5
PALE='#F0F1EB';NAVY='#173B53'
def box(x,y,z,w,d,h):return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
def cy(x,y,z,d,l):return b.Pos(x,y+l/2,z)*b.Rot(-90,0,0)*b.Cylinder(d/2,l)
def cz(x,y,z,d,l):return b.Pos(x,y,z+l/2)*b.Cylinder(d/2,l)
def vol(s):return sum(v.volume for v in s.solids()) if s else 0.
a=b.import_step(ROOT/'cad/output/v37_logo_spacing/whole_enclosure_review.step')
p={s.label:copy.deepcopy(s) for s in a.children}
local=lambda name:b.Pos(-SHIFT,0,0)*p[name]
old_shell=local('shell');tray=local('cradle_tray')
# Recover the square rear outer rail from the original V28 geometry, while
# retaining V37's lower-band inset and all front geometry.
# The rear corner was cropped from a full 9 mm rear rail and 4 mm roof.
shell=old_shell+box(166,147,33,9,14,H-33)+box(166,147,9,8.2,13.2,24)
# Broaden the right internal screw land so screws sit on the FLAT region of
# the new cover, inward of its rounded outside corner. Tray remains below it.
shell+=box(155,141,17,12,20,180)
# Close obsolete right bores, and left intermediate bar holes.
for x,zs in [(170.5,(40,58,137,180)),(4.5,(58,137))]:
 for z in zs:shell+=cy(x,154.7,z,4.2,6.3)
# New cover uses four M3x14 screws; 9.75mm grip leaves 4.25mm engagement.
axes=[(x,z) for x in (4.5,161.) for z in (40.,180.)]
for x,z in axes:shell-=cy(x,154.6,z,4.2,6.5)
# Vertical rear outer radius belongs entirely to the detachable cap. The
# structural shell ends flat at y161. Its exterior joins at a 0.25mm seam.
def cap_envelope(inset,z,h):
 cx=W-R;radius=R-inset
 solid=box(inset,CAP_Y,z,W-2*inset,BACK-inset-CAP_Y,h)
 waste=box(cx,CAP_Y,z,radius,radius,h)-cz(cx,CAP_Y,z,2*radius,h)
 return solid-waste
outer=cap_envelope(0,9,H-9)
inner=cap_envelope(3,12,H-12-3.5)
cover=outer-inner
# Leave an open insertion-facing surface (inner shape starts at same Y).
# Continue the 0.8mm lower body band at the external side/back.
band=cap_envelope(.8,9,24)
cover=(cover-box(-1,160,8,W+2,12,25))+(cover & band)
# Two tested retention rib sets become integral with the rear skin.
for name,z in [('retaining_bar_58',58),('retaining_bar_137',137)]:
 rib=local(name) & box(12,120,0,141,49,200)
 cover+=rib
 cover+=box(12,166.9,z-7,141,1,14)
# Four solid standoffs seat directly against the flat shell lands.
for x,z in axes:
 cover+=box(x-4,161,z-4,8,BACK-161,8)
 cover-=cy(x,160.9,z,3.4,BACK-160.9+.1)
# Keep the bottom cable exit, including the underside relief, fully open.
cable=box(40,95,-1,78,100,48)
rocker=box(35,67,-1,31,130,25)
cover-=box(35,95,-1,83,100,48)
# The cable opening also clears the rocker's complete rear service path.
# Base follows the extended rear cap; front and all bond-bed datums retained.
inset=2.5
foot=box(0,inset,0,W-inset,BACK-2*inset,9)
front_edges=[e for e in foot.edges().filter_by(b.Axis.Z) if e.center().X>172 and e.center().Y<3]
foot=b.fillet(front_edges,11.5)
rear_edges=[e for e in foot.edges().filter_by(b.Axis.Z) if e.center().X>172 and e.center().Y>168]
foot=b.fillet(rear_edges,7.)
foot=b.chamfer([e for e in foot.edges().group_by(b.Axis.Z)[0] if abs(e.center().X)>.01],5.)
for r in [rocker,cable,box(-1,126,-1,12,20,11)]:foot-=r
beds=[(16,18,18,35),(138,18,18,35),(12,84,14,27),(133,93,22,28),(53,20,62,28)]
for x,y,w,d in beds:foot-=box(x,y,8.7,w,d,1)
changed={'shell':shell,'rear_cover_integrated':cover,'foot_right_bonded':foot}
for k,s in changed.items():
 assert s.is_valid and len(s.solids())==1,(k,s.is_valid,len(s.solids()))
 mpath=OUT/(k+'_assembly.stl');b.export_stl(s,mpath,tolerance=.035)
 assert trimesh.load_mesh(mpath).is_watertight,k
# Retention and assembly clearance checks against the physical reference.
printer=b.import_step(ROOT/'cad/output/v28_integrated_top/printer_reference.step')
checks={}
for k,s in [('shell',shell),('cradle',tray),('printer',printer),('base',foot)]:
 checks['cover_vs_'+k]=vol(cover.intersect(s))
assert max(checks.values())<.02,checks
checks['shell_printer']=vol(shell.intersect(printer));checks['shell_tray']=vol(shell.intersect(tray))
assert checks['shell_printer']<.02 and checks['shell_tray']<.02,checks
for name,offset in [('rear_clear',(0,.45,0)),('up_clear',(0,0,.45)),('rear_captured',(0,.75,0)),('up_captured',(0,0,.75))]:
 checks[name]=vol(cover.intersect(b.Pos(*offset)*tray))
assert checks['rear_clear']<.01 and checks['up_clear']<.01,checks
assert checks['rear_captured']>1 and checks['up_captured']>1,checks
for distance in [.1,1,5,20,50,100]:
 for k,s in [('shell',shell),('tray',tray),('printer',printer),('base',foot)]:
  v=vol((b.Pos(0,distance,0)*cover).intersect(s));assert v<.02,('removal',distance,k,v)
for x,z in axes:
 annulus=cy(x,160.5,z,7.6,.4)-cy(x,160.49,z,4.25,.42)
 ratio=vol(shell.intersect(annulus))/annulus.volume
 assert ratio>.999,('screw land',x,z,ratio)
 bore=cy(x,154.61,z,4.18,6.48)
 assert vol(shell.intersect(bore))<.01
assert vol(cover.intersect(cable))<.01
assert vol(cover.intersect(rocker))<.01
for x,y,w,d in beds:
 probe=box(x+.01,y+.01,9.01,w-.02,d-.02,.1)
 assert abs(vol(shell.intersect(probe))-probe.volume)<.01
# Keep the user-confirmed front features and all other components unchanged.
front=box(-1,-1,0,W+2,140,H+2)
assert abs(vol(shell.intersect(front))-vol(old_shell.intersect(front)))<.01
for k in ['retaining_bar_58','retaining_bar_137','rear_cover']:p.pop(k)
for k,s in changed.items():p[k]=b.Pos(SHIFT,0,0)*s
for k,s in p.items():s.label=k;s.color=b.Color(NAVY if k in {'foot_left','foot_right_bonded','display_bezel','logo'} else PALE)
b.export_step(b.Compound(children=list(p.values()),label='LUMON_V38_INTEGRATED_REAR'),OUT/'whole_enclosure_review.step')
# Rear-facing side-by-side inspection: open shell and inward-facing cover.
inspection=[]
for k in ['shell','cradle_tray','foot_right_bonded']:
 s=b.Rot(0,0,180)*b.Pos(-306.46,-100,0)*copy.deepcopy(p[k])
 s.label=k+'_REAR_VIEW';s.color=b.Color(NAVY if k=='foot_right_bonded' else PALE)
 inspection.append(s)
s=b.Pos(210-306.46,-165,0)*copy.deepcopy(p['rear_cover_integrated'])
s.label='COVER_INNER_FACE_WITH_INTEGRATED_RETAINERS';s.color=b.Color(PALE);inspection.append(s)
b.export_step(b.Compound(children=inspection,label='V38_REAR_INSPECTION_NOT_ASSEMBLY_LAYOUT'),OUT/'V38_REAR_INSPECTION.step')
# Orientation for later slicing. Cosmetic rear lies on bed for combined cover.
for k,s in changed.items():
 t=b.Rot(-90 if k=='rear_cover_integrated' else 90,0,0)*s if k!='foot_right_bonded' else s
 bb=t.bounding_box();t=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*t
 b.export_stl(t,OUT/(k+'_print.stl'),tolerance=.035)
report=dict(status='CAD checked; Fusion review and slicing pending; not dispatched',shell_front_unchanged=True,cradle_unchanged=True,retention_contacts_unchanged=True,cover_solids=1,fastener_count=4,screw='M3x14',grip_mm=9.75,thread_engagement_mm=4.25,axes_xz_mm=axes,outer_rear_radius_mm=R,seam_mm=GAP,closed_depth_mm=BACK,previous_closed_depth_mm=170.5,clearance_checks_mm3=checks,printability='Rear face down; slicer support review required at curved outside edge and inner ribs')
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
for mode in ['installed','exploded']:
 sc=Scene(1300,1000,ss=1,bg_top='#DEE4E8',bg_bot='#B7C1CA')
 for k in ['shell','cradle_tray','rear_cover_integrated','foot_right_bonded']:
  s=p[k]
  if mode=='exploded' and k=='rear_cover_integrated':s=b.Pos(0,85,0)*s
  sc.add(s,NAVY if k=='foot_right_bonded' else PALE)
 sc.look_at((550,730,345),(306,125,104),fov=31);sc.save(OUT/('rear_'+mode+'.png'))
