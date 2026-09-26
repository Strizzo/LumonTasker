from pathlib import Path
import shutil
import build123d as b
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'cad/output/p1s_fit_plate'
for n in ('seam_left','seam_right','screen_corner'):
 shutil.copy2(ROOT/'cad/output/v19/fit_coupons'/f'{n}.stl',out/f'light_{n}.stl')
a=b.import_step(ROOT/'cad/output/v19/LUMON_v19_colored_review.step')
bezel=next(c for c in a.children if c.label=='display_bezel')
cut=b.Pos(21,15,52)*b.Box(42,40,38)
part=bezel.intersect(cut)
if isinstance(part,list):part=b.Compound(children=[s for x in part for s in x.solids()])
part=b.Rot(90,0,0)*b.Pos(0,0,33)*b.Rot(14,0,0)*b.Pos(0,0,-33)*part
bb=part.bounding_box();part=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*part
assert len(part.solids())==1 and part.is_valid
b.export_stl(part,out/'dark_bezel_corner.stl',tolerance=.03)
print('Four fit-test parts prepared. Bezel corner:',part.bounding_box().size)
