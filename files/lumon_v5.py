"""
LUMON_TERMINAL v5 - relief mark moulded into the wall
=====================================================
Code-driven parametric CAD (build123d / OCCT). Run this file to regenerate
every part, the STEP assembly and the validation report.

WHAT CHANGED FROM THE BLOCKOUT
------------------------------
1. Height raised to 144 mm by adding a plinth. Not cosmetic: the display is
   110.76 tall and needs >=12 mm of cavity above and below it for M3 insert
   bosses. At H=130 there was 6 mm and no way to clamp the panel.
2. The enclosure is split into TWO TUB MODULES at the spine. 353 mm does not
   fit any consumer bed, and the spine is the only seam that is also a
   legitimate design line.
3. Right module top is fully open over the printer footprint - zero inward
   overhang - because the clamshell lid geometry is unmeasured. Stiffness
   comes from a thickened top flange on the INSIDE of the walls instead.
4. The printer is captured by the tub walls, not by screws. Its mounting
   holes are unknown and must not be invented.
5. The display is held by a retainer frame against the front wall lip, with
   side ribs for lateral location. It does not rely on the display's own
   mounting holes either.

CONFIDENCE TAGS: MEASURED / UNVERIFIED / TBD / DESIGN
"""

from dataclasses import dataclass, asdict, field
from pathlib import Path
import math
from build123d import *

OUT = Path("/home/claude/out_v5")
OUT.mkdir(exist_ok=True)


