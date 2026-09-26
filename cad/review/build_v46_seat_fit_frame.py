"""Extract the actual V45 display interface for one integral-mount fit print.

This retains the final seat, glass pocket and all four integral arms. The outer
crop is a test boundary, not a new production face. No printer dispatch here.
"""
from pathlib import Path
import copy, json, math, sys
import build123d as b
import trimesh

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'files'))
from render3d import Scene
OUT=ROOT/'cad/output/v46_display_seat_fit'; OUT.mkdir(exist_ok=True)
PREV=ROOT/'cad/output/v45_display_seat_3mm/glass_0p8'
BASE=33.; CX=109.48
CZ=BASE+(201-16-BASE)/math.cos(math.radians(25))/2
GX,GZ=CX-193/2,CZ-111/2

def box(x,y,z,w,d,h): return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
def cy(x,y,z,d,h): return b.Pos(x,y+h/2,z)*b.Rot(-90,0,0)*b.Cylinder(d/2,h)
def rounded(x,y,z,w,d,h,r):
    return b.Pos(x+w/2,y,z+h/2)*b.Rot(-90,0,0)*b.extrude(b.RectangleRounded(w,h,r),amount=d)
def unrake(s): return b.Pos(0,0,BASE)*b.Rot(25,0,0)*b.Pos(0,0,-BASE)*s
def vol(s): return sum(t.volume for t in s.solids()) if s else 0.

body=unrake(b.import_step(PREV/'tub_left.step'))
crop=rounded(CX-212.36/2,-.01,CZ-67,212.36,16.02,134,13.7)
fixture=body & crop
assert fixture.is_valid and len(fixture.solids())==1
# All four mount arms and their roots must survive the crop unchanged.
lug_centres=json.loads((PREV/'audit.json').read_text())['lug_centres_local_xz']
mount_checks={}
for x,z in lug_centres:
    az=GZ-5.5 if z<CZ else GZ+111+5.5
    lo,hi=sorted((az,z))
    mask=box(x-7.1,2.4,lo-5.1,14.2,13.6,hi-lo+10.2)
    missing=vol((body & mask)-fixture)
    bore=cy(x,6.959,z,3.39,9)
    recess=cy(x,10.861,z,6.49,5.05)
    land=cy(x,6.96,z,9.9,.15)-cy(x,6.959,z,3.41,.152)
    mount_checks[f'{x:.2f},{z:.2f}']={
        'missing_mount_material_mm3':missing,
        'bore_obstruction_mm3':vol(fixture & bore),
        'counterbore_obstruction_mm3':vol(fixture & recess),
        'bearing_land_fraction':vol(fixture & land)/vol(land)}
assert all(v['missing_mount_material_mm3']<.01 and v['bore_obstruction_mm3']<.01 and
           v['counterbore_obstruction_mm3']<.01 and v['bearing_land_fraction']>.999
           for v in mount_checks.values()),mount_checks
glass=rounded(GX,1,GZ,193,.8,111,8)
seat=rounded(GX,1.8,GZ,193,2.3,111,8)-rounded(GX+3,1.79,GZ+3,187,2.32,105,5)
seat_fraction=vol(seat & fixture)/vol(seat)
assert seat_fraction>.999
assert vol(glass & fixture)<.01
assert vol((b.Pos(0,.05,0)*glass)&fixture)>80
assert vol((b.Pos(0,-.05,0)*glass)&fixture)<.01
sweeps={
    'glass':rounded(GX,-100,GZ,193,101.8,111,8),
    'chassis_nominal':box(GX+12,-100,GZ+3.35,166.2,106.96,100.6),
    'Pi_nominal':box(GX+51.12,-100,GZ+30.65,85,141,56),
    'band_conservative':rounded(GX+3,-100,GZ+3,187,102.6,105,5)}
hits={n:vol(s & fixture) for n,s in sweeps.items()}
assert all(v<.01 for v in hits.values()),hits
fixture.label='Display seat and four integral mounts'
b.export_step(fixture,OUT/'display_seat_fit_local.step')
b.export_stl(fixture,OUT/'display_seat_fit_local.stl',tolerance=.025)
# White front face lies on the bed. Local +y becomes print +z. Same-colour
# removable supports are needed beneath ledge/arms; inspect GUI slice.
printed=b.Rot(90,0,0)*fixture
bb=printed.bounding_box()
printed=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*printed
b.export_stl(printed,OUT/'display_seat_fit_print.stl',tolerance=.025)
mesh=trimesh.load_mesh(OUT/'display_seat_fit_print.stl')
assert mesh.is_watertight
assert (mesh.bounds[0]>=-.001).all()
assert max(mesh.extents[:2])<220 and mesh.extents[2]<17
sc=Scene(1000,720,ss=1)
sc.add(fixture,'#ECEBE1')
sc.look_at((280,440,330),(CX,8,CZ),fov=31)
sc.save(str(OUT/'integral_fit_frame.png'))
report={
    'status':'Fit-frame CAD checks passed; slice/support review and bed clearance required before dispatch',
    'source':'V45 0.8 mm glass / 3 mm seat, exact interface cropped from final body',
    'objects':1,'separate_brackets':0,'case_side_heat_set_inserts':0,
    'glass_opening_mm':[193.4,111.4],'opening_radius_mm':8.2,
    'ledge_width_mm':3.,'ledge_material_thickness_mm':2.3,'glass_recess_mm':1.,
    'full_depth_seat_material_fraction':seat_fraction,
    'lug_checks':mount_checks,'front_sweep_collisions_mm3':hits,
    'valid':True,'solid_count':1,'watertight':True,
    'print_extents_mm':mesh.extents.tolist(),'cad_volume_mm3':vol(fixture),
    'print_orientation':'Front face on bed; integral arms point up; supports required',
    'filament':'PolyTerra Cotton White PLA / AMS A2 only',
    'fasteners':'4 x M3x6 into existing outer metal lugs; nominal engagement2.1mm, verify before tightening',
    'physical_test':['Remove supports and inspect bearing/holes for residue',
                     'Insert display and attached Pi from front with screws absent; glass rests evenly on ledge',
                     'Check black band is clear and display is not rocking',
                     'Check four metal lugs meet pads without pulling display across a gap',
                     'Only then gently secure four M3x6 screws and check front withdrawal is prevented'],
    'limits':['Nominal chassis-to-ledge gap0.35mm needs real test',
              'This open frame does not verify final rear screwdriver or cable/power routing',
              'Full case remains unreleased; fixture does not resolve inherited cable/divider overlap'],
    'print_dispatched':False}
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
