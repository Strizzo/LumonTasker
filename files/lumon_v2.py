"""
LUMON_TERMINAL v2 - split, joints and mounting
==============================================
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
from build123d import *

OUT = Path("/home/claude/out_v2")
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

    # ELECTRONICS placeholders
    pi_w: float = 85.0                  # TBD
    pi_d: float = 56.0                  # TBD
    pi_h: float = 30.0                  # TBD
    psu_w: float = 100.0                # TBD
    psu_d: float = 55.0                 # TBD
    psu_h: float = 35.0                 # TBD

    # ENCLOSURE
    wall: float = 3.0                   # DESIGN
    base_thickness: float = 4.0         # DESIGN
    plinth: float = 18.0                # DESIGN  raises display clear of the floor
    rear_cavity: float = 25.0           # DESIGN
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
        self.D = self.wall + self.printer_d + self.rear_cavity + self.wall
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


# ------------------------------------------------- joint layout (shared data)
# spine screws: through LEFT module wall into inserts in RIGHT module bosses
SPINE_SCREWS = [(25, 22), (25, 118), (76, 70), (140, 22), (140, 118)]   # (y, z)
SPINE_DOWELS = [(15, 118), (140, 70)]                                   # (y, z)
TOPPLATE_SCREWS_L = None   # filled below
REAR_SCREWS = None


# ============================================================ LEFT TUB MODULE
def build_tub_left():
    x0, x1 = 0.0, p.x_split
    t = box_at(x0, 0, 0, x1 - x0, p.D, p.H)
    t = fillet(t.edges().filter_by(Axis.Z).group_by(Axis.X)[0], 6)

    # cavity, open top
    cav = box_at(p.wall, p.wall, p.base_thickness,
                 x1 - 2 * p.wall, p.D - 2 * p.wall, p.H)
    t = t - cav

    # display window through the front wall
    t = t - box_at(p.display_x + p.bezel_overlap, -1,
                   p.display_z + p.bezel_overlap,
                   p.display_w - 2 * p.bezel_overlap, p.wall + 2,
                   p.display_h - 2 * p.bezel_overlap)

    # top rebate: the top plate drops in flush
    t = t - box_at(p.wall / 2, p.wall / 2, p.H - p.lid_rebate,
                   x1 - p.wall, p.D - p.wall, p.lid_rebate + 1)

    # top flange - local wall thickening under the rebate (stiffness).
    # It must start ABOVE the display, or it clamps the panel's top edge.
    fz = max(p.H - p.lid_rebate - p.top_flange,
             p.display_z + p.display_h + 1.5)
    fh = p.H - p.lid_rebate - fz
    for bx, by, bw, bd in [
        (p.wall, p.wall, x1 - 2 * p.wall, p.top_flange_t),                    # front
        (p.wall, p.D - p.wall - p.top_flange_t, x1 - 2 * p.wall, p.top_flange_t),
        (p.wall, p.wall, p.top_flange_t, p.D - 2 * p.wall),                   # left
        (x1 - p.wall - p.top_flange_t, p.wall, p.top_flange_t, p.D - 2 * p.wall),
    ]:
        t = t + box_at(bx, by, fz, bw, bd, fh)

    # display retention: side ribs + retainer bosses on the inner front wall
    for rx in (p.display_x - 3.0, p.display_x + p.display_w + p.display_clear):
        t = t + box_at(rx, p.wall, p.display_z - 4,
                       3.0, p.display_t + 2, p.display_h + 8)
    bosses = []
    for sx in (p.display_x + 40, p.display_x + p.display_w - 40):
        for sz in (p.base_thickness + 5, p.H - p.lid_rebate - 5):
            bosses.append((sx, sz))
    for sx, sz in bosses:
        t = t + cyl_y(sx, p.wall, sz, p.boss_d, p.display_t + 4)
        t = t - cyl_y(sx, p.wall + p.display_t + 4 - p.insert_depth, sz,
                      p.insert_hole_d, p.insert_depth + 1)

    # spine joint: clearance holes + counterbores through the right wall
    for (jy, jz) in SPINE_SCREWS:
        t = t - cyl_x(x1 - p.wall - 1, jy, jz, p.screw_clear_d, p.wall + 2)
        t = t - cyl_x(x1 - p.wall - 1, jy, jz, p.cbore_d, p.cbore_depth + 1)
    for (jy, jz) in SPINE_DOWELS:
        t = t - cyl_x(x1 - p.wall - 1, jy, jz,
                      p.dowel_d + 2 * p.dowel_fit, p.wall + 2)

    # top plate bosses
    global TOPPLATE_SCREWS_L
    # corner bosses must touch the walls, otherwise they print as islands
    TOPPLATE_SCREWS_L = [(p.wall + 4, p.wall + 4),
                         (x1 - p.wall - 4, p.wall + 4),
                         (p.wall + 4, p.D - p.wall - 4),
                         (x1 - p.wall - 4, p.D - p.wall - 4)]
    bz = max(p.H - p.lid_rebate - 14, p.display_z + p.display_h + 1)
    for (sx, sy) in TOPPLATE_SCREWS_L:
        t = t + cyl_z(sx, sy, bz, p.boss_d, p.H - p.lid_rebate - bz)
        t = t - cyl_z(sx, sy, p.H - p.lid_rebate - p.insert_depth,
                      p.insert_hole_d, p.insert_depth + 1)

    # rear service opening + panel bosses
    ow, oh = x1 - 2 * p.wall - 30, p.H - p.base_thickness - 40
    ox, oz = p.wall + 15, p.base_thickness + 20
    t = t - box_at(ox, p.D - p.wall - 1, oz, ow, p.wall + 2, oh)
    global REAR_SCREWS
    REAR_SCREWS = [(ox - 7.5, oz - 8), (ox + ow + 7.5, oz - 8),
                   (ox - 7.5, oz + oh + 8), (ox + ow + 7.5, oz + oh + 8)]
    for (sx, sz) in REAR_SCREWS:
        t = t + cyl_y(sx, p.D - p.wall - 10, sz, p.boss_d, 10)
        t = t - cyl_y(sx, p.D - p.wall - p.insert_depth, sz,
                      p.insert_hole_d, p.insert_depth + 1)

    # feet recesses
    for fx in (18, x1 - 18):
        for fy in (18, p.D - 18):
            t = t - cyl_z(fx, fy, -0.5, p.foot_d, p.foot_recess + 0.5)
    return t


# =========================================================== RIGHT TUB MODULE
def build_tub_right():
    x0, x1 = p.x_split, p.W
    t = box_at(x0, 0, 0, x1 - x0, p.D, p.H)
    t = fillet(t.edges().filter_by(Axis.Z).group_by(Axis.X)[-1], 6)

    cav = box_at(x0 + p.spine_wall, p.wall, p.base_thickness,
                 x1 - x0 - p.spine_wall - p.wall, p.D - 2 * p.wall, p.H)
    t = t - cav

    # printer well: open all the way to the top face, no inward overhang,
    # so the clamshell lid can rotate freely
    t = t - box_at(p.printer_x - p.printer_clear - p.printer_top_rim,
                   p.wall - p.printer_clear,
                   p.printer_z - 1,
                   p.printer_w + 2 * p.printer_clear + 2 * p.printer_top_rim,
                   p.printer_d + 2 * p.printer_clear,
                   p.printer_h + 2)

    # top flange on the three exposed walls (stiffness without overhang)
    fz = p.H - p.top_flange
    for bx, by, bw, bd in [
        (x0 + p.spine_wall, p.wall, x1 - x0 - p.spine_wall - p.wall, p.top_flange_t),
        (x0 + p.spine_wall, p.D - p.wall - p.top_flange_t,
         x1 - x0 - p.spine_wall - p.wall, p.top_flange_t),
        (x1 - p.wall - p.top_flange_t, p.wall, p.top_flange_t, p.D - 2 * p.wall),
    ]:
        blk = box_at(bx, by, fz, bw, bd, p.top_flange)
        blk = blk - box_at(p.printer_x - p.printer_clear, p.wall - p.printer_clear,
                           fz - 1, p.printer_w + 2 * p.printer_clear,
                           p.printer_d + 2 * p.printer_clear, p.top_flange + 2)
        t = t + blk

    # printer riser: lifts the printer so its top sits flush with the top face
    riser_h = p.printer_z - p.base_thickness
    for rx in (p.printer_x + 12, p.printer_x + p.printer_w - 12 - 22):
        t = t + box_at(rx, p.wall + 10, p.base_thickness,
                       22, p.printer_d - 20, riser_h)
    # cable pass-through under the printer stays open between the two rails

    # spine joint: inserts are sunk INTO the 9 mm wall from the seam face.
    # Nothing protrudes, so the printer envelope stays clear.
    for (jy, jz) in SPINE_SCREWS:
        t = t - cyl_x(x0 - 0.5, jy, jz, p.insert_hole_d, p.insert_depth + 0.5)
    for (jy, jz) in SPINE_DOWELS:
        t = t - cyl_x(x0 - 0.5, jy, jz,
                      p.dowel_d + 2 * p.dowel_fit, p.insert_depth + 2.5)

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
    oh = (p.H - p.lid_rebate - 5 + 6) - (p.base_thickness + 5 - 6)
    ox = p.display_x - p.display_clear + p.fit_clear
    oz = p.base_thickness + 5 - 6
    y0 = p.wall + p.display_t
    fr = box_at(ox, y0, oz, ow, 4.0, oh)
    fr = fr - box_at(ox + 14, y0 - 1, p.display_z + 8, ow - 28, 6, p.display_h - 16)
    for sx in (p.display_x + 40, p.display_x + p.display_w - 40):
        for sz in (p.base_thickness + 5, p.H - p.lid_rebate - 5):
            fr = fr - cyl_y(sx, y0 - 1, sz, p.screw_clear_d, 6)
            fr = fr - cyl_y(sx, y0 + 4 - p.cbore_depth, sz, p.cbore_d, p.cbore_depth + 1)
    return fr


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


_owL, _ohL = p.x_split - 2 * p.wall - 30, p.H - p.base_thickness - 40
REAR_PANEL_LEFT = rear_panel(p.wall + 15, p.base_thickness + 20, _owL, _ohL, REAR_SCREWS)

_owR, _ohR = 90.0, 70.0
_oxR = p.x_split + (p.W - p.x_split - _owR) / 2
_ozR = p.base_thickness + 15
REAR_PANEL_RIGHT = rear_panel(_oxR, _ozR, _owR, _ohR,
                              [(_oxR - 8, _ozR - 8), (_oxR + _owR + 8, _ozR - 8),
                               (_oxR - 8, _ozR + _ohR + 8), (_oxR + _owR + 8, _ozR + _ohR + 8)])

# ------------------------------------------------------- reference bodies
DISPLAY_REFERENCE = box_at(p.display_x, p.wall, p.display_z,
                           p.display_w, p.display_t, p.display_h)
PRINTER_REFERENCE = box_at(p.printer_x, p.wall, p.printer_z,
                           p.printer_w, p.printer_d, p.printer_h)
PI_REFERENCE = box_at(p.display_x + 25, p.wall + p.display_t + 18,
                      p.base_thickness, p.pi_w, p.pi_d, p.pi_h)
PSU_REFERENCE = box_at(p.display_x + 25, p.D - p.wall - p.psu_d - 8,
                       p.base_thickness, p.psu_w, p.psu_d, p.psu_h)

PARTS = {
    "tub_left": TUB_LEFT,
    "tub_right": TUB_RIGHT,
    "top_plate_left": TOP_PLATE_LEFT,
    "display_retainer": DISPLAY_RETAINER,
    "rear_panel_left": REAR_PANEL_LEFT,
    "rear_panel_right": REAR_PANEL_RIGHT,
}
REFS = {
    "ref_display": DISPLAY_REFERENCE,
    "ref_printer": PRINTER_REFERENCE,
    "ref_pi": PI_REFERENCE,
    "ref_psu": PSU_REFERENCE,
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
