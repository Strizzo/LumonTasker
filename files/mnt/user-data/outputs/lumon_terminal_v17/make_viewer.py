"""Emit a self-contained interactive WebGL viewer for the current model."""

import base64
import json
import sys
import numpy as np

sys.path.insert(0, "/home/claude")
import lumon_v17 as m                                    # noqa: E402

p = m.p

PARTS = [
    ("tub_left",         m.TUB_LEFT,           "#DEE9EE", True,  "printed"),
    ("tub_right",        m.TUB_RIGHT,          "#DEE9EE", True,  "printed"),
    ("top_plate_left",   m.TOP_PLATE_LEFT,     "#DEE9EE", True,  "printed"),
    ("printer_lid",      m.PRINTER_LID,        "#DEE9EE", True,  "printed"),
    ("display_bezel",    m.DISPLAY_BEZEL,      "#10161E", True,  "printed"),
    ("display_retainer", m.DISPLAY_RETAINER,   "#C0C8CE", False, "printed"),
    ("rear_panel_left",  m.REAR_PANEL_LEFT,    "#DEE9EE", True,  "printed"),
    ("rear_panel_right", m.REAR_PANEL_RIGHT,   "#DEE9EE", True,  "printed"),
    ("foot_left",        m.FOOT_LEFT,          "#10161E", True,  "printed"),
    ("foot_right",       m.FOOT_RIGHT,         "#10161E", True,  "printed"),
    ("logo_fill",        m.LOGO_FILL,          "#0B4F7E", True,  "printed"),
    ("display",          m.DISPLAY_REFERENCE,  "#10161E", True,  "hardware"),
    ("printer",          m.PRINTER_REFERENCE,  "#1B222B", True,  "hardware"),
    ("psu",              m.PSU_REFERENCE,      "#93ACC3", False, "hardware"),
    ("raspberry_pi",     m.PI_REFERENCE,       "#2E7D52", False, "hardware"),
    ("mains_inlet",      m.IEC_REFERENCE,      "#3A4149", False, "hardware"),
    ("buck_converter",   m.BUCK_REFERENCE,     "#7A6A3A", False, "hardware"),
]

TOL = 0.09          # fine enough that the r12 fillets read as curves


