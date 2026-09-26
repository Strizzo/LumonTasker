from pathlib import Path
import zipfile,json,xml.etree.ElementTree as E
root=Path(__file__).resolve().parents[2]/'cad/output/p1s_fit_plate'
src=root/'LUMON_v19_fit_test_setup.3mf'; dst=root/'LUMON_v19_fit_test.3mf'
with zipfile.ZipFile(src) as z: files={n:z.read(n) for n in z.namelist()}
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
E.register_namespace('',ns);E.register_namespace('p','http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
m=E.fromstring(files['3D/3dmodel.model'])
positions={'2':(90,80),'4':(150,140),'6':(150,80),'8':(90,140)}
for item in m.find('{'+ns+'}build'):
 t=item.get('transform').split();t[9:11]=map(str,positions[item.get('objectid')]);item.set('transform',' '.join(t))
files['3D/3dmodel.model']=E.tostring(m,encoding='utf-8',xml_declaration=True)
c=E.fromstring(files['Metadata/model_settings.config'])
for o in c.findall('object'):
 name=o.find("part/metadata[@key='source_file']").get('value')
 for n in o.findall(".//metadata[@key='name']"):n.set('value',name)
 o.find("metadata[@key='extruder']").set('value','1' if name.startswith('dark') else '2')
 if 'screen' in name:E.SubElement(o,'metadata',key='enable_support',value='1')
c.find("plate/metadata[@key='plater_name']").set('value','LUMON v19 fit tests')
files['Metadata/model_settings.config']=E.tostring(c,encoding='utf-8',xml_declaration=True)
d=json.loads(files['Metadata/project_settings.config']);d.update(wall_loops='3',sparse_infill_density='20%',brim_type='outer_only',brim_width='3',support_type='normal(auto)',support_on_build_plate_only='1')
files['Metadata/project_settings.config']=json.dumps(d,indent=2).encode()
with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
 for n,data in files.items():z.writestr(n,data)
print(dst)
