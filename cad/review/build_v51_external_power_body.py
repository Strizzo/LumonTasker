"""Prepare the measured display shell for one external 24 V power adapter.

V49 supplied the physically accepted glass seat and metal-lug contacts. V39
supplied the already printed roof and rear hatch. This edit removes only the
obsolete internal AC supply supports, their floor slots, and duplicate Pi
standoffs; the rear IEC-sized opening becomes a modular low-voltage inlet bay.
No inlet bore is fixed until its actual connector is selected/measured.
"""
from pathlib import Path
import copy
import json
import math
import sys

import build123d as b
import trimesh

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'cad/output/v51_external_power_body'
OUT.mkdir(parents=True, exist_ok=True)
PREV = ROOT / 'cad/output/v49_measured_display_depth'
V39 = ROOT / 'cad/output/v39_aligned_rear'
parts = {s.label: copy.deepcopy(s) for s in b.import_step(PREV / 'whole_enclosure_review.step').children}
old_body, old_base = parts['tub_left'], parts['foot_left']
# V40 hollowed this base from below with six exposed pockets. Use the last
# closed-surface V39 base instead; Bambu's sparse infill keeps the interior
# light while both visible surfaces remain continuous.
closed_base = {s.label:s for s in b.import_step(V39/'whole_enclosure_review.step').children}['foot_left']


def box(x, y, z, w, d, h):
    return b.Pos(x+w/2, y+d/2, z+h/2) * b.Box(w, d, h)


def cyl_x(x, y, z, diameter, length):
    return b.Pos(x+length/2, y, z) * b.Rot(0, 90, 0) * b.Cylinder(diameter/2, length)


def vol(s):
    return sum(q.volume for q in s.solids()) if s else 0.


def mesh(path, shape):
    b.export_stl(shape, path, tolerance=.035)
    m = trimesh.load_mesh(path)
    assert m.is_watertight and m.is_volume, path
    return m


# Original V29 PSU envelope was 129 x 97 x 30 at x83.96,y57.75. These
# dimensions are exact inherited CAD coordinates, not newly measured hardware.
psu_x, psu_y, floor_z = 83.96, 57.75, 13.
body = old_body
base = closed_base
# Rebuild only the outer plinth envelope to clip slot plugs flush with the
# 5 mm bottom chamfer. Rectangular plugs by themselves leave six small tabs
# beyond the sloping rear perimeter when the part is turned over for printing.
base_envelope = box(2.5, 2.5, 0., 218.96-2.5, 170.75-5., 9.)
base_envelope = b.fillet(base_envelope.edges().filter_by(b.Axis.Z).group_by(b.Axis.X)[0], 7.)
base_envelope = b.chamfer(
    [e for e in base_envelope.edges().group_by(b.Axis.Z)[0]
     if abs(e.center().X-218.96)>.01], 5.)
assert vol(closed_base-base_envelope)<.01

# Mains/low-voltage divider: save the lower floor and rear outside skin.
body -= box(76.959, 40., floor_z+.001, 3.002, 127.75, 46.001)

# The PSU retaining blocks are isolated above the floor. Their right rear
# members end at the inside of the existing wall, so the wall remains intact.
psu_blocks = []
for bx, bw in ((psu_x-12, 12.), (psu_x+129, 3.)):
    psu_blocks.append(box(bx-.001, psu_y+2-.001, floor_z+.001,
                          bw+.002, 14.002, 24.001))
for by, bd in ((psu_y-6, 6.), (psu_y+97, 13.)):
    psu_blocks.append(box(psu_x-.001, by-.001, floor_z+.001,
                          14.002, bd+.002, 24.001))
for block in psu_blocks:
    body -= block

# The Pi is physically attached to the back of the display. Four old x-wall
# standoffs duplicate it and steal service/wiring room. Subtract only their
# protruding cylindrical volume, retaining the 3 mm outside skin.
old_pi_y = 94.
for y in (old_pi_y+3.5, old_pi_y+3.5+49):
    for z in (43.+3.5, 43.+3.5+58):
        body -= cyl_x(3.001, y, z, 8.002, 15.001)

# Restore six old floor slots and matching underside base channels. No internal
# AC supply remains to need floor intake. The high rear vents stay open.
floor_slot_x = []
for i in range(6):
    x = psu_x+12+i*18
    floor_slot_x.append(x)
    body += box(x, psu_y+12, 9., 4., 73., 4.)
    plug = box(x-.15, psu_y+11.8, -.1, 4.3, 170.75-(psu_y+11.8), 9.2)
    base += plug & base_envelope

