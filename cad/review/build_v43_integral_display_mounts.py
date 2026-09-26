"""Four integral display mounts; front installation and four rear M3 screws.

Preserve V41 glass/pad datums. Eliminate four case-side screws, heat-set inserts,
and detachable brackets. Do not change the active printer-base print.
"""
from pathlib import Path
import copy, json, math, sys
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'files'))
from render3d import Scene
OUT=ROOT/'cad/output/v43_integral_display_mounts';OUT.mkdir(exist_ok=True)
BASE=33.;CX=109.48;CZ=BASE+(201-16-BASE)/math.cos(math.radians(25))/2
GX,GZ=CX-193/2,CZ-111/2
def box(x,y,z,w,d,h):return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
def cy(x,y,z,d,h):return b.Pos(x,y+h/2,z)*b.Rot(-90,0,0)*b.Cylinder(d/2,h)
def rake(s):return b.Pos(0,0,BASE)*b.Rot(-25,0,0)*b.Pos(0,0,-BASE)*s
def unrake(s):return b.Pos(0,0,BASE)*b.Rot(25,0,0)*b.Pos(0,0,-BASE)*s
def vol(s):return sum(q.volume for q in s.solids()) if s else 0.
def rounded(x,y,z,w,d,h,r):return b.Pos(x+w/2,y,z+h/2)*b.Rot(-90,0,0)*b.extrude(b.RectangleRounded(w,h,r),amount=d)
before={s.label:s for s in b.import_step(ROOT/'cad/output/v41_recessed_glass/whole_enclosure_review.step').children}
parts={n:copy.deepcopy(s) for n,s in before.items() if not n.startswith('display_mount_')}
old_tub=parts['tub_left'];tub=copy.deepcopy(old_tub)
lug_centres=json.loads((ROOT/'cad/output/v40_display_mount/audit.json').read_text())['lug_centres_local_xz']
for name,s in before.items():
    if name.startswith('display_mount_'):tub+=s
for x in sorted({xz[0] for xz in lug_centres}):
    for az in (GZ-5.5,GZ+111+5.5):
        # A broad root fuses the old pad and arm, closing both obsolete holes.
        # The root remains outside the glass footprint; load remains on metal.
        tub+=rake(box(x-7,2.4,az-4,14,13.5,8))
        tub+=rake(cy(x,5.99,az,4.24,9.91))
assert tub.is_valid and len(tub.solids())==1
parts['tub_left']=tub
checks={}
for x,z in lug_centres:
    clearance=cy(x,6.959,z,3.39,9.0)
    recess=cy(x,10.861,z,6.49,5.05)
    land=cy(x,6.96,z,9.9,.15)-cy(x,6.959,z,3.41,.152)
    checks[f'{x:.2f},{z:.2f}']={
      'bore_obstruction_mm3':vol(tub&rake(clearance)),
      'counterbore_obstruction_mm3':vol(tub&rake(recess)),
      'bearing_land_fraction':vol(tub&rake(land))/vol(land)}
assert all(v['bore_obstruction_mm3']<.01 and v['counterbore_obstruction_mm3']<.01 and v['bearing_land_fraction']>.999 for v in checks.values()),checks

# Exact translational sweeps include the now-fixed arms throughout front entry.
# Retention screws are removed for service; integral mounts remain in place.
sweeps={
 'glass_1p1mm':rounded(GX,-100,GZ,193,102.1,111,8),
 'chassis_nominal':box(GX+12,-100,GZ+3.35,166.2,106.96,100.6),
 'Pi_nominal':box(GX+51.12,-100,GZ+30.65,85,141,56)}
sweep_hits={name:{n:v for n,p in parts.items() if (v:=vol(rake(s)&p))>.1} for name,s in sweeps.items()}
assert not any(sweep_hits.values()),sweep_hits
clashes={n:v for n,s in parts.items() if n!='tub_left' and (v:=vol(tub&s))>.1}
assert not clashes,clashes
pi_margin=rake(box(GX+46.12,6.96,GZ+25.65,95,41-5.96,66))
assert vol(pi_margin&tub)<.1
cable=rake(box(GX+41.12,42,GZ+20.65,105,20,76))

