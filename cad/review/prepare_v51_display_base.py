"""Package the closed-bottom navy display plinth for later Bambu review.

This only makes a plate project. The display body is currently occupying the
printer; the plate must be sliced/reviewed before it can be sent.
"""
from pathlib import Path
import json
import zipfile

import trimesh
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'cad/output/v51_external_power_body'
mesh = trimesh.load_mesh(OUT/'display_base_print.stl')
assert mesh.is_watertight and mesh.is_volume
assert abs(mesh.bounds[0][2]) < .01 and abs(mesh.bounds[1][2]-9) < .01
assert mesh.extents[0] < 220 and mesh.extents[1] < 170
flipped = mesh.copy()
flipped.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
flipped.apply_translation(-flipped.bounds[0])
assert flipped.is_watertight and flipped.is_volume
assert abs(flipped.bounds[0][2]) < .01
flipped.export(OUT/'display_base_top_down_print.stl')

source = (ROOT/'cad/review/pack_shell_v37.py').read_text()
source = source.replace("OUT=ROOT/'cad/output/v37_logo_spacing'",
                        "OUT=ROOT/'cad/output/v51_external_power_body'")
source = source[:source.index("project('01_shell_with_logo'")]
namespace = {'__file__':str(__file__)}
exec(compile(source, __file__, 'exec'), namespace)
with zipfile.ZipFile(ROOT/'cad/output/v50_full_display_preflight/02_V50_display_roof_and_hatch.3mf') as z:
    settings = json.loads(z.read('Metadata/project_settings.config'))
changes = {
    'wall_loops':'3',
    'top_shell_layers':'4',
    'bottom_shell_layers':'4',
    'sparse_infill_density':'8%',
    'sparse_infill_pattern':'gyroid',
    'enable_support':'0',
    'enable_prime_tower':'0',
    'brim_type':'no_brim',
}
settings.update(changes)
settings['different_settings_to_system'][0] = ';'.join(sorted(set(
    settings['different_settings_to_system'][0].split(';')) | set(changes)))
namespace['settings'] = settings
namespace['project']('03_V51_closed_display_base', [
    ('Display bay navy plinth — closed underside',
     [('display_base_print.stl', 1)], (18, 42))])
namespace['project']('04_V51_closed_display_base_top_down', [
    ('Display bay navy plinth — top face on bed',
     [('display_base_top_down_print.stl', 1)], (19, 43))])
(OUT/'base_plate_manifest.json').write_text(json.dumps({
    'status':'Revised closed-surface base prepared; native slice and print pending',
    'project':'04_V51_closed_display_base_top_down.3mf',
    'base_down_comparison_project':'03_V51_closed_display_base.3mf',
    'filament':'A1 Bambu navy blue PLA only',
    'mesh_bounds_mm':mesh.bounds.tolist(),
    'profile_changes':changes,
    'superseded_open_pocket_slice':'4h38m, 124.03g, floating-cantilever warning; not sent',
    'note':'Both surfaces are now closed. Native slice/review top-down project before print.'
},indent=2)+'\n')
