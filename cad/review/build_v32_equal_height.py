"""Equal-height display bay, preserving the exact V31 printer-side assembly.

Review geometry only: inherited display/Pi/power envelopes are unverified.
Reuse V29's modelling functions in this process without modifying that source.
"""
from pathlib import Path
import copy
import itertools
import json
import math
import sys

import build123d as b
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'files')]
from cad import lumon_v29 as m
from render3d import Scene

OUT = ROOT / 'cad/output/v32_equal_height'
OUT.mkdir(parents=True, exist_ok=True)
PALE, NAVY = '#DEE9EE', '#173B53'
NAVY_PARTS = {'foot_left', 'foot_right_bonded', 'display_bezel', 'logo'}


def volume(shape):
    return sum(s.volume for s in shape.solids()) if shape else 0.


def bounds(shape):
    bb = shape.bounding_box()
    return {'min': list(bb.min), 'max': list(bb.max)}


previous = b.import_step(ROOT / 'cad/output/v31_cradle_retention/whole_enclosure_review.step')
before = {s.label: s for s in previous.children}
parts = {name: copy.deepcopy(s) for name, s in before.items()}
old_h = m.p.H
old_display = copy.deepcopy(m.DISPLAY_REFERENCE)
old_lid_xy = copy.deepcopy(m.LID_SCREWS_L)
target_h = before['shell'].bounding_box().max.Z
rise = target_h - old_h
assert abs(rise - 20.) < .001

# Grow the body above the existing foot/base. The screen stays centred in the
# usable raked face; its vertical rise is half the overall height increase.
m.p.H = target_h
m.FACE_LEN = (m.p.H - m.p.lid_t - m.p.skirt_h) / m.CR
m.DZL = m.p.skirt_h + (m.FACE_LEN - m.p.display_h) / 2
m.BEZ_CZ = m.DZL + m.p.display_h / 2

# Move the front cover screws rearward with the taller raked upper wall.
# Both the tub insert lands and cover sleeves use these same coordinates.
original_add_lands = m.add_lid_lands
front_screw_y = old_lid_xy[0][1] + rise * math.tan(math.radians(m.p.rake_deg))


def add_equal_height_lands(tub, side):
    assert side == 'left'
    m.LID_SCREWS_L = [(x, front_screw_y if y == old_lid_xy[0][1] else y)
                      for x, y in m.LID_SCREWS_L]
    return original_add_lands(tub, side)


m.add_lid_lands = add_equal_height_lands
tub = m.build_tub_left()

# Keep the exhaust at its previous distance below the top. The hatch, Pi
# mounts, base ventilation, cable passage and all bay-joining axes stay put.
tub += m.box_at(30, m.p.D - m.p.wall, 120,
                m.p.x_split - 60, m.p.wall, 18)
for i in range(5):
    tub -= m.box_at(30, m.p.D - m.p.wall - 1, 120 + rise + i * 4,
                    m.p.x_split - 60, m.p.wall + 2, 2)
parts['tub_left'] = tub
parts['top_plate_left'] = m.build_lid('left')
parts['display_bezel'] = m.build_display_bezel()
parts['display_retainer'] = m.build_retainer()
display = m.raked(m.box_at(m.p.display_x, m.p.wall, m.DZL,
                          m.p.display_w, m.p.display_t, m.p.display_h))
changed = ['tub_left', 'top_plate_left', 'display_bezel', 'display_retainer']
report = {
    'status': 'CAD review only, not sliced, printed, or physically fitted.',
    'scope': 'Grow display bay to the printer bay height; preserve exact V31 printer assembly and joint datums.',
    'old_height_mm': old_h, 'new_height_mm': target_h,
    'screen_centre_rise_mm': display.center().Z - old_display.center().Z,
    'screen_rearward_movement_mm': display.center().Y - old_display.center().Y,
    'front_cover_screw_y_mm': front_screw_y,
    'changed_parts': changed, 'parts': {}, 'interferences': [],
    'joining_screws_yz_mm': m.SPINE_SCREWS,
    'joining_dowels_yz_mm': m.SPINE_DOWELS,
    'left_hardware': 'Inherited dimensions, unverified: display, Pi/cooler, PSU and inlet are not released.',
    'printer_fit_kit': 'V31 cradle/bar project remains unchanged and compatible; launch approval still required.',
}
assert abs(report['screen_centre_rise_mm'] - rise / 2) < .001