# Inspect material additions ahead of the nominal metal pad plane. All are
# confined outside the glass outline, so they cannot become hidden glass clamps.
glass_column=rake(rounded(GX-.2,-5,GZ-.2,193.4,7.5,111.4,8.2))
assert vol((tub-old_tub)&glass_column)<.01
new_material=vol(tub)-vol(old_tub)
old_arms=sum(vol(s) for n,s in before.items() if n.startswith('display_mount_'))

tub.label='tub_left';b.export_step(tub,OUT/'tub_left.step')
b.export_stl(tub,OUT/'tub_left_assembly.stl',tolerance=.035)
assert trimesh.load_mesh(OUT/'tub_left_assembly.stl').is_watertight
for n,s in parts.items():s.label=n;s.color=b.Color('#173B53' if n in ('foot_left','foot_right_bonded','logo') else '#F0F1EB')
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()]),OUT/'whole_enclosure_review.step')

glass=rounded(GX,1,GZ,193,1.1,111,8)
chassis=box(GX+12,1.7,GZ+3.35,166.2,5.26,100.6)
pi=box(GX+51.12,6.96,GZ+30.65,85,34.04,56)
refs={'REFERENCE_glass':rake(glass),'REFERENCE_chassis_nominal':rake(chassis),'REFERENCE_Pi_nominal':rake(pi)}
for n,s in refs.items():s.label=n
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in [*parts.values(),*refs.values()]]),OUT/'whole_enclosure_with_hardware.step')

# Show only the display panel and integral mounts, viewed from the inside.
# Crop the CAD for illustration; do not export this crop as a production part.
front=unrake(tub)&box(3,-.1,GZ-16,212.96,25,143)
sc=Scene(1000,700,ss=1)
sc.add(front,'#E9E9E1');sc.add(glass,'#17262F');sc.add(chassis,'#969EA4');sc.add(pi,'#346D51')
sc.look_at((265,470,310),(109,10,CZ),fov=29)
sc.save(str(OUT/'integral_mounts_rear.png'))
report={
 'status':'Integral-mount CAD candidate checked; full-case slicing and physical mounting test pending',
 'case_mounts':'Four integral arms; no separate brackets or case-side insert bores',
 'fasteners':{'count':4,'type':'M3x6 into original metal display lugs','bearing_pad_mm':3.9,'nominal_engagement_mm':2.1,'manufacturer_thread_depth_max_mm':2.5,'actual_screw_check_required':True},
 'removed_hardware':{'M3x8_case_screws':4,'M3_case_heat_set_inserts':4,'separate_printed_brackets':4},
 'service':'Insert display and attached Pi from front, secure four screws from rear. Remove screws to withdraw through front; mounts remain integral.',
 'opening_mm':[193.4,111.4],'opening_radius_mm':8.2,'glass_recess_mm':1,'metal_lug_plane_y_mm':6.96,
 'lug_centres_local_xz':lug_centres,'lug_hole_checks':checks,'part_intersections_mm3':clashes,
 'exact_front_sweep_clashes_mm3':sweep_hits,'pi_margin_collision_mm3':vol(pi_margin&tub),
 'cable_allowance_collision_mm3':vol(cable&tub),
 'body_solid_count':1,'body_valid':True,'body_watertight':True,
 'body_and_mounts_volume_increase_vs_V41_mm3':new_material-old_arms,
 'physical_lug_pattern_or_stack_confirmed':False,
 'printability':'Integral overhanging arms may need local support depending on full-body orientation. V40 separate-flat-bracket support-free result does not apply; full-body GUI slice review required.',
 'limits':['User has validated glass outline only; use existing frame/brackets to check unchanged metal lug pattern and stack',
           'Screwdriver access with actual cables/power hardware unverified',
           'Internal power architecture unresolved; inherited divider cable conflict retained',
           'No new print dispatched; active navy base job unchanged; Fusion remains closed/latestV39']}
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
