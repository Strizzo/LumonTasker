"""Prepare the V51 DC inlet cover with a 5 mm inward glue sleeve.

User explicitly chooses to glue the socket instead of a separate rear retainer.
The sleeve adds adhesive contact around its nominal 10 mm round neck. Actual
socket neck length/diameter and physical seating still require a dry fit.
No existing printed body/base is changed and no print is dispatched here.
"""
from pathlib import Path
import copy
import json
import sys
import zipfile

import build123d as b
import trimesh

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'cad/output/v51_dc_inlet_panel'
OUT.mkdir(parents=True, exist_ok=True)
PREV = ROOT / 'cad/output/v51_external_power_body'
sys.path.insert(0, str(ROOT / 'files'))
from render3d import Scene

NOMINAL_SOCKET_DIAMETER = 10.0  # User specifies 1 cm mounting hole.
PRINT_DIAMETER = 10.2          # 0.2 mm diametral fit allowance, not a measured fit.
CX, CZ = 176.98, 62.0
SLEEVE_LENGTH = 5.0           # Added inside existing locating shoulder.
SLEEVE_WALL = 2.0
SHOULDER_INNER_Y = 167.76

def volume(shape):
    return sum(s.volume for s in shape.solids()) if shape else 0.0

parts = {s.label: copy.deepcopy(s)
         for s in b.import_step(PREV / 'whole_enclosure_review.step').children}
original = b.import_step(PREV / 'dc_inlet_blank.step')
sleeve = b.Pos(CX, SHOULDER_INNER_Y - SLEEVE_LENGTH / 2 + 0.01, CZ) * b.Rot(-90, 0, 0) * b.Cylinder(
    PRINT_DIAMETER / 2 + SLEEVE_WALL, SLEEVE_LENGTH + 0.02)
bore = b.Pos(CX, 166.75, CZ) * b.Rot(-90, 0, 0) * b.Cylinder(PRINT_DIAMETER / 2, 20)
panel = (original + sleeve) - bore
assert panel.is_valid and len(panel.solids()) == 1
clashes = {name: overlap for name, part in parts.items()
           if (overlap := volume(panel & part)) > 0.1}
assert not clashes, clashes
assert volume(panel & bore) < 0.001
assert volume(panel - (original + sleeve)) < 0.001
panel.label = 'DC_INLET_GLUE_PANEL_10mm_SOCKET_5mm_INWARD_SLEEVE'
panel.color = b.Color('#F0F1EB')
b.export_step(panel, OUT / 'dc_inlet_glue_panel.step')

# Outside face against the bed; locating shoulder grows upward, so the panel
# and round through-hole need no support in this orientation.
oriented = b.Rot(-90, 0, 0) * panel
bb = oriented.bounding_box()
oriented = b.Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * oriented
b.export_stl(oriented, OUT / 'dc_inlet_glue_panel_print.stl', tolerance=0.02)
mesh = trimesh.load_mesh(OUT / 'dc_inlet_glue_panel_print.stl')
assert mesh.is_watertight and mesh.is_volume
assert abs(mesh.extents[2] - (2.99 + SLEEVE_LENGTH)) < 0.01

preview = b.Compound(children=[*parts.values(), panel])
b.export_step(preview, OUT / 'LUMON_v51_GLUE_DC_INLET_ASSEMBLY.step')

scene = Scene(950, 650, ss=1)
scene.add(panel, '#F0F1EB')
scene.look_at((225, 270, 115), (CX, 169, CZ), fov=30)
scene.save(str(OUT / 'dc_inlet_glue_panel_front.png'))
scene = Scene(950, 650, ss=1)
scene.add(panel, '#F0F1EB')
scene.look_at((215, 75, 110), (CX, 166, CZ), fov=32)
scene.save(str(OUT / 'dc_inlet_glue_panel_rear.png'))

source = (ROOT / 'cad/review/pack_shell_v37.py').read_text()
source = source.replace("OUT=ROOT/'cad/output/v37_logo_spacing'",
                        "OUT=ROOT/'cad/output/v51_dc_inlet_panel'")
source = source[:source.index("project('01_shell_with_logo'")]
ns = {'__file__': str(__file__)}
exec(compile(source, __file__, 'exec'), ns)
with zipfile.ZipFile(PREV / '04_V51_closed_display_base_top_down.3mf') as archive:
    settings = json.loads(archive.read('Metadata/project_settings.config'))
updates = {
    'layer_height': '0.2',
    'initial_layer_print_height': '0.2',
    'wall_loops': '3',
    'top_shell_layers': '4',
    'bottom_shell_layers': '4',
    'sparse_infill_density': '15%',
    'sparse_infill_pattern': 'gyroid',
    'enable_support': '0',
    'enable_prime_tower': '0',
    'brim_type': 'no_brim',
}
settings.update(updates)
settings['different_settings_to_system'][0] = ';'.join(sorted(set(
    settings['different_settings_to_system'][0].split(';')) | set(updates)))
ns['settings'] = settings
ns['project']('02_DC_inlet_glue_panel', [
    ('DC inlet cover — 5 mm inward glue sleeve',
     [('dc_inlet_glue_panel_print.stl', 2)], (100, 105)),
])

report = {
    'status': 'User-selected glue sleeve CAD and unsliced Bambu project prepared; physical socket/panel dry fit pending; not dispatched',
    'socket_nominal_mount_diameter_mm': NOMINAL_SOCKET_DIAMETER,
    'printed_bore_mm': PRINT_DIAMETER,
    'diametral_fit_allowance_mm': PRINT_DIAMETER - NOMINAL_SOCKET_DIAMETER,
    'outer_face_mm': [56.0, 37.1],
    'locating_shoulder_mm': [46.9, 28.0],
    'panel_and_locating_shoulder_thickness_mm': 2.99,
    'inward_sleeve_length_mm': SLEEVE_LENGTH,
    'sleeve_radial_wall_mm': SLEEVE_WALL,
    'sleeve_outer_diameter_mm': PRINT_DIAMETER + SLEEVE_WALL * 2,
    'total_thickness_mm': 2.99 + SLEEVE_LENGTH,
    'printed_case_interface_preserved': True,
    'body_overlap_mm3': volume(panel & parts['tub_left']),
    'assembly_clashes': clashes,
    'watertight': bool(mesh.is_watertight),
    'support_required': False,
    'filament': 'Cotton White PLA, AMS slot 2',
    'socket_retention': 'User chooses glue to the 5 mm inward sleeve; no separate clamp or black-body measurements required',
    'panel_retention': 'Glue fitted locating shoulder/outer face into existing rear recess; no drilling',
    'physical_fit': 'Dry fit socket neck, sleeve clearance and case recess before glue; dimensions of rectangular rear socket body remain unmeasured',
    'dispatch': False,
}
(OUT / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2), flush=True)
