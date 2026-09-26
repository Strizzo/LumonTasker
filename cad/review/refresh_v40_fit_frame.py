"""Refresh only the small fixture; avoid rebuilding the large enclosure."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
src=(ROOT/'cad/review/build_v40_display_mount.py').read_text()
ns={'__file__':str(ROOT/'cad/review/build_v40_display_mount.py')}
exec(compile(src[:src.index('before={')],ns['__file__'],'exec'),ns)
exec('''
window=rounded(GX-GAP,-6,GZ-GAP,193+2*GAP,32,111+2*GAP,CORNER_R+GAP)
fixture=rounded(CX-(212.96-.6)/2,-2,CZ-132/2,212.96-.6,3,132,13.7)-window
for x in LUG_X:
 for z in ANCHOR_Z:
  a=cy(x,1.,z,9.,ANCHOR_PLANE-1)-cy(x,ANCHOR_PLANE-6,z,4.2,6.1)
  a+=box(x-6,1.,z-4.7,12.,2.,9.4)
  a-=cy(x,ANCHOR_PLANE-6,z,4.2,6.1)
  fixture+=a
export(fixture,'display_fit_frame',b.Rot(90,0,0))
print('Refreshed support-free fit frame',flush=True)
''',ns)