# No changes to measured display contacts or to the already printed cover
# interfaces. Rear connector opening is left open for a replaceable carrier.
assert body.is_valid and len(body.solids()) == 1
assert base.is_valid and len(base.solids()) == 1
assert vol(base-base_envelope)<.01
assert vol(old_base-base) < .1
assert abs(base.bounding_box().min.Z-old_base.bounding_box().min.Z)<.01
assert abs(base.bounding_box().max.Z-old_base.bounding_box().max.Z)<.01
parts['tub_left'] = body
parts['foot_left'] = base
roof = parts['top_plate_left']
hatch = parts['rear_panel_left']
assert vol(old_body & roof) < .01
assert vol(body & roof) < .01
assert vol(old_body & hatch) < .01
assert vol(body & hatch) < .01
assert vol((body-old_body) & roof) < .01
assert vol((body-old_body) & hatch) < .01

# Verify the measured display pocket/arms were untouched in local raked space.
BASE = 33.
def unrake(s):
    return b.Pos(0, 0, BASE)*b.Rot(25, 0, 0)*b.Pos(0, 0, -BASE)*s

def rake(s):
    return b.Pos(0, 0, BASE)*b.Rot(-25, 0, 0)*b.Pos(0, 0, -BASE)*s

cx = 109.48
cz = BASE+(201-16-BASE)/math.cos(math.radians(25))/2
glass_zone = rake(box(cx-106.2, -.01, cz-67, 212.4, 16.02, 134))
glass_change = vol(((body-old_body)+(old_body-body)) & glass_zone)
assert glass_change < .05, glass_change

# A 2.5 mm pilot in an independent plate marks the inlet without assuming a
# particular connector's panel diameter, thread, or cable clearance.
inlet_blank = box(148.98, 169.25, 43.45, 56., 1.5, 37.1)
inlet_blank += box(153.53, 167.76, 48.0, 46.9, 1.49, 28.0)
inlet_blank -= b.Pos(176.98, 168.5, 62.)*b.Rot(-90, 0, 0)*b.Cylinder(1.25, 5.)
assert inlet_blank.is_valid and len(inlet_blank.solids()) == 1
assert vol(inlet_blank & body) < .1

for n, s in parts.items():
    s.label = n
    s.color = b.Color('#173B53' if n in ('foot_left','foot_right_bonded','logo') else '#F0F1EB')
b.export_step(b.Compound(children=list(parts.values())), OUT/'whole_enclosure_review.step')
for name, shape in [('display_body',body),('display_base',base),('dc_inlet_blank',inlet_blank)]:
    standalone=copy.deepcopy(shape)
    standalone.parent=None
    b.export_step(standalone, OUT/(name+'.step'))

front = b.Rot(90, 0, 0)*unrake(body)
bb = front.bounding_box()
front = b.Pos(-bb.min.X, -bb.min.Y, -bb.min.Z)*front
body_mesh = mesh(OUT/'display_body_front_down_print.stl', front)
upright = b.Pos(0, 0, -9)*body
upright_mesh = mesh(OUT/'display_body_upright_print.stl', upright)
base_mesh = mesh(OUT/'display_base_print.stl', base)
blank_mesh = mesh(OUT/'dc_inlet_blank_print.stl', inlet_blank)
assert body_mesh.extents[0] < 256 and body_mesh.extents[1] < 256

report = {
    'status':'V51 geometry prepared; see BUILD_STATUS.md for print and Fusion status',
    'source':'V49 accepted display geometry and V39 already printed roof/hatch',
    'changes':['removed internal AC PSU divider and corner blocks',
               'removed unused left-wall Pi standoffs',
               'restored a closed base underside in place of exposed pockets',
               'closed obsolete PSU floor and base intake slots',
               'kept IEC-sized rear aperture as replaceable low-voltage inlet carrier'],
    'body_volume_mm3_before':vol(old_body),
    'body_volume_mm3_after':vol(body),
    'base_volume_mm3_before':vol(old_base),
    'base_volume_mm3_after':vol(base),
    'measured_display_zone_difference_mm3':glass_change,
    'printed_roof_rear_hatch_interfaces_unchanged':True,
    'body_print_bounds_mm':body_mesh.extents.tolist(),
    'body_upright_print_bounds_mm':upright_mesh.extents.tolist(),
    'base_print_bounds_mm':base_mesh.extents.tolist(),
    'inlet_blank_bounds_mm':blank_mesh.extents.tolist(),
    'inlet_plate':'Pilot only. Bore for actual selected bulkhead connector later.',
}
(OUT/'audit.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2), flush=True)