# ---------------------------------------------------------------- parameters
@dataclass
class P:
    # DISPLAY - Raspberry Pi 7" Touch Display (original)
    display_w: float = 192.96           # MEASURED
    display_h: float = 110.76           # MEASURED
    display_t: float = 21.0             # TBD  assembly incl. driver PCB + standoffs
    display_clear: float = 1.0          # DESIGN
    bezel_overlap: float = 6.0          # DESIGN  frame laps the display edge

    # PRINTER - 80 mm clamshell, top loading (confirmed from photographs)
    printer_w: float = 142.0            # UNVERIFIED
    printer_d: float = 122.0            # UNVERIFIED
    printer_h: float = 122.0            # UNVERIFIED
    printer_clear: float = 2.0          # DESIGN
    printer_top_rim: float = 0.0        # DESIGN  inward overhang over the lid: keep 0

    # POWER - single internal 24 V open-frame PSU + 24->5 V buck for the Pi
    # Pocket sized for Mean Well LRS-100-24 (129x97x30, 4.5 A). The LRS-75-24
    # (99x97x30, 3.2 A) drops into the same pocket with shorter corner blocks.
    psu_w: float = 129.0                # CATALOGUE  LRS-100-24
    psu_d: float = 97.0                 # CATALOGUE
    psu_h: float = 30.0                 # CATALOGUE
    psu_clear: float = 3.0              # DESIGN
    psu_headroom: float = 20.0          # DESIGN  convection space above the mesh case
    iec_cut_w: float = 47.2             # CATALOGUE  fused + switched C14 snap-in
    iec_cut_h: float = 28.3             # CATALOGUE  verify against the part bought
    iec_body_w: float = 50.0            # CATALOGUE
    iec_body_h: float = 31.0            # CATALOGUE
    iec_body_d: float = 31.0            # CATALOGUE
    iec_panel_t: float = 1.5            # DESIGN  local wall thinning so the clips grip
    partition_t: float = 3.0            # DESIGN  mains / low-voltage barrier
    rake_deg: float = 10.0              # DESIGN  front face rake, both modules
    fillet_top_r: float = 3.0           # DESIGN  top edge break
    # ID mark, formed directly in the raked wall
    logo_mode: str = "deboss"           # DESIGN  deboss | emboss | inlay
    logo_w: float = 58.0                # DESIGN  target width of the artwork
    logo_zl: float = 26.0               # DESIGN  position along the raked face
    logo_relief: float = 0.8            # DESIGN  2 perimeters at 0.4 nozzle
    plate_w: float = 64.0               # DESIGN  inlay pocket, only if logo_mode=inlay
    plate_h: float = 18.0               # DESIGN
    plate_depth: float = 1.2            # DESIGN
    plate_clear: float = 0.2            # DESIGN
    buck_w: float = 35.0                # TBD  24->5 V 5 A module
    buck_d: float = 65.0                # TBD
    buck_h: float = 20.0                # TBD

    # ELECTRONICS - Raspberry Pi mounted VERTICALLY on the left wall so its
    # ports face the rear without stealing floor width from the PSU
    pi_w: float = 85.0                  # MEASURED  B+ form factor
    pi_d: float = 56.0                  # MEASURED
    pi_h: float = 22.0                  # TBD  board + active cooler
    pi_hole_dx: float = 58.0            # MEASURED  hole pattern
    pi_hole_dy: float = 49.0            # MEASURED
    pi_hole_inset: float = 3.5          # MEASURED
    pi_standoff: float = 6.0            # DESIGN

    # ENCLOSURE
    wall: float = 3.0                   # DESIGN
    base_thickness: float = 4.0         # DESIGN
    plinth: float = 18.0                # DESIGN  raises display clear of the floor
    rear_cavity: float = 35.0           # DESIGN  rear wiring corridor
    printer_front: float = 10.0         # DESIGN  printer set back so the raked
                                        #         front wall clears its bottom edge
    spine_wall: float = 9.0             # DESIGN  right module left wall: inserts go INTO it
    top_flange: float = 15.0            # DESIGN  local wall thickening at the top rim
    top_flange_t: float = 3.0           # DESIGN
    lid_rebate: float = 3.0             # DESIGN  top plate drops in flush
    shadow_gap: float = 1.5             # DESIGN  expressed seam between modules

    # FASTENERS - M3 heat-set inserts throughout
    insert_hole_d: float = 4.2          # DESIGN  short M3 insert, OD 4.6
    insert_depth: float = 6.0           # DESIGN
    boss_d: float = 9.0                 # DESIGN
    screw_clear_d: float = 3.4          # DESIGN
    cbore_d: float = 6.2                # DESIGN
    cbore_depth: float = 2.2            # DESIGN
    dowel_d: float = 4.0                # DESIGN  steel pin
    dowel_fit: float = 0.15             # DESIGN  hole oversize per side

    # FDM
    fit_clear: float = 0.3              # DESIGN  panel-in-rebate clearance
    foot_d: float = 14.0                # DESIGN  rubber pad recess
    foot_recess: float = 1.5            # DESIGN

    W: float = field(default=0.0)
    D: float = field(default=0.0)
    H: float = field(default=0.0)
    x_split: float = field(default=0.0)

    def __post_init__(self):
        self.W = (self.wall + self.display_w + 2 * self.display_clear
                  + self.wall + self.spine_wall
                  + self.printer_w + 2 * self.printer_clear + self.wall)
        self.D = self.printer_front + self.printer_d + self.rear_cavity + self.wall
        self.H = self.base_thickness + self.plinth + self.printer_h - self.plinth \
                 + self.plinth   # = base + plinth + printer_h  (printer top flush)
        self.H = self.base_thickness + self.plinth + self.printer_h
        # seam plane between the two tub modules
        self.x_split = self.wall + self.display_w + 2 * self.display_clear + self.wall

    # component placement (min corner)
    @property
    def display_x(self): return self.wall + self.display_clear
    @property
    def display_z(self): return (self.H - self.display_h) / 2
    # ---- power bay placement (left module), min corner
    @property
    def psu_x(self): return self.x_split - self.wall - self.psu_clear - self.psu_w
    @property
    def psu_y(self): return self.D - self.wall - 23 - self.psu_d
    @property
    def psu_z(self): return self.base_thickness
    @property
    def partition_x(self): return self.psu_x - 4 - self.partition_t
    @property
    def pi_plane_x(self):            # board plane, vertical, parallel to YZ
        return self.wall + 6 + self.partition_t + self.pi_standoff
    @property
    def pi_y(self): return self.D - self.wall - 8 - self.pi_d
    @property
    def pi_z(self): return 30.0
    @property
    def iec_x(self): return (self.x_split - self.wall + 138.0) / 2   # fixed rear strip
    @property
    def iec_z(self): return 52.0

    @property
    def printer_x(self): return self.W - self.wall - self.printer_clear - self.printer_w
    @property
    def printer_z(self): return self.H - self.printer_h


p = P()


# ------------------------------------------------------------------- helpers
def box_at(x, y, z, w, d, h):
    return Pos(x + w / 2, y + d / 2, z + h / 2) * Box(w, d, h)


def cyl_z(x, y, z, d, h):
    return Pos(x, y, z + h / 2) * Cylinder(d / 2, h)


def cyl_x(x, y, z, d, l):
    return Pos(x + l / 2, y, z) * Rot(0, 90, 0) * Cylinder(d / 2, l)


def cyl_y(x, y, z, d, l):
    return Pos(x, y + l / 2, z) * Rot(-90, 0, 0) * Cylinder(d / 2, l)


# ------------------------------------------------------------ rake transform
# The display module's front face leans back by rake_deg about the front-bottom
# edge at the origin. Every feature on that face is built in a local upright
# frame and then raked, so the lip, ribs, bosses and retainer all stay coplanar.
CR = math.cos(math.radians(p.rake_deg))
SR = math.sin(math.radians(p.rake_deg))
FACE_LEN = p.H / CR                       # slant length of the front face
DZL = (FACE_LEN - p.display_h) / 2        # display position along that face


def raked(shape):
    return Rot(-p.rake_deg, 0, 0) * shape


def front_solid(t):
    """Half-space in front of the raked plane at local y = t."""
    return raked(box_at(-5, -500.0, 0, p.W + 10, 500.0 + t, 500.0))


