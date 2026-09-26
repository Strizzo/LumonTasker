"""Apply measured V46 corrections to the production body and its fit fixture.

Local X is right viewed from the FRONT, Z is up along the display plane.
User's rear-view right/down correction is therefore X=-3.6, Z=-2.0.
Only lug positions are measured; do not translate the nominal metal chassis
or Pi by this offset and pretend their position was also measured.
"""
raise SystemExit('V47 mount shift withdrawn by user; run build_v48_display_original_mounts.py and prepare_v48_fit.py instead.')

from pathlib import Path
import copy, json, math, sys
import build123d as b
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'files'))
from render3d import Scene
OUT = ROOT / 'cad/output/v47_display_fit_correction'
OUT.mkdir(exist_ok=True)
PREV = ROOT / 'cad/output/v45_display_seat_3mm/glass_0p8'
BASE, CX = 33., 109.48
CZ = BASE + (201 - 16 - BASE) / math.cos(math.radians(25)) / 2
GX, GZ = CX - 193/2, CZ - 111/2
DX, DZ = -3.6, -2.
LUG_Y, SEAT_Y, BACK_Y = 6.96, 1.8, 15.9

def box(x,y,z,w,d,h): return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
def cy(x,y,z,d,h): return b.Pos(x,y+h/2,z)*b.Rot(-90,0,0)*b.Cylinder(d/2,h)
def rounded(x,y,z,w,d,h,r):
    return b.Pos(x+w/2,y,z+h/2)*b.Rot(-90,0,0)*b.extrude(b.RectangleRounded(w,h,r),amount=d)
def rake(s): return b.Pos(0,0,BASE)*b.Rot(-25,0,0)*b.Pos(0,0,-BASE)*s
def unrake(s): return b.Pos(0,0,BASE)*b.Rot(25,0,0)*b.Pos(0,0,-BASE)*s
def vol(s): return sum(t.volume for t in s.solids()) if s else 0.

parts = {s.label:s for s in b.import_step(PREV/'whole_enclosure_review.step').children}
old = unrake(parts['tub_left'])
body = copy.deepcopy(old)
old_centres = json.loads((PREV/'audit.json').read_text())['lug_centres_local_xz']
centres = [[x+DX,z+DZ] for x,z in old_centres]

# Remove all old arms/raised roots above the broad front skin. The affected
# portions of the 3 mm ledge are restored below. The front skin stays intact.
edit_masks = []
for x,z in old_centres:
    az = GZ-5.5 if z<CZ else GZ+111+5.5
    lo,hi = sorted((az,z))
    mask = box(x-7.1,2.4,lo-5.1,14.2,13.6,hi-lo+10.2)
    body -= mask
    edit_masks.append(mask)

# Rebuild the exact glass-bearing ring: support width 3 mm, thickness 2.3 mm.
seat_extension = rounded(GX-2.2,SEAT_Y,GZ-2.2,197.4,2.3,115.4,10.2)
seat_extension -= rounded(GX+3,SEAT_Y-.01,GZ+3,187,2.32,105,5)
body += seat_extension
edit_masks.append(seat_extension)

# Wider pocket only above the ledge. Total +0.2 mm width, centred: +0.1/side.
# Height, corner radius, nominal glass position and inner bearing edge stay put.
opening = rounded(GX-.3,-.1,GZ-.2,193.6,1.9,111.4,8.2)
body -= opening
edit_masks.append(opening)

arms = []
for x,z in centres:
    az = GZ-5.5 if z<CZ else GZ+111+5.5
    lo,hi = sorted((az,z))
    arm = box(x-7,2.4,az-4,14,13.5,8)
    arm += box(x-5,12,lo-5,10,3.9,hi-lo+10)
    arm += cy(x,LUG_Y,z,10,12.1-LUG_Y)
    arm -= cy(x,LUG_Y-.01,z,3.4,9.1)
    arm -= cy(x,LUG_Y+3.9,z,6.5,5.1)
    assert arm.is_valid and len(arm.solids())==1
    body += arm
    arms.append(arm)
    edit_masks.append(arm)

assert body.is_valid and len(body.solids())==1
allowed = b.Compound(children=edit_masks)
assert vol((old-body)-allowed)<.01
assert vol((body-old)-allowed)<.01
print('Corrected production interface built', flush=True)

crop = rounded(CX-212.36/2,-.01,CZ-67,212.36,16.02,134,13.7)
fixture = body & crop
assert fixture.is_valid and len(fixture.solids())==1
assert all(vol(a-fixture)<.01 for a in arms)
glass = rounded(GX,1,GZ,193,.8,111,8)
seat = rounded(GX,SEAT_Y,GZ,193,2.3,111,8)-rounded(GX+3,1.79,GZ+3,187,2.32,105,5)
assert vol(seat-fixture)<.01
assert vol(fixture & glass)<.01
assert vol(fixture & (b.Pos(0,.05,0)*glass))>80
assert vol(fixture & (b.Pos(0,-.05,0)*glass))<.01

mount_checks = {}
for x,z in centres:
    bore = cy(x,LUG_Y-.001,z,3.39,9)
    recess = cy(x,10.861,z,6.49,5.05)
    land = cy(x,LUG_Y,z,9.9,.15)-cy(x,LUG_Y-.001,z,3.41,.152)
    mount_checks[f'{x:.2f},{z:.2f}'] = {
        'bore_obstruction_mm3':vol(body & bore),
        'counterbore_obstruction_mm3':vol(body & recess),
        'bearing_land_fraction':vol(body & land)/vol(land)}
assert all(v['bore_obstruction_mm3']<.01 and v['counterbore_obstruction_mm3']<.01
           and v['bearing_land_fraction']>.999 for v in mount_checks.values()), mount_checks
