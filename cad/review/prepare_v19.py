from pathlib import Path
root=Path(__file__).resolve().parents[2]
s=(root/'files/lumon_v18.py').read_text()
s=s.replace('LUMON_TERMINAL v5 - relief mark moulded into the wall','LUMON_TERMINAL v19 - prototype engineering review')
s=s.replace('OUT = Path("/home/claude/out_v18")','ROOT = Path(__file__).resolve().parents[1]\nOUT = ROOT / "cad/output/v19"')
s=s.replace('OUT.mkdir(exist_ok=True)','OUT.mkdir(parents=True, exist_ok=True)')
a=s.index('LOGO_FILE ='); z=s.index('\ndef skin_front',a)
s=s[:a]+'''# Recover the supplied artwork exactly from the archived v18 recess.\n# The small STEP is a reproducible extracted asset; no font/image retracing.\n_LOGO = import_step(Path(__file__).parent / "review/logo_v18.step")\nLOGO_SRC = "archived v18 recess"\ndef logo_solid(cx, y0, thickness):\n    local = Pos(-297.96, 0, -62.0) * _LOGO\n    return Pos(cx, y0, p.logo_zl) * scale(local, by=(1, thickness / 0.8, 1))\n\n''' +s[z:]
# Rebuild the sloping front edge rather than slicing a previously rounded upright corner.
a=s.index('    t = box_at(x0, 0, 0, x1 - x0, p.D, p.H)',s.index('def build_tub_left'))
z=s.index('    # cavity, open top',a)
s=s[:a]+'''    t = box_at(0, 0, p.skirt_h, x1, p.D, p.H-p.lid_t-p.skirt_h)\n    rear = [e for e in t.edges().filter_by(Axis.Z) if abs(e.center().X)<0.01 and e.center().Y>p.D-1]\n    t = fillet(rear, p.fillet_main)\n    t = t - front_solid(0.0)\n    front = [e for e in t.edges() if e.geom_type == GeomType.LINE\n             and abs(e.center().X)<0.01 and e.center().Y<45 and e.length>100]\n    if len(front) != 1: raise RuntimeError(f"front corner selection: {len(front)}")\n    t = fillet(front, 3.0)\n    t = t + base_step_left(p.band_inset, p.foot_h, p.band_h)\n\n''' +s[z:]
# Protect the inset base wall: leave full 3mm thickness below the step.
s=s.replace('    t = t - cav\n','    lower_keep = box_at(-30,-30,0,p.W+60,p.D+60,p.skirt_h) - (base_step_left(p.band_inset+p.wall,0,p.skirt_h) if x0 == 0 else base_step_right(p.band_inset+p.wall,0,p.skirt_h))\n    cav = cav - lower_keep\n    t = t - cav\n')
# Bezel fit: clearance around perimeter, not around viewing aperture.
s=s.replace('RectangleRounded(BEZ_W, BEZ_H, p.bezel_r), amount=p.bezel_t)', 'RectangleRounded(BEZ_W-2*p.fit_clear, BEZ_H-2*p.fit_clear, p.bezel_r-p.fit_clear), amount=p.bezel_t)')
# Move left service rebate out of the rounded rear corner; preserve its right edge.
s=s.replace('ow, oh = 120.0, 94.0','ow, oh = 112.0, 94.0').replace('ox, oz = p.wall + 15, 30.0','ox, oz = p.wall + 23, 30.0')
s=s.replace('_owL, _ohL = 120.0, 94.0','_owL, _ohL = 112.0, 94.0').replace('rear_panel(p.wall + 15, 30.0','rear_panel(p.wall + 23, 30.0')
# Remove the through-cut head recess from thin rear-panel skin. Use external pan heads.
s=s.replace('    pl = pl - cyl_y(sx, p.D - p.cbore_depth, sz, p.cbore_d, p.cbore_depth + 1)','    # External pan head: retain the complete 1.8mm bearing skin.')
# Replace nonexistent/buried magnet seats with connected screw lands.
s=s.replace('LID_MAGNETS = [(x0 + p.spine_wall + 4, 18.0), (x1 - p.wall - 4, 18.0),\n                   (x0 + p.spine_wall + 4, p.D - 18.0), (x1 - p.wall - 4, p.D - 18.0)]','LID_MAGNETS = [(x0 + p.spine_wall + 4, p.D - 18.0), (x1 - p.wall - 4, p.D - 18.0)]')
# Original pocket cuts have no value and can leave closed internal voids.
s=s.replace('    for (mx, my) in LID_MAGNETS_L:\n        t = t - cyl_z(mx, my, p.H - p.lid_t - p.magnet_h, p.magnet_d,\n                      p.magnet_h + 0.1)','')
s=s.replace('    for (mx, my) in LID_MAGNETS:\n        t = t - cyl_z(mx, my, p.H - p.lid_t - p.magnet_h, p.magnet_d, p.magnet_h + 0.1)','')
# Replace both foot insert loops, after all union operations, with connected bosses.
old='''    for fx in (28, x1 - 28):
        for fy in (28, p.D - 28):
            t = t - cyl_z(fx, fy, p.foot_h, p.insert_hole_d, p.insert_depth + 1)
    return t'''
