"""Increase O–N spacing after physical prototype review; preserve V36 outlet."""
from pathlib import Path
import copy,json
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'cad/output/v37_logo_spacing';OUT.mkdir(exist_ok=True)
a=b.import_step(ROOT/'cad/output/v36_outlet_alignment/whole_enclosure_review.step')
p={s.label:copy.deepcopy(s) for s in a.children}
solids=list(p['logo'].solids())
letters=sorted([s for s in solids if s.bounding_box().size.X<10],key=lambda s:s.bounding_box().min.X)
assert len(letters)==5
n=letters[-1];o=letters[-2];gap=n.bounding_box().min.X-o.bounding_box().max.X
new_n=b.Pos(.3,0,0)*n
p['shell']=(p['shell']+n)-new_n
new_solids=[new_n if s==n else s for s in solids]
# Identity-independent replacement by distinctive bounding box.
new_solids=[new_n if abs(s.bounding_box().min.X-n.bounding_box().min.X)<1e-6 else s for s in solids]
p['logo']=b.Compound(children=new_solids)
assert p['shell'].is_valid and len(p['shell'].solids())==1
for i,s in enumerate(new_solids):
 assert s.is_valid
 for t in new_solids[i+1:]:
  overlap=s.intersect(t)
  assert overlap is None or sum(v.volume for v in overlap.solids())<1e-6
for name,s in p.items():s.label=name
b.export_step(b.Compound(children=list(p.values())),OUT/'whole_enclosure_review.step')
for name in ['shell','logo']:
 b.export_stl(p[name],OUT/(name+'_assembly.stl'),tolerance=.035)
 assert trimesh.load_mesh(OUT/(name+'_assembly.stl')).is_watertight
(OUT/'audit.json').write_text(json.dumps(dict(old_on_gap_mm=gap,new_on_gap_mm=gap+.3,n_shift_right_mm=.3,shell_valid=True,watertight=True,outlet_correction_preserved=True),indent=2)+'\n')
(OUT/'README.md').write_text('''# V37 logo spacing

Physical prototype feedback: N too close to O. Moved N 0.3 mm right; O–N bounding gap increases from 0.294 to 0.594 mm, comparable to neighbouring gaps. Updated shell recess together with coloured logo. All other geometry inherited unchanged from V36, including paper opening raised 3 mm and unchanged LED.

Shell valid single solid, logo components valid and mutually non-overlapping; shell and logo STL watertight. STEP ready for Fusion synchronization, not yet imported. Assembly STLs are not oriented/sliced print releases. No print dispatched.

User reports final filaments arrived. Exact brands/materials/colours and current slot loading asked, awaiting reply. Secured retention and feed/cut/service checks still pending.
''')
print('V37 validated; O–N gap',gap,'->',gap+.3)
