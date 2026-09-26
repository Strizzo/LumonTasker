"""Measured glass and attached Pi; close-fit, rear-lug-supported display revision.

No tight glass clamping. 193 x 111 x 40 mm are user measurements. Lug datums
are nominal manufacturer drawing values and require the small physical test.
Keep the already fitted printer side byte-equivalent in geometry.
"""
from pathlib import Path
import copy, json, math, sys
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'files')]
from render3d import Scene
OUT=ROOT/'cad/output/v40_display_mount'; OUT.mkdir(exist_ok=True)
W,H,D,SPLIT=393.96,201.,170.75,218.96
ANGLE=25.; BASE=33.; CX=109.48
CR=math.cos(math.radians(ANGLE))
CZ=BASE+(H-16-BASE)/CR/2
GX,GZ=CX-193/2,CZ-111/2
OLD_GZ=CZ-110.76/2
GLASS_FRONT=-1.; GLASS_W=193.; GLASS_H=111.; TOTAL_DEPTH=40.
GAP=.20; CORNER_R=8.; LUG_PLANE=GLASS_FRONT+5.96
BRACKET_T=3.9; ANCHOR_PLANE=10.
# Drawing is a REAR view. Mirror X for front-view coordinates, and centre
# the nominal 192.96 x 110.76 outline within the user's rounded measurement.
LUG_X=[GX+(192.96-158.09)+.02,GX+(192.96-31.89)+.02]
LUG_Z=[GZ+23.35+.12,GZ+23.35+65.65+.12]
ANCHOR_Z=[GZ-5.5,GZ+111+5.5]
PALE,NAVY='#F0F1EB','#173B53'
NAVY_PARTS={'foot_left','foot_right_bonded','display_bezel','logo'}
def box(x,y,z,w,d,h):return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
def cy(x,y,z,d,h):return b.Pos(x,y+h/2,z)*b.Rot(-90,0,0)*b.Cylinder(d/2,h)
def cx(x,y,z,d,h):return b.Pos(x+h/2,y,z)*b.Rot(0,90,0)*b.Cylinder(d/2,h)
def cz(x,y,z,d,h):return b.Pos(x,y,z+h/2)*b.Cylinder(d/2,h)
def rake(s):return b.Pos(0,0,BASE)*b.Rot(-ANGLE,0,0)*b.Pos(0,0,-BASE)*s
def rounded(x,y,z,w,d,h,r):
    return b.Pos(x+w/2,y,z+h/2)*b.Rot(-90,0,0)*b.extrude(b.RectangleRounded(w,h,r),amount=d)
def volume(s):return sum(t.volume for t in s.solids()) if s else 0.
def diff(a,c):return volume(a-c)+volume(c-a)
def export(s,name,print_rot=None):
    s.label=name;b.export_step(s,OUT/(name+'.step'))
    b.export_stl(s,OUT/(name+'_assembly.stl'),tolerance=.025)
    assert trimesh.load_mesh(OUT/(name+'_assembly.stl')).is_watertight,name
    if print_rot:
        t=print_rot*s;bb=t.bounding_box();t=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*t
        b.export_stl(t,OUT/(name+'_print.stl'),tolerance=.025)
        assert trimesh.load_mesh(OUT/(name+'_print.stl')).is_watertight
    assert s.is_valid and len(s.solids())==1,(name,s.is_valid,len(s.solids()))

before={s.label:s for s in b.import_step(ROOT/'cad/output/v39_aligned_rear/whole_enclosure_review.step').children}
parts={n:copy.deepcopy(s) for n,s in before.items() if n!='display_retainer'}
print('Loaded V39',flush=True)
tub=parts['tub_left']
# Remove obsolete deep glass ribs and generic retainer bosses, preserving skin.
for x in (10.,206.96):
    tub-=rake(box(x,3.,OLD_GZ-4,3.,20.6,110.76+8))
for x in (53.,165.96):
    for z in (OLD_GZ-8,OLD_GZ+110.76+5.5):
        tub-=rake(cy(x,3.,z,9.02,21.1))
# Attached Pi replaces four unused independent Pi standoffs on the left wall.
for y in (97.5,146.5):
    for z in (42.5,100.5):tub-=cx(3.,y,z,8.02,15.1)
# Open the entire measured glass outline. Radius includes the same radial gap.
window=rounded(GX-GAP,-6,GZ-GAP,193+2*GAP,32,111+2*GAP,CORNER_R+GAP)
tub-=rake(window)
# Thin the broad front skin to 2.4 mm, with local reinforcement below added mounts.
tub-=rake(box(5,2.4,34,SPLIT-10,.6,148))
# Four independent rear brackets; each rests on a metal lug and a case boss.
# Anchor inserts are 6mm deep; no plastic or screw bears on the glass edge.
anchors=None
for x in LUG_X:
    for z in ANCHOR_Z:
        a=cy(x,1.,z,9.,ANCHOR_PLANE-1)-cy(x,ANCHOR_PLANE-6,z,4.2,6.1)
        # Add a shallow pad into the unthinned front face under the root.
        a+=box(x-6,1.,z-4.7,12.,2.,9.4)
        a-=cy(x,ANCHOR_PLANE-6,z,4.2,6.1)
        anchors=a if anchors is None else anchors+a
        tub+=rake(a)