for name, s in parts.items():
    s.label = name
    s.color = b.Color(NAVY if name in NAVY_PARTS else PALE)
    expected_solids = 1 if name in changed else len(before[name].solids())
    assert s.is_valid and len(s.solids()) == expected_solids, (name, s.is_valid, len(s.solids()))
    report['parts'][name] = {'valid': True, 'solids': len(s.solids()), 'bounds_mm': bounds(s)}
    if name in changed:
        b.export_stl(s, OUT / (name + '_assembly.stl'), tolerance=.03)
        mesh = trimesh.load_mesh(OUT / (name + '_assembly.stl'))
        assert mesh.is_watertight, name
        report['parts'][name]['watertight'] = True
    else:
        # Exact unchanged parts are copied, not regenerated from old parameters.
        assert abs(s.volume - before[name].volume) < .001, name

assert abs(parts['top_plate_left'].bounding_box().max.Z - target_h) < .001
assert abs(parts['foot_left'].bounding_box().min.Z -
           parts['foot_right_bonded'].bounding_box().min.Z) < .001

for (an, a), (bn, c) in itertools.combinations(parts.items(), 2):
    ba, bc = a.bounding_box(), c.bounding_box()
    if any(min(getattr(ba.max, k), getattr(bc.max, k)) -
           max(getattr(ba.min, k), getattr(bc.min, k)) < .001
           for k in ('X', 'Y', 'Z')):
        continue
    overlap = volume(a.intersect(c))
    if overlap > .1:
        report['interferences'].append([an, bn, overlap])

report['vent_obstructions_mm3'] = []
for i in range(5):
    probe = m.box_at(30.01, 148, 120 + rise + i * 4 + .01,
                     m.p.x_split - 60 - .02, 14, 1.98)
    overlap = sum(volume(s.intersect(probe)) for s in parts.values())
    report['vent_obstructions_mm3'].append(overlap)
    assert overlap < .01, (i, overlap)
report['vent_to_hatch_gap_mm'] = 120 + rise - parts['rear_panel_left'].bounding_box().max.Z

report['seam_bore_obstructions_mm3'] = []
for y, z in m.SPINE_SCREWS:
    probe = m.cyl_x(m.p.x_split - m.p.wall - .1, y, z, 3.3, m.p.wall + .2)
    overlap = volume(parts['tub_left'].intersect(probe))
    report['seam_bore_obstructions_mm3'].append(overlap)
    assert overlap < .01, (y, z, overlap)
for y, z in m.SPINE_DOWELS:
    probe = m.cyl_x(m.p.x_split - m.p.wall - .1, y, z, 4.2, m.p.wall + .2)
    assert volume(parts['tub_left'].intersect(probe)) < .01

# Check all cover screw passages and report hardware-envelope intersections.
for x, y in m.LID_SCREWS_L:
    probe = m.cyl_z(x, y, target_h - m.p.lid_t, 3.3, m.p.lid_t + .1)
    assert volume(parts['top_plate_left'].intersect(probe)) < .01
report['display_envelope_clashes_mm3'] = {
    name: volume(display.intersect(s)) for name, s in parts.items()
}
(OUT / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
assert not report['interferences'], report['interferences']
assert max(report['display_envelope_clashes_mm3'].values()) < .1, report['display_envelope_clashes_mm3']

b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()],
                        label='LUMON_V32_EQUAL_HEIGHT_REVIEW'), OUT / 'whole_enclosure_review.step')
display.label = 'REFERENCE_ONLY_unverified_display'
b.export_step(display, OUT / 'display_reference.step')

# Actual CAD views, with only an unverified dark display envelope added to
# make the window readable. No generated product illustration or styling cap.
for name, collection, screen, eye, target in [
    ('before_front', before, old_display, (555, -745, 365), (197, 67, 109)),
    ('equal_height_front', parts, display, (555, -745, 365), (197, 67, 109)),
    ('equal_height_rear', parts, None, (540, 780, 390), (195, 85, 108)),
]:
    sc = Scene(1400, 900, ss=1)
    for part_name, s in collection.items():
        sc.add(s, NAVY if part_name in NAVY_PARTS else PALE)
    if screen is not None:
        sc.add(screen, '#142B35')
    sc.look_at(eye, target, fov=32)
    sc.save(str(OUT / (name + '.png')))
print(json.dumps({k: report[k] for k in ('new_height_mm', 'screen_centre_rise_mm',
    'screen_rearward_movement_mm', 'front_cover_screw_y_mm', 'interferences',
    'vent_to_hatch_gap_mm')}, indent=2), flush=True)