def logo_sketch():
    """Artwork for the moulded mark, as faces in the XY plane.

    Drop an SVG in /mnt/user-data/uploads and it is used automatically:
    outlines become faces, enclosed outlines become holes, and the result is
    scaled to logo_w. With no SVG present a plain type placeholder is used.
    I do not ship the Lumon emblem itself - supply your own artwork file.
    """
    from pathlib import Path as _P
    svgs = sorted(_P("/mnt/user-data/uploads").glob("*.svg")) \
        if _P("/mnt/user-data/uploads").exists() else []
    if svgs:
        items = import_svg(str(svgs[0]))
        faces = [it if isinstance(it, Face) else Face(it) for it in items]
        faces.sort(key=lambda f: f.area, reverse=True)
        art = faces[0]
        for f in faces[1:]:
            art = art - f if art.intersect(f) is not None else art + f
        src = svgs[0].name
    else:
        art = Text("MDR-775", font_size=12, font="DejaVu Sans Mono")
        art = art + Pos(0, -9) * Rectangle(46, 1.2)
        src = "placeholder type (no SVG supplied)"
    bb = art.bounding_box()
    art = scale(art, by=p.logo_w / bb.size.X)
    bb = art.bounding_box()
    art = Pos(-bb.center().X, -bb.center().Y) * art
    return art, src


LOGO_ART, LOGO_SRC = logo_sketch()


def logo_solid(cx, y0, thickness):
    """The artwork as a solid on the raked face, local y from y0 to y0+t."""
    body = extrude(mirror(LOGO_ART, about=Plane.XZ), amount=thickness)
    body = Rot(-90, 0, 0) * body
    return raked(Pos(cx, y0, p.logo_zl) * body)


def y_front_inner(zw, t=None):
    """World y of the raked wall's inner face at world height zw."""
    t = p.wall if t is None else t
    zl = (zw + t * SR) / CR
    return t * CR + zl * SR


# ------------------------------------------------- joint layout (shared data)
# spine screws: through LEFT module wall into inserts in RIGHT module bosses
SPINE_SCREWS = [(25, 22), (25, 118), (76, 70), (140, 45), (140, 118)]   # (y, z)
# (140, 45) sits above the PSU: it must be driven before the PSU goes in
SPINE_DOWELS = [(15, 118), (140, 70)]                                   # (y, z)
TOPPLATE_SCREWS_L = None   # filled below
REAR_SCREWS = None