new='''    for fx, fy in foot_mounts("left"):
        t = t + cyl_z(fx, fy, p.foot_h, 11, 12)
        t = t - cyl_z(fx, fy, p.foot_h-0.1, p.insert_hole_d, p.insert_depth+0.1)
    t = add_lid_lands(t, "left")
    return t'''
assert old in s;s=s.replace(old,new)
old='''    for fx in (x0 + 28, x1 - 28):
        for fy in (28, p.D - 28):
            t = t - cyl_z(fx, fy, p.foot_h, p.insert_hole_d, p.insert_depth + 1)
    return t'''
new='''    for fx, fy in foot_mounts("right"):
        t = t + cyl_z(fx, fy, p.foot_h, 11, 12)
        t = t - cyl_z(fx, fy, p.foot_h-0.1, p.insert_hole_d, p.insert_depth+0.1)
    t = add_lid_lands(t, "right")
    return t'''
assert old in s;s=s.replace(old,new)
pos=s.index('def build_tub_left():')
s=s[:pos]+'''def foot_mounts(side):
    xs = (55, p.x_split-28) if side == "left" else (p.x_split+28,p.W-28)
    return [(x,y) for x in xs for y in (20,p.D-9)]

def add_lid_lands(t, side):
    coords = LID_MAGNETS_L if side == "left" else LID_MAGNETS
    z = p.H-p.lid_t
    for x,y in coords:
        # Square lands overlap the existing side wall; bore opens on top.
        t = t + box_at(x-5.5,y-5.5,z-15,11,11,15)
    for x,y in coords:
        t = t - cyl_z(x,y,z-p.insert_depth,p.insert_hole_d,p.insert_depth+0.1)
    return t

''' +s[pos:]
a=s.index('    xs = ((28, p.x_split - 28)',s.index('def build_foot'))
z=s.index('    return f',a)
s=s[:a]+'''    for fx,fy in foot_mounts(side):
        f = f - cyl_z(fx,fy,-0.1,p.screw_clear_d,p.foot_h+0.2)
        f = f - cyl_z(fx,fy,-0.1,p.cbore_d,3.1)
    if side == "left":
        for i in range(6):
            x=p.psu_x+12+i*18
            f = f - box_at(x,p.psu_y+12,-0.1,4,p.psu_d-24,p.foot_h+0.2)
            # Underfoot channels open at the rear, even before pads are fitted.
            f = f - box_at(x,p.psu_y+12,-0.1,4,p.D-(p.psu_y+12)+1,2.1)
''' +s[z:]
# Expose hardware instead of guessing a paper slot and covering the controls.
a=s.index('    # paper exit and finger notch');z=s.index('    return lid',a)
s=s[:a]+'''    if slot:
        lid = lid - box_at(p.printer_x-p.printer_clear,
                           p.printer_front-p.printer_clear,z0-10,
                           p.printer_w+2*p.printer_clear,
                           p.printer_d+2*p.printer_clear,p.lid_t+20)
    for mx,my in (LID_MAGNETS if side == "right" else LID_MAGNETS_L):
        lid = lid - cyl_z(mx,my,z0-1,p.screw_clear_d,p.lid_t+3)
        lid = lid - cyl_z(mx,my,p.H-2,p.cbore_d,3)
''' +s[z:]
# Drop stale legacy validation text; independent audit produces the report.
s=s[:s.index('# ---------------------------------------------------------------- validation')]+'''# The independent release audit checks every exported body and pair.
LOGO_FILL = logo_solid((p.x_split+p.W)/2,0,p.logo_relief)
'''
s=s.replace('"printer_lid": PRINTER_LID','"printer_trim": PRINTER_LID')
(root/'cad/lumon_v19.py').write_text(s)
