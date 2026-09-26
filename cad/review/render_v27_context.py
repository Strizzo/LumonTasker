from pathlib import Path
import sys,copy
import build123d as b
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'files'))
from render3d import Scene
out=ROOT/'cad/output/v27_refined_printer'
old=b.import_step(ROOT/'cad/output/v19/LUMON_v19_colored_review.step')
new=b.import_step(out/'printer_bay.step')
keep={'tub_left','top_plate_left','display_retainer','rear_panel_left','foot_left','display_bezel'}
sc=Scene(1400,900,ss=1)
parts=[]
for s in old.children:
 if s.label in keep:
  sc.add(s,'#173B53' if s.label in {'foot_left','display_bezel'} else '#DEE9EE');parts.append(copy.deepcopy(s))
for s in new.children:
 moved=b.Pos(218.96,0,0)*s
 sc.add(moved,'#173B53' if s.label=='logo' else '#DEE9EE');parts.append(moved)
ref=b.Pos(218.96,0,0)*b.import_step(out/'printer_reference.step');sc.add(ref,'#656A70')
sc.look_at((560,-690,385),(185,65,102),fov=32)
sc.save(str(out/'whole_enclosure_study.png'))
b.export_step(b.Compound(children=parts,label='V27_CONTEXT_STUDY_NOT_FULL_CASE_RELEASE'),out/'whole_enclosure_study.step')