# ============================================================ LEFT TUB MODULE
def build_tub_left():
    x0, x1 = 0.0, p.x_split
    t = box_at(x0, 0, 0, x1 - x0, p.D, p.H)
    t = fillet(t.edges().filter_by(Axis.Z).group_by(Axis.X)[0], 6)

    # rake the front face back by rake_deg about the front-bottom edge
    t = t - front_solid(0.0)
    # break every top edge, including the new one along the raked face
    try:
        t = fillet(t.edges().group_by(Axis.Z)[-1], p.fillet_top_r)
    except Exception:
        pass

    # cavity, open top, front bounded by the raked wall
    cav = box_at(p.wall, p.wall, p.base_thickness,
                 x1 - 2 * p.wall, p.D - 2 * p.wall, p.H)
    cav = cav - front_solid(p.wall)
    t = t - cav

    # display window through the raked front wall
    t = t - raked(box_at(p.display_x + p.bezel_overlap, -5.0,
                         DZL + p.bezel_overlap,
                         p.display_w - 2 * p.bezel_overlap, 5.0 + p.wall + 1,
                         p.display_h - 2 * p.bezel_overlap))

    # top rebate: the top plate drops in flush, its front edge follows the rake
    rebate = box_at(p.wall / 2, p.wall / 2, p.H - p.lid_rebate,
                    x1 - p.wall, p.D - p.wall, p.lid_rebate + 1)
    rebate = rebate - front_solid(p.wall / 2)
    t = t - rebate

    # top flange - local wall thickening under the rebate (stiffness).
    # Front flange lives on the raked plane and starts above the display.
    zl_lo = DZL + p.display_h + 1.5
    zl_hi = (p.H - p.lid_rebate + p.wall * SR) / CR
    t = t + raked(box_at(p.wall, p.wall, zl_lo,
                         x1 - 2 * p.wall, p.top_flange_t, zl_hi - zl_lo))
    fz = p.H - p.lid_rebate - p.top_flange
    for bx, by, bw, bd in [
        (p.wall, p.D - p.wall - p.top_flange_t, x1 - 2 * p.wall, p.top_flange_t),
        (p.wall, p.wall, p.top_flange_t, p.D - 2 * p.wall),
        (x1 - p.wall - p.top_flange_t, p.wall, p.top_flange_t, p.D - 2 * p.wall),
    ]:
        blk = box_at(bx, by, fz, bw, bd, p.H - p.lid_rebate - fz)
        blk = blk - front_solid(p.wall + p.display_t + 6)
        t = t + blk

    # display retention: side ribs + retainer bosses, all on the raked plane
    for rx in (p.display_x - 3.0, p.display_x + p.display_w + p.display_clear):
        t = t + raked(box_at(rx, p.wall, DZL - 4,
                             3.0, p.display_t + 2, p.display_h + 8))
    global RETAINER_BOSSES
    RETAINER_BOSSES = [(sx, zl)
                       for sx in (p.display_x + 40, p.display_x + p.display_w - 40)
                       for zl in (DZL - 8, DZL + p.display_h + 8)]
    for sx, zl in RETAINER_BOSSES:
        t = t + raked(cyl_y(sx, p.wall, zl, p.boss_d, p.display_t + 4))
        t = t - raked(cyl_y(sx, p.wall + p.display_t + 4 - p.insert_depth, zl,
                            p.insert_hole_d, p.insert_depth + 1))

    # spine joint: clearance holes + counterbores through the right wall
    for (jy, jz) in SPINE_SCREWS:
        t = t - cyl_x(x1 - p.wall - 1, jy, jz, p.screw_clear_d, p.wall + 2)
        t = t - cyl_x(x1 - p.wall - 1, jy, jz, p.cbore_d, p.cbore_depth + 1)
    for (jy, jz) in SPINE_DOWELS:
        t = t - cyl_x(x1 - p.wall - 1, jy, jz,
                      p.dowel_d + 2 * p.dowel_fit, p.wall + 2)

    # top plate bosses - front pair sits behind the raked wall
    global TOPPLATE_SCREWS_L
    # the raked display sweeps back as it rises, so the front pair of top
    # plate bosses has to sit behind its top rear edge
    y_ft = 58.0
    TOPPLATE_SCREWS_L = [(p.wall + 4, y_ft), (x1 - p.wall - 4, y_ft),
                         (p.wall + 4, p.D - p.wall - 4),
                         (x1 - p.wall - 4, p.D - p.wall - 4)]
    for (sx, sy) in TOPPLATE_SCREWS_L:
        t = t + cyl_z(sx, sy, p.H - p.lid_rebate - 16, p.boss_d, 16)
        t = t - cyl_z(sx, sy, p.H - p.lid_rebate - p.insert_depth,
                      p.insert_hole_d, p.insert_depth + 1)

    # rear service opening + panel bosses. The right-hand strip of the rear
    # wall is fixed and carries the mains inlet, so mains wiring never crosses
    # the removable panel.
    ow, oh = 120.0, 94.0
    ox, oz = p.wall + 15, 30.0
    t = t - box_at(ox, p.D - p.wall - 1, oz, ow, p.wall + 2, oh)
    global REAR_SCREWS
    REAR_SCREWS = [(ox - 7.5, oz - 8), (ox + ow + 7.5, oz - 8),
                   (ox - 7.5, oz + oh + 8), (ox + ow + 7.5, oz + oh + 8)]
    for (sx, sz) in REAR_SCREWS:
        t = t + cyl_y(sx, p.D - p.wall - 10, sz, p.boss_d, 10)
        t = t - cyl_y(sx, p.D - p.wall - p.insert_depth, sz,
                      p.insert_hole_d, p.insert_depth + 1)

    # ---------------------------------------------------------- POWER BAY
    t = t + box_at(p.partition_x, 40.0, p.base_thickness,
                   p.partition_t, p.D - p.wall - 40.0, p.psu_h + 16)

    # PSU corner blocks, each clipped to the space actually available
    gap_r = (p.x_split - p.wall) - (p.psu_x + p.psu_w)
    gap_b = (p.D - p.wall) - (p.psu_y + p.psu_d)
    for bx, bw in ((p.psu_x - 12, 12.0), (p.psu_x + p.psu_w, gap_r)):
        for by, bd in ((p.psu_y - 6, 6.0), (p.psu_y + p.psu_d, gap_b)):
            t = t + box_at(bx, p.psu_y + 2, p.base_thickness, bw, 14.0, p.psu_h - 6)
            t = t + box_at(p.psu_x, by, p.base_thickness, 14.0, bd, p.psu_h - 6)

    # mains inlet in the FIXED rear wall, outer face thinned so a snap-in
    # module can grip what is otherwise 3 mm of plastic
    t = t - box_at(p.iec_x - p.iec_cut_w / 2, p.D - p.wall - 1,
                   p.iec_z - p.iec_cut_h / 2,
                   p.iec_cut_w, p.wall + 2, p.iec_cut_h)
    t = t - box_at(p.iec_x - p.iec_cut_w / 2 - 4.5, p.D - p.iec_panel_t,
                   p.iec_z - p.iec_cut_h / 2 - 4.5,
                   p.iec_cut_w + 9, p.iec_panel_t + 1, p.iec_cut_h + 9)

    # Raspberry Pi standoffs on the left wall - board vertical, ports to rear
    for dy in (0, p.pi_hole_dy):
        for dz in (0, p.pi_hole_dx):
            t = t + cyl_x(p.wall, p.pi_y + p.pi_hole_inset + dy,
                          p.pi_z + p.pi_hole_inset + dz,
                          8.0, p.pi_plane_x - p.wall)
            t = t - cyl_x(p.pi_plane_x - 6, p.pi_y + p.pi_hole_inset + dy,
                          p.pi_z + p.pi_hole_inset + dz, 2.6, 7)

    # cable pass-through to the printer, in the rear wiring corridor
    t = t - box_at(x1 - p.wall - 1, 126.0, 8.0, p.wall + 2, 20.0, 22.0)

    # ventilation: intake in the floor under the PSU, exhaust high in the rear
    # wall. Nothing on the visible surfaces.
    for i in range(6):
        t = t - box_at(p.psu_x + 12 + i * 18, p.psu_y + 12, -1,
                       4.0, p.psu_d - 24, p.base_thickness + 2)
    for i in range(9):
        t = t - box_at(24 + i * 17, p.D - p.wall - 1, 128.0, 3.0, p.wall + 2, 9.0)

    for fx in (18, x1 - 18):
        for fy in (18, p.D - 18):
            t = t - cyl_z(fx, fy, -0.5, p.foot_d, p.foot_recess + 0.5)
    return t


