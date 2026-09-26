"""Lumon v19: provisional mechanical review, derived from archived v18.

Hardware dimensions remain inherited and unverified. Generated reference
images guide color and overall appearance only. See README.md for assembly,
print orientation and release blockers. Regenerate using export_review.py.
"""

from dataclasses import dataclass, asdict, field
from pathlib import Path
import math
from build123d import *

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad/output/v19"
OUT.mkdir(parents=True, exist_ok=True)


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
    printer_sink: float = 6.5           # FORM   drop the printer below the top plate
    paper_slot_w: float = 86.0          # DESIGN 80 mm paper + margin
    paper_slot_d: float = 9.0           # DESIGN
    paper_slot_y: float = 45.0          # TBD    distance back from the printer's face
                                        #        to the centre of its lid slot

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
    rake_deg: float = 14.0              # FORM   DISPLAY MODULE ONLY. The printer
                                        #        block and the base stay upright,
                                        #        as in the reference render.
    fillet_main: float = 14.0           # FORM   soft vertical corners
    fillet_top_r: float = 12.0          # FORM   matches the vertical corners,
                                        #        so the front-top corner reads as
                                        #        one radius like the bezel's
    chamfer_bottom: float = 1.2         # DESIGN  bottom edge break
    bezel_chamfer: float = 1.2          # DESIGN  around the display window
    bezel_margin: float = 9.0          # FORM   dark surround around the panel
    bezel_t: float = 3.0                # FORM   surround thickness
    bezel_rebate: float = 1.0           # FORM   locating step into the face
    bezel_r: float = 14.0               # FORM   same radius as the body corners
    gap_w: float = 1.0                  # DESIGN  seam shadow gap, per module
    gap_d: float = 1.0                  # DESIGN
    # Base steps INWARD as it descends, as in the render: body, then a
    # slightly narrower light band, then a darker foot narrower again.
    foot_h: float = 9.0                 # FORM   dark plinth height
    foot_taper: float = 5.0             # FORM   chamfer at its lower edge
    foot_inset: float = 2.5             # FORM   dark plinth barely steps in;
                                        #        its taper does the shaping
    band_h: float = 24.0                # FORM   light base band height
    band_inset: float = 1.5             # FORM   how far the band steps in
    skirt_h: float = 24.0               # = foot_h + band_h (derived, kept for refs)
    skirt_out: float = 0.0              # FORM   nothing stands proud any more
    plinth_z: float = 17.0              # DESIGN  (unused when skirt_h is set)
    plinth_gap_h: float = 1.5           # DESIGN
    plinth_gap_d: float = 0.0           # superseded by the skirt
    # ID mark, formed directly in the raked wall
    logo_mode: str = "deboss"           # DESIGN  deboss | emboss | inlay
    logo_w: float = 58.0                # CHOSEN  option A
    drop_w: float = 16.0                # BRAND   droplet secondary mark
    drop_zl: float = 118.0              # DESIGN  on the display module, upper left
    logo_zl: float = 62.0               # DESIGN  CENTRE of the mark on the raked face
    logo_clear: float = 8.0             # DESIGN  keep-out around the mark
    logo_relief: float = 0.8            # DESIGN  2 perimeters at 0.4 nozzle
    logo_thicken: float = 0.2           # CHOSEN  option A: hairlines fattened to print
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
    plinth: float = 55.0                # FORM   height budget term (H = base+plinth+printer_h)
    rear_cavity: float = 25.0           # DESIGN  rear wiring corridor
    printer_front: float = 11.0         # DESIGN  the raked wall leans BACK as it
                                        #         rises, so the binding constraint
                                        #         is the wall at the TOP (28.4),
                                        #         not at the printer's base (6.9)
    spine_wall: float = 9.0             # DESIGN  right module left wall: inserts go INTO it
    top_flange: float = 15.0            # DESIGN  local wall thickening at the top rim
    top_flange_t: float = 3.0           # DESIGN
    lid_rebate: float = 3.0             # DESIGN  left service panel thickness
    lid_t: float = 16.0                 # FORM   printer lid: full-outline cover,
                                        #        carries the top fillet itself
    lid_rim: float = 4.5                # FORM   solid rim: only 5 mm exists between
                                        #        the outer face and the printer
    lid_skin: float = 3.5               # FORM   lid top skin
    lid_spigot: float = 5.0             # FORM   locating skirt into the cavity
    shadow_gap: float = 1.5             # DESIGN  expressed seam between modules

    # FASTENERS - M3 heat-set inserts throughout
    insert_hole_d: float = 4.2          # USER TEST PASSED: M3 insert in seam coupon
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
        self.W = (self.wall + self.bezel_margin + self.display_w
                  + 2 * self.display_clear + self.bezel_margin
                  + self.wall + self.spine_wall
                  + self.printer_w + 2 * self.printer_clear + self.wall)
        self.D = self.printer_front + self.printer_d + self.rear_cavity + self.wall
        self.H = self.base_thickness + self.plinth + self.printer_h - self.plinth \
                 + self.plinth   # = base + plinth + printer_h  (printer top flush)
        self.H = self.base_thickness + self.plinth + self.printer_h
        # seam plane between the two tub modules
        self.skirt_h = self.foot_h + self.band_h
        self.x_split = (self.wall + self.bezel_margin + self.display_w
                        + 2 * self.display_clear + self.bezel_margin + self.wall)

    # component placement (min corner)
    @property
    def display_x(self): return self.wall + self.bezel_margin + self.display_clear
    @property
    def display_z(self): return (self.H - self.display_h) / 2
    # ---- power bay placement (left module), min corner
    @property
    def psu_x(self): return self.x_split - self.wall - self.psu_clear - self.psu_w
    @property
    def psu_y(self): return self.D - self.wall - 13 - self.psu_d
    @property
    def psu_z(self): return self.foot_h + self.base_thickness
    @property
    def partition_x(self): return self.psu_x - 4 - self.partition_t
    @property
    def pi_plane_x(self):            # board plane, vertical, parallel to YZ
        return self.wall + 6 + self.partition_t + self.pi_standoff
    @property
    def pi_y(self): return self.D - self.wall - 8 - self.pi_d
    @property
    def pi_z(self): return self.foot_h + 30.0
    @property
    def iec_x(self): return (self.x_split - self.wall + 138.0) / 2   # fixed rear strip
    @property
    def iec_z(self): return 62.0

    @property
    def printer_x(self): return self.W - self.wall - self.printer_clear - self.printer_w
    @property
    def printer_z(self): return self.H - self.printer_h - self.printer_sink


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
# usable slant runs from the base block up to the underside of the lid
FACE_LEN = (p.H - p.lid_t - p.skirt_h) / CR
DZL = p.skirt_h + (FACE_LEN - p.display_h) / 2   # absolute z, pre-rotation


