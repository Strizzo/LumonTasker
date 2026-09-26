"""Apply measured display lug depth and 4 mm screws; retain accepted XY fit.

The 8.4 mm dimension is from glass FRONT to the metal mounting face.
It replaces the inherited 5.96 mm assumption, not the glass thickness.
"""
from pathlib import Path
import copy, json, math, sys
import build123d as b
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'files'))
from render3d import Scene
OUT = ROOT / 'cad/output/v49_measured_display_depth'
OUT.mkdir(exist_ok=True)
PREV = ROOT / 'cad/output/v48_display_original_mounts'
BASE, CX = 33., 109.48
CZ = BASE + (201 - 16 - BASE) / math.cos(math.radians(25)) / 2
GX, GZ = CX - 193/2, CZ - 111/2
GLASS_FRONT_Y, SEAT_Y, BACK_Y = 1., 1.8, 15.9
FRONT_TO_LUG = 8.4
OLD_LUG_Y = 6.96
LUG_Y = GLASS_FRONT_Y + FRONT_TO_LUG
SCREW_LENGTH, GRIP = 4., 2.
HEAD_SEAT_Y = LUG_Y + GRIP

def box(x,y,z,w,d,h): return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
def cy(x,y,z,d,h): return b.Pos(x,y+h/2,z)*b.Rot(-90,0,0)*b.Cylinder(d/2,h)
def rounded(x,y,z,w,d,h,r):
    return b.Pos(x+w/2,y,z+h/2)*b.Rot(-90,0,0)*b.extrude(b.RectangleRounded(w,h,r),amount=d)
def rake(s): return b.Pos(0,0,BASE)*b.Rot(-25,0,0)*b.Pos(0,0,-BASE)*s
def unrake(s): return b.Pos(0,0,BASE)*b.Rot(25,0,0)*b.Pos(0,0,-BASE)*s
def vol(s): return sum(t.volume for t in s.solids()) if s else 0.
def mesh_export(s, name):
    assert s.is_valid and len(s.solids()) == 1, name
    s.label = name
    b.export_step(s, OUT/(name+'.step'))
    b.export_stl(s, OUT/(name+'.stl'), tolerance=.025)
    mesh = trimesh.load_mesh(OUT/(name+'.stl'))
    assert mesh.is_watertight and mesh.is_volume, name
    return mesh
def front_down(s):
    s = b.Rot(90,0,0)*s
    bb = s.bounding_box()
    return b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*s

parts = {s.label:s for s in b.import_step(PREV/'whole_enclosure_review.step').children}
old = unrake(parts['tub_left'])
body = copy.deepcopy(old)
centres = json.loads((PREV/'audit.json').read_text())['lug_centres_local_xz']

# Edit only the four cylindrical pads. Arm beams/roots, glass pocket/seat,
# and all XY screw axes remain exactly as in V48.
edit_masks = []
for x,z in centres:
    body -= box(x-5.01, OLD_LUG_Y-.01, z-5.01, 10.02, LUG_Y-OLD_LUG_Y+.01, 10.02)
    body += cy(x, LUG_Y, z, 10., HEAD_SEAT_Y-LUG_Y)
    body -= cy(x, LUG_Y-.01, z, 3.4, BACK_Y-LUG_Y+.03)
    body -= cy(x, HEAD_SEAT_Y, z, 6.5, BACK_Y-HEAD_SEAT_Y+.02)
    edit_masks.append(cy(x, OLD_LUG_Y-.02, z, 10.002, BACK_Y-OLD_LUG_Y+.04))
allowed = b.Compound(children=edit_masks)
removed_outside = vol((old-body)-allowed)
added_outside = vol((body-old)-allowed)
assert removed_outside<.01 and added_outside<.01
assert body.is_valid and len(body.solids())==1
print('Measured-depth pads built; original arms, roots and hole axes preserved', flush=True)

crop = rounded(CX-212.36/2,-.01,CZ-67,212.36,16.02,134,13.7)
fixture = body & crop
glass = rounded(GX,GLASS_FRONT_Y,GZ,193,.8,111,8)
seat = rounded(GX,SEAT_Y,GZ,193,2.3,111,8)-rounded(GX+3,1.79,GZ+3,187,2.32,105,5)
assert vol(seat-fixture)<.01
assert vol(fixture & glass)<.01
assert vol(fixture & (b.Pos(0,.05,0)*glass))>80
assert vol(fixture & (b.Pos(0,-.05,0)*glass))<.01

