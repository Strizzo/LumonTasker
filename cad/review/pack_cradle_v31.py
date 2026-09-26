"""Prepare one-colour v31 cradle and bar plate from the v28 project.

No slicing or printer dispatch. Recheck native Bambu settings and current AMS
contents before print approval; historical project profiles are not live data.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as E
from zipfile import ZipFile, ZIP_DEFLATED
import trimesh

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'cad/output/v31_cradle_retention'
TEMPLATE = ROOT / 'cad/output/v28_integrated_top/02_cradle_and_bars.3mf'
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
E.register_namespace('', NS)


def tag(name):
    return '{' + NS + '}' + name


with ZipFile(TEMPLATE) as z:
    content = {name: z.read(name) for name in z.namelist()}
model = E.fromstring(content['3D/3dmodel.model'])
cfg = E.fromstring(content['Metadata/model_settings.config'])
settings = json.loads(content['Metadata/project_settings.config'])
settings.update(enable_prime_tower='0', enable_support='0', brim_width='3',
                wall_loops='4', top_shell_layers='5', bottom_shell_layers='5',
                sparse_infill_density='15%', sparse_infill_pattern='gyroid')
# Bambu restores preset defaults on import unless process overrides are also
# listed here. Keep the settings and the override list in sync.
process_overrides = {'enable_prime_tower', 'enable_support', 'brim_type',
                     'brim_width', 'wall_loops', 'top_shell_layers',
                     'bottom_shell_layers', 'sparse_infill_density',
                     'sparse_infill_pattern'}
settings['brim_type'] = 'outer_only'
different = settings.setdefault('different_settings_to_system', ['', '', '', ''])
different[0] = ';'.join(sorted(set(filter(None, different[0].split(';'))) |
                                process_overrides))
placement = {'cradle_tray': (45, 10), 'retaining_bar_58': (35, 176),
             'retaining_bar_137': (35, 236)}
resources = model.find(tag('resources'))
build = model.find(tag('build'))
bounds = {}
for obj in cfg.findall('object'):
    name = obj.find("metadata[@key='name']").attrib['value']
    part = obj.find('part')
    mesh = trimesh.load_mesh(OUT / (name + '.stl'))
    assert mesh.is_watertight, name
    geo_obj = resources.find(f"{tag('object')}[@id='{part.attrib['id']}']")
    geo_obj.remove(geo_obj.find(tag('mesh')))
    geo = E.SubElement(geo_obj, tag('mesh'))
    vertices = E.SubElement(geo, tag('vertices'))
    triangles = E.SubElement(geo, tag('triangles'))
    for vertex in mesh.vertices:
        E.SubElement(vertices, tag('vertex'), **dict(zip(('x', 'y', 'z'),
                     (f'{v:.7f}' for v in vertex))))
    for face in mesh.faces:
        E.SubElement(triangles, tag('triangle'), **dict(zip(('v1', 'v2', 'v3'), map(str, face))))
    part.find('mesh_stat').set('face_count', str(len(mesh.faces)))
    x, y = placement[name]
    build.find(f"{tag('item')}[@objectid='{obj.attrib['id']}']").set(
        'transform', f'1 0 0 0 1 0 0 0 1 {x} {y} 0')
    lo, hi = mesh.bounds
    bounds[name] = [float(x+lo[0]-3), float(y+lo[1]-3),
                    float(x+hi[0]+3), float(y+hi[1]+3)]
    assert min(bounds[name][:2]) >= 0 and max(bounds[name][2:]) <= 256, name
    assert bounds[name][0] > 18 or bounds[name][1] > 28, name

for i, (name, a) in enumerate(bounds.items()):
    for other, c in list(bounds.items())[i+1:]:
        assert a[2] <= c[0] or c[2] <= a[0] or a[3] <= c[1] or c[3] <= a[1], (name, other)
cfg.find("plate/metadata[@key='plater_name']").set('value', 'V31 revised cradle and retaining bars')
content['3D/3dmodel.model'] = E.tostring(model, encoding='utf-8', xml_declaration=True)
content['Metadata/model_settings.config'] = E.tostring(cfg, encoding='utf-8', xml_declaration=True)
content['Metadata/project_settings.config'] = json.dumps(settings, indent=2).encode()
destination = OUT / '02_cradle_and_bars.3mf'
with ZipFile(destination, 'w', ZIP_DEFLATED) as z:
    for name, data in content.items():
        z.writestr(name, data)
(OUT / 'plate_layout.json').write_text(json.dumps({
    'status': 'Prepared only; native slicer review, current filament selection and print approval pending.',
    'parts': list(placement), 'brim_inclusive_bounds_xy_mm': bounds,
    'filament': 'Single PLA project filament 2; verify actual AMS slot/material before release.',
    'print_time': None,
}, indent=2) + '\n')
print(destination)
