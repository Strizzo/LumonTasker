"""Pocket the unprinted printer foot, keeping V39 shell/bond interfaces.

Pockets open upwards into the hidden shell interface so the original underside
still prints on the bed, without bridging a hollow underside or using supports.
"""
from pathlib import Path
import copy,json,sys
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'files'))
from render3d import Scene
OUT=ROOT/'cad/output/v42_light_printer_base';OUT.mkdir(exist_ok=True)
SHIFT=218.96
def box(x,y,z,w,d,h):return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
def vol(s):return sum(q.volume for q in s.solids()) if s else 0.
def delta(a,c):return vol(a-c)+vol(c-a)
parts={s.label:s for s in b.import_step(ROOT/'cad/output/v41_recessed_glass/whole_enclosure_review.step').children}
old=b.Pos(-SHIFT,0,0)*parts['foot_right_bonded']
foot=copy.deepcopy(old)
beds=[(16,18,18,35),(138,18,18,35),(12,84,14,27),(133,93,22,28),(53,20,62,28)]
protected=[box(x-3,y-3,-1,w+6,d+6,12) for x,y,w,d in beds]
# Preserve 3 mm rails beside existing underside service openings.
protected += [box(32,64,-1,37,140,12),box(37,92,-1,84,110,12),box(-4,123,-1,18,26,12)]
for xa,xb in ((10,78),(84,162.5)):
    for ya,yb in ((13,76),(82,158.25)):
        pocket=box(xa,ya,2.4,xb-xa,yb-ya,8)
        for p in protected:pocket-=p
        foot-=pocket
assert foot.is_valid and len(foot.solids())==1
# Accepted appearance, ground support, bond pads, and reliefs are untouched.
assert delta(foot & box(-1,-1,-1,177,174,3.4),old & box(-1,-1,-1,177,174,3.4))<.001
for x,y,w,d in beds:
    region=box(x-2.9,y-2.9,-1,w+5.8,d+5.8,12)
    assert delta(foot&region,old&region)<.001
channels={'rocker':box(35,67,-1,31,130,25),'cable':box(40,95,-1,78,100,48),'interbay':box(-1,126,-1,12,20,11)}
assert all(vol(foot & c)<.001 for c in channels.values())
placed=b.Pos(SHIFT,0,0)*foot
clashes={n:vol(placed&s) for n,s in parts.items() if n!='foot_right_bonded'}
assert max(clashes.values())<.05,clashes
for a,c in zip(foot.bounding_box().size,old.bounding_box().size):assert abs(a-c)<.001
foot.label='foot_right_bonded';b.export_step(foot,OUT/'printer_base_local.step')
placed.label='foot_right_bonded';b.export_step(placed,OUT/'printer_base_assembly.step')
bb=foot.bounding_box();printable=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*foot
b.export_stl(printable,OUT/'printer_base_print.stl',tolerance=.025)
mesh=trimesh.load_mesh(OUT/'printer_base_print.stl');assert mesh.is_watertight
parts['foot_right_bonded']=placed
for n,s in parts.items():s.label=n;s.color=b.Color('#173B53' if n in ('foot_left','foot_right_bonded','logo') else '#F0F1EB')
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()]),OUT/'whole_enclosure_pocketed_candidate.step')
report={'status':'CAD checks passed; GUI slice review pending; no print dispatched',
 'scope':'Printer foot only, compatible with physically accepted V39 shell and integrated rear cover',
 'old_volume_mm3':vol(old),'new_volume_mm3':vol(foot),'cad_volume_reduction_percent':100*(1-vol(foot)/vol(old)),
 'solid_count':1,'valid':True,'watertight':True,'print_dimensions_mm':mesh.extents.tolist(),
 'floor_thickness_mm':2.4,'cross_rib_width_mm':6,'bond_pad_surround_mm':3,
 'bond_pads_xywh_mm':beds,'adhesive_recess_mm':.3,
 'ground_and_lower_bevel_preserved':True,'bond_interfaces_preserved':True,'service_channels_clear':True,
 'assembly_clashes_mm3':{n:v for n,v in clashes.items() if v>.01},
 'retention':'Same recessed bonding pads as V39; dry-fit before bonding. No new screw holes.',
 'print_orientation':'Original underside down; hidden upper pockets open upwards; no cavity roofs to bridge.',
 'physical_stiffness_verified':False,'sliced_mass_saving_verified':False,
 'inherited_display_hold':'Recessed display bracket physical check and power/cable layout still pending; no full display-body release'}
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
sc=Scene(900,650,ss=1);sc.add(foot,'#173B53');sc.look_at((265,-330,345),(85,83,3),fov=29);sc.save(str(OUT/'pocketed_base.png'))
print(json.dumps(report,indent=2))
