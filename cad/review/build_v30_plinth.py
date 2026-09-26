"""Matching dark base for the exact v28 shell, retaining v29 left hatch fix.
No shell changes or unprovided mounting holes. Recessed adhesive beds retain
base while flat lands carry compression. All coordinates below local right bay.
"""
from pathlib import Path
import copy,json,sys
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'files'))
from render3d import Scene
OUT=ROOT/'cad/output/v30_printer_plinth';OUT.mkdir(parents=True,exist_ok=True)
W,D,H=175.,161.,9.
INSET,RADIUS,CHAMFER=2.5,11.5,5.
SHIFT=218.96

def box(x,y,z,w,d,h):return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
def volume(s):return sum(v.volume for v in s.solids()) if s else 0.

foot=box(0,INSET,0,W-INSET,D-2*INSET,H)
foot=b.fillet(foot.edges().filter_by(b.Axis.Z).group_by(b.Axis.X)[-1],RADIUS)
# Match the left foot's 5 mm lower bevel, leaving the module seam straight.
foot=b.chamfer([e for e in foot.edges().group_by(b.Axis.Z)[0] if abs(e.center().X)>.01],CHAMFER)
# Cutouts continue through to the ground and open at the back. No rocker contact
# or closed cable well is introduced by adding a base under the current shell.
reliefs={
 'rocker_channel':box(35,67,-1,31,100,11),
 'rear_cable_channel':box(40,95,-1,78,80,11),
 'interbay_cable_notch':box(-1,126,-1,12,20,11),
}
for s in reliefs.values():foot-=s
# Adhesive recesses stop short of edges and all voids. Flat surrounding lands
# remain at z9, so bond thickness <=0.3 mm does not alter ground alignment.
adhesive_beds=[(16,18,18,35),(138,18,18,35),(12,84,14,27),(133,93,22,28),(53,20,62,28)]
for x,y,w,d in adhesive_beds:foot-=box(x,y,H-.3,w,d,1)
assert foot.is_valid and len(foot.solids())==1
foot.label='foot_right_bonded';foot.color=b.Color('#173B53')
b.export_stl(foot,OUT/'foot_right_navy.stl',tolerance=.025)
mesh=trimesh.load_mesh(OUT/'foot_right_navy.stl')
assert mesh.is_watertight
old=b.import_step(ROOT/'cad/output/v29_rear_vent_fix/whole_enclosure_review.step')
parts={s.label:s for s in old.children}
shell=b.Pos(-SHIFT,0,0)*parts['shell']
# Every glue bed must sit completely underneath solid shell floor.
for x,y,w,d in adhesive_beds:
 probe=box(x+.01,y+.01,9.01,w-.02,d-.02,.1)
 assert abs(volume(shell.intersect(probe))-probe.volume)<.01,('unsupported bed',x,y)
obstructions={k:volume(foot.intersect(s)) for k,s in reliefs.items()}
assert max(obstructions.values())<.01
placed=b.Pos(SHIFT,0,0)*foot;placed.label=foot.label;placed.color=foot.color
clashes={k:volume(s.intersect(placed)) for k,s in parts.items()}
assert max(clashes.values())<.05,clashes
# Foot occupies no part of the printed bay and can be presented vertically
# from below; there are no snap tabs requiring shell flex or rear disassembly.
parts[placed.label]=placed
for k,s in parts.items():s.label=k;s.color=b.Color('#173B53' if k in {'foot_left','foot_right_bonded','display_bezel','logo'} else '#DEE9EE')
assembly=b.Compound(children=[copy.deepcopy(s) for s in parts.values()],label='LUMON_V30_MATCHING_BASE_REVIEW')
b.export_step(assembly,OUT/'whole_enclosure_review.step')
# Reference dimensions and assumptions remain those of v28/v29, unchanged.
report={'scope':'Added bonded navy printer base only. Existing assembly geometry retained verbatim.',
 'height_mm':9,'outer_inset_mm':2.5,'bottom_bevel_mm':5,'outer_corner_radius_mm':11.5,
 'ground_z_mm':[parts['foot_left'].bounding_box().min.Z,placed.bounding_box().min.Z],
 'foot_valid':bool(foot.is_valid),'foot_solids':len(foot.solids()),'watertight':bool(mesh.is_watertight),
 'print_bounds_mm':mesh.extents.tolist(),'volume_mm3':foot.volume,
 'adhesive_recess_depth_mm':.3,'adhesive_beds_xywh_mm':adhesive_beds,
 'adhesive_beds_backed_by_shell':True,'retention':'Bond within recessed beds; hard top lands contact shell underside at z9. No fasteners or shell drilling.',
 'relief_obstructions_mm3':obstructions,'base_interferences_mm3':clashes,
 'printing':'Separate single navy PLA part, flat underside on bed, support-free geometry; not sliced or dispatched.'}
(OUT/'audit.json').write_text(json.dumps(report,indent=2))
for name,camera,target in [('front',(560,-690,385),(195,65,108)),('rear',(540,760,350),(195,85,105))]:
 sc=Scene(1400,900,ss=1)
 for k,s in parts.items():sc.add(s,'#173B53' if k in {'foot_left','foot_right_bonded','display_bezel','logo'} else '#DEE9EE')
 sc.look_at(camera,target,fov=32);sc.save(str(OUT/(name+'_review.png')))
sc=Scene(1000,700,ss=1);sc.add(foot,'#173B53');sc.look_at((310,-390,360),(W/2,D/2,0),fov=30);sc.save(str(OUT/'base_detail.png'))
print(json.dumps(report,indent=2),flush=True)
