from pathlib import Path
import sys,struct,numpy as np
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'files'))
from render3d import Scene
class Mesh:
 def __init__(self,path):
  buf=path.read_bytes(); a=np.frombuffer(buf[84:],dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])['v']; self.a=a
 def tessellate(self,tolerance):
  a=self.a.reshape(-1,3);return [SimpleNamespace(X=float(v[0]),Y=float(v[1]),Z=float(v[2])) for v in a],np.arange(len(a)).reshape(-1,3)
base=ROOT/'files/mnt/user-data/outputs/lumon_terminal_v18'
for name,eye,target in [('v18_colored',(490,-680,380),(188,70,85)),('v18_screen_corner',(-85,-170,95),(17,8,40))]:
 s=Scene(1100,800,ss=1)
 for p in base.glob('*.stl'):
  if p.stem.startswith('ref_') and p.stem!='ref_display':continue
  c='#10161E' if p.stem in ['display_bezel','foot_left','foot_right','ref_display'] else '#0B4F7E' if p.stem=='logo_fill' else '#DEE9EE'
  s.add(Mesh(p),c)
 s.look_at(eye,target,fov=20 if 'corner' in name else 32);s.save(str(ROOT/'cad/output'/f'{name}.png'))
