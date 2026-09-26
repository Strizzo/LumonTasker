"""Assembly / exploded / section drawings for LUMON_TERMINAL v2."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from build123d import *
from lumon_v5 import (p, PARTS, REFS, SPINE_SCREWS, SPINE_DOWELS, OUT)

INK, REF, HID, DIM = "#1b1f23", "#c0392b", "#9aa0a6", "#2e6fb7"
FAR = 2000
c = (p.W / 2, p.D / 2, p.H / 2)


def lines(shape, origin, up, look_at):
    vis, hid = shape.project_to_viewport(origin, up, look_at)
    out = []
    for grp, kind in ((vis, "v"), (hid, "h")):
        for e in grp:
            n = 2 if e.geom_type == GeomType.LINE else 28
            out.append((np.array([[(e @ (i / (n - 1))).X, (e @ (i / (n - 1))).Y]
                                  for i in range(n)]), kind))
    return out


def draw(ax, items, origin, up, look_at, title, hidden=True):
    for shape, col, lw in items:
        for pts, kind in lines(shape, origin, up, look_at):
            if kind == "h" and not hidden:
                continue
            ax.plot(pts[:, 0], pts[:, 1],
                    color=col if kind == "v" else HID,
                    lw=lw if kind == "v" else 0.35,
                    ls="-" if kind == "v" else (0, (4, 3)),
                    zorder=3 if kind == "v" else 1)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=9.5, color=INK, family="monospace", y=-0.14)


PART_COL = {"tub_left": INK, "tub_right": INK, "top_plate_left": "#3d6b3d",
            "display_retainer": "#8a5a00", "rear_panel_left": "#4a4a8a",
            "rear_panel_right": "#4a4a8a", "id_plate": "#b5179e"}

assembled = [(s, PART_COL[k], 1.0) for k, s in PARTS.items()] + \
            [(REFS["ref_display"], REF, 0.8), (REFS["ref_printer"], REF, 0.8)]
POWER = [(REFS[k], "#0a7", 0.9) for k in ("ref_psu", "ref_iec", "ref_buck", "ref_pi")]

fig = plt.figure(figsize=(16, 11), dpi=150)
fig.patch.set_facecolor("white")

# ---------------------------------------------------------------- 1. FRONT
ax = fig.add_subplot(2, 2, 1)
draw(ax, assembled, (c[0], c[1] - FAR, c[2]), (0, 0, 1), c, "FRONT ELEVATION", hidden=False)
ax.annotate("", (-p.W / 2, -p.H / 2 - 12), (p.W / 2, -p.H / 2 - 12),
            arrowprops=dict(arrowstyle="<->", color=DIM, lw=0.8))
ax.text(0, -p.H / 2 - 10, f"{p.W:.1f}", color=DIM, ha="center", va="bottom", fontsize=8, family="monospace")
ax.annotate("", (p.W / 2 + 12, -p.H / 2), (p.W / 2 + 12, p.H / 2),
            arrowprops=dict(arrowstyle="<->", color=DIM, lw=0.8))
ax.text(p.W / 2 + 18, 0, f"{p.H:.0f}", color=DIM, fontsize=8, family="monospace", rotation=90, va="center")
sx = p.x_split - p.W / 2
ax.plot([sx, sx], [-p.H / 2 - 4, p.H / 2 + 6], color=DIM, lw=0.6, ls=(0, (6, 4)))
ax.text(sx, p.H / 2 + 10, "seam / spine", color=DIM, fontsize=7.5,
        family="monospace", ha="center")
_leg = [("tub_left / tub_right", INK), ("top_plate_left", "#3d6b3d"),
        ("display_retainer", "#8a5a00"), ("rear panels", "#4a4a8a"),
        ("debossed mark, 0.8 mm", "#b5179e"),
        ("reference hardware, not printed", REF)]
for _i, (_t, _c) in enumerate(_leg):
    ax.text(0.0, -0.10 - _i * 0.062, "\u25a0 " + _t, transform=ax.transAxes,
            color=_c, fontsize=7.5, family="monospace", va="top")

# ------------------------------------------------------------- 2. EXPLODED
EXPL = {"tub_left": (-95, 0, 0), "tub_right": (95, 0, 0),
        "top_plate_left": (-95, 0, 105), "display_retainer": (-95, 95, 0),
        "rear_panel_left": (-95, 130, 0), "rear_panel_right": (95, 130, 0),
        "id_plate": (95, -70, 0)}
exploded = [(Pos(*EXPL[k]) * s, PART_COL[k], 1.0) for k, s in PARTS.items() if k in EXPL]
exploded += [(Pos(-95, 55, 0) * REFS["ref_display"], REF, 0.8),
             (Pos(95, 0, 120) * REFS["ref_printer"], REF, 0.8)]
ax = fig.add_subplot(2, 2, 2)
draw(ax, exploded, (c[0] - FAR, c[1] - FAR * 1.15, c[2] + FAR * 0.75), (0, 0, 1), c,
     "EXPLODED  (red = real hardware, drops in from above / behind)", hidden=False)

# ------------------------------------------------------- 3. SIDE (the rake)
ax = fig.add_subplot(2, 2, 3)
draw(ax, assembled + POWER, (c[0] + FAR, c[1], c[2]), (0, 0, 1), c,
     f"SIDE  (one raked plane across both modules, no seam step)", hidden=True)
import math as _m
lean = p.H * _m.tan(_m.radians(p.rake_deg))
ax.text(0.01, 0.99, f"one raked plane across both modules, no step\n"
                    f"front leans back {lean:.0f} mm over {p.H:.0f} mm\n"
                    f"printer set back to y={p.printer_front:.0f}; depth {p.D:.0f} mm (was 153)",
        transform=ax.transAxes, fontsize=7.5, family="monospace", color=DIM,
        va="top", ha="left")

# ------------------------------------------------- 4. SECTION THROUGH SPINE
slabz = 20.0
slab = Pos(p.W / 2, p.D / 2, slabz) * Box(p.W + 10, p.D + 10, 2)
sect = []
for k, s in PARTS.items():
    r = s.intersect(slab)
    if r is None:
        continue
    for sol in (r.solids() if hasattr(r, "solids") else [r]):
        sect.append((sol, PART_COL[k], 1.1))
for k in ("ref_display", "ref_printer", "ref_psu", "ref_pi", "ref_buck"):
    r = REFS[k].intersect(slab)
    if r is not None:
        for sol in (r.solids() if hasattr(r, "solids") else [r]):
            sect.append((sol, REF, 0.8))
ax = fig.add_subplot(2, 2, 4)
draw(ax, sect, (c[0], c[1], c[2] + FAR), (0, 1, 0), c,
     f"SECTION z = {slabz:.0f}  (power bay: PSU right, Pi + buck left)", hidden=False)
ax.text(0.01, 0.99,
        "one 24 V open-frame PSU, mains barrier, Pi vertical on the wall\n"
        "24 V -> printer through the spine; 24->5 V buck feeds the Pi\n"
        "mains inlet in the FIXED rear wall, never on the service panel",
        transform=ax.transAxes, fontsize=7.5, family="monospace",
        color=DIM, va="top", ha="left")

fig.suptitle("LUMON_TERMINAL v5  -  identification mark moulded into the wall",
             fontsize=13, family="monospace", color=INK, y=0.97)
fig.text(0.5, 0.015,
         f"{p.W:.0f} x {p.D:.0f} x {p.H:.0f} mm   |   left module {p.x_split:.0f} mm, "
         f"right module {p.W - p.x_split:.0f} mm   |   printer envelope still UNVERIFIED",
         ha="center", fontsize=8.5, color=REF, family="monospace")
fig.tight_layout(rect=[0, 0.035, 1, 0.945])
fig.savefig(OUT / "v5_views.png", facecolor="white")
print("ok")
