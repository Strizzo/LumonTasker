"""Apply physical V31 cradle fit feedback to the V35 shell: outlet +3 mm."""
from pathlib import Path
import copy, json
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/output/v36_outlet_alignment'
OUT.mkdir(parents=True,exist_ok=True)
def box(x,y,z,w,d,h):
    return b.Pos(x+w/2,y+d/2,z+h/2)*b.Box(w,d,h)
assembly=b.import_step(ROOT/'cad/output/v35_desktop_terminal/whole_enclosure_review.step')
parts={s.label:copy.deepcopy(s) for s in assembly.children}
shell=parts['shell']
x=218.96+45.5
old_center=130.1
new_center=old_center+3
# Fill the old rectangular aperture within the 3 mm front wall, then recut.
shell=shell+box(x,0,old_center-7,90,3,14)
shell=shell-box(x,-1,new_center-7,90,5,14)
assert shell.is_valid and len(shell.solids())==1
assert abs(shell.volume-parts['shell'].volume)<0.01
intersection=shell.intersect(box(x,-.1,new_center-7,90,3.2,14))
assert intersection is None or sum(s.volume for s in intersection.solids())<.001
parts['shell']=shell
for name,shape in parts.items(): shape.label=name
b.export_step(b.Compound(children=list(parts.values())),OUT/'whole_enclosure_review.step')
b.export_stl(shell,OUT/'shell_assembly.stl',tolerance=.035)
mesh=trimesh.load_mesh(OUT/'shell_assembly.stl')
assert mesh.is_watertight
(OUT/'audit.json').write_text(json.dumps(dict(valid=True,solids=1,watertight=True,old_outlet_center_z_mm=old_center,new_outlet_center_z_mm=new_center,opening_mm=[90,14],led_changed=False,cradle_changed=False,print_released=False),indent=2)+'\n')
(OUT/'README.md').write_text('''# V36 physical outlet alignment correction

User reports V31 cradle fits well. With the printer seated in the printed prototype, move the enclosure paper aperture upward 3 mm; LED alignment is acceptable.

Applied to V35 desktop-terminal assembly: paper opening remains 90 x 14 mm, centre Z moves from 130.1 to 133.1 mm (edges 126.1–140.1 mm). Cradle, printer pose and LED stay unchanged. This is the latest physical correction, superseding earlier outlet-position estimates.

Shell is one valid watertight solid; unchanged volume and new opening clearance verified. All other components are copied unchanged from V35. STEP is ready for Fusion review; not yet imported/saved in Fusion. STL is in assembly coordinates, not a sliced print release. No print dispatched.

Current prototype remains useful for retention, feed/cut, cable and rear-service tests. Secured retention and those functional checks remain pending. Final shell waits for final filaments and remaining fit checks.
''')
print('V36 validated and exported:',OUT)
