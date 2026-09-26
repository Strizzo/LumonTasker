"""Two small identical depth samples; compare only support top-contact gap."""
from pathlib import Path
import json, zipfile, xml.etree.ElementTree as E
import trimesh

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/output/v49_measured_display_depth'
audit=json.loads((OUT/'audit.json').read_text())
assert audit['production_body_valid'] and audit['fixture_valid']
src=(ROOT/'cad/review/pack_shell_v37.py').read_text()
src=src.replace("OUT=ROOT/'cad/output/v37_logo_spacing'", "OUT=ROOT/'cad/output/v49_measured_display_depth'")
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
    'support_base_pattern_spacing':'2.5','support_interface_loop_pattern':'1',
    'top_surface_speed':['50','50'],'bridge_speed':['30','30'],
    'brim_type':'no_brim','support_filament':'0','support_interface_filament':'0',
    'enable_prime_tower':'0'}
settings.update(updates)
settings['different_settings_to_system'][0]=';'.join(sorted(set(settings['different_settings_to_system'][0].split(';'))|set(updates)))
ns['settings']=settings
filename='corner_depth_coupon_front_down.stl'
mesh=trimesh.load_mesh(OUT/filename)
assert mesh.is_watertight
name='01_V49_depth_and_screw_coupons'
objects=[('LEFT - reference support gap 0.20',[(filename,2)],(65,100)),
         ('RIGHT - closer support gap 0.12',[(filename,2)],(140,100))]
ns['project'](name,objects)
path=OUT/(name+'.3mf')
with zipfile.ZipFile(path) as z:
    archive={n:z.read(n) for n in z.namelist()}
cfg=E.fromstring(archive['Metadata/model_settings.config'])
objs=cfg.findall('object')
assert len(objs)==2
for obj,gap in zip(objs,('0.2','0.12')):
    E.SubElement(obj,'metadata',key='support_top_z_distance',value=gap)
archive['Metadata/model_settings.config']=E.tostring(cfg,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
    for n,data in archive.items(): z.writestr(n,data)
(OUT/'plate_manifest.json').write_text(json.dumps({
    'project':path.name,'filament':'PolyTerra Cotton White PLA, A2 only',
    'colour_swaps':0,'objects':2,'print_orientation':'Front face down, restored V46 orientation',
    'geometry':'Two identical cropped production upper-right corners, one integral arm each',
    'left_support_top_gap_mm':.2,'right_support_top_gap_mm':.12,
    'comparison':'All other support/material/process settings identical; compare finish and removability',
    'changes':updates,'bed_leveling':False,'timelapse':False,
    'status':'Prepared; GUI slice and per-object support-gap verification pending',
    'bed_clear':False,'bed_clear_evidence':'No fresh confirmation after V48 removal',
    'dispatched':False},indent=2)+'\n')