def raked(shape):
    """Tilt back about the top edge of the base block."""
    return (Pos(0, 0, p.skirt_h) * Rot(-p.rake_deg, 0, 0)
            * Pos(0, 0, -p.skirt_h)) * shape


def front_solid(t):
    """Half-space in front of the raked plane, above the base block only."""
    slab = raked(box_at(-5, -500.0, 0, p.W + 10, 500.0 + t, 500.0))
    return slab & box_at(-60, -500, p.skirt_h, p.W + 120, 700.0, p.H + 60)


# Recover the supplied artwork exactly from the archived v18 recess.
# The small STEP is a reproducible extracted asset; no font/image retracing.
_LOGO = import_step(Path(__file__).parent / "review/logo_v18.step")
LOGO_SRC = "archived v18 recess"
def logo_solid(cx, y0, thickness):
    local = Pos(-297.96, 0, -62.0) * _LOGO
    return Pos(cx, y0, p.logo_zl) * scale(local, by=(1, thickness / 0.8, 1))


def skin_front(band, depth):
    """The outer `depth` mm of the raked front wall, within `band`."""
    return (band & front_solid(depth)) - front_solid(0.0)


def y_front_inner(zw, t=None):
    """World y of the raked wall's inner face at world height zw.

    The rake pivots at the top of the base block, so the pivot height has to
    come out before converting into the tilted frame.
    """
    t = p.wall if t is None else t
    zl = (zw - p.skirt_h + t * SR) / CR
    return t * CR + zl * SR