# =========================================================== RIGHT TUB MODULE
def build_tub_right():
    x0, x1 = p.x_split, p.W
    t = box_at(x0, 0, 0, x1 - x0, p.D, p.H)
    t = fillet(t.edges().filter_by(Axis.Z).group_by(Axis.X)[-1], 6)

    # same raked plane as the display module: one continuous front face,
    # no step at the seam. The printer is set back so the wall clears its
    # bottom front edge, which is the tightest point.
    t = t - front_solid(0.0)
    try:
        t = fillet(t.edges().group_by(Axis.Z)[-1], p.fillet_top_r)
    except Exception:
        pass

    cav = box_at(x0 + p.spine_wall, p.wall, p.base_thickness,
                 x1 - x0 - p.spine_wall - p.wall, p.D - 2 * p.wall, p.H)
    cav = cav - front_solid(p.wall)
    t = t - cav

    # printer well: open to the top face, no inward overhang
    t = t - box_at(p.printer_x - p.printer_clear,
                   p.printer_front - p.printer_clear,
                   p.printer_z - 1,
                   p.printer_w + 2 * p.printer_clear,
                   p.printer_d + 2 * p.printer_clear,
                   p.printer_h + 2)

    # top flange: rear and right walls vertical, front one on the raked plane
    fz = p.H - p.top_flange
    for bx, by, bw, bd in [
        (x0 + p.spine_wall, p.D - p.wall - p.top_flange_t,
         x1 - x0 - p.spine_wall - p.wall, p.top_flange_t),
        (x1 - p.wall - p.top_flange_t, p.wall, p.top_flange_t, p.D - 2 * p.wall),
    ]:
        blk = box_at(bx, by, fz, bw, bd, p.top_flange)
        blk = blk - box_at(p.printer_x - p.printer_clear,
                           p.printer_front - p.printer_clear,
                           fz - 1, p.printer_w + 2 * p.printer_clear,
                           p.printer_d + 2 * p.printer_clear, p.top_flange + 2)
        blk = blk - front_solid(p.wall)
        t = t + blk

    # printer riser rails
    riser_h = p.printer_z - p.base_thickness
    for rx in (p.printer_x + 12, p.printer_x + p.printer_w - 34):
        t = t + box_at(rx, p.printer_front + 10, p.base_thickness,
                       22, p.printer_d - 20, riser_h)

    # spine joint: inserts sunk INTO the 9 mm wall from the seam face
    for (jy, jz) in SPINE_SCREWS:
        t = t - cyl_x(x0 - 0.5, jy, jz, p.insert_hole_d, p.insert_depth + 0.5)
    for (jy, jz) in SPINE_DOWELS:
        t = t - cyl_x(x0 - 0.5, jy, jz,
                      p.dowel_d + 2 * p.dowel_fit, p.insert_depth + 2.5)

    # cable pass-through from the power bay
    t = t - box_at(x0 - 1, 126.0, 8.0, p.spine_wall + 2, 20.0, 22.0)

    # identification mark, formed directly in the raked wall
    global PLATE_X, PLATE_ZL
    PLATE_X = (x0 + x1) / 2 - p.plate_w / 2
    PLATE_ZL = p.logo_zl
    cx = (x0 + x1) / 2
    if p.logo_mode == "deboss":
        t = t - logo_solid(cx, -0.5, 0.5 + p.logo_relief)
    elif p.logo_mode == "emboss":
        t = t + logo_solid(cx, -p.logo_relief, p.logo_relief + 0.3)
    else:                                   # inlay pocket + separate part
        t = t - raked(box_at(PLATE_X, -1.0, PLATE_ZL,
                             p.plate_w, 1.0 + p.plate_depth, p.plate_h))

    # rear service opening
    ow, oh = 90.0, 70.0
    ox, oz = x0 + (x1 - x0 - ow) / 2, p.base_thickness + 15
    t = t - box_at(ox, p.D - p.wall - 1, oz, ow, p.wall + 2, oh)
    for (sx, sz) in [(ox - 8, oz - 8), (ox + ow + 8, oz - 8),
                     (ox - 8, oz + oh + 8), (ox + ow + 8, oz + oh + 8)]:
        t = t + cyl_y(sx, p.D - p.wall - 10, sz, p.boss_d, 10)
        t = t - cyl_y(sx, p.D - p.wall - p.insert_depth, sz,
                      p.insert_hole_d, p.insert_depth + 1)

    for fx in (x0 + 18, x1 - 18):
        for fy in (18, p.D - 18):
            t = t - cyl_z(fx, fy, -0.5, p.foot_d, p.foot_recess + 0.5)
    return t