mount_checks = {}
for x,z in centres:
    land = cy(x,LUG_Y,z,9.9,.15)-cy(x,LUG_Y-.001,z,3.41,.152)
    grip = cy(x,LUG_Y,z,6.49,GRIP)-cy(x,LUG_Y-.001,z,3.41,GRIP+.002)
    relief = cy(x,OLD_LUG_Y,z,9.99,LUG_Y-OLD_LUG_Y-.001)
    bore = cy(x,LUG_Y-.001,z,3.39,BACK_Y-LUG_Y+.002)
    recess = cy(x,HEAD_SEAT_Y+.001,z,6.49,BACK_Y-HEAD_SEAT_Y)
    values = dict(bore_obstruction_mm3=vol(body&bore),
                  counterbore_obstruction_mm3=vol(body&recess),
                  relieved_material_remaining_mm3=vol(body&relief),
                  contact_land_fraction=vol(body&land)/vol(land),
                  screw_grip_fraction=vol(body&grip)/vol(grip))
    assert max(values[k] for k in values if k.endswith('_mm3')) < .01, values
    assert values['contact_land_fraction']>.999 and values['screw_grip_fraction']>.999
    mount_checks[f'{x:.2f},{z:.2f}'] = values
assert abs(centres[2][0]-centres[0][0]-126.2)<1e-6
assert abs(centres[1][1]-centres[0][1]-65.65)<1e-6

# Only the lug DEPTH is newly measured. Chassis XY and Pi location remain
# nominal. Enlarge the conservative metal envelope to the new contact plane.
sweeps = {
    'glass':rounded(GX,-100,GZ,193,101.8,111,8),
    'chassis_conservative_xy_nominal':box(GX+12,-100,GZ+3.35,166.2,100+LUG_Y,100.6),
    'Pi_nominal_not_remeasured':box(GX+51.12,-100,GZ+30.65,85,141,56),
    'band_conservative':rounded(GX+3,-100,GZ+3,187,102.6,105,5)}
parts['tub_left'] = rake(body)
sweep_hits = {n:{pn:v for pn,p in parts.items() if (v:=vol(rake(s)&p))>.1}
              for n,s in sweeps.items()}
assert not any(sweep_hits.values()), sweep_hits
clashes = {n:v for n,p in parts.items() if n!='tub_left' and (v:=vol(p&parts['tub_left']))>.1}
assert not clashes, clashes

mesh_export(parts['tub_left'],'tub_left')
full_mesh = mesh_export(fixture,'display_fit_local')
print_mesh = mesh_export(front_down(fixture),'display_fit_front_down_print')

# One real upper-right corner + complete integral mounting arm, cropped from
# the production interface. Two identical copies allow a support-gap A/B test
# and direct screw/seat trial with a fraction of a full frame's material.
x,z = centres[3]
coupon = fixture & box(x-7.2,-.02,z-5.2,60,16.04,CZ+67-(z-5.2)+.1)
assert coupon.is_valid and len(coupon.solids())==1
coupon_print = front_down(coupon)
coupon_mesh = mesh_export(coupon_print,'corner_depth_coupon_front_down')
assert all(v<220 for v in print_mesh.extents[:2])
assert coupon_mesh.bounds[0].min()>-.001

for n,s in parts.items():
    s.label=n
    s.color=b.Color('#173B53' if n in ('foot_left','foot_right_bonded','logo') else '#F0F1EB')
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()]),OUT/'whole_enclosure_review.step')
refs = {'REFERENCE_glass':glass,
        'REFERENCE_chassis_conservative_xy_nominal':box(GX+12,1.8,GZ+3.35,166.2,LUG_Y-1.8,100.6),
        'REFERENCE_Pi_nominal_not_remeasured':box(GX+51.12,6.96,GZ+30.65,85,34.04,56)}