# ------------------------------------------------- joint layout (shared data)
# spine screws: through LEFT module wall into inserts in RIGHT module bosses
SPINE_SCREWS = [(25, 22), (50, 118), (76, 70), (140, 45), (140, 118)]   # (y, z)
# (140, 45) sits above the PSU: it must be driven before the PSU goes in
SPINE_DOWELS = [(35, 118), (140, 70)]                                   # (y, z)
LID_SCREWS = None   # filled below
LID_SCREWS_L = None # filled below
REAR_SCREWS = None


# ============================================================ LEFT TUB MODULE
BEZ_W = p.display_w + 2 * p.display_clear + 2 * p.bezel_margin
BEZ_H = p.display_h + 2 * p.bezel_margin
BEZ_CX = p.display_x + p.display_w / 2
BEZ_CZ = DZL + p.display_h / 2


def plate_region(side, inset, z0, h, r):
    """Top-plate footprint: rounded on the three outer corners to follow the
    shell, square where it meets the other module."""
    if side == "left":
        x0, x1 = inset, p.x_split
    else:
        x0, x1 = p.x_split, p.W - inset
    w, d = x1 - x0, p.D - 2 * inset
    # extrude already spans 0..h, so the placement offset is z0, not z0+h/2
    reg = (Pos((x0 + x1) / 2, p.D / 2, z0)
           * extrude(RectangleRounded(w, d, r), amount=h))
    sq = (box_at(x1 - r, inset, z0, r, d, h) if side == "left"
          else box_at(x0, inset, z0, r, d, h))
    return reg + sq


CAVITY_R = []
REAR_PANEL_T = 1.8          # flush skin thickness sitting in a rebate


def base_step_left(inset, z0, h):
    """Left module outline, inset on its three outer faces, flush at the seam."""
    b = box_at(inset, inset, z0, p.x_split - inset, p.D - 2 * inset, h)
    return fillet(b.edges().filter_by(Axis.Z).group_by(Axis.X)[0],
                  max(1.0, p.fillet_main - inset))


def base_step_right(inset, z0, h):
    b = box_at(p.x_split, inset, z0, p.W - p.x_split - inset, p.D - 2 * inset, h)
    return fillet(b.edges().filter_by(Axis.Z).group_by(Axis.X)[-1],
                  max(1.0, p.fillet_main - inset))


def foot_mounts(side):
    xs = (55, p.x_split-28) if side == "left" else (p.x_split+28,p.W-28)
    return [(x,y) for x in xs for y in (20,p.D-9)]

def add_lid_lands(t, side):
    coords = LID_SCREWS_L if side == "left" else LID_SCREWS
    z = p.H-p.lid_t
    for x,y in coords:
        # Square lands overlap the existing side wall; bore opens on top.
        t = t + box_at(x-5.5,y-5.5,z-15,11,11,15)
    for x,y in coords:
        t = t - cyl_z(x,y,z-p.insert_depth,p.insert_hole_d,p.insert_depth+0.1)
    return t

