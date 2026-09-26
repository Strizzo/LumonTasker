from pathlib import Path
import build123d as b
import math,json
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN
root=Path(__file__).resolve().parents[2]
out=root/'cad/output/v19'
rows={}
for ver,file in [('v18',root/'files/LUMON_TERMINAL_v18.step'),('v19',out/'LUMON_v19_colored_review.step')]:
 assembly=b.import_step(file);tub=next(c for c in assembly.children if c.label.lower()=='tub_left').solids()[0]
 classifier=BRepClass3d_SolidClassifier(tub.wrapped)
 samples=[]
 for z in (20,28,38,60,90,115,140):
  for deg in (90,105,120,135,150,165,180):
   a=math.radians(deg);inside=[]
   for i in range(241):
    r=3+i*.05
    classifier.Perform(gp_Pnt(14+r*math.cos(a),147+r*math.sin(a),z),1e-7)
    if classifier.State()==TopAbs_IN or classifier.IsOnAFace():
     inside.append(r)
   if inside:
    # Outer contiguous occupied run, excluding unrelated internal features.
    end=inside[-1];start=end
    for r in reversed(inside[:-1]):
     if start-r>.051:break
     start=r
    samples.append({'z':z,'angle':deg,'wall_mm':round(end-start+.05,2)})
 rows[ver]={'minimum_sampled_rear_corner_wall_mm':min(x['wall_mm'] for x in samples),'samples':samples}
 print(ver,rows[ver]['minimum_sampled_rear_corner_wall_mm'],flush=True)
(out/'rear_corner_wall_check.json').write_text(json.dumps(rows,indent=2))
