from pathlib import Path
import sys, math
import build123d as b
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'files'))
from render3d import Scene
OUT=ROOT/'cad/output/v40_display_mount'
parts=b.import_step(OUT/'display_fit_kit_assembled.step')
cz=33+(201-16-33)/math.cos(math.radians(25))/2
box=lambda x,y,z,w,d,h:b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
glass=b.Pos(109.48,-1,cz)*b.Rot(-90,0,0)*b.extrude(b.RectangleRounded(193,111,8),amount=.7)
chassis=box(24.98,-.3,cz-55.5+3.35,166.2,5.26,100.6)
pi=box(64.10,4.96,cz-55.5+30.65,85,34.04,56)
sc=Scene(900,650,ss=1)
for s in parts.children:sc.add(s,'#EEEDE5')
sc.add(glass,'#1A252B');sc.add(chassis,'#B7BEC3');sc.add(pi,'#317B58')
sc.look_at((300,490,340),(109,6,cz),fov=27)
sc.save(str(OUT/'fit_kit_rear.png'))
print(OUT/'fit_kit_rear.png')
