"""Prepare the unchanged, PLA-fit-tested LED insert as a separate PETG job.

The current assembly supplies the actual insert geometry. Generic PETG is an
installed Bambu preset compatible with this P1S; physical AMS slot 3 is mapped
in the Send dialog. No PLA/PETG bonded print or enclosure revision is created.
"""
from pathlib import Path
import copy
import hashlib
import json
import zipfile

import build123d as b
import trimesh

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'cad/output/v51_petg_led_insert'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'cad/output/v51_dc_inlet_panel/LUMON_v51_GLUE_DC_INLET_ASSEMBLY.step'
parts = {p.label: p for p in b.import_step(SOURCE).children}
insert = copy.deepcopy(parts['led_diffuser'])
insert.parent = None
assert insert.is_valid and len(insert.solids()) == 1
def volume(shape):
    return sum(q.volume for q in shape.solids()) if shape else 0.

clashes = {n: volume(insert & p)
           for n, p in parts.items() if n != 'led_diffuser'}
assert max(clashes.values()) < .05, clashes
b.export_step(insert, OUT / 'led_insert.step')

# Existing flange-down orientation: broad rear flange touches the bed; the
# 0.8 mm light-transmitting face bridges only the short cavity dimension.
oriented = b.Rot(-90, 0, 0) * insert
bb = oriented.bounding_box()
oriented = b.Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * oriented
b.export_stl(oriented, OUT / 'led_insert_print.stl', tolerance=.02)
m = trimesh.load_mesh(OUT / 'led_insert_print.stl')
assert m.is_watertight and m.is_volume
previous = trimesh.load_mesh(ROOT / 'cad/output/v31_cradle_retention/led_diffuser.stl')
assert abs(m.volume - previous.volume) < .05
assert max(abs(m.extents - previous.extents)) < .01

code = (ROOT / 'cad/review/pack_printer_projects_v25.py').read_text()
code = code.replace("OUT=ROOT/'cad/output/v25_tapered_printer'",
                    "OUT=ROOT/'cad/output/v51_petg_led_insert'")
code = code[:code.index("project('01_shell_with_logo'")]
ns = {'__file__': str(__file__)}
exec(compile(code, __file__, 'exec'), ns)
with zipfile.ZipFile(ROOT / 'cad/output/v51_dc_inlet_panel/02_DC_inlet_glue_panel.3mf') as z:
    settings = json.loads(z.read('Metadata/project_settings.config'))

profiles = Path('/Applications/BambuStudio.app/Contents/Resources/profiles/BBL/filament')
index = {}
for path in profiles.rglob('*.json'):
    data = json.loads(path.read_text())
    if 'name' in data:
        index[data['name']] = data

def resolve(name):
    d = index[name]
    result = resolve(d['inherits']) if d.get('inherits') else {}
    for included in d.get('include', []):
        result.update(resolve(included))
    result.update(d)
    return result

preset = resolve('Generic PETG')
assert 'Bambu Lab P1S 0.4 nozzle' in preset['compatible_printers']
ignored = {'type', 'name', 'inherits', 'from', 'setting_id', 'instantiation',
           'compatible_printers', 'compatible_printers_condition',
           'compatible_prints', 'compatible_prints_condition', 'filament_id', 'include'}
for key, value in preset.items():
    if key not in ignored:
        settings[key] = copy.deepcopy(value)
settings.update({
    'filament_settings_id': ['Generic PETG'],
    'filament_ids': ['GFG99'],
    'filament_colour': ['#E2EEF2'],
    'filament_multi_colour': ['#E2EEF2'],
    'filament_colour_type': ['0'],
    'filament_map': ['1'],
    'filament_nozzle_map': ['0'],
    'filament_volume_map': ['0'],
    'filament_self_index': ['1'],
    'filament_printable': ['1'],
    'layer_height': '0.2', 'initial_layer_print_height': '0.2',
    'wall_loops': '2', 'top_shell_layers': '4', 'bottom_shell_layers': '4',
    'sparse_infill_density': '15%', 'sparse_infill_pattern': 'gyroid',
    'enable_support': '0', 'support_filament': '0', 'support_interface_filament': '0',
    'enable_prime_tower': '0', 'brim_type': 'no_brim', 'brim_width': '0',
    'outer_wall_speed': '30', 'inner_wall_speed': '60',
    'top_surface_speed': '30', 'internal_solid_infill_speed': '60',
    'sparse_infill_speed': '60', 'bridge_speed': '25',
    'default_acceleration': '3000', 'elefant_foot_compensation': '0.1',
    'flush_volumes_matrix': ['0'], 'flush_volumes_vector': ['140','140'],
})
process_keys = {'layer_height', 'initial_layer_print_height', 'wall_loops',
    'top_shell_layers', 'bottom_shell_layers', 'sparse_infill_density',
    'sparse_infill_pattern', 'enable_support', 'support_filament',
    'support_interface_filament', 'enable_prime_tower', 'brim_type', 'brim_width',
    'outer_wall_speed', 'inner_wall_speed', 'top_surface_speed',
    'internal_solid_infill_speed', 'sparse_infill_speed', 'bridge_speed',
    'default_acceleration', 'elefant_foot_compensation'}
settings['different_settings_to_system'] = [';'.join(sorted(process_keys)), '', '']
ns['settings'] = settings
ns['project']('01_LED_insert_PETG', [
    ('Translucent PETG LED insert', [('led_insert_print.stl', 1)], (105, 123))])

report = {
    'status': 'Geometry checked and project prepared; native slicing and fresh plate clearance pending; not dispatched',
    'source': str(SOURCE.relative_to(ROOT)),
    'geometry_matches_fit_test': True,
    'watertight': bool(m.is_watertight),
    'print_dimensions_mm': m.extents.tolist(),
    'volume_mm3': float(m.volume),
    'assembly_clashes_mm3': {n: v for n, v in clashes.items() if v > .001},
    'material': 'User-confirmed translucent PETG in AMS slot 3',
    'preset': 'Installed Generic PETG, brand unspecified',
    'project_extruder': 1, 'physical_ams_mapping_required': 'A3',
    'nozzle_c': settings['nozzle_temperature'],
    'textured_bed_c': settings['textured_plate_temp'],
    'orientation': 'Rear flange on bed; short cavity bridge; no supports',
    'installation': 'Insert from behind the light opening; test fit and blue-light transmission before small adhesive points on flange. Do not load native buttons or LED.',
    'dispatch': False,
    'stl_sha256': hashlib.sha256((OUT / 'led_insert_print.stl').read_bytes()).hexdigest(),
}
(OUT / 'audit.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
