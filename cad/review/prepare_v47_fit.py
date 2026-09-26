"""Prepare corrected display fixture rear-down; GUI slicing remains required."""
raise SystemExit('V47 mount shift withdrawn by user; run build_v48_display_original_mounts.py and prepare_v48_fit.py instead.')

from pathlib import Path
import json,zipfile
import trimesh
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/output/v47_display_fit_correction'
audit=json.loads((OUT/'audit.json').read_text())
assert audit['production_body_valid'] and audit['fixture_valid']
src=(ROOT/'cad/review/pack_shell_v37.py').read_text()
src=src.replace("OUT=ROOT/'cad/output/v37_logo_spacing'", "OUT=ROOT/'cad/output/v47_display_fit_correction'")
src=src[:src.index("project('01_shell_with_logo'")]
ns={'__file__':str(__file__)}
exec(compile(src,__file__,'exec'),ns)
with zipfile.ZipFile(ROOT/'cad/output/v46_display_seat_fit/01_V46_display_seat_fit.3mf') as z:
    settings=json.loads(z.read('Metadata/project_settings.config'))
updates={
    'support_style':'snug','support_top_z_distance':'0.2',
    'support_interface_top_layers':'3','support_interface_spacing':'0.15',
    'support_interface_pattern':'rectilinear','support_interface_speed':['40','40'],
    'support_speed':['100','100'],'support_object_xy_distance':'0.3',
    'support_base_pattern_spacing':'4','support_interface_loop_pattern':'1',
    'top_surface_speed':['50','50'],'bridge_speed':['30','30'],
    'brim_type':'outer_only','brim_width':'3',
    'support_filament':'0','support_interface_filament':'0','enable_prime_tower':'0'}
settings.update(updates)
settings['different_settings_to_system'][0]=';'.join(sorted(set(settings['different_settings_to_system'][0].split(';'))|set(updates)))
ns['settings']=settings
mesh=trimesh.load_mesh(OUT/'display_fit_seat_up_print.stl')
xy=tuple((256-mesh.extents[:2])/2)
assert min(xy)>10
ns['project']('01_V47_display_corrected_seat_up',[
    ('Corrected display seat and integral mounts', [('display_fit_seat_up_print.stl',2)],xy)])
(OUT/'plate_manifest.json').write_text(json.dumps({
    'project':'01_V47_display_corrected_seat_up.3mf',
    'filament':'PolyTerra Cotton White PLA, A2 only','colour_swaps':0,
    'objects':1,'placement_xy_mm':xy,'changes':updates,
    'support_reason':'Rear-down print puts glass and metal bearing lands upward; supports touch non-contact reverse faces',
    'support_gap_reason':'Retain 0.2 mm same-PLA release gap, use denser three-layer interface; never set zero gap for this same-material print',
    'source_reference':'https://csm.bblcdn.com/hub/4668d0ca43994ff3bff4b37f1a65c2e7.pdf#page=66',
    'status':'Prepared, GUI slicing and support review pending',
    'bed_clear':False,'bed_clear_evidence':'Asked user; awaiting fresh confirmation',
    'dispatched':False},indent=2)+'\n')