def pack(shape):
    """Tessellate and compute crease-aware vertex normals.

    OCC gives every face its own vertices, so nothing can be smoothed.
    Welding everything is worse - it smooths across genuine 90 degree edges
    too. Instead, group the faces meeting at each position by angle: within
    CREASE they share an averaged normal (fillets read as curves), beyond it
    they stay separate (box edges stay crisp).
    """
    CREASE = np.cos(np.radians(28.0))
    verts, faces = shape.tessellate(tolerance=TOL)
    V = np.array([[q.X, q.Y, q.Z] for q in verts], dtype=np.float64)
    F = np.array(faces, dtype=np.int64)

    e1 = V[F[:, 1]] - V[F[:, 0]]
    e2 = V[F[:, 2]] - V[F[:, 0]]
    fn = np.cross(e1, e2)
    area = np.linalg.norm(fn, axis=1)
    good = area > 1e-12
    F, fn, area = F[good], fn[good], area[good]
    fn = fn / area[:, None]

    key = np.round(V * 1000).astype(np.int64)
    _, pos_id = np.unique(key, axis=0, return_inverse=True)

    buckets = {}
    for t in range(len(F)):
        for k in range(3):
            buckets.setdefault(pos_id[F[t, k]], []).append((t, k))

    out_pos, out_nrm = [], []
    new_idx = np.zeros_like(F)
    for pid, entries in buckets.items():
        clusters = []                      # [sum_normal, [(t,k), ...]]
        for (t, k) in entries:
            n = fn[t]
            for c in clusters:
                rep = c[0] / np.linalg.norm(c[0])
                if float(np.dot(rep, n)) >= CREASE:
                    c[0] = c[0] + n * area[t]
                    c[1].append((t, k))
                    break
            else:
                clusters.append([n * area[t], [(t, k)]])
        for c in clusters:
            vid = len(out_pos)
            out_pos.append(V[F[c[1][0][0], c[1][0][1]]])
            out_nrm.append(c[0] / np.linalg.norm(c[0]))
            for (t, k) in c[1]:
                new_idx[t, k] = vid

    P = np.array(out_pos, dtype=np.float32)
    N = np.array(out_nrm, dtype=np.float32)
    I = new_idx.astype(np.uint32).ravel()
    return (base64.b64encode(P.tobytes()).decode(),
            base64.b64encode(N.tobytes()).decode(),
            base64.b64encode(I.tobytes()).decode(),
            len(I) // 3)


meshes, total = [], 0
for name, shape, colour, on, kind in PARTS:
    pos, nrm, idx, n = pack(shape)
    total += n
    meshes.append(dict(name=name, colour=colour, on=on, kind=kind,
                       pos=pos, nrm=nrm, idx=idx, tris=n))
    print(f"{name:18s} {n:7d} tris")
print("total", total)

DATA = json.dumps(dict(
    meshes=meshes,
    dims=dict(W=round(p.W, 2), D=round(p.D, 2), H=round(p.H, 2),
              rake=p.rake_deg, seam=round(p.x_split, 2)),
))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>LUMON_TERMINAL v17 - viewer</title>
<style>
  :root{
    --bg:#93ACC3; --bg2:#5b7183; --panel:rgba(16,22,30,.82); --ink:#eaeff3;
    --line:rgba(234,239,243,.18); --accent:#8fc6ff;
  }
  :root:not([data-theme="light"]){}
  @media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#2a3640;--bg2:#10161E;}}
  :root[data-theme="dark"]{--bg:#2a3640;--bg2:#10161E;}
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;background:var(--bg);
    font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:var(--ink)}
  #c{display:block;width:100%;height:100%;touch-action:none}
  .panel{position:fixed;background:var(--panel);border:1px solid var(--line);
    border-radius:10px;padding:10px 12px;font-size:12px;line-height:1.5;
    backdrop-filter:blur(8px);max-width:min(46vw,260px)}
  #ui{top:52px;left:10px;max-height:calc(100% - 64px);overflow:auto;
    transition:opacity .15s, transform .15s}
  #ui.hidden{opacity:0;transform:translateX(-14px);pointer-events:none}
  #toggle{position:fixed;top:10px;left:10px;z-index:5;width:34px;height:34px;
    border-radius:9px;font-size:15px;line-height:1;padding:0;
    background:var(--panel);border:1px solid var(--line);color:var(--ink);
    backdrop-filter:blur(8px);cursor:pointer}
  #hud{bottom:10px;left:10px;font-size:11px;opacity:.85}
  h1{font-size:12px;margin:0 0 8px;letter-spacing:.06em;font-weight:600}
  .grp{margin:8px 0 4px;font-size:10px;letter-spacing:.09em;opacity:.6;
    border-top:1px solid var(--line);padding-top:7px}
  label{display:flex;align-items:center;gap:7px;cursor:pointer;padding:2px 0}
  input[type=checkbox]{accent-color:var(--accent);flex:none}
  .sw{width:11px;height:11px;border-radius:2px;flex:none;
    border:1px solid rgba(255,255,255,.35)}
  .btns{display:flex;flex-wrap:wrap;gap:5px;margin-top:7px}
  button{font:inherit;font-size:11px;color:var(--ink);background:rgba(255,255,255,.09);
    border:1px solid var(--line);border-radius:6px;padding:4px 9px;cursor:pointer}
  button:hover{background:rgba(255,255,255,.17)}
  input[type=range]{width:100%;accent-color:var(--accent);margin:4px 0 0}
  @media (max-width:640px){.panel{font-size:11px;max-width:52vw}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<button id="toggle" title="show/hide panel">&#9776;</button>
<div class="panel" id="ui">
  <h1>LUMON_TERMINAL v17</h1>
  <div id="printed"></div>
  <div class="grp">HARDWARE</div>
  <div id="hardware"></div>
  <div class="grp">VIEW</div>
  <div class="btns">
    <button data-v="iso">iso</button><button data-v="front">front</button>
    <button data-v="side">side</button><button data-v="top">top</button>
    <button data-v="back">back</button>
  </div>
  <div class="grp">EXPLODE</div>
  <input type="range" id="explode" min="0" max="100" value="0">
  <div class="grp">SECTION (front to back)</div>
  <input type="range" id="clip" min="0" max="100" value="100">
  <label style="margin-top:6px"><input type="checkbox" id="edges"> show edges</label>
</div>
<div class="panel" id="hud"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const DATA = __DATA__;

function b64f32(s){const b=atob(s),u=new Uint8Array(b.length);
  for(let i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return new Float32Array(u.buffer);}
function b64u32(s){const b=atob(s),u=new Uint8Array(b.length);
  for(let i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return new Uint32Array(u.buffer);}

const cv=document.getElementById('c');
const renderer=new THREE.WebGLRenderer({canvas:cv,antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.localClippingEnabled=true;
const scene=new THREE.Scene();

const css=getComputedStyle(document.documentElement);
scene.background=new THREE.Color(css.getPropertyValue('--bg').trim()||'#aab4be');

const camera=new THREE.PerspectiveCamera(32,1,1,6000);
const D=DATA.dims, C=new THREE.Vector3(D.W/2,D.D/2,D.H/2);

scene.add(new THREE.HemisphereLight(0xffffff,0x5a6670,0.55));
const key=new THREE.DirectionalLight(0xffffff,0.85); key.position.set(-420,-760,640);
const fill=new THREE.DirectionalLight(0xffffff,0.3); fill.position.set(700,-260,180);
const rim=new THREE.DirectionalLight(0xffffff,0.22); rim.position.set(80,780,320);
scene.add(key,fill,rim);

const grid=new THREE.GridHelper(1200,24,0x8a949e,0x8a949e);
grid.material.opacity=.25; grid.material.transparent=true;
grid.rotation.x=Math.PI/2; grid.position.set(C.x,C.y,0); scene.add(grid);

const clipPlane=new THREE.Plane(new THREE.Vector3(0,-1,0), 1e5);
const root=new THREE.Group(); scene.add(root);
const items=[];

DATA.meshes.forEach(md=>{
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(b64f32(md.pos),3));
  g.setAttribute('normal',new THREE.BufferAttribute(b64f32(md.nrm),3));
  g.setIndex(new THREE.BufferAttribute(b64u32(md.idx),1));
  const mat=new THREE.MeshPhongMaterial({color:md.colour,shininess:18,
    specular:0x111418,flatShading:false,clippingPlanes:[clipPlane],
    side:THREE.DoubleSide});
  const mesh=new THREE.Mesh(g,mat);
  const eg=new THREE.LineSegments(new THREE.EdgesGeometry(g,32),
    new THREE.LineBasicMaterial({color:0x2b333c,transparent:true,opacity:.5}));
  eg.visible=false; mesh.add(eg);
  mesh.visible=md.on; root.add(mesh);
  g.computeBoundingBox();
  const ctr=new THREE.Vector3(); g.boundingBox.getCenter(ctr);
  items.push({md,mesh,eg,home:ctr.clone()});
});

// ---- panel
for(const kind of ['printed','hardware']){
  const host=document.getElementById(kind);
  items.filter(i=>i.md.kind===kind).forEach(i=>{
    const l=document.createElement('label');
    l.innerHTML=`<input type="checkbox" ${i.md.on?'checked':''}>
      <span class="sw" style="background:${i.md.colour}"></span>${i.md.name}`;
    l.querySelector('input').onchange=e=>{i.mesh.visible=e.target.checked;};
    host.appendChild(l);
  });
}

// ---- orbit (written by hand: no external controls script needed)
let dist=Math.max(D.W,D.D,D.H)*2.1, yaw=-0.62, pitch=0.42;
let target=C.clone(), dragging=null, lx=0, ly=0;
function place(){
  const cp=Math.cos(pitch), sp=Math.sin(pitch);
  camera.position.set(target.x+dist*cp*Math.sin(yaw),
                      target.y-dist*cp*Math.cos(yaw),
                      target.z+dist*sp);
  camera.up.set(0,0,1); camera.lookAt(target);
}
function onDown(e){dragging=e.shiftKey||e.button===2?'pan':'rot';lx=e.clientX;ly=e.clientY;}
function onMove(e){
  if(!dragging)return;
  const dx=e.clientX-lx, dy=e.clientY-ly; lx=e.clientX; ly=e.clientY;
  if(dragging==='rot'){
    yaw-=dx*0.0075;
    pitch=Math.max(-1.45,Math.min(1.45,pitch+dy*0.0075));
  }else{
    const s=dist*0.0016;
    const right=new THREE.Vector3(Math.cos(yaw),Math.sin(yaw),0);
    const up=new THREE.Vector3().crossVectors(right,
      camera.position.clone().sub(target).normalize()).normalize();
    target.addScaledVector(right,-dx*s).addScaledVector(up,-dy*s);
  }
  place();
}
addEventListener('pointerdown',e=>{if(e.target===cv)onDown(e);});
addEventListener('pointermove',onMove);
addEventListener('pointerup',()=>dragging=null);
cv.addEventListener('contextmenu',e=>e.preventDefault());
cv.addEventListener('wheel',e=>{e.preventDefault();
  dist=Math.max(60,Math.min(2600,dist*Math.pow(1.0016,e.deltaY)));place();},{passive:false});
let pinch=0;
cv.addEventListener('touchmove',e=>{
  if(e.touches.length===2){
    const d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,
                       e.touches[0].clientY-e.touches[1].clientY);
    if(pinch)dist=Math.max(60,Math.min(2600,dist*pinch/d));
    pinch=d; place(); e.preventDefault();
  }},{passive:false});
cv.addEventListener('touchend',()=>pinch=0);

const VIEWS={iso:[-0.62,0.42],front:[0,0.02],side:[-1.5708,0.02],
             top:[0,1.44],back:[3.1416,0.05]};
document.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>{
  [yaw,pitch]=VIEWS[b.dataset.v]; target=C.clone(); place();});

document.getElementById('explode').oninput=e=>{
  const t=e.target.value/100*90;
  items.forEach(i=>{
    const d=i.home.clone().sub(C).normalize();
    i.mesh.position.copy(d.multiplyScalar(t));
  });
};
document.getElementById('clip').oninput=e=>{
  const v=e.target.value/100;
  // keep everything with y <= constant; 1e5 disables the cut
  clipPlane.set(new THREE.Vector3(0,-1,0), v>=1 ? 1e5 : D.D*v);
};
document.getElementById('edges').onchange=e=>{
  items.forEach(i=>i.eg.visible=e.target.checked);};

const ui=document.getElementById('ui');
document.getElementById('toggle').onclick=()=>ui.classList.toggle('hidden');
// start collapsed on a phone, where the panel would cover the model
if(innerWidth<760) ui.classList.add('hidden');

const hud=document.getElementById('hud');
hud.innerHTML=`${D.W} x ${D.D} x ${D.H} mm &nbsp;|&nbsp; rake ${D.rake}&deg;<br>
  drag rotate &nbsp; wheel zoom &nbsp; shift-drag pan`;

function resize(){
  const w=innerWidth,h=innerHeight;
  renderer.setSize(w,h,false); camera.aspect=w/h; camera.updateProjectionMatrix();
}
addEventListener('resize',resize); resize(); place();
(function loop(){requestAnimationFrame(loop);renderer.render(scene,camera);})();
</script>
</body>
</html>
"""

out = "/mnt/user-data/outputs/lumon_viewer.html"
open(out, "w").write(HTML.replace("__DATA__", DATA))
import os
print("wrote", out, round(os.path.getsize(out) / 1e6, 2), "MB")
