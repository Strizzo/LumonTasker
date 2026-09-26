"""Independent fit-kit release audit; a full-enclosure cable check remains open."""
from pathlib import Path
import json, math, copy
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'cad/output/v40_display_mount'
fixture=b.import_step(OUT/'display_fit_frame.step')
parts={'display_fit_frame':fixture}
for side in ('left','right'):
 for level in ('lower','upper'):
  n=f'display_mount_{side}_{level}_local';parts[n]=b.import_step(OUT/(n+'.step'))
vol=lambda s:sum(x.volume for x in s.solids()) if s else 0.
report={'scope':'Full-outline display fit fixture and four brackets only; not a left enclosure release','parts':{},'pair_intersections_mm3':{},'nominal_glass_intersections_mm3':{},'measured_glass_mm':[193,111],'clearance_per_side_mm':.2,'radius_reference_mm':8.,'radius_physically_confirmed':False,'dispatched':False}
for n,s in parts.items():
 assert s.is_valid and len(s.solids())==1,n
 mesh=trimesh.load_mesh(OUT/(n+'_print.stl'))
 assert mesh.is_watertight and abs(mesh.bounds[0,2])<.001,n
 rotation=b.Rot(90 if n=='display_fit_frame' else -90,0,0)
 oriented=rotation*s;bb=oriented.bounding_box()
 assert max(abs(mesh.extents[i]-[bb.size.X,bb.size.Y,bb.size.Z][i]) for i in range(3))<.01,n
 # Bed-contact surface: front face for fixture, flat rear for each bracket.
 report['parts'][n]={'valid':True,'watertight':True,'volume_mm3':vol(s),'print_extent_mm':mesh.extents.tolist()}
for i,(an,a) in enumerate(parts.items()):
 for bn,c in list(parts.items())[i+1:]:
  hit=vol(a&c);assert hit<.01,(an,bn,hit)
  report['pair_intersections_mm3'][an+' / '+bn]=hit
cz=33+(201-16-33)/math.cos(math.radians(25))/2
# Same glass datum as candidate: 1mm below the front of its protective frame.
glass=b.Pos(109.48,-1,cz)*b.Rot(-90,0,0)*b.extrude(b.RectangleRounded(193,111,8),amount=.7)
for n,s in parts.items():
 hit=vol(glass&s);assert hit<.01,(n,hit);report['nominal_glass_intersections_mm3'][n]=hit
report['status']='Fit-kit CAD checks passed; physical glass and lug fit still unverified'
report['full_enclosure_hold']='Provisional rear cable allowance overlaps the inherited divider by 188.72 mm3. Resolve cable routing/real power hardware before large display enclosure release.'
(OUT/'fit_audit.json').write_text(json.dumps(report,indent=2)+'\n')
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()],label='V40_DISPLAY_FIT_KIT_ASSEMBLED'),OUT/'display_fit_kit_assembled.step')
print(json.dumps(report,indent=2))
