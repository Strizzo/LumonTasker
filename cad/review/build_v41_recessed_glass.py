"""White integral display seat, no separate bezel or lip over the glass.

Incremental review from V40; no Fusion launch or print dispatch. Keep the
physically accepted glass outline and the existing printed bracket shapes.
The glass, metal bearing planes and case anchor planes move rearwards together.
"""
from pathlib import Path
import copy
import json
import sys
import math
import build123d as b
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'files'))
from render3d import Scene

OUT = ROOT / 'cad/output/v41_recessed_glass'
OUT.mkdir(exist_ok=True)
PREV = ROOT / 'cad/output/v40_display_mount'
CX = 109.48
BASE = 33.
ANGLE = 25.
CZ = BASE + (201 - 16 - BASE) / math.cos(math.radians(ANGLE)) / 2
GX, GZ = CX - 193 / 2, CZ - 111 / 2
SHIFT = 2.
GLASS_FRONT = 1.
LUG_PLANE = 6.96
ANCHOR_PLANE = 12.
PALE, NAVY = '#F0F1EB', '#173B53'


def box(x, y, z, w, d, h):
    return b.Pos(x+w/2, y+d/2, z+h/2) * b.Box(w, d, h)


def cy(x, y, z, diameter, length):
    return b.Pos(x, y+length/2, z) * b.Rot(-90, 0, 0) * b.Cylinder(diameter/2, length)


def rounded(x, y, z, w, d, h, radius):
    return b.Pos(x+w/2, y, z+h/2) * b.Rot(-90, 0, 0) * b.extrude(b.RectangleRounded(w, h, radius), amount=d)


def rake(s):
    return b.Pos(0, 0, BASE) * b.Rot(-ANGLE, 0, 0) * b.Pos(0, 0, -BASE) * s


def volume(s):
    return sum(q.volume for q in s.solids()) if s else 0.


def export(s, name):
    assert s.is_valid and len(s.solids()) == 1, name
    s.label = name
    b.export_step(s, OUT / (name + '.step'))
    b.export_stl(s, OUT / (name + '_assembly.stl'), tolerance=.035)
    assert trimesh.load_mesh(OUT / (name + '_assembly.stl')).is_watertight, name


v39 = {s.label: s for s in b.import_step(ROOT / 'cad/output/v39_aligned_rear/whole_enclosure_review.step').children}
parts = {n: copy.deepcopy(s) for n, s in v39.items() if n not in ('display_bezel', 'display_retainer')}
tub = b.import_step(PREV / 'tub_left.step')
parts['foot_left'] = b.import_step(PREV / 'foot_left.step')

# Fill the original separate bezel rebate back to the white front plane y=0.
# Slight outward overlap joins the inherited pocket wall robustly.
fill = rounded(CX-213.16/2, 0, CZ-128.96/2, 213.16, 2.4, 128.96, 14.1)
glass_opening = rounded(GX-.2, -5, GZ-.2, 193.4, 12, 111.4, 8.2)
tub += rake(fill - glass_opening)

# A shallow rear shoulder makes a true pocket. It is entirely BEHIND the
# glass, with 0.4 mm clearance even for the thicker 1.1 mm glass variant.
# Brackets take load; the shoulder is not a rigid clamping surface.
shoulder = rounded(GX-2.2, 2.3, GZ-2.2, 197.4, 1.8, 115.4, 10.2)
inner = rounded(GX+2, 2.2, GZ+2, 189, 2.1, 107, 6)
shoulder -= inner
shoulder -= rounded(GX-.2, -5, GZ-.2, 193.4, 7.5, 111.4, 8.2)
tub += rake(shoulder)

# Preserve the entire tested relative bracket stack by translating it 2 mm.
# Fill the old insert depth before recutting the same 6 mm engagement depth.
audit40 = json.loads((PREV / 'audit.json').read_text())
lug_centres = audit40['lug_centres_local_xz']
for x in sorted({p[0] for p in lug_centres}):
    for z in (GZ-5.5, GZ+111+5.5):
        tub += rake(cy(x, 3.99, z, 4.22, 6.03))
        tub += rake(cy(x, 9.99, z, 9, 2.01))
        tub -= rake(cy(x, ANCHOR_PLANE-6, z, 4.2, 6.1))
parts['tub_left'] = tub
local_brackets = {}
for side in ('left', 'right'):
    for level in ('lower', 'upper'):
        name = f'display_mount_{side}_{level}'
        old = b.import_step(PREV / (name + '_local.step'))
        local = b.Pos(0, SHIFT, 0) * old
        # No revised bracket print required: geometry identical, position only.
        assert abs(volume(local)-volume(old)) < 1e-5
        local_brackets[name] = local
        parts[name] = rake(local)

