from pathlib import Path
import copy
import build123d as b
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'cad/output/v37_logo_spacing'
p={s.label:s for s in b.import_step(OUT/'whole_enclosure_review.step').children}
shapes=[]
for k in ['shell','cradle_tray','retaining_bar_58','retaining_bar_137','rear_cover','foot_right_bonded']:
 s=copy.deepcopy(p[k])
 if k=='rear_cover':s=b.Pos(0,85,0)*s
 s=b.Rot(0,0,180)*b.Pos(-306.46,-100,0)*s
 s.label=k+'_CURRENT_V37'+('_EXPLODED_85mm' if k=='rear_cover' else '')
 s.color=b.Color('#173B53' if k.startswith('retaining') or k=='foot_right_bonded' else '#F0F1EB')
 shapes.append(s)
b.export_step(b.Compound(children=shapes,label='CURRENT_REAR_INSPECTION_NOT_PRINT_LAYOUT'),OUT/'V37_REAR_INSPECTION.step')
print('Rear inspection STEP exported')
