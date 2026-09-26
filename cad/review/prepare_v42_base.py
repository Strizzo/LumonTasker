"""Single navy plate for the lightweight printer foot. GUI review required."""
from pathlib import Path
import json,zipfile
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/output/v42_light_printer_base'
src=(ROOT/'cad/review/pack_shell_v37.py').read_text()
src=src.replace("OUT=ROOT/'cad/output/v37_logo_spacing'", "OUT=ROOT/'cad/output/v42_light_printer_base'")
src=src[:src.index("project('01_shell_with_logo'")]
ns={'__file__':str(__file__)}
exec(compile(src,__file__,'exec'),ns)
with zipfile.ZipFile(ROOT/'cad/output/v40_display_mount/01_V40_display_fit_kit.3mf') as z:
    settings=json.loads(z.read('Metadata/project_settings.config'))
settings.update(wall_loops='3',top_shell_layers='4',top_shell_thickness='0.8',bottom_shell_layers='4',bottom_shell_thickness='0',
                sparse_infill_density='10%',sparse_infill_pattern='gyroid',enable_support='0',enable_prime_tower='0',brim_type='no_brim')
settings['different_settings_to_system'][0]=';'.join(sorted(set(settings['different_settings_to_system'][0].split(';'))|{
    'wall_loops','top_shell_layers','top_shell_thickness','bottom_shell_layers','bottom_shell_thickness',
    'sparse_infill_density','sparse_infill_pattern','enable_support','enable_prime_tower','brim_type'}))
ns['settings']=settings
ns['project']('01_V42_light_printer_base',[('Light printer base',[('printer_base_print.stl',1)],(40,40))])
(OUT/'plate_manifest.json').write_text(json.dumps({
    'file':'01_V42_light_printer_base.3mf','material':'A1 Bambu Navy Blue PLA only',
    'layer_mm':.2,'walls':3,'top_layers':4,'bottom_layers':4,'infill':'10% gyroid',
    'supports':False,'colour_swaps':0,'status':'Prepared; GUI settings/slice/mass comparison pending',
    'dispatch_authorization':'User says go on with the project and retains printing authorization; confirm current plate is clear before dispatch.',
    'dispatched':False},indent=2)+'\n')
