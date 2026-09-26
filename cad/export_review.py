"""Rebuild a colored review assembly, oriented meshes, and geometry checks.
No printer profile or G-code is implied by these exports.
"""
from pathlib import Path
import sys, json, copy
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'files'))
from cad import lumon_v19 as m
from render3d import Scene
OUT=m.OUT
PALE='#DEE9EE';DARK='#10161E';BLUE='#0B4F7E'
colors={k:(DARK if k in ('foot_left','foot_right','display_bezel','printer_trim') else PALE) for k in m.PARTS}
colors['logo_fill']=BLUE
parts={**m.PARTS,'logo_fill':m.LOGO_FILL}
children=[]
for k,v in parts.items():
 s=copy.deepcopy(v);s.label=k;s.color=b.Color(colors[k]);children.append(s)
assembly=b.Compound(label='LUMON_v19_REVIEW_NOT_PRINT_RELEASE',children=children)
b.export_step(assembly,OUT/'LUMON_v19_colored_review.step')
print('Colored STEP exported',flush=True)
report={'status':'ENGINEERING REVIEW — hardware and printer measurements pending','parts':{},'interferences':[],'checks':{}}
for name,s in parts.items():
 assembly_dir=OUT/'assembly_stl';assembly_dir.mkdir(exist_ok=True)
 b.export_stl(s,assembly_dir/f'{name}.stl',tolerance=.03)
 if name=='logo_fill':continue
 oriented=s
 if name in ('display_bezel','display_retainer'):
  oriented=b.Rot(90,0,0)*b.Pos(0,0,m.p.skirt_h)*b.Rot(m.p.rake_deg,0,0)*b.Pos(0,0,-m.p.skirt_h)*s
 elif name.startswith('rear_panel'):oriented=b.Rot(-90,0,0)*s
 elif name in ('top_plate_left','printer_trim'):oriented=b.Rot(180,0,0)*s
 bb=oriented.bounding_box();oriented=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*oriented
 print_dir=OUT/'oriented_stl';print_dir.mkdir(exist_ok=True)
 b.export_stl(oriented,print_dir/f'{name}.stl',tolerance=.03)
 mesh=trimesh.load_mesh(print_dir/f'{name}.stl')
 report['parts'][name]={'solids':len(s.solids()),'valid':bool(s.is_valid),'watertight':bool(mesh.is_watertight),'volume_mm3':round(s.volume,2),'print_bounds_mm':[round(x,2) for x in (bb.size.X,bb.size.Y,bb.size.Z)],'color':colors[name]}
 print('PART',name,report['parts'][name],flush=True)
# Ref bodies are excluded from the print assembly and exported separately for fit review.
b.export_step(b.Compound(label='REFERENCE_HARDWARE_UNVERIFIED',children=[copy.deepcopy(v) for v in m.REFS.values()]),OUT/'reference_hardware.step')
allparts={**parts,**m.REFS}
for i,(an,a) in enumerate(allparts.items()):
 for bn,bs in list(allparts.items())[i+1:]:
  ba,bb=a.bounding_box(),bs.bounding_box()
  if any(min(getattr(ba.max,ax),getattr(bb.max,ax))-max(getattr(ba.min,ax),getattr(bb.min,ax))<.0001 for ax in ('X','Y','Z')):continue
  ov=a.intersect(bs);vol=sum(s.volume for s in ov.solids()) if ov else 0
  if vol>.1:
   row={'a':an,'b':bn,'overlap_mm3':round(vol,3)};report['interferences'].append(row);print('CLASH',row,flush=True)
# Quantitative fastening checks, independent of how the features were built.
def occupied(shape,x,y,z,size=.15):
 probe=m.box_at(x-size/2,y-size/2,z-size/2,size,size,size)
 cut=shape.intersect(probe)
 return bool(cut and sum(s.volume for s in cut.solids())>size**3*.9)
