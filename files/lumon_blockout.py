"""
LUMON_TERMINAL - Milestone 1 blockout
=====================================
Parametric, code-driven CAD. No Fusion required.

Design rule (spec sec.34): the enclosure is built around physical reference
bodies, not around a render.

Confidence tags on every parameter:
    MEASURED   - from official vendor documentation
    UNVERIFIED - from a product listing, must be confirmed with calipers
    TBD        - placeholder, do not trust for fit
    DESIGN     - chosen by the designer, free to change
"""

from dataclasses import dataclass, asdict, field
from pathlib import Path
from build123d import *

OUT = Path("/home/claude/out")
OUT.mkdir(exist_ok=True)


# ---------------------------------------------------------------- parameters
@dataclass
class P:
    # --- DISPLAY: Raspberry Pi 7" Touch Display (original, not Display 2)
    display_w: float = 192.96          # MEASURED  official RPi drawing
    display_h: float = 110.76          # MEASURED  official RPi drawing
    display_active_w: float = 154.08   # MEASURED
    display_active_h: float = 85.92    # MEASURED
    display_t: float = 21.0            # TBD       full assembly incl. driver PCB + standoffs
    display_clear: float = 1.0         # DESIGN
    display_bezel_overlap: float = 6.0 # DESIGN    frame overlaps display edge, does NOT add width

    # --- PRINTER: 80 mm clamshell thermal printer (Sunydog POS-8370 class)
    # Photographs confirm: TOP-loading clamshell lid, paper exits through a
    # slot in the top face, status LED on the front edge of the black lid,
    # one round connector recess on the right side face.
    printer_w: float = 142.0           # UNVERIFIED likely packaging dimension
    printer_d: float = 122.0           # UNVERIFIED
    printer_h: float = 122.0           # UNVERIFIED
    printer_clear: float = 2.0         # DESIGN
    printer_lid_swing: float = 60.0    # TBD       lid rotation clearance needed above top face

    # --- ELECTRONICS placeholders
    pi_w: float = 85.0                 # TBD  Raspberry Pi 4/5 board footprint
    pi_d: float = 56.0                 # TBD
    pi_h: float = 30.0                 # TBD  board + active cooler
    psu_w: float = 100.0               # TBD  internal PSU brick
    psu_d: float = 55.0                # TBD
    psu_h: float = 35.0                # TBD

    # --- ENCLOSURE
    wall: float = 3.0                  # DESIGN
    base_thickness: float = 4.0        # DESIGN
    rib: float = 6.0                   # DESIGN  structural spine between the two zones
    rear_cavity: float = 25.0          # DESIGN  behind printer: connectors + cable radius
    foot_h: float = 4.0                # DESIGN
    fillet_main: float = 6.0           # DESIGN
    fillet_top: float = 3.0            # DESIGN

    # --- derived (filled in __post_init__)
    W: float = field(default=0.0)
    D: float = field(default=0.0)
    H: float = field(default=0.0)

    def __post_init__(self):
        # width: display and printer sit side by side; the bezel overlaps the
        # display edge rather than adding to it
        self.W = (self.wall + self.display_w + 2 * self.display_clear
                  + self.rib
                  + self.printer_w + 2 * self.printer_clear + self.wall)
        # depth: printer flush at front, electronics cavity behind it
        self.D = self.wall + self.printer_d + self.rear_cavity + self.wall
        # height: printer top must be FLUSH with the enclosure top face so the
        # clamshell lid can open and paper can exit
        self.H = self.base_thickness + self.printer_h + 4.0

    # zone origins (x,y,z of the min corner), origin = front-left-bottom
    @property
    def printer_x(self): return self.W - self.wall - self.printer_clear - self.printer_w
    @property
    def printer_y(self): return self.wall
    @property
    def printer_z(self): return self.H - self.printer_h      # top flush
    @property
    def display_x(self): return self.wall + self.display_clear
    @property
    def display_y(self): return self.wall
    @property
    def display_z(self): return (self.H - self.display_h) / 2


p = P()


# ------------------------------------------------------------------- helpers
def box_at(x, y, z, w, d, h):
    """Box placed by its minimum corner."""
    return Pos(x + w / 2, y + d / 2, z + h / 2) * Box(w, d, h)


# --------------------------------------------------------- reference bodies
DISPLAY_REFERENCE = box_at(p.display_x, p.display_y, p.display_z,
                           p.display_w, p.display_t, p.display_h)

PRINTER_REFERENCE = box_at(p.printer_x, p.printer_y, p.printer_z,
                           p.printer_w, p.printer_d, p.printer_h)

# Pi sits behind the display, on the floor, board flat
PI_REFERENCE = box_at(p.display_x + 20,
                      p.display_y + p.display_t + 15,
                      p.base_thickness,
                      p.pi_w, p.pi_d, p.pi_h)

PSU_REFERENCE = box_at(p.display_x + 20,
                       p.D - p.wall - p.psu_d - 5,
                       p.base_thickness,
                       p.psu_w, p.psu_d, p.psu_h)


# ------------------------------------------------------------- outer housing
shell = box_at(0, 0, 0, p.W, p.D, p.H)
shell = fillet(shell.edges().filter_by(Axis.Z), p.fillet_main)
shell = fillet(shell.edges().filter_by(Plane.XY).group_by(Axis.Z)[-1], p.fillet_top)

# hollow it out
cavity = box_at(p.wall, p.wall, p.base_thickness,
                p.W - 2 * p.wall, p.D - 2 * p.wall, p.H - p.base_thickness)
shell = shell - cavity

