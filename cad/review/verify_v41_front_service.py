"""Exact translational sweeps of nominal unplugged display envelopes."""
from pathlib import Path
import json,math
import build123d as b
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/output/v41_recessed_glass'
BASE=33.;CZ=BASE+(201-16-BASE)/math.cos(math.radians(25))/2
GX,GZ=109.48-193/2,CZ-111/2
def box(x,y,z,w,d,h):return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
def rake(s):return b.Pos(0,0,BASE)*b.Rot(-25,0,0)*b.Pos(0,0,-BASE)*s
def vol(s):return sum(q.volume for q in s.solids()) if s else 0.
parts={s.label:s for s in b.import_step(OUT/'whole_enclosure_review.step').children if not s.label.startswith('display_mount_')}
sweeps={
 'glass_1p1mm':b.Pos(109.48,-100,CZ)*b.Rot(-90,0,0)*b.extrude(b.RectangleRounded(193,111,8),amount=102.1),
 'chassis':box(GX+12,-100,GZ+3.35,166.2,106.96,100.6),
 'attached_Pi_nominal':box(GX+51.12,-100,GZ+30.65,85,141,56)}
hits={}
for name,s in sweeps.items():
 s=rake(s)
 hits[name]={n:v for n,p in parts.items() if (v:=vol(s&p))>.1}
report={'status':'Nominal front extraction geometry clear' if not any(hits.values()) else 'Front extraction collision',
 'method':'Exact prism sweeps along display normal; four detachable rear brackets removed',
 'clashes_mm3':hits,'limits':['Nominal board/chassis references only; actual loose wires and cables must be disconnected and kept clear','Rear bracket physical fit remains unconfirmed'],
 'printed_parts_reused':'V40 frame and four brackets remain useful for mount validation; V41 bracket shapes unchanged'}
(OUT/'front_service_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));assert not any(hits.values()),hits
