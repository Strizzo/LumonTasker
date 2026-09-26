"""One-colour support-free full-outline mount fit test; never dispatch here."""
from pathlib import Path
import json, trimesh
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/output/v40_display_mount'
audit=json.loads((OUT/'fit_audit.json').read_text())
assert audit['status'].startswith('Fit-kit CAD checks passed'),audit['status']
src=(ROOT/'cad/review/pack_shell_v37.py').read_text()
src=src.replace("OUT=ROOT/'cad/output/v37_logo_spacing'","OUT=ROOT/'cad/output/v40_display_mount'")
src=src[:src.index("project('01_shell_with_logo'")]
ns={'__file__':str(__file__)}
exec(compile(src,__file__,'exec'),ns)
s=ns['settings']
updates={'wall_loops':'3','top_shell_layers':'4','top_shell_thickness':'0.8','bottom_shell_layers':'4','sparse_infill_density':'10%',
         'enable_support':'0','enable_prime_tower':'0','brim_type':'no_brim',
         'layer_height':'0.2','initial_layer_print_height':'0.2','elefant_foot_compensation':'0.15'}
s.update(updates)
s['different_settings_to_system'][0]=';'.join(sorted(set(s['different_settings_to_system'][0].split(';'))|set(updates)))
files=['display_fit_frame_print.stl']+[f'display_mount_{side}_{level}_local_print.stl' for level in ['lower','upper'] for side in ['left','right']]
placements=[(21.82,60),(62,100),(102,100),(142,100),(182,100)]
objects=[]
for filename,xy in zip(files,placements):
    m=trimesh.load_mesh(OUT/filename)
    assert m.is_watertight and m.bounds[0][2]>-.001
    assert max(m.bounds[1][:2]+xy)<248
    objects.append((Path(filename).stem,[(filename,2)],xy))
ns['project']('01_V40_display_fit_kit',objects)
(OUT/'fit_plate_manifest.json').write_text(json.dumps({'filament':'A2 PolyTerra Cotton White PLA only','supports':False,'colour_changes':0,'settings':updates,'objects':[{'file':f,'xy':xy} for f,xy in zip(files,placements)],'release':'Small mechanical fit test; no final left-body print yet','dispatched':False},indent=2)+'\n')
