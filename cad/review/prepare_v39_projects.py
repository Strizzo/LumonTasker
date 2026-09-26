"""Separate-colour V39 plate projects and verified reuse of unchanged right plates."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile
import build123d as b
import trimesh

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/output/v39_aligned_rear'
PREV=ROOT/'cad/output/v38_integrated_rear'
parts={s.label:s for s in b.import_step(OUT/'whole_enclosure_review.step').children}
src=(ROOT/'cad/review/pack_shell_v37.py').read_text()
src=src.replace("OUT=ROOT/'cad/output/v37_logo_spacing'","OUT=ROOT/'cad/output/v39_aligned_rear'")
src=src[:src.index("project('01_shell_with_logo'")]
ns={'__file__':str(ROOT/'cad/review/pack_shell_v39.py')}
exec(compile(src,ns['__file__'],'exec'),ns)
settings=ns['settings']
settings.update(enable_prime_tower='0',support_type='tree(auto)',support_style='default')
settings['different_settings_to_system'][0]+=';enable_prime_tower;support_style'
items=[('04_V39_display_body','tub_left',0,2,True),
       ('05_V39_display_roof','top_plate_left',180,2,True),
       ('06_V39_display_rear_hatch','rear_panel_left',-90,2,False),
       ('07_V39_display_base','foot_left',0,1,False)]
report={'left_plates':[],'right_plates_reused':[],
        'left_release':'Prepared for slicing and fit review; actual electronics fit is unverified'}
for name,key,rx,slot,supports in items:
    s=b.Rot(rx,0,0)*parts[key]
    bb=s.bounding_box();s=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*s
    filename=key+'_print.stl';b.export_stl(s,OUT/filename,tolerance=.035)
    mesh=trimesh.load_mesh(OUT/filename);assert mesh.is_watertight
    size=mesh.extents
    assert max(size)<246,(name,size)
    settings['enable_support']='1' if supports else '0'
    ns['project'](name,[(name,[(filename,slot)],((256-size[0])/2,(256-size[1])/2))])
    report['left_plates'].append({'project':name+'.3mf','part':key,'filament':slot,
                                 'dimensions_mm':size.tolist(),'supports':supports})
for src,dst in [('V38_final_shell_tree.gcode.3mf','01_V39_printer_shell.gcode.3mf'),
                ('V38_rear_cover.gcode.3mf','02_V39_printer_rear_cover.gcode.3mf'),
                ('V38_navy_base.gcode.3mf','03_V39_printer_base.gcode.3mf'),
                ('01_V38_shell_reviewed.3mf','01_V39_printer_shell.3mf'),
                ('02_V38_integrated_rear_cover.3mf','02_V39_printer_rear_cover.3mf'),
                ('03_V38_navy_base.3mf','03_V39_printer_base.3mf')]:
    shutil.copy2(PREV/src,OUT/dst)
    assert (PREV/src).read_bytes()==(OUT/dst).read_bytes()
    report['right_plates_reused'].append({'file':dst,'source':str(PREV/src),
        'sha256':hashlib.sha256((OUT/dst).read_bytes()).hexdigest(),
        'reason':'V39 CAD validation proves all printer-side components unchanged'})
(OUT/'plate_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print('V39 plate projects prepared; no print dispatched',flush=True)
