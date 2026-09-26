"""Review current printer bay against retained v19 left module, without mutation."""
from pathlib import Path
import json,copy,sys
import build123d as b
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'files'))
from render3d import Scene
out=ROOT/'cad/output/v28_integrated_top'
old=b.import_step(ROOT/'cad/output/v19/LUMON_v19_colored_review.step')
new=b.import_step(out/'printer_bay.step')
keep={'tub_left','top_plate_left','display_retainer','rear_panel_left','foot_left','display_bezel'}
left={s.label:s for s in old.children if s.label in keep}
right={s.label:b.Pos(218.96,0,0)*s for s in new.children}
report={'scope':'Exact exported v19 and v28 STEP comparison; live Fusion documents are unsaved review imports, not measured hardware','parts':{},'cross_module_interferences':[]}
for group,parts in [('left_v19',left),('right_v28',right)]:
 for name,s in parts.items():
  q=s.bounding_box();report['parts'][group+'/'+name]={'min':[q.min.X,q.min.Y,q.min.Z],'max':[q.max.X,q.max.Y,q.max.Z]}
for an,a in left.items():
 for bn,v in right.items():
  hit=a.intersect(v);vol=sum(s.volume for s in hit.solids()) if hit else 0
  if vol>.05:report['cross_module_interferences'].append({'left':an,'right':bn,'volume_mm3':vol})
(out/'context_audit.json').write_text(json.dumps(report,indent=2))
sc=Scene(1400,900,ss=1);allparts=[]
for name,s in {**left,**right}.items():
 color='#173B53' if name in {'foot_left','display_bezel','logo'} else '#DEE9EE'
 sc.add(s,color);c=copy.deepcopy(s);c.label=name;c.color=b.Color(color);allparts.append(c)
sc.look_at((560,-690,385),(195,65,108),fov=32)
sc.save(str(out/'whole_enclosure_review.png'))
b.export_step(b.Compound(children=allparts,label='V28_CONTEXT_REVIEW_LEFT_HARDWARE_UNVERIFIED'),out/'whole_enclosure_review.step')
print(json.dumps({'cross_module_interferences':report['cross_module_interferences'],'parts':list(report['parts'])},indent=2))
