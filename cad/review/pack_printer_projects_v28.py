"""Build Bambu project archives from verified oriented meshes and known P1S settings."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E
import trimesh
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'cad/output/v28_integrated_top'
TEMPLATE=ROOT/'cad/output/v27_refined_printer/01_shell_supported.3mf'
with zipfile.ZipFile(TEMPLATE) as z:
 settings=json.loads(z.read('Metadata/project_settings.config'))
 types=z.read('[Content_Types].xml');rels=z.read('_rels/.rels')
settings.update(wall_loops='4',sparse_infill_density='15%',sparse_infill_pattern='gyroid',top_shell_layers='5',bottom_shell_layers='5',brim_type='outer_only',brim_width='5',enable_support='0',outer_wall_speed='80',inner_wall_speed='150',default_acceleration='3000',wipe_tower_x=['215'],wipe_tower_y=['20'],prime_tower_width='30')
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
E.register_namespace('',NS)
def tag(n):return '{'+NS+'}'+n
def project(name,objects):
 model=E.Element(tag('model'),{'xmlns:p':'http://schemas.microsoft.com/3dmanufacturing/production/2015/06','requiredextensions':'p','unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
 E.SubElement(model,tag('metadata'),name='Application').text='BambuStudio-02.05.00.66'
 E.SubElement(model,tag('metadata'),name='BambuStudio:3mfVersion').text='1'
 resources=E.SubElement(model,tag('resources'));build=E.SubElement(model,tag('build'))
 cfg=E.Element('config');plate=E.SubElement(cfg,'plate')
 for k,v in [('plater_id','1'),('plater_name',name),('locked','false')]:E.SubElement(plate,'metadata',key=k,value=v)
 ident=1
 for objname,meshes,xy in objects:
  entries=[]
  for filename,extruder in meshes:
   mesh=trimesh.load_mesh(OUT/filename);assert mesh.is_watertight
   obj=E.SubElement(resources,tag('object'),id=str(ident),type='model')
   geo=E.SubElement(obj,tag('mesh'));verts=E.SubElement(geo,tag('vertices'));faces=E.SubElement(geo,tag('triangles'))
   for v in mesh.vertices:E.SubElement(verts,tag('vertex'),**dict(zip(('x','y','z'),(f'{a:.7f}' for a in v))))
   for f in mesh.faces:E.SubElement(faces,tag('triangle'),**dict(zip(('v1','v2','v3'),map(str,f))))
   entries.append((ident,filename,extruder,len(mesh.faces)));ident+=1
  parent=ident;ident+=1
  obj=E.SubElement(resources,tag('object'),id=str(parent),type='model');components=E.SubElement(obj,tag('components'))
  objcfg=E.SubElement(cfg,'object',id=str(parent))
  E.SubElement(objcfg,'metadata',key='name',value=objname);E.SubElement(objcfg,'metadata',key='extruder',value=str(entries[0][2]))
  for mid,filename,extruder,count in entries:
   E.SubElement(components,tag('component'),objectid=str(mid),transform='1 0 0 0 1 0 0 0 1 0 0 0')
   part=E.SubElement(objcfg,'part',id=str(mid),subtype='normal_part')
   for k,v in [('name',Path(filename).stem),('extruder',str(extruder)),('source_file',filename),('matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')]:E.SubElement(part,'metadata',key=k,value=v)
   E.SubElement(part,'mesh_stat',face_count=str(count),edges_fixed='0',degenerate_facets='0',facets_removed='0',facets_reversed='0',backwards_edges='0')
  E.SubElement(build,tag('item'),objectid=str(parent),transform=f'1 0 0 0 1 0 0 0 1 {xy[0]} {xy[1]} 0',printable='1')
  inst=E.SubElement(plate,'model_instance')
  for k,v in [('object_id',str(parent)),('instance_id','0'),('identify_id',str(parent*10))]:E.SubElement(inst,'metadata',key=k,value=v)
 dst=OUT/(name+'.3mf')
 with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('[Content_Types].xml',types);z.writestr('_rels/.rels',rels)
  z.writestr('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))
  z.writestr('Metadata/model_settings.config',E.tostring(cfg,encoding='utf-8',xml_declaration=True))
  z.writestr('Metadata/project_settings.config',json.dumps(settings,indent=2))
 print(dst)
settings.update(enable_support='1',support_type='normal(auto)',support_threshold_angle='30',support_on_build_plate_only='0')
project('01_shell_with_logo',[('Integral front shell',[('shell_registered.stl',2),('logo_registered.stl',1)],(25,35))])
settings.update(enable_prime_tower='0',enable_support='0')
project('02_cradle_and_bars',[(n,[(n+'.stl',2)],xy) for n,xy in [('cradle_tray',(30,20)),('retaining_bar_58',(35,191)),('retaining_bar_137',(35,222))]])
project('04_rear_cover',[('Rear cover',[('rear_cover.stl',2)],(49,34))])


project('07_retaining_bars_only',[(n,[(n+'.stl',2)],xy) for n,xy in [('retaining_bar_58',(35,65)),('retaining_bar_137',(35,105))]])