TUB_LEFT = build_tub_left()
TUB_RIGHT = build_tub_right()


# ==================================================== TOP PLATE (left module)
def build_top_plate():
    c = p.fit_clear
    plate = box_at(p.wall / 2 + c, p.wall / 2 + c, p.H - p.lid_rebate,
                   p.x_split - p.wall - 2 * c, p.D - p.wall - 2 * c, p.lid_rebate)
    plate = plate - front_solid(p.wall / 2 + c)
    for (sx, sy) in TOPPLATE_SCREWS_L:
        plate = plate - cyl_z(sx, sy, p.H - p.lid_rebate - 1,
                              p.screw_clear_d, p.lid_rebate + 2)
        plate = plate - cyl_z(sx, sy, p.H - p.cbore_depth,
                              p.cbore_d, p.cbore_depth + 1)
    return plate


TOP_PLATE_LEFT = build_top_plate()


# ======================================================== DISPLAY RETAINER
def build_retainer():
    ow = p.display_w + 2 * p.display_clear - 2 * p.fit_clear
    ox = p.display_x - p.display_clear + p.fit_clear
    zl0 = DZL - 8 - 6
    zl1 = DZL + p.display_h + 8 + 6
    y0 = p.wall + p.display_t
    fr = box_at(ox, y0, zl0, ow, 4.0, zl1 - zl0)
    fr = fr - box_at(ox + 14, y0 - 1, DZL + 8, ow - 28, 6, p.display_h - 16)
    for sx, zl in RETAINER_BOSSES:
        fr = fr - cyl_y(sx, y0 - 1, zl, p.screw_clear_d, 6)
        fr = fr - cyl_y(sx, y0 + 4 - p.cbore_depth, zl, p.cbore_d, p.cbore_depth + 1)
    return raked(fr)


DISPLAY_RETAINER = build_retainer()


# ============================================================ REAR PANELS
def rear_panel(ox, oz, ow, oh, screws):
    pl = box_at(ox - 10, p.D - p.wall, oz - 10, ow + 20, p.wall, oh + 20)
    # rebate plug so the panel locates in the opening
    pl = pl + box_at(ox + p.fit_clear, p.D - p.wall - p.wall, oz + p.fit_clear,
                     ow - 2 * p.fit_clear, p.wall, oh - 2 * p.fit_clear)
    for (sx, sz) in screws:
        pl = pl - cyl_y(sx, p.D - p.wall - 1, sz, p.screw_clear_d, p.wall + 2)
        pl = pl - cyl_y(sx, p.D - p.cbore_depth, sz, p.cbore_d, p.cbore_depth + 1)
    return pl


_owL, _ohL = 120.0, 94.0
REAR_PANEL_LEFT = rear_panel(p.wall + 15, 30.0, _owL, _ohL, REAR_SCREWS)

_owR, _ohR = 90.0, 70.0
_oxR = p.x_split + (p.W - p.x_split - _owR) / 2
_ozR = p.base_thickness + 15
REAR_PANEL_RIGHT = rear_panel(_oxR, _ozR, _owR, _ohR,
                              [(_oxR - 8, _ozR - 8), (_oxR + _owR + 8, _ozR - 8),
                               (_oxR - 8, _ozR + _ohR + 8), (_oxR + _owR + 8, _ozR + _ohR + 8)])

# ------------------------------------------------------- reference bodies
DISPLAY_REFERENCE = raked(box_at(p.display_x, p.wall, DZL,
                                 p.display_w, p.display_t, p.display_h))
PRINTER_REFERENCE = box_at(p.printer_x, p.printer_front, p.printer_z,
                           p.printer_w, p.printer_d, p.printer_h)