glass = rounded(GX, GLASS_FRONT, GZ, 193, 1.1, 111, 8)
chassis = box(GX+12, GLASS_FRONT+.7, GZ+3.35, 166.2, 5.26, 100.6)
pi = box(GX+51.12, LUG_PLANE, GZ+30.65, 85, 40-5.96, 56)
refs = {'REFERENCE_glass_max_thickness': rake(glass),
        'REFERENCE_chassis_nominal': rake(chassis),
        'REFERENCE_attached_Pi_nominal': rake(pi)}
keepouts = {
 'Pi_5mm_lateral_1mm_rear_allowance': rake(box(GX+46.12, LUG_PLANE, GZ+25.65, 95, 41-5.96, 66)),
 'provisional_20mm_rear_cable_space': rake(box(GX+41.12, GLASS_FRONT+41, GZ+20.65, 105, 20, 76))}
power = {'PSU_placeholder': box(83.96, 48, 13, 129, 97, 30),
         'buck_placeholder': box(10, 30, 13, 35, 65, 20),
         'IEC_placeholder': box(151.98, 138.25, 47.85, 50, 32.5, 28.3)}
report = {
 'status': 'Review candidate only; not sliced, printed or synchronized to Fusion',
 'appearance': 'Integral cotton-white sloped front with recessed glass; original black glass border remains visible. No separate bezel and no front overlap.',
 'opening_mm': [193.4, 111.4], 'opening_corner_radius_mm': 8.2,
 'opening_physical_fit': 'V40 contour accepted by user on 24 September',
 'glass_recess_mm': 1., 'glass_overlap_on_front_mm': 0.,
 'shoulder_behind_glass_y_mm': 2.5, 'shoulder_thickness_mm': 1.6,
 'clearance_for_1p1mm_glass_mm': .4,
 'bracket_geometry': 'Unchanged V40 printed parts; translated 2 mm with glass and anchor planes',
 'rear_lug_y_mm': LUG_PLANE, 'anchor_y_mm': ANCHOR_PLANE,
 'rear_bracket_physical_fit_verified': False,
 'part_intersections_mm3': {}, 'hardware_clashes_mm3': {}, 'keepout_clashes_mm3': {},
 'release_hold': ['Rear bracket and screw stack physically unconfirmed',
                  'Power hardware and cable routing are placeholders; keepout review required',
                  'Recess depth/shoulder and print orientation not physically tested']}

print('Checking revised body and retained bracket geometry', flush=True)
export(tub, 'tub_left')
for n in local_brackets:
    export(parts[n], n)
changed = {'tub_left', *local_brackets}
for an, a in parts.items():
    for bn, c in parts.items():
        if an >= bn or not ({an, bn} & changed):
            continue
        ba, bc = a.bounding_box(), c.bounding_box()
        if any(min(getattr(ba.max,k),getattr(bc.max,k))-max(getattr(ba.min,k),getattr(bc.min,k)) < .001 for k in 'XYZ'):
            continue
        v = volume(a & c)
        if v > .1: report['part_intersections_mm3'][an+' / '+bn] = v
for rn, r in refs.items():
    report['hardware_clashes_mm3'][rn] = {n: v for n, s in parts.items() if (v := volume(r & s)) > .1}
for rn, r in keepouts.items():
    report['keepout_clashes_mm3'][rn] = {n: v for n, s in {**parts, **power}.items() if (v := volume(r & s)) > .1}
report['body_volume_mm3'] = volume(tub)
(OUT / 'audit.json').write_text(json.dumps(report, indent=2)+'\n')
assert not report['part_intersections_mm3'], report['part_intersections_mm3']
assert not any(report['hardware_clashes_mm3'].values()), report['hardware_clashes_mm3']
# Record unresolved cable keepouts explicitly; exporting a review is not release.
for n, s in parts.items():
    s.label = n
    s.color = b.Color(NAVY if n in ('foot_left', 'foot_right_bonded', 'logo') else PALE)
for n, s in refs.items():
    s.label = n
    s.color = b.Color('#253B47')
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()]), OUT / 'whole_enclosure_review.step')
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in [*parts.values(), *refs.values()]]), OUT / 'whole_enclosure_with_hardware.step')

# Lightweight actual-CAD view. The black inactive border belongs to the glass.
sc = Scene(1000, 720, ss=1)
for n, s in parts.items():
    sc.add(s, NAVY if n in ('foot_left', 'foot_right_bonded', 'logo') else PALE)
sc.add(rake(glass), '#131C23')
active = box(CX-154.08/2, GLASS_FRONT-.02, CZ-85.92/2, 154.08, .01, 85.92)
sc.add(rake(active), '#30434E')
sc.look_at((460, -720, 425), (197, 65, 100), fov=31)
sc.save(str(OUT / 'recessed_glass_front.png'))
print(json.dumps(report, indent=2), flush=True)
