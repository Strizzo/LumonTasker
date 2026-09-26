"""Package the external-supply display body for Bambu Studio review.

This does not start a print. The V50 roof/hatch can attach after the body is
printed; the navy base and low-voltage inlet insert remain separate parts.
"""
from pathlib import Path
import json
import zipfile

import trimesh

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/output/v51_external_power_body'
audit=json.loads((OUT/'audit.json').read_text())
assert audit['printed_roof_rear_hatch_interfaces_unchanged']
mesh=trimesh.load_mesh(OUT/'display_body_front_down_print.stl')
assert mesh.is_watertight and mesh.is_volume
assert mesh.extents[0]<220 and mesh.extents[1]<235

source=(ROOT/'cad/review/pack_shell_v37.py').read_text()
source=source.replace("OUT=ROOT/'cad/output/v37_logo_spacing'", "OUT=ROOT/'cad/output/v51_external_power_body'")
source=source[:source.index("project('01_shell_with_logo'")]
ns={'__file__':str(__file__)}
exec(compile(source,__file__,'exec'),ns)
with zipfile.ZipFile(ROOT/'cad/output/v50_full_display_preflight/02_V50_display_roof_and_hatch.3mf') as z:
    settings=json.loads(z.read('Metadata/project_settings.config'))
updates={
    'wall_loops':'3',
    'top_shell_layers':'4',
    'bottom_shell_layers':'4',
    'sparse_infill_density':'8%',
    'sparse_infill_pattern':'gyroid',
    'support_top_z_distance':'0.12',
    'enable_support':'1',
    'support_type':'tree(auto)',
    'support_style':'default',
    'enable_prime_tower':'0',
    'brim_type':'no_brim',
}
settings.update(updates)
settings['different_settings_to_system'][0]=';'.join(sorted(set(
    settings['different_settings_to_system'][0].split(';'))|set(updates)))
ns['settings']=settings
ns['project']('01_V51_display_body_external_power',[
    ('Display bay body — external 24 V adapter',
     [('display_body_front_down_print.stl',2)],(18,10))])
settings['support_type']='tree(auto)'
settings['support_style']='default'
ns['project']('02_V51_display_body_upright',[
    ('Display bay body — upright support comparison',
     [('display_body_upright_print.stl',2)],((256-218.96)/2,(256-170.75)/2))])
(OUT/'body_plate_manifest.json').write_text(json.dumps({
    'status':'Prepared; requires native slice and toolpath review before print',
    'project':'01_V51_display_body_external_power.3mf',
    'upright_comparison_project':'02_V51_display_body_upright.3mf',
    'filament':'A2 PolyTerra Cotton White PLA only',
    'body_print_bounds_mm':mesh.extents.tolist(),
    'bed_origin_xy_mm':[18,10],
    'profile_changes':updates,
    'bed_clear_since_V50':False,
    'dispatched':False,
    'physical_fit_dependency':'Print body, then seat measured display and trial V50 roof and hatch',
},indent=2)+'\n')
print('Prepared',OUT/'01_V51_display_body_external_power.3mf')