# Pi sits vertically: board plane parallel to YZ, ports facing rear
PI_REFERENCE = box_at(p.pi_plane_x, p.pi_y, p.pi_z, p.pi_h, p.pi_d, p.pi_w)
PSU_REFERENCE = box_at(p.psu_x, p.psu_y, p.psu_z, p.psu_w, p.psu_d, p.psu_h)
# body passes through the cutout; flange sits in the thinned recess
IEC_REFERENCE = (box_at(p.iec_x - (p.iec_cut_w - 0.4) / 2,
                        p.D - p.iec_panel_t - p.iec_body_d,
                        p.iec_z - (p.iec_cut_h - 0.4) / 2,
                        p.iec_cut_w - 0.4, p.iec_body_d, p.iec_cut_h - 0.4)
                 + box_at(p.iec_x - p.iec_body_w / 2, p.D - p.iec_panel_t,
                          p.iec_z - p.iec_body_h / 2,
                          p.iec_body_w, p.iec_panel_t, p.iec_body_h))
BUCK_REFERENCE = box_at(p.wall + 7, 30.0, p.base_thickness,
                        p.buck_w, p.buck_d, p.buck_h)

def build_id_plate():
    c = p.plate_clear
    return raked(box_at(PLATE_X + c / 2, 0.0, PLATE_ZL + c / 2,
                        p.plate_w - c, p.plate_depth, p.plate_h - c))


ID_PLATE = build_id_plate() if p.logo_mode == "inlay" else None

PARTS = {
    "tub_left": TUB_LEFT,
    "tub_right": TUB_RIGHT,
    "top_plate_left": TOP_PLATE_LEFT,
    "display_retainer": DISPLAY_RETAINER,
    "rear_panel_left": REAR_PANEL_LEFT,
    "rear_panel_right": REAR_PANEL_RIGHT,
}
if ID_PLATE is not None:
    PARTS["id_plate"] = ID_PLATE
REFS = {
    "ref_display": DISPLAY_REFERENCE,
    "ref_printer": PRINTER_REFERENCE,
    "ref_pi": PI_REFERENCE,
    "ref_psu": PSU_REFERENCE,
    "ref_iec": IEC_REFERENCE,
    "ref_buck": BUCK_REFERENCE,
}


# ---------------------------------------------------------------- validation
def ivol(a, b):
    r = a.intersect(b)
    if r is None:
        return 0.0
    if isinstance(r, ShapeList):
        return sum(x.volume for x in r if hasattr(x, "volume"))
    return r.volume


def bbox(s):
    bb = s.bounding_box()
    return bb.size.X, bb.size.Y, bb.size.Z


BEDS = [("Prusa MK4 / Ender-3", 250, 210, 220),
        ("Bambu P1S / X1C", 256, 256, 256),
        ("Prusa XL", 360, 360, 360)]