# display window through the front face (frame overlaps the display edge)
win_w = p.display_w - 2 * p.display_bezel_overlap
win_h = p.display_h - 2 * p.display_bezel_overlap
shell = shell - box_at(p.display_x + p.display_bezel_overlap,
                       -1,
                       p.display_z + p.display_bezel_overlap,
                       win_w, p.wall + 2, win_h)

# printer aperture in the TOP face - the clamshell lid must be reachable and
# the paper must exit upward
shell = shell - box_at(p.printer_x - p.printer_clear,
                       p.printer_y - p.printer_clear,
                       p.H - p.wall - 1,
                       p.printer_w + 2 * p.printer_clear,
                       p.printer_d + 2 * p.printer_clear,
                       p.wall + 2)

# rear service panel opening
svc_w = p.W - 2 * p.wall - 2 * 10
svc_h = p.H - p.base_thickness - 2 * 10
shell = shell - box_at(p.wall + 10, p.D - p.wall - 1, p.base_thickness + 10,
                       svc_w, p.wall + 2, svc_h)

OUTER_HOUSING = shell


# ------------------------------------------------------------------- exports
def export_all():
    asm = Compound(label="LUMON_TERMINAL", children=[
        Compound(label="OUTER_HOUSING", children=[OUTER_HOUSING.solid()]),
        Compound(label="DISPLAY_REFERENCE", children=[DISPLAY_REFERENCE.solid()]),
        Compound(label="PRINTER_REFERENCE", children=[PRINTER_REFERENCE.solid()]),
        Compound(label="RASPBERRY_PI_REFERENCE", children=[PI_REFERENCE.solid()]),
        Compound(label="PSU_REFERENCE", children=[PSU_REFERENCE.solid()]),
    ])
    export_step(asm, str(OUT / "LUMON_TERMINAL_blockout.step"))
    for name, obj in [("outer_housing", OUTER_HOUSING),
                      ("ref_display", DISPLAY_REFERENCE),
                      ("ref_printer", PRINTER_REFERENCE),
                      ("ref_pi", PI_REFERENCE),
                      ("ref_psu", PSU_REFERENCE)]:
        export_stl(obj, str(OUT / f"{name}.stl"), tolerance=0.05)
    return asm


# ---------------------------------------------------------------- validation
def ivol(a, b):
    r = a.intersect(b)
    return 0.0 if r is None else r.volume


def validate():
    lines = []
    ok = lambda c: "PASS" if c else "FAIL"

    lines.append("=== PROPORTIONAL CHECK (spec sec.27) ===")
    rw = p.printer_w / p.display_w
    rh = p.printer_h / p.display_h
    lines.append(f"printer/display width  = {rw:6.1%}  (spec: ~73.6%)  {ok(abs(rw-0.736)<0.01)}")
    lines.append(f"printer/display height = {rh:6.1%}  (spec: ~110.1%) {ok(abs(rh-1.101)<0.01)}")
    lines.append(f"printer is {p.printer_h - p.display_h:.2f} mm taller than the display")

    lines.append("\n=== OVERALL ENVELOPE ===")
    lines.append(f"width  {p.W:7.2f} mm   spec target 340-350   {ok(340<=p.W<=350)}")
    lines.append(f"depth  {p.D:7.2f} mm   spec target 145-160   {ok(145<=p.D<=160)}")
    lines.append(f"height {p.H:7.2f} mm   spec target 135-145   {ok(135<=p.H<=145)}")

    lines.append("\n=== COLLISION / CLEARANCE ===")
    inter = ivol(DISPLAY_REFERENCE, PRINTER_REFERENCE)
    lines.append(f"display vs printer overlap     {inter:8.2f} mm3  {ok(inter<1e-6)}")
    for nm, ref in [("display", DISPLAY_REFERENCE), ("printer", PRINTER_REFERENCE),
                    ("pi", PI_REFERENCE), ("psu", PSU_REFERENCE)]:
        v = ivol(OUTER_HOUSING, ref)
        lines.append(f"{nm:8s} vs housing overlap    {v:8.2f} mm3  {ok(v<1.0)}")

    gap = p.printer_x - (p.display_x + p.display_w)
    lines.append(f"spine between display and printer  {gap:.2f} mm")

    lines.append("\n=== PRINTABILITY ===")
    lines.append(f"housing bounding box {p.W:.0f} x {p.D:.0f} x {p.H:.0f} mm")
    for bed, nm in [(220, "Ender-3 / Prusa Mini"), (256, "Bambu P1/X1"), (350, "Bambu X1E / large")]:
        lines.append(f"  fits {nm:22s} ({bed} mm): {ok(p.W <= bed)}")
    lines.append("  -> the front shell MUST be split; place the seam deliberately.")

    lines.append("\n=== FUNCTIONAL NOTES FROM PHOTOGRAPHS ===")
    lines.append("  paper exits through the TOP face  -> top aperture, not a front slot")
    lines.append(f"  clamshell lid needs ~{p.printer_lid_swing:.0f} mm free above the top face (TBD)")
    lines.append("  printer top is FLUSH with the enclosure top face")
    lines.append("  display driver PCB + DSI ribbon sit on the rear -> display_t is TBD")

    lines.append("\n=== PARAMETERS NOT SAFE TO BUILD AGAINST ===")
    lines.append("  printer_w/d/h : UNVERIFIED - likely the packaging size, measure the unit")
    lines.append("  printer mounting holes, connector positions : NOT MODELLED, do not invent")
    lines.append("  display_t, pi_*, psu_* : TBD placeholders")
    return "\n".join(lines)


if __name__ == "__main__":
    export_all()
    print(validate())
    print("\n=== PARAMETER TABLE ===")
    for k, v in asdict(p).items():
        print(f"{k:24s} {v:10.2f}")
