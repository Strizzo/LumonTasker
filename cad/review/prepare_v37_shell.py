"""Prepare registered front-face-down meshes; no print dispatch or slice claim."""
from pathlib import Path
import json
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'cad/output/v37_logo_spacing'
shell=trimesh.load_mesh(OUT/'shell_assembly.stl')
logo=trimesh.load_mesh(OUT/'logo_assembly.stl')
rotation=trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0])
for m in (shell,logo):m.apply_transform(rotation)
shift=-shell.bounds[0]
for name,m in [('shell',shell),('logo',logo)]:
 m.apply_translation(shift)
 assert m.is_watertight
 m.export(OUT/(name+'_registered.stl'))
assert max(shell.extents[:2])<256
(OUT/'print_preparation.json').write_text(json.dumps(dict(status='Registered meshes only; slicer review and final print approval pending',orientation='front face down',shell_bounds_mm=shell.bounds.tolist(),shell_material='PolyTerra Cotton White PLA',shell_ams_slot=2,logo_material='Bambu Navy Blue PLA',logo_ams_slot=1,bed_leveling=False,supports='Must review rounded roof and internal features in slicer',colour_changes='Logo embedded in front face; quantify after slicing',retention_passed=True,paper_feed_tear_passed=True),indent=2)+'\n')
print('Registered meshes prepared:',shell.extents)
