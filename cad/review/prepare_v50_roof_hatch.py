"""Prepare existing aligned display roof and rear hatch on one white plate.
Does not change the enclosure or dispatch a job. These parts are independent
of the pending internal/external power choice (hatch may be superseded if
an internal supply forces new access requirements).
"""
from pathlib import Path
import json,zipfile
import build123d as b
import trimesh
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/output/v50_full_display_preflight';OUT.mkdir(exist_ok=True)
parts={s.label:s for s in b.import_step(ROOT/'cad/output/v49_measured_display_depth/whole_enclosure_review.step').children}
src=(ROOT/'cad/review/pack_shell_v37.py').read_text().replace("OUT=ROOT/'cad/output/v37_logo_spacing'", "OUT=ROOT/'cad/output/v50_full_display_preflight'")
src=src[:src.index("project('01_shell_with_logo'")]
ns={'__file__':str(__file__)};exec(compile(src,__file__,'exec'),ns)
with zipfile.ZipFile(ROOT/'cad/output/v49_measured_display_depth/01_V49_depth_and_screw_coupons.3mf') as z:
 settings=json.loads(z.read('Metadata/project_settings.config'))
updates={'wall_loops':'3','top_shell_layers':'4','bottom_shell_layers':'4','sparse_infill_density':'10%','sparse_infill_pattern':'gyroid','support_top_z_distance':'0.12','enable_support':'1','support_type':'normal(auto)','support_style':'snug','enable_prime_tower':'0','brim_type':'no_brim'}
settings.update(updates)
settings['different_settings_to_system'][0]=';'.join(sorted(set(settings['different_settings_to_system'][0].split(';'))|set(updates)))
ns['settings']=settings
items=[('Display rounded roof','top_plate_left',180,(18,22)),('Display rear hatch','rear_panel_left',-90,(62,144))]
objects=[];data=[]
for label,name,rx,xy in items:
 s=b.Rot(rx,0,0)*parts[name];bb=s.bounding_box();s=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*s
 filename=name+'_print.stl';b.export_stl(s,OUT/filename,tolerance=.025)
 mesh=trimesh.load_mesh(OUT/filename);assert mesh.is_watertight
 assert all(xy[i]+mesh.extents[i]<250 for i in range(2))
 objects.append((label,[(filename,2)],xy));data.append({'name':name,'bounds_mm':mesh.extents.tolist(),'bed_origin_xy':list(xy)})
ns['project']('02_V50_display_roof_and_hatch',objects)
(OUT/'roof_hatch_manifest.json').write_text(json.dumps({'status':'Prepared for native slice and toolpath review; not sent','filament':'A2 PolyTerra Cotton White PLA','parts':data,'changes':updates,'inter_colour_swaps':0,'source':'Exact existing V49/V39 aligned roof and hatch geometry','bed_clear_after_v49':False},indent=2)+'\n')
