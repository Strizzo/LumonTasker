from pathlib import Path
import json
import build123d as b
import trimesh
BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'cad/output'; OUT.mkdir(exist_ok=True)
a=b.import_step(BASE/'files/LUMON_TERMINAL_v18.step')
parts={n.label.lower():n for n in a.children}
print('parts', list(parts),flush=True)
r={'parts':{},'interferences':[]}
for name,s in parts.items():
 bb=s.bounding_box(); item={'solids':len(s.solids()),'valid':s.is_valid,'volume_mm3':s.volume,'bounds_mm':[[bb.min.X,bb.min.Y,bb.min.Z],[bb.max.X,bb.max.Y,bb.max.Z]]}
 r['parts'][name]=item
 print(name, item,flush=True)
for i,(na,sa) in enumerate(parts.items()):
 for nb,sb in list(parts.items())[i+1:]:
  x=sa.intersect(sb); v=sum(s.volume for s in x.solids()) if x else 0
  if v>0.1:
   item={'a':na,'b':nb,'overlap_mm3':round(v,3)};r['interferences'].append(item); print('CLASH',item,flush=True)
for f in (BASE/'files/mnt/user-data/outputs/lumon_terminal_v18').glob('*.stl'):
 if f.stem.startswith('ref_'):continue
 m=trimesh.load_mesh(f); components=m.split(only_watertight=False)
 r.setdefault('meshes',{})[f.stem]={'watertight':bool(m.is_watertight),'components':len(components),'component_volumes':sorted([round(float(c.volume),4) for c in components],reverse=True)}
 print('MESH',f.stem,r['meshes'][f.stem],flush=True)
(OUT/'audit_v18.json').write_text(json.dumps(r,indent=2))