assert abs(centres[2][0]-centres[0][0]-126.2)<1e-6
assert abs(centres[1][1]-centres[0][1]-65.65)<1e-6

sweeps = {
    'glass':rounded(GX,-100,GZ,193,101.8,111,8),
    'chassis_nominal_not_remeasured':box(GX+12,-100,GZ+3.35,166.2,106.96,100.6),
    'Pi_nominal_not_remeasured':box(GX+51.12,-100,GZ+30.65,85,141,56),
    'band_conservative':rounded(GX+3,-100,GZ+3,187,102.6,105,5)}
parts['tub_left'] = rake(body)
sweep_hits = {n:{pn:v for pn,p in parts.items() if (v:=vol(rake(s)&p))>.1}
              for n,s in sweeps.items()}
assert not any(sweep_hits.values()), sweep_hits
clashes = {n:v for n,p in parts.items() if n!='tub_left' and (v:=vol(p&parts['tub_left']))>.1}
assert not clashes, clashes

for name,s in [('tub_left',parts['tub_left']),('display_fit_local',fixture)]:
    s.label = name
    b.export_step(s,OUT/(name+'.step'))
    b.export_stl(s,OUT/(name+'.stl'),tolerance=.025)
    assert trimesh.load_mesh(OUT/(name+'.stl')).is_watertight

# Print rear face down: bearing ledge and lug lands face UP. Supports remain
# under the reverse sides of the frame, away from these contact surfaces.
printed = b.Rot(-90,0,0)*fixture
bb = printed.bounding_box()
printed = b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*printed
b.export_stl(printed,OUT/'display_fit_seat_up_print.stl',tolerance=.025)
mesh = trimesh.load_mesh(OUT/'display_fit_seat_up_print.stl')
assert mesh.is_watertight and max(mesh.extents[:2])<220
assert mesh.bounds[0].min()>-.001

for n,s in parts.items():
    s.label=n
    s.color=b.Color('#173B53' if n in ('foot_left','foot_right_bonded','logo') else '#F0F1EB')
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()]),OUT/'whole_enclosure_review.step')
refs = {'REFERENCE_glass':glass,
        'REFERENCE_chassis_nominal_not_remeasured':box(GX+12,1.8,GZ+3.35,166.2,5.16,100.6),
        'REFERENCE_Pi_nominal_not_remeasured':box(GX+51.12,6.96,GZ+30.65,85,34.04,56)}
ref_parts=[]
for n,s in refs.items():
    s=rake(s);s.label=n;s.color=b.Color('#17262F' if n=='REFERENCE_glass' else '#969EA4')
    ref_parts.append(s)
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in [*parts.values(),*ref_parts]]),OUT/'whole_enclosure_with_hardware.step')

sc=Scene(1000,720,ss=1)
sc.add(fixture,'#ECEBE1')
sc.look_at((280,440,330),(CX,8,CZ),fov=31)
sc.save(str(OUT/'corrected_mounts_rear.png'))
sc=Scene(1000,720,ss=1)
sc.add(printed,'#ECEBE1')
sc.look_at((285,-255,340),(106,67,8),fov=34)
sc.save(str(OUT/'seat_up_print_orientation.png'))

report={
    'status':'Corrected CAD checked; fit fixture requires GUI slice/support review and clear bed before dispatch',
    'source':'V45 body corrected using physical V46 test feedback',
    'opening_mm':[193.6,111.4], 'opening_radius_mm':8.2,
    'width_change_mm':.2, 'width_change_interpretation':'Overall width increase, centred; +0.1 mm each side',
    'glass_recess_mm':1., 'glass_thickness_mm':.8,
    'ledge_width_mm':3., 'ledge_thickness_mm':2.3,
    'full_depth_bearing_fraction':vol(seat & fixture)/vol(seat),
    'mount_correction_user_rear_view_mm':{'right':3.6,'down':2.},
    'mount_correction_local_xz_mm':[DX,DZ],
    'rear_view_mapping':'Rear is camera at +Y looking toward -Y, up +Z: image-right=-X',
    'old_lug_centres_local_xz':old_centres,'lug_centres_local_xz':centres,
    'lug_pitch_mm':[126.2,65.65], 'mount_checks':mount_checks,
    'mounts_integral':True,'separate_bezel':False,'front_overlap_mm':0,
    'nominal_front_sweep_clashes_mm3':sweep_hits,'case_part_clashes_mm3':clashes,
    'production_body_valid':True,'fixture_valid':True,'single_solids':True,'watertight':True,
    'unchanged_outside_interface_edit_masks':True,
    'fixture_volume_mm3':vol(fixture),'print_extents_mm':mesh.extents.tolist(),
    'print_orientation':'Rear faces of four arms on bed; glass-bearing seat and lug contact lands upward',
    'print_seat_top_z_mm':BACK_Y-SEAT_Y,'print_lug_land_z_mm':BACK_Y-LUG_Y,
    'fasteners':'4 M3x6, nominal 3.9 mm grip and 2.1 mm engagement; verify actual simultaneous seating',
    'physical_test':['Remove supports under frame without scraping glass seat',
                     'Glass enters freely without forcing the tight corner',
                     'Glass rests on full 3 mm ledge without rocking, screws absent',
                     'All four shifted bores align and lug pads meet metal without forcing',
                     'Only then install four M3x6 gently'],
    'limits':['User offset applies to lug pattern only; chassis and Pi references remain nominal',
              'Test needed for corrected lug positions and actual bearing stack',
              'Full-body print orientation/screw access/power routing remain unresolved',
              'Inherited provisional cable/divider clash remains; not a full-case print release'],
    'provisional_cable_divider_clash_mm3':vol(body&box(GX+41.12,42,GZ+20.65,105,20,76)),
    'fusion_synced':False,'print_dispatched':False}
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
