"""Prepare the one-part V46 display seat fixture in white PLA; GUI slice next."""
from pathlib import Path
import json, zipfile
import trimesh
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/output/v46_display_seat_fit'
audit=json.loads((OUT/'audit.json').read_text())
assert audit['status'].startswith('Fit-frame CAD checks passed')
src=(ROOT/'cad/review/pack_shell_v37.py').read_text()
src=src.replace("OUT=ROOT/'cad/output/v37_logo_spacing'", "OUT=ROOT/'cad/output/v46_display_seat_fit'")
src=src[:src.index("project('01_shell_with_logo'")]
ns={'__file__':str(__file__)}
exec(compile(src,__file__,'exec'),ns)
with zipfile.ZipFile(ROOT/'cad/output/v40_display_mount/01_V40_display_fit_kit.3mf') as z:
    settings=json.loads(z.read('Metadata/project_settings.config'))
updates={
    'wall_loops':'3','top_shell_layers':'4','top_shell_thickness':'0.8',
    'bottom_shell_layers':'4','bottom_shell_thickness':'0',
    'sparse_infill_density':'10%','sparse_infill_pattern':'gyroid',
    'enable_support':'1','support_type':'normal(auto)','support_style':'default',
    'support_threshold_angle':'30','support_on_build_plate_only':'0',
    'support_remove_small_overhang':'0','support_top_z_distance':'0.2',
    'support_bottom_z_distance':'0.2','support_interface_top_layers':'2',
    'support_interface_bottom_layers':'2','support_object_xy_distance':'0.35',
    'support_filament':'0','support_interface_filament':'0',
    'enable_prime_tower':'0','brim_type':'no_brim',
    'layer_height':'0.2','initial_layer_print_height':'0.2',
    'elefant_foot_compensation':'0.15'}
settings.update(updates)
settings['different_settings_to_system'][0]=';'.join(sorted(set(settings['different_settings_to_system'][0].split(';'))|set(updates)))
ns['settings']=settings
mesh=trimesh.load_mesh(OUT/'display_seat_fit_print.stl')
xy=((256-mesh.extents[0])/2,(256-mesh.extents[1])/2)
assert min(xy)>10 and max(mesh.bounds[1][:2]+xy)<246
ns['project']('01_V46_display_seat_fit',[('3 mm display seat with integral mounts',
                [('display_seat_fit_print.stl',2)],xy)])
(OUT/'plate_manifest.json').write_text(json.dumps({
    'project':'01_V46_display_seat_fit.3mf','material':'A2 PolyTerra Cotton White PLA only',
    'objects':1,'placement_xy_mm':xy,'colour_swaps':0,'supports':'Normal auto, same white PLA, removable',
    'settings':updates,'status':'Prepared; GUI slicing/support review pending',
    'bed_clear':False,'bed_clear_evidence':'User answered Not yet after navy base completion',
    'print_authorization':'Existing authorization for mechanical test prints; await current bed clearance',
    'dispatched':False},indent=2)+'\n')