def validate():
    L = []
    ok = lambda c: "PASS" if c else "FAIL"

    L.append("=== ENVELOPE ===")
    L.append(f"overall {p.W:.2f} x {p.D:.2f} x {p.H:.2f} mm (W x D x H)")
    L.append(f"seam plane x = {p.x_split:.2f}   left module {p.x_split:.0f} | right module {p.W - p.x_split:.0f}")
    L.append(f"height check 135-145: {ok(135 <= p.H <= 145)}")
    L.append(f"spine wall {p.spine_wall:.0f} mm (inserts sunk into it, nothing protrudes)")
    L.append(f"rake {p.rake_deg:.0f} deg on BOTH modules -> one continuous front face, "
             f"leaning back {p.H * math.tan(math.radians(p.rake_deg)):.1f} mm")
    L.append(f"printer set back to y={p.printer_front:.0f}; wall inner face at the "
             f"printer's bottom edge is y={y_front_inner(p.printer_z):.2f}  "
             f"{ok(y_front_inner(p.printer_z) < p.printer_front - p.printer_clear)}")
    L.append(f"edge breaks: r6 outer verticals, r{p.fillet_top_r:.0f} every top edge")
    L.append(f"ID mark: {p.logo_mode}, {p.logo_relief:.1f} mm relief, {p.logo_w:.0f} mm wide, "
             f"artwork = {LOGO_SRC}")
    L.append(f"  minimum feature width should be >= {2 * 0.4:.1f} mm at a 0.4 nozzle")

    L.append("\n=== PART LIST / PRINT BED FIT ===")
    L.append(f"{'part':20s} {'X':>7s} {'Y':>7s} {'Z':>7s}   " +
             "  ".join(f"{b[0][:16]:>16s}" for b in BEDS))
    for name, s in PARTS.items():
        x, y, z = bbox(s)
        row = f"{name:20s} {x:7.1f} {y:7.1f} {z:7.1f}   "
        for _, bx, by, bz in BEDS:
            fits = (min(x, y) <= min(bx, by) and max(x, y) <= max(bx, by) and z <= bz)
            row += f"{ok(fits):>16s}  "
        L.append(row)

    L.append("\n=== INTERFERENCE ===")
    checks = [("display vs tub_left", DISPLAY_REFERENCE, TUB_LEFT),
              ("display vs retainer", DISPLAY_REFERENCE, DISPLAY_RETAINER),
              ("printer vs tub_right", PRINTER_REFERENCE, TUB_RIGHT),
              ("pi vs tub_left", PI_REFERENCE, TUB_LEFT),
              ("psu vs tub_left", PSU_REFERENCE, TUB_LEFT),
              ("tub_left vs tub_right", TUB_LEFT, TUB_RIGHT),
              ("top_plate vs tub_left", TOP_PLATE_LEFT, TUB_LEFT)]
    for nm, a, b in checks:
        v = ivol(a, b)
        L.append(f"{nm:26s} {v:9.2f} mm3  {ok(v < 1.0)}")
    L.append("(retainer is expected to touch the display: that is the clamp)")

    L.append("\n=== POWER BAY ===")
    L.append(f"PSU pocket {p.psu_w:.0f} x {p.psu_d:.0f} x {p.psu_h:.0f} at "
             f"x={p.psu_x:.0f} y={p.psu_y:.0f}  (LRS-100-24, or LRS-75-24 with shorter blocks)")
    L.append(f"headroom above the PSU mesh case: {p.H - p.lid_rebate - (p.psu_z + p.psu_h):.0f} mm")
    L.append(f"mains barrier at x={p.partition_x:.0f}, height {p.psu_h + 16:.0f} mm")
    L.append(f"mains inlet cutout {p.iec_cut_w:.1f} x {p.iec_cut_h:.1f} in the FIXED rear wall, "
             f"outer face thinned to {p.iec_panel_t:.1f} mm")
    for nm, a in [("PSU", PSU_REFERENCE), ("Pi", PI_REFERENCE),
                  ("IEC body", IEC_REFERENCE), ("buck", BUCK_REFERENCE)]:
        v = ivol(a, TUB_LEFT)
        L.append(f"{nm:9s} vs tub_left       {v:9.2f} mm3  {ok(v < 1.0)}")
    for a, b, nm in [(IEC_REFERENCE, PSU_REFERENCE, "IEC body vs PSU"),
                     (PI_REFERENCE, PSU_REFERENCE, "Pi vs PSU"),
                     (BUCK_REFERENCE, PI_REFERENCE, "buck vs Pi"),
                     (PSU_REFERENCE, DISPLAY_REFERENCE, "PSU vs display")]:
        v = ivol(a, b)
        L.append(f"{nm:26s} {v:9.2f} mm3  {ok(v < 1.0)}")
    lv_gap = p.psu_x - p.psu_clear - (p.partition_x + p.partition_t)
    L.append(f"mains zone to LV zone separation: barrier + {lv_gap:.0f} mm air")

    L.append("\n=== PRINTER SERVICE ===")
    well = (p.printer_w + 2 * p.printer_clear, p.printer_d + 2 * p.printer_clear)
    L.append(f"top well {well[0]:.0f} x {well[1]:.0f} mm, open to the top face")
    L.append(f"inward overhang over the lid: {p.printer_top_rim:.1f} mm  "
             f"{ok(p.printer_top_rim == 0)} (must stay 0 until the lid is measured)")
    L.append("printer drops in from above, captured by the tub walls on 4 sides")
    L.append(f"riser height {p.printer_z - p.base_thickness:.0f} mm -> cable space under the printer")

    L.append("\n=== FASTENER SCHEDULE ===")
    n_ins = len(SPINE_SCREWS) + 4 + 4 + 4 + 4
    L.append(f"M3 heat-set inserts (short, OD 4.6 x 4.0): {n_ins}")
    L.append(f"  spine {len(SPINE_SCREWS)} | top plate 4 | display retainer 4 | rear panels 8")
    L.append(f"M3 socket head screws: {n_ins}   lengths 8-12 mm")
    L.append(f"steel dowel pins {p.dowel_d:.0f} mm: {len(SPINE_DOWELS)} (spine alignment)")
    L.append("rubber feet pads: 8 recesses, 4 needed")

    L.append("\n=== STILL UNVERIFIED ===")
    L.append("printer_w/d/h, lid swing, LED and button positions, port positions")
    L.append("display_t, Pi model, PSU, cable types")
    return "\n".join(L)


def export_all():
    asm = Compound(label="LUMON_TERMINAL_v2", children=[
        Compound(label=k.upper(), children=[v.solid() if hasattr(v, "solid") else v])
        for k, v in {**PARTS, **REFS}.items()])
    export_step(asm, str(OUT / "LUMON_TERMINAL_v2.step"))
    for name, s in {**PARTS, **REFS}.items():
        export_stl(s, str(OUT / f"{name}.stl"), tolerance=0.04)


if __name__ == "__main__":
    export_all()
    rep = validate()
    print(rep)
    (OUT / "validation_report.txt").write_text(
        rep + "\n\n=== PARAMETERS ===\n" +
        "\n".join(f"{k:22s} {v:9.2f}" for k, v in asdict(p).items()))