parts['tub_left']=tub
# Preserve outer styling and location of the separate navy bezel; enlarge opening.
parts['display_bezel']=before['display_bezel']-rake(window)

local_brackets={}
for xi,x in enumerate(LUG_X):
    for zi,z in enumerate(LUG_Z):
        az=ANCHOR_Z[zi]
        lo,hi=sorted((az,z))
        # Flat back surface gives a support-free printing orientation. A relief
        # on the forward side clears the metal chassis while the lug pad reaches it.
        s=box(x-5,ANCHOR_PLANE,lo-5,10,BRACKET_T,hi-lo+10)
        s+=cy(x,LUG_PLANE,z,10,ANCHOR_PLANE-LUG_PLANE+.1)
        s-=cy(x,LUG_PLANE-.1,z,3.4,ANCHOR_PLANE+BRACKET_T-LUG_PLANE+.2)
        # Counterbore leaves 3.9 mm bearing thickness at the metal lug for M3x6.
        s-=cy(x,LUG_PLANE+BRACKET_T,z,6.5,20)
        s-=cy(x,ANCHOR_PLANE-.1,az,3.4,BRACKET_T+.2)
        name=f'display_mount_{"left" if xi==0 else "right"}_{"lower" if zi==0 else "upper"}'
        local_brackets[name]=s
        parts[name]=rake(s)
        export(s,name+'_local',b.Rot(-90,0,0))
print('Mount geometry created',flush=True)
# Full-outline test is small in volume: same bezel/window, metal bearing planes
# and four body bosses. No large enclosure is needed to establish the fit.
# Test-only outer ring is slightly taller to support all boss pads from the bed.
fixture=rounded(CX-(212.96-.6)/2,-2,CZ-132/2,212.96-.6,3,132,13.7)-window
fixture+=anchors
export(fixture,'display_fit_frame',b.Rot(90,0,0))
# Alternate small corner gauges are not needed until the full outline is tried.
# Nominal references are deliberately labelled: the 40mm depth is measured,
# but board position, lug offsets and local chassis thickness use the drawing.
glass=rounded(GX,GLASS_FRONT,GZ,193,.7,111,CORNER_R)
chassis=box(GX+12.,GLASS_FRONT+.7,GZ+3.35,166.2,5.26,100.6)
# Pi orientation/position based on rear view M2.5 datum; add a 5mm lateral margin
# to form a conservative central keep-out rather than a detailed board model.
pi_nom=box(GX+51.12,GLASS_FRONT+5.96,GZ+30.65,85,40-5.96,56)
pi_keepout=box(GX+46.12,GLASS_FRONT+5.96,GZ+25.65,95,41-5.96,66)
# Plug/wire bend allowance behind the assembly, provisional until routed.
cable_allowance=box(GX+41.12,GLASS_FRONT+41,GZ+20.65,105,20,76)
refs={'REFERENCE_glass_measured_193x111':rake(glass),
      'REFERENCE_chassis_nominal':rake(chassis),
      'REFERENCE_attached_Pi_nominal_40mm_total':rake(pi_nom)}
keepouts={'Pi_5mm_lateral_1mm_rear_allowance':rake(pi_keepout),
          'provisional_20mm_rear_cable_space':rake(cable_allowance)}
psu=box(83.96,48,13,129,97,30)
buck=box(10,30,13,35,65,20)
iec=box(151.98,138.25,47.85,50,32.5,28.3)
power={'PSU_placeholder':psu,'buck_placeholder':buck,'IEC_placeholder':iec}
# Lighten the unprinted left foot using open underside pockets, retaining a
# 2.4mm continuous upper skin, perimeter, crossing ribs and screw columns.
foot=parts['foot_left']
for x0,x1 in ((16,72),(80,139),(147,203)):
    for y0,y1 in ((16,77),(85,153)):
        pocket=box(x0,y0,-.1,x1-x0,y1-y0,6.7)
        for sx in (55,SPLIT-28):
            for sy in (20,D-9):pocket-=cz(sx,sy,-1,18,9)
        foot-=pocket
parts['foot_left']=foot