def build_tub_left():
    x0, x1 = 0.0, p.x_split
    t = box_at(0, 0, p.skirt_h, x1, p.D, p.H-p.lid_t-p.skirt_h)
    rear = [e for e in t.edges().filter_by(Axis.Z) if abs(e.center().X)<0.01 and e.center().Y>p.D-1]
    t = fillet(rear, p.fillet_main)
    t = t - front_solid(0.0)
    front = [e for e in t.edges() if e.geom_type == GeomType.LINE
             and abs(e.center().X)<0.01 and e.center().Y<45 and e.length>100]
    if len(front) != 1: raise RuntimeError(f"front corner selection: {len(front)}")
    t = fillet(front, 3.0)
    t = t + base_step_left(p.band_inset, p.foot_h, p.band_h)

    # cavity, open top, front bounded by the raked wall
    cav = box_at(p.wall, p.wall, p.foot_h + p.base_thickness,
                 x1 - 2 * p.wall, p.D - 2 * p.wall, p.H)
    # the outer corners are filleted; the cavity must be too, or the wall
    # thins to zero at the tangent point and prints as a slit
    cav = fillet(cav.edges().filter_by(Axis.Z).group_by(Axis.X)[0],
                 p.fillet_main - p.wall)
    cav = cav - front_solid(p.wall)
    lower_keep = box_at(-30,-30,0,p.W+60,p.D+60,p.skirt_h) - (base_step_left(p.band_inset+p.wall,0,p.skirt_h) if x0 == 0 else base_step_right(p.band_inset+p.wall,0,p.skirt_h))
    cav = cav - lower_keep
    t = t - cav

    # display window through the raked front wall
    t = t - raked(box_at(p.display_x + p.bezel_overlap, -5.0,
                         DZL + p.bezel_overlap,
                         p.display_w - 2 * p.bezel_overlap, 5.0 + p.wall + 1,
                         p.display_h - 2 * p.bezel_overlap))

    # locating rebate for the dark display surround
    t = t - raked(Pos(BEZ_CX, -0.01, BEZ_CZ) * Rot(-90, 0, 0)
                  * extrude(RectangleRounded(BEZ_W, BEZ_H, p.bezel_r),
                            amount=p.bezel_rebate + 0.02))

    # chamfer around the display window, on the raked plane
    ww = p.display_w - 2 * p.bezel_overlap
    wh = p.display_h - 2 * p.bezel_overlap
    bc = p.bezel_chamfer
    outer = raked(box_at(p.display_x + p.bezel_overlap - bc, -0.01,
                         DZL + p.bezel_overlap - bc,
                         ww + 2 * bc, bc, wh + 2 * bc))
    inner = raked(box_at(p.display_x + p.bezel_overlap, -0.01,
                         DZL + p.bezel_overlap, ww, bc, wh))
    t = t - (outer - inner)

    # seam shadow gap: half the groove on this module, half on the other
    t = t - skin_front(box_at(p.x_split - p.gap_w, -10, p.skirt_h,
                              p.gap_w, p.D + 20, p.H), p.gap_d)
    t = t - box_at(p.x_split - p.gap_w, -0.01, 0, p.gap_w, p.gap_d, p.skirt_h)
    t = t - box_at(p.x_split - p.gap_w, -10, p.H - p.gap_d,
                   p.gap_w, p.D + 20, p.gap_d + 1)

    # plinth parting line, front and outer side
    if p.plinth_gap_d > 0:
        pass
        t = t - box_at(-0.01, -10, p.plinth_z, p.plinth_gap_d,
                       p.D + 20, p.plinth_gap_h)

    # Screw-land centers; connected lands are added after the cavity cuts.
    global LID_SCREWS_L
    LID_SCREWS_L = [(p.wall + 4, 46.0), (x1 - p.wall - 4, 46.0),
                     (p.wall + 4, p.D - 18.0), (x1 - p.wall - 4, p.D - 18.0)]


    # top flange - local wall thickening under the rebate (stiffness).
    # Front flange lives on the raked plane and starts above the display.
    zl_lo = DZL + p.display_h + 1.5
    zl_hi = (p.H - p.lid_t - p.lid_spigot - 1.0 + p.wall * SR) / CR
    if zl_hi - zl_lo > 2.0:      # only if the panel leaves room for one
        t = t + raked(box_at(p.wall, p.wall, zl_lo,
                             x1 - 2 * p.wall, p.top_flange_t, zl_hi - zl_lo))
    fz = p.H - p.lid_t - p.lid_spigot - p.top_flange
    for bx, by, bw, bd in [
        (p.wall, p.D - p.wall - p.top_flange_t, x1 - 2 * p.wall, p.top_flange_t),
        (p.wall, p.wall, p.top_flange_t, p.D - 2 * p.wall),
        (x1 - p.wall - p.top_flange_t, p.wall, p.top_flange_t, p.D - 2 * p.wall),
    ]:
        blk = box_at(bx, by, fz, bw, bd, p.H - p.lid_t - p.lid_spigot - fz)
        blk = blk - front_solid(p.wall + p.display_t + 6)
        t = t + blk

    # display retention: side ribs + retainer bosses, all on the raked plane
    for rx in (p.display_x - 3.0, p.display_x + p.display_w + p.display_clear):
        t = t + raked(box_at(rx, p.wall, DZL - 4,
                             3.0, p.display_t - 0.5, p.display_h + 8))
    global RETAINER_BOSSES
    RETAINER_BOSSES = [(sx, zl)
                       for sx in (p.display_x + 40, p.display_x + p.display_w - 40)
                       for zl in (DZL - 8, DZL + p.display_h + 5.5)]
    for sx, zl in RETAINER_BOSSES:
        t = t + raked(cyl_y(sx, p.wall, zl, p.boss_d, p.display_t))
        t = t - raked(cyl_y(sx, p.wall + p.display_t - p.insert_depth, zl,
                            p.insert_hole_d, p.insert_depth))

    # spine joint: clearance holes + counterbores through the right wall
    for (jy, jz) in SPINE_SCREWS:
        t = t - cyl_x(x1 - p.wall - 1, jy, jz, p.screw_clear_d, p.wall + 2)
        # External head inside the left bay: preserve the full 3mm wall.
    for (jy, jz) in SPINE_DOWELS:
        t = t - cyl_x(x1 - p.wall - 1, jy, jz,
                      p.dowel_d + 2 * p.dowel_fit, p.wall + 2)

    # top plate bosses - front pair sits behind the raked wall
    global TOPPLATE_SCREWS_L
    # the raked display sweeps back as it rises, so the front pair of top
    # plate bosses has to sit behind its top rear edge
    # rear service opening + panel bosses. The right-hand strip of the rear
    # wall is fixed and carries the mains inlet, so mains wiring never crosses
    # the removable panel.
    ow, oh = 112.0, 94.0
    ox, oz = p.wall + 23, 30.0
    t = t - box_at(ox, p.D - p.wall - 1, oz, ow, p.wall + 2, oh)
    t = t - box_at(ox - 10 - p.fit_clear, p.D - REAR_PANEL_T,
                   oz - 10 - p.fit_clear, ow + 20 + 2 * p.fit_clear,
                   REAR_PANEL_T + 1, oh + 20 + 2 * p.fit_clear)
    global REAR_SCREWS
    # inboard of the corner radius: a boss out at the corner leaves the
    # outer wall under 2 mm there
    REAR_SCREWS = [(ox + 16, oz - 8), (ox + ow - 16, oz - 8),
                   (ox + 16, oz + oh + 8), (ox + ow - 16, oz + oh + 8)]
    for (sx, sz) in REAR_SCREWS:
        t = t + cyl_y(sx, p.D - p.wall - 10, sz, p.boss_d, 10)
        t = t - cyl_y(sx, p.D - p.wall - p.insert_depth, sz,
                      p.insert_hole_d, p.insert_depth)

    # ---------------------------------------------------------- POWER BAY
    t = t + box_at(p.partition_x, 40.0, p.foot_h + p.base_thickness,
                   p.partition_t, p.D - p.wall - 40.0, p.psu_h + 16)

    # PSU corner blocks, each clipped to the space actually available
    gap_r = (p.x_split - p.wall) - (p.psu_x + p.psu_w)
    gap_b = (p.D - p.wall) - (p.psu_y + p.psu_d)
    for bx, bw in ((p.psu_x - 12, 12.0), (p.psu_x + p.psu_w, gap_r)):
        for by, bd in ((p.psu_y - 6, 6.0), (p.psu_y + p.psu_d, gap_b)):
            t = t + box_at(bx, p.psu_y + 2, p.foot_h + p.base_thickness, bw, 14.0, p.psu_h - 6)
            t = t + box_at(p.psu_x, by, p.foot_h + p.base_thickness, 14.0, bd, p.psu_h - 6)

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
        t = t - box_at(p.psu_x + 12 + i * 18, p.psu_y + 12, p.foot_h - 1,
                       4.0, p.psu_d - 24, p.base_thickness + 2)
    # exhaust: stacked horizontal rules, the motif used on Lumon print
    for i in range(5):
        t = t - box_at(30, p.D - p.wall - 1, 120.0 + i * 4.0,
                       p.x_split - 60, p.wall + 2, 2.0)

    for fx, fy in foot_mounts("left"):
        t = t + cyl_z(fx, fy, p.foot_h, 11, 12)
        t = t - cyl_z(fx, fy, p.foot_h-0.1, p.insert_hole_d, p.insert_depth+0.1)
    t = add_lid_lands(t, "left")
    return t


