"""Capture the removable cradle with the existing lower rear-bar screws.

The printed v28 shell and the approved v27/v28 cradle remain unchanged.
Two downward legs and forward lips are added to the lower bar, outside the
switch/cable channels. Remove this bar before removing the cradle.
"""
from pathlib import Path
import copy
import json
import shutil
import sys

import build123d as b
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'files'))
from render3d import Scene

OUT = ROOT / 'cad/output/v31_cradle_retention'
OUT.mkdir(parents=True, exist_ok=True)
SHIFT = 218.96
PALE, NAVY = '#DEE9EE', '#173B53'


def box(x, y, z, w, d, h):
    return b.Pos(x+w/2, y+d/2, z+h/2) * b.Box(w, d, h)


def volume(s):
    return sum(v.volume for v in s.solids()) if s else 0.


previous = b.import_step(ROOT / 'cad/output/v30_printer_plinth/whole_enclosure_review.step')
parts = {s.label: s for s in previous.children}
old_bar = b.Pos(-SHIFT, 0, 0) * parts['retaining_bar_58']
tray = b.Pos(-SHIFT, 0, 0) * parts['cradle_tray']
shell = b.Pos(-SHIFT, 0, 0) * parts['shell']
printer = b.import_step(ROOT / 'cad/output/v28_integrated_top/printer_reference.step')

# Tray ends at y160.5, with its top at z16. Allow 0.5 mm in both axes;
# this is a removable keeper, not a preload or interference fit.
bar = copy.deepcopy(old_bar)
for x in (20., 140.):
    bar += box(x, 161, 13.5, 10, 6, 38.5)
    bar += box(x, 156.5, 16.5, 10, 5, 3)
assert bar.is_valid and len(bar.solids()) == 1
assert abs(volume(bar.intersect(old_bar)) - old_bar.volume) < .01

# The installed bar must not contact any installed part or reference hardware.
placed = b.Pos(SHIFT, 0, 0) * bar
clashes = {name: volume(placed.intersect(s)) for name, s in parts.items()
           if name != 'retaining_bar_58'}
assert max(clashes.values()) < .05, clashes
assert volume(bar.intersect(printer)) < .01

# Existing rear screw axes and 6 mm grip length are preserved exactly.
for x in (4.5, 170.5):
    probe = b.Pos(x, 164, 58) * b.Rot(-90, 0, 0) * b.Cylinder(1.69, 6)
    assert volume(bar.intersect(probe)) < .01

# Clear the entire conservative rear cable and rocker paths, not only the
# switch's parked position. The two keeper legs sit on solid side strips.
reliefs = {
    'rocker_sweep': box(35, 67, 0, 31, 120, 24),
    'rear_cables': box(40, 95, 8, 78, 90, 39),
}
obstructions = {name: volume(bar.intersect(s)) for name, s in reliefs.items()}
assert max(obstructions.values()) < .01, obstructions

# Meaningful retention checks: the tray is free inside the intended clearance,
# but is stopped if translated farther rearward or lifted at its rear edge.
motion = {}
for name, offset in [('rear_clear', (0, .45, 0)),
                     ('up_clear', (0, 0, .45)),
                     ('rear_stopped', (0, .75, 0)),
                     ('up_stopped', (0, 0, .75))]:
    motion[name] = volume(bar.intersect(b.Pos(*offset) * tray))
assert motion['rear_clear'] < .01 and motion['up_clear'] < .01, motion
assert motion['rear_stopped'] > 1 and motion['up_stopped'] > 1, motion

# The replacement bar can be installed from the rear without crossing the
# shell, seated cradle or printer. Contact at its screw-mounting face is allowed.
for rear_offset in (.1, 1, 5, 20, 45):
    shifted = b.Pos(0, rear_offset, 0) * bar
    for name, s in [('shell', shell), ('cradle', tray), ('printer', printer)]:
        assert volume(shifted.intersect(s)) < .05, (name, rear_offset)

placed.label = 'retaining_bar_58'
placed.color = b.Color(PALE)
parts[placed.label] = placed
for name, s in parts.items():
    s.label = name
    s.color = b.Color(NAVY if name in {'foot_left', 'foot_right_bonded', 'display_bezel', 'logo'} else PALE)
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()],
                        label='LUMON_V31_CRADLE_RETENTION_REVIEW'), OUT / 'whole_enclosure_review.step')

# Rear face down on the bed, as with the previous retaining bars. The legs
# are flat bed-contact features; the inward-facing lips grow from those legs.
oriented = b.Rot(-90, 0, 0) * bar
bb = oriented.bounding_box()
oriented = b.Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * oriented
b.export_stl(oriented, OUT / 'retaining_bar_58.stl', tolerance=.03)
mesh = trimesh.load_mesh(OUT / 'retaining_bar_58.stl')
assert mesh.is_watertight
for filename in ('cradle_tray.stl', 'retaining_bar_137.stl', 'rear_cover.stl', 'led_diffuser.stl'):
    shutil.copyfile(ROOT / 'cad/output/v28_integrated_top' / filename, OUT / filename)

report = {
    'scope': 'Only lower rear retaining bar changed; printed v28 shell and approved cradle unchanged.',
    'status': 'Prepared fit-test geometry; not sliced, physically tested, or dispatched.',
    'bar_valid': bool(bar.is_valid), 'bar_solids': len(bar.solids()),
    'watertight': bool(mesh.is_watertight), 'print_bounds_mm': mesh.extents.tolist(),
    'added_volume_mm3': bar.volume - old_bar.volume,
    'rear_clearance_mm': .5, 'vertical_clearance_mm': .5,
    'retaining_lip_overlap_mm': 4.,
    'screws': 'Existing two M3x12 lower-bar screws; upper bar uses two more. Check insert depth/bottoming.',
    'assembly_intersections_mm3': clashes, 'relief_intersections_mm3': obstructions,
    'tray_motion_intersections_mm3': motion,
    'bar_installation_path_checked': True,
    'physical_checks_pending': ['tray seating', 'retaining-lip clearance', 'real printer and plugs',
                                'paper feeding/cutting', 'switch clearance', 'rear service'],
}
(OUT / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')

sc = Scene(1100, 750, ss=1)
sc.add(tray, PALE)
sc.add(bar, NAVY)  # Contrast for instructional preview only; print both in one PLA.
sc.look_at((345, 490, 275), (87, 90, 29), fov=32)
sc.save(str(OUT / 'cradle_retention_detail.png'))

print(json.dumps(report, indent=2), flush=True)
