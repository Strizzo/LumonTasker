"""Shorter left service hatch; preserve exact v28 printer assembly."""
from pathlib import Path
import sys, copy, json, itertools
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'files')]
from cad import lumon_v29 as m
from render3d import Scene
out=m.OUT
old=b.import_step(ROOT/'cad/output/v28_integrated_top/whole_enclosure_review.step')
parts={s.label:s for s in old.children}
for name in ('tub_left','rear_panel_left'): parts[name]=m.PARTS[name]
report={'scope':'Only left tub and rear hatch changed; exact v28 printer geometry retained. Left hardware remains unverified.','parts':{},'interferences':[],'vent_obstructions_mm3':[]}
for name,s in parts.items():
 s.label=name;s.color=b.Color('#173B53' if name in {'foot_left','display_bezel','logo'} else '#DEE9EE')
 assert s.is_valid,name
 report['parts'][name]={'valid':bool(s.is_valid),'solids':len(s.solids())}
for name in ('tub_left','rear_panel_left'):
 s=parts[name];b.export_stl(s,out/f'{name}.stl',tolerance=.03)
 mesh=trimesh.load_mesh(out/f'{name}.stl');assert mesh.is_watertight,name
 report['parts'][name]['watertight']=bool(mesh.is_watertight)
for i in range(5):
 probe=m.box_at(30.01,148,120+i*4+.01,m.p.x_split-60-.02,14,1.98)
 vol=0
 for s in parts.values():
  hit=s.intersect(probe)
  vol+=sum(x.volume for x in hit.solids()) if hit else 0
 report['vent_obstructions_mm3'].append(vol)
 assert vol<.01,(i,vol)
for (an,a),(bn,c) in itertools.combinations(parts.items(),2):
 ba,bc=a.bounding_box(),c.bounding_box()
 if any(min(getattr(ba.max,k),getattr(bc.max,k))-max(getattr(ba.min,k),getattr(bc.min,k))<.001 for k in ('X','Y','Z')):continue
 hit=a.intersect(c);vol=sum(x.volume for x in hit.solids()) if hit else 0
 if vol>.1:report['interferences'].append([an,bn,vol])
report['hatch_height_mm']=parts['rear_panel_left'].bounding_box().size.Z
report['vent_to_hatch_gap_mm']=120-parts['rear_panel_left'].bounding_box().max.Z
report['rear_screw_centres_xz_mm']=m.REAR_SCREWS
(out/'audit.json').write_text(json.dumps(report,indent=2))
assert not report['interferences'],report['interferences']
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()],label='LUMON_V29_REAR_VENT_REVIEW'),out/'whole_enclosure_review.step')
sc=Scene(1400,900,ss=1)
for s in parts.values():sc.add(s,'#173B53' if s.label in {'foot_left','display_bezel','logo'} else '#DEE9EE')
sc.look_at((540,760,350),(195,85,105),fov=32);sc.save(str(out/'rear_review.png'))
print(json.dumps(report,indent=2),flush=True)