# =========================================================== RIGHT TUB MODULE
def build_tub_right():
    x0, x1 = p.x_split, p.W
    t = box_at(x0, 0, 0, x1 - x0, p.D, p.H)
    t = fillet(t.edges().filter_by(Axis.Z).group_by(Axis.X)[-1], p.fillet_main)
    # the lid carries the top edge, so the tub stops below it with straight
    # walls - that is what makes the closed joint a single continuous surface
    t = t - box_at(x0 - 30, -30, p.H - p.lid_t, x1 - x0 + 60, p.D + 60, 60.0)

    t = t - (box_at(x0 - 30, -30, p.foot_h, x1 - x0 + 60, p.D + 60, p.band_h)
             - base_step_right(p.band_inset, p.foot_h, p.band_h))
    t = t - box_at(x0 - 30, -30, -30, x1 - x0 + 60, p.D + 60, 30 + p.foot_h)

    # same raked plane as the display module: one continuous front face,
    # no step at the seam. The printer is set back so the wall clears its
    # bottom front edge, which is the tightest point.
    cav = box_at(x0 + p.spine_wall, p.wall, p.foot_h + p.base_thickness,
                 x1 - x0 - p.spine_wall - p.wall, p.D - 2 * p.wall, p.H)
    cav = fillet(cav.edges().filter_by(Axis.Z).group_by(Axis.X)[-1],
                 p.fillet_main - p.wall)
    lower_keep = box_at(-30,-30,0,p.W+60,p.D+60,p.skirt_h) - (base_step_left(p.band_inset+p.wall,0,p.skirt_h) if x0 == 0 else base_step_right(p.band_inset+p.wall,0,p.skirt_h))
    cav = cav - lower_keep
    t = t - cav
    CAVITY_R.append(cav)

    # seam shadow gap and plinth line, matching the display module
    t = t - box_at(p.x_split, -0.01, 0, p.gap_w, p.gap_d, p.H)
    t = t - box_at(p.x_split, -10, p.H - p.gap_d, p.gap_w, p.D + 20, p.gap_d + 1)
    if p.plinth_gap_d > 0:
        t = t - skin_front(box_at(p.x_split - 10, -10, p.plinth_z,
                                  p.W - p.x_split + 20, p.D + 20, p.plinth_gap_h),
                           p.plinth_gap_d)
        t = t - box_at(p.W - p.plinth_gap_d, -10, p.plinth_z, p.plinth_gap_d + 0.01,
                       p.D + 20, p.plinth_gap_h)

    # printer well: open to the top face, no inward overhang
    well = box_at(p.printer_x - p.printer_clear,
                  p.printer_front - p.printer_clear,
                  p.printer_z - 1,
                  p.printer_w + 2 * p.printer_clear,
                  p.printer_d + 2 * p.printer_clear,
                  p.printer_h + 2)
    t = t - (well & CAVITY_R[0])

    # Screw-land centers; connected lands are added after the cavity cuts.
    global LID_SCREWS
    LID_SCREWS = [(x0 + p.spine_wall + 4, p.D - 18.0), (x1 - p.wall - 4, p.D - 18.0)]


    # top flange: rear and right walls, stopping under the cover plate
    fz = p.H - p.lid_t - p.lid_spigot - p.top_flange   # clear of the lid skirt
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
        t = t + blk

    # printer riser rails
    riser_h = p.printer_z - (p.foot_h + p.base_thickness)
    for rx in (p.printer_x + 12, p.printer_x + p.printer_w - 34):
        t = t + box_at(rx, p.printer_front + 10, p.foot_h + p.base_thickness,
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
    ox, oz = x0 + (x1 - x0 - ow) / 2, p.foot_h + p.base_thickness + 15
    t = t - box_at(ox, p.D - p.wall - 1, oz, ow, p.wall + 2, oh)
    t = t - box_at(ox - 10 - p.fit_clear, p.D - REAR_PANEL_T,
                   oz - 10 - p.fit_clear, ow + 20 + 2 * p.fit_clear,
                   REAR_PANEL_T + 1, oh + 20 + 2 * p.fit_clear)
    for (sx, sz) in [(ox + 16, oz - 8), (ox + ow - 16, oz - 8),
                     (ox + 16, oz + oh + 8), (ox + ow - 16, oz + oh + 8)]:
        t = t + cyl_y(sx, p.D - p.wall - 10, sz, p.boss_d, 10)
        t = t - cyl_y(sx, p.D - p.wall - p.insert_depth, sz,
                      p.insert_hole_d, p.insert_depth)

    for fx, fy in foot_mounts("right"):
        t = t + cyl_z(fx, fy, p.foot_h, 11, 12)
        t = t - cyl_z(fx, fy, p.foot_h-0.1, p.insert_hole_d, p.insert_depth+0.1)
    t = add_lid_lands(t, "right")
    return t


TUB_LEFT = build_tub_left()
TUB_RIGHT = build_tub_right()


# ==================================================== TOP PLATE (left module)
def build_foot(side):
    """Dark foot under each module: narrowest element, sets the object down."""
    f = (base_step_left if side == "left" else base_step_right)(
        p.foot_inset, 0.0, p.foot_h)
    try:
        f = chamfer([e for e in f.edges().group_by(Axis.Z)[0]
                     if abs(e.center().X-p.x_split)>0.01], p.foot_taper)
    except Exception:
        try:
            f = chamfer([e for e in f.edges().group_by(Axis.Z)[0]
                         if abs(e.center().X-p.x_split)>0.01], p.chamfer_bottom)
        except Exception:
            pass
    for fx,fy in foot_mounts(side):
        f = f - cyl_z(fx,fy,-0.1,p.screw_clear_d,p.foot_h+0.2)
        f = f - cyl_z(fx,fy,-0.1,p.cbore_d,3.1)
    if side == "left":
        for i in range(6):
            x=p.psu_x+12+i*18
            f = f - box_at(x,p.psu_y+12,-0.1,4,p.psu_d-24,p.foot_h+0.2)
            # Underfoot channels open at the rear, even before pads are fitted.
            f = f - box_at(x,p.psu_y+12,-0.1,4,p.D-(p.psu_y+12)+1,2.1)
    return f


FOOT_LEFT = build_foot("left")
FOOT_RIGHT = build_foot("right")


def build_lid(side, slot=False):
    """Full-outline lid: its own outer wall and top fillet continue the shell,
    so closed it reads as one surface with a single parting line low on the
    wall. A rebated panel cannot work here - a 12 mm top fillet on a 3 mm
    wall leaves no ledge for it to rest on."""
    z0 = p.H - p.lid_t
    rim = p.lid_rim if side == "right" else 6.0
    lid = plate_region(side, 0.0, z0, p.lid_t, p.fillet_main)
    if side == "left":
        # plate_region is a plain rectangle in plan; on the display module the
        # front face is raked, so trim the lid to it or it juts out over the
        # screen like a visor
        lid = lid - front_solid(0.0)
    try:
        lid = fillet(lid.edges().group_by(Axis.Z)[-1], p.fillet_top_r)
    except Exception:
        pass
    # hollow the underside, leaving a rim and a top skin
    hollow = plate_region(side, rim, z0 - 0.1,
                          p.lid_t - p.lid_skin + 0.1,
                          max(1.0, p.fillet_main - rim))
    # keep a rim at the seam too, so the lid seats on the spine wall
    hollow = (hollow & box_at(p.x_split + rim, -60, z0 - 60, p.W, p.D + 120, p.H + 120)
              if side == "right"
              else (hollow & box_at(-60, -60, z0 - 60, p.x_split - rim + 60,
                                    p.D + 120, p.H + 120)) - front_solid(rim))
    lid = lid - hollow
    # locating skirt dropping into the cavity
    # locating skirt on the front and rear only: on the right side the
    # printer sits 2 mm inside the wall and leaves no room for one
    o = p.wall + p.fit_clear
    if side == "right":
        sx0 = p.x_split + p.spine_wall + p.fit_clear
        sx1 = p.W - p.wall - p.fillet_main
    else:
        sx0 = p.wall + p.fillet_main
        sx1 = p.x_split - p.wall - p.fit_clear
    # on the display module the front edge is raked, so no front skirt there
    sys_ = (o, p.D - o - 2.4) if side == "right" else (p.D - o - 2.4,)
    for sy in sys_:
        lid = lid + box_at(sx0, sy, z0 - p.lid_spigot, sx1 - sx0, 2.4, p.lid_spigot)
    if slot:
        lid = lid - box_at(p.printer_x-p.printer_clear,
                           p.printer_front-p.printer_clear,z0-10,
                           p.printer_w+2*p.printer_clear,
                           p.printer_d+2*p.printer_clear,p.lid_t+20)
    for mx,my in (LID_SCREWS if side == "right" else LID_SCREWS_L):
        # Compression sleeve carries screw load down to the tub land rather
        # than bending the thin cover skin across an empty cavity.
        lid = lid + cyl_z(mx,my,z0,8.0,p.lid_t-p.lid_skin+0.5)
        lid = lid - cyl_z(mx,my,z0-1,p.screw_clear_d,p.lid_t+3)
        lid = lid - cyl_z(mx,my,p.H-2,p.cbore_d,3)
    return lid


PRINTER_LID = build_lid("right", slot=True)
TOP_PLATE_LEFT = build_lid("left")
TOP_PLATE_RIGHT = PRINTER_LID


# ======================================================== DISPLAY RETAINER
def build_display_bezel():
    """Dark surround that frames the panel, as in the reference render."""
    plate = (Pos(BEZ_CX, p.bezel_rebate - p.bezel_t, BEZ_CZ) * Rot(-90, 0, 0)
             * extrude(RectangleRounded(BEZ_W-2*p.fit_clear, BEZ_H-2*p.fit_clear, p.bezel_r-p.fit_clear), amount=p.bezel_t))
    win = box_at(p.display_x + p.bezel_overlap, -p.bezel_t - 1,
                 DZL + p.bezel_overlap,
                 p.display_w - 2 * p.bezel_overlap, p.bezel_t + 3,
                 p.display_h - 2 * p.bezel_overlap)
    return raked(plate - win)


DISPLAY_BEZEL = build_display_bezel()


def build_retainer():
    ow = p.display_w + 2 * p.display_clear - 2 * p.fit_clear
    ox = p.display_x - p.display_clear + p.fit_clear
    zl0 = DZL - 8 - 6
    zl1 = DZL + p.display_h + 5.5 + 6
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
    pl = box_at(ox - 10, p.D - REAR_PANEL_T, oz - 10, ow + 20,
                REAR_PANEL_T, oh + 20)
    # rebate plug so the panel locates in the opening
    pl = pl + box_at(ox + p.fit_clear, p.D - p.wall, oz + p.fit_clear,
                     ow - 2 * p.fit_clear, p.wall - REAR_PANEL_T + 0.2,
                     oh - 2 * p.fit_clear)
    for (sx, sz) in screws:
        pl = pl - cyl_y(sx, p.D - REAR_PANEL_T - 1, sz, p.screw_clear_d,
                        REAR_PANEL_T + 2)
        # External pan head: retain the complete 1.8mm bearing skin.
    return pl


_owL, _ohL = 112.0, 94.0
REAR_PANEL_LEFT = rear_panel(p.wall + 23, 30.0, _owL, _ohL, REAR_SCREWS)

_owR, _ohR = 90.0, 70.0
_oxR = p.x_split + (p.W - p.x_split - _owR) / 2
_ozR = p.foot_h + p.base_thickness + 15
REAR_PANEL_RIGHT = rear_panel(_oxR, _ozR, _owR, _ohR,
                              [(_oxR + 16, _ozR - 8), (_oxR + _owR - 16, _ozR - 8),
                               (_oxR + 16, _ozR + _ohR + 8),
                               (_oxR + _owR - 16, _ozR + _ohR + 8)])

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
BUCK_REFERENCE = box_at(p.wall + 7, 30.0, p.foot_h + p.base_thickness,
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
    "printer_trim": PRINTER_LID,
    "display_retainer": DISPLAY_RETAINER,
    "rear_panel_left": REAR_PANEL_LEFT,
    "rear_panel_right": REAR_PANEL_RIGHT,
    "foot_left": FOOT_LEFT,
    "foot_right": FOOT_RIGHT,
    "display_bezel": DISPLAY_BEZEL,
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


# The independent release audit checks every exported body and pair.
LOGO_FILL = logo_solid((p.x_split+p.W)/2,0,p.logo_relief)