report={'status':'CAD and fit-kit preparation; physical test not yet performed',
 'user_dimensions_mm':[193,111,40],'glass_clearance_per_side_mm':GAP,
 'opening_mm':[193+2*GAP,111+2*GAP],
 'glass_radius_reference_mm':8,'opening_radius_mm':8.2,
 'radius_status':'Estimated from drawing; verify against actual glass with fit frame.',
 'display_front_recess_below_navy_bezel_mm':1.,
 'outer_lug_pitch_mm':[126.2,65.65],'lug_datum_status':'Nominal drawing, mirrored from rear view; test required',
 'lug_centres_local_xz':[[x,z] for x in LUG_X for z in LUG_Z],
 'lug_bearing_y_mm':LUG_PLANE,'case_anchor_y_mm':ANCHOR_PLANE,
 'screws':{'metal_lugs':'4 x M3x6; 3.9mm bearing pad leaves nominal 2.1mm engagement in 2.5mm thread; verify actual screw/washer stack before tightening',
           'case_anchors':'4 x M3x8; 3.9mm bracket leaves nominal 4.1mm engagement in tested 4.2mm insert bores'},
 'parts':{},'interferences':[],'hardware_clashes_mm3':{},'keepout_clashes_mm3':{},
 'limits':['Fit frame not physically tested; 0.2mm per-side FDM fit is a target, not a guaranteed result.',
           'Board/lug placement is nominal; only outer glass and full depth are physically measured.',
           'Power parts and cable routes remain inherited placeholders, not purchased-hardware verification.',
           'Lightweight foot stiffness and actual fitted clearance require physical review.'],
 'print_release':'Fit kit only after slicer verification; large display bay remains on hold.'}
changed=[n for n in parts if n not in before or n in ['tub_left','display_bezel','foot_left']]
for n,s in parts.items():
    s.label=n;s.color=b.Color(NAVY if n in NAVY_PARTS else PALE)
    expected=1 if n in changed else len(before[n].solids())
    assert s.is_valid and len(s.solids())==expected,(n,s.is_valid,len(s.solids()))
    report['parts'][n]={'volume_mm3':volume(s),'solid_count':len(s.solids())}
    if n in before:
        report['parts'][n]['volume_change_percent']=100*(volume(s)/volume(before[n])-1)
    if n in changed:export(s,n)
    else:assert diff(s,before[n])<.01,n
for i,(an,a) in enumerate(parts.items()):
    for bn,c in list(parts.items())[i+1:]:
        ab,cb=a.bounding_box(),c.bounding_box()
        if any(min(getattr(ab.max,k),getattr(cb.max,k))-max(getattr(ab.min,k),getattr(cb.min,k))<.001 for k in 'XYZ'):continue
        hit=volume(a&c)
        if hit>.1:report['interferences'].append([an,bn,hit])
for rn,r in refs.items():
    report['hardware_clashes_mm3'][rn]={n:volume(r&s) for n,s in parts.items() if volume(r&s)>.1}
for rn,r in keepouts.items():
    report['keepout_clashes_mm3'][rn]={n:volume(r&s) for n,s in {**parts,**power}.items() if volume(r&s)>.1}
report['hardware_to_power_mm']={rn:{n:round(r.distance_to(s),3) for n,s in power.items()} for rn,r in refs.items()}
report['unchanged_printer_side']=True
report['fixture_volume_mm3']=volume(fixture)
report['all_brackets_volume_mm3']=sum(volume(s) for s in local_brackets.values())
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['interferences','hardware_clashes_mm3','keepout_clashes_mm3','hardware_to_power_mm']},indent=2),flush=True)
assert not report['interferences'],report['interferences']
assert not any(report['hardware_clashes_mm3'].values()),report['hardware_clashes_mm3']
assert not any(report['keepout_clashes_mm3'].values()),report['keepout_clashes_mm3']
# STEP review includes hardware references in clearly named separate components.
for name,s in refs.items():s.label=name;s.color=b.Color('#344956')
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()],label='LUMON_V40_DISPLAY_MOUNT_CANDIDATE'),OUT/'whole_enclosure_review.step')
b.export_step(b.Compound(children=[copy.deepcopy(s) for s in list(parts.values())+list(refs.values())],label='LUMON_V40_WITH_HARDWARE_REFERENCES'),OUT/'whole_enclosure_with_hardware.step')
b.export_step(b.Compound(children=[fixture]+[copy.deepcopy(s) for s in local_brackets.values()],label='V40_DISPLAY_FIT_KIT_ASSEMBLED'),OUT/'display_fit_kit_assembled.step')
for name,eye,target in [('front',(500,-740,390),(197,65,105)),('display_mount_rear',(300,560,260),(109,55,105))]:
    sc=Scene(1400,950,ss=1)
    for n,s in parts.items():
        if name=='display_mount_rear' and n not in ['tub_left','display_bezel'] and not n.startswith('display_mount_'):continue
        sc.add(s,NAVY if n in NAVY_PARTS else PALE)
    for n,s in refs.items():sc.add(s,'#172B36')
    sc.look_at(eye,target,fov=32);sc.save(str(OUT/(name+'.png')))
sc=Scene(1400,950,ss=1)
sc.add(fixture,PALE)
for s in local_brackets.values():sc.add(s,NAVY)
sc.add(glass,'#16272F');sc.add(chassis,'#BCC3C8');sc.add(pi_nom,'#2B815B')
sc.look_at((300,500,300),(109,10,CZ),fov=27);sc.save(str(OUT/'fit_kit_rear.png'))
report['status']='CAD checks passed; fit kit awaits physical test; large left enclosure not released'
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('V40 CAD ready',flush=True)
