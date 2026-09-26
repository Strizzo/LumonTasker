"""Registered meshes and separate white shell/cover/navy base Bambu projects."""
from pathlib import Path
import numpy as np
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'cad/output/v38_integrated_rear'
a=b.import_step(OUT/'whole_enclosure_review.step');p={s.label:s for s in a.children}
meshes={}
for k in ['shell','logo']:
 path=OUT/(k+'_global_assembly.stl');b.export_stl(p[k],path,tolerance=.035)
 meshes[k]=trimesh.load_mesh(path);meshes[k].apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
shift=-meshes['shell'].bounds[0]
for k,m in meshes.items():m.apply_translation(shift);assert m.is_watertight;m.export(OUT/(k+'_registered.stl'))
# Reuse known packer definitions without executing its V37 output section.
src=(ROOT/'cad/review/pack_shell_v37.py').read_text()
src=src.replace("OUT=ROOT/'cad/output/v37_logo_spacing'","OUT=ROOT/'cad/output/v38_integrated_rear'")
src=src[:src.index("project('01_shell_with_logo'")]
code=compile(src,str(ROOT/'cad/review/pack_shell_v38.py'),'exec');ns={'__file__':str(ROOT/'cad/review/pack_shell_v38.py')};exec(code,ns)
ns['project']('01_V38_shell_with_logo',[('V38 square rear shell',[('shell_registered.stl',2),('logo_registered.stl',1)],(25,35))])
settings=ns['settings'];settings['enable_prime_tower']='0'
settings['different_settings_to_system'][0]+=';enable_prime_tower'
ns['project']('02_V38_integrated_rear_cover',[('V38 integrated rear retaining cover',[('rear_cover_integrated_print.stl',2)],(35,25))])
settings['enable_support']='0'
ns['project']('03_V38_navy_base',[('V38 matching navy base',[('foot_right_bonded_print.stl',1)],(35,35))])