for side in ('left','right'):
 tub=parts['tub_'+side]
 for i,(x,y) in enumerate(m.foot_mounts(side)):
  report['checks'][f'{side}_foot_{i}_insert_roof']=occupied(tub,x,y,16)
  report['checks'][f'{side}_foot_{i}_insert_bore']=not occupied(tub,x,y,12)
 coords=m.LID_SCREWS_L if side=='left' else m.LID_SCREWS
 for i,(x,y) in enumerate(coords):
  report['checks'][f'{side}_lid_{i}_bore_open']=not occupied(tub,x,y,164.5)
  report['checks'][f'{side}_lid_{i}_insert_floor']=occupied(tub,x,y,158)
  cover=parts['top_plate_left' if side=='left' else 'printer_trim']
  report['checks'][f'{side}_lid_{i}_compression_sleeve']=occupied(cover,x+2.5,y,172)
  report['checks'][f'{side}_lid_{i}_screw_passage']=not occupied(cover,x,y,172)
for i,(x,z) in enumerate(m.REAR_SCREWS):
 report['checks'][f'rear_panel_left_{i}_head_bearing']=occupied(parts['rear_panel_left'],x+2.5,160,z)
for side in ('left','right'):
 tub=parts['tub_'+side]
 x=m.p.x_split-1.5 if side=='left' else m.p.x_split+3
 for i,(y,z) in enumerate(m.SPINE_DOWELS):
  report['checks'][f'{side}_dowel_{i}_bore']=not occupied(tub,x,y,z)
  report['checks'][f'{side}_dowel_{i}_surround']=occupied(tub,x,y,z+3)
 for i,(y,z) in enumerate(m.SPINE_SCREWS):
  report['checks'][f'{side}_spine_screw_{i}_bore']=not occupied(tub,x,y,z)
  report['checks'][f'{side}_spine_screw_{i}_surround']=occupied(tub,x,y,z+3)
# Seam and corner coupons: cut from the actual revised solids, not mockups.
coupons={}
for side in ('left','right'):
 cutter=m.box_at(m.p.x_split-14,126,36,28,29,45)
 coupons['seam_'+side]=parts['tub_'+side].intersect(cutter)
coupons['screen_corner']=parts['tub_left'].intersect(m.box_at(0,-5,33,42,40,38))
cp=OUT/'fit_coupons';cp.mkdir(exist_ok=True)
for name,s in coupons.items():
 if isinstance(s,list):
  solids=[solid for item in s for solid in item.solids() if solid.volume>0.001]
  s=b.Compound(children=solids)
 if name.startswith('seam'):s=b.Rot(0,90,0)*s
 bb=s.bounding_box();s=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*s
 b.export_stl(s,cp/f'{name}.stl',tolerance=.03)
 report.setdefault('coupons',{})[name]={'solids':len(s.solids()),'valid':bool(s.is_valid)}
(OUT/'geometry_review.json').write_text(json.dumps(report,indent=2))
print('Audit saved',flush=True)
assert all(v['valid'] and v['watertight'] and v['solids']==1 for v in report['parts'].values()), 'Invalid main part'
assert all(report['checks'].values()), 'Failed fastening check; see geometry_review.json'
assert not report['interferences'], 'Interference found; see geometry_review.json'
assert all(v['valid'] and v['solids']==1 for v in report['coupons'].values()), 'Invalid coupon'
for name,eye,target in [('assembly',(490,-680,380),(188,70,85)),('screen_corner',(-85,-170,95),(17,8,40)),('exploded',(580,-790,430),(188,70,95))]:
 sc=Scene(1200,880,ss=1)
 for k,s in parts.items():
  if name=='exploded':
   if k in ('top_plate_left','printer_trim'):s=b.Pos(0,0,55)*s
   elif k in ('display_bezel','logo_fill'):s=b.Pos(0,-50,0)*s
   elif k.startswith('foot'):s=b.Pos(0,0,-35)*s
   elif k.startswith('rear_panel'):s=b.Pos(0,45,0)*s
  sc.add(s,colors[k],tol=.15)
 if name!='exploded':sc.add(m.DISPLAY_REFERENCE,DARK)
 sc.look_at(eye,target,fov=20 if name=='screen_corner' else 32);sc.save(str(OUT/f'{name}.png'))
print('Previews exported',flush=True)