ref_parts=[]
for n,s in refs.items():
    s=rake(s);s.label=n;s.color=b.Color('#17262F' if n=='REFERENCE_glass' else '#969EA4')
    ref_parts.append(s)
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in [*parts.values(),*ref_parts]]),OUT/'whole_enclosure_with_hardware.step')

sc=Scene(1000,720,ss=1)
sc.add(fixture,'#ECEBE1')
sc.look_at((280,440,330),(CX,8,CZ),fov=31)
sc.save(str(OUT/'measured_mounts_rear.png'))
sc=Scene(1000,720,ss=1)
sc.add(coupon_print,'#ECEBE1')
sc.look_at((90,-95,95),(24,19,8),fov=32)
sc.save(str(OUT/'corner_depth_coupon.png'))

report={
    'status':'Measured-depth CAD verified; compact coupons need slice review and clear bed before dispatch',
    'measurements':{'glass_front_to_metal_lug_mm':FRONT_TO_LUG,'screw_under_head_mm':SCREW_LENGTH,
                    'head_fits_existing_counterbore':True,'source':'User measurement 24 September 2026'},
    'old_front_to_lug_mm':OLD_LUG_Y-GLASS_FRONT_Y,
    'pad_relief_mm':round(LUG_Y-OLD_LUG_Y,3),
    'old_plastic_grip_mm':3.9,'plastic_grip_mm':GRIP,
    'nominal_thread_engagement_mm':SCREW_LENGTH-GRIP,
    'screw_depth_limit_note':'2 mm protrusion is a design target. The earlier 2.5 mm maximum-thread-depth claim is not explicitly specified as such in the drawing; actual blind-hole clearance still needs a gentle physical trial.',
    'glass_front_local_y_mm':GLASS_FRONT_Y,'metal_contact_local_y_mm':LUG_Y,
    'screw_head_seat_local_y_mm':HEAD_SEAT_Y,'rear_arm_extent_y_mm':BACK_Y,
    'opening_mm':[193.6,111.4],'opening_radius_mm':8.2,
    'glass_recess_mm':1.,'glass_thickness_mm':.8,'ledge_width_mm':3.,'ledge_thickness_mm':2.3,
    'full_depth_bearing_fraction':vol(seat & fixture)/vol(seat),
    'lug_centres_local_xz':centres,'lug_pitch_mm':[126.2,65.65],
    'hole_xy_shift_mm':[0.,0.],'original_hole_alignment_physically_confirmed':True,
    'mount_checks':mount_checks,'removed_outside_pad_masks_mm3':removed_outside,
    'added_outside_pad_masks_mm3':added_outside,'nominal_front_sweep_clashes_mm3':sweep_hits,
    'case_part_clashes_mm3':clashes,'production_body_valid':True,'fixture_valid':True,
    'watertight':True,'single_solids':True,'simultaneous_glass_lug_bearing_physically_verified':False,
    'print_orientation':'Front panel face on bed, as V46; rear arms upward',
    'full_fixture_volume_mm3':vol(fixture),'coupon_volume_mm3':vol(coupon),
    'two_coupon_vs_full_fixture_volume_ratio':2*vol(coupon)/vol(fixture),
    'coupon_extents_mm':coupon_mesh.extents.tolist(),
    'coupon_location':'Upper-right glass corner as viewed from front, original upper-right mount',
    'mounts_integral':True,'separate_bezel':False,'front_overlap_mm':0,
    'physical_test':['Remove support without leaving high spots on glass or metal bearing faces',
                     'Seat corner on matching upper-right glass corner with screw absent; arm must not bow',
                     'Check pad meets metal at same time as glass meets 3 mm seat, without forcing',
                     'Use measured 4 mm under-head screw; stop if it resists before its head seats',
                     'Compare 0.20 and 0.12 support-gap copies for bearing finish and clean release'],
    'limits':['Only lug depth is measured; full chassis/Pi geometry remains provisional',
              'Printed tolerances and actual screw blind-hole clearance require physical trial',
              'Full-body print orientation/screw access/power routing remain unresolved',
              'Inherited provisional cable/divider clash remains; not a full-case print release'],
    'provisional_cable_divider_clash_mm3':vol(body&box(GX+41.12,42,GZ+20.65,105,20,76)),
    'fusion_synced':False,'print_dispatched':False}
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
