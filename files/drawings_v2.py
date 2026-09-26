"""Assembly / exploded / section drawings for LUMON_TERMINAL v2."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from build123d import *
from lumon_v2 import (p, PARTS, REFS, SPINE_SCREWS, SPINE_DOWELS, OUT)

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
            "rear_panel_right": "#4a4a8a"}

assembled = [(s, PART_COL[k], 1.0) for k, s in PARTS.items()] + \
            [(REFS["ref_display"], REF, 0.8), (REFS["ref_printer"], REF, 0.8)]

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

# ------------------------------------------------------------- 2. EXPLODED
EXPL = {"tub_left": (-95, 0, 0), "tub_right": (95, 0, 0),
        "top_plate_left": (-95, 0, 105), "display_retainer": (-95, 95, 0),
        "rear_panel_left": (-95, 130, 0), "rear_panel_right": (95, 130, 0)}
exploded = [(Pos(*EXPL[k]) * s, PART_COL[k], 1.0) for k, s in PARTS.items()]
exploded += [(Pos(-95, 55, 0) * REFS["ref_display"], REF, 0.8),
             (Pos(95, 0, 120) * REFS["ref_printer"], REF, 0.8)]
ax = fig.add_subplot(2, 2, 2)
draw(ax, exploded, (c[0] - FAR, c[1] - FAR * 1.15, c[2] + FAR * 0.75), (0, 0, 1), c,
     "EXPLODED  (red = real hardware, drops in from above / behind)", hidden=False)

# ------------------------------------------------------------------ 3. TOP
ax = fig.add_subplot(2, 2, 3)
draw(ax, assembled, (c[0], c[1], c[2] + FAR), (0, 1, 0), c,
     "TOP  (printer well fully open, zero overhang over the lid)", hidden=False)

# ------------------------------------------------- 4. SECTION THROUGH SPINE
slabz = 70.0
slab = Pos(p.W / 2, p.D / 2, slabz) * Box(p.W + 10, p.D + 10, 2)
sect = []
for k, s in PARTS.items():
    r = s.intersect(slab)
    if r is None:
        continue
    for sol in (r.solids() if hasattr(r, "solids") else [r]):
        sect.append((sol, PART_COL[k], 1.1))
for k in ("ref_display", "ref_printer"):
    r = REFS[k].intersect(slab)
    if r is not None:
        for sol in (r.solids() if hasattr(r, "solids") else [r]):
            sect.append((sol, REF, 0.8))
ax = fig.add_subplot(2, 2, 4)
draw(ax, sect, (c[0], c[1], c[2] + FAR), (0, 1, 0), c,
     f"HORIZONTAL SECTION z = {slabz:.0f}  (spine joint)", hidden=False)
ax.text(0.01, 0.99,
        "spine joint\n"
        "  5x M3 through the 3 mm wall of tub_left\n"
        "  into inserts sunk in the 9 mm wall of tub_right\n"
        "  2x 4 mm steel dowels locate the seam\n"
        "  nothing protrudes into the printer well",
        transform=ax.transAxes, fontsize=7.5, family="monospace",
        color=DIM, va="top", ha="left")

fig.suptitle("LUMON_TERMINAL v2  -  two-module split, joints and mounting",
             fontsize=13, family="monospace", color=INK, y=0.97)
fig.text(0.5, 0.015,
         f"{p.W:.0f} x {p.D:.0f} x {p.H:.0f} mm   |   left module {p.x_split:.0f} mm, "
         f"right module {p.W - p.x_split:.0f} mm   |   printer envelope still UNVERIFIED",
         ha="center", fontsize=8.5, color=REF, family="monospace")
fig.tight_layout(rect=[0, 0.035, 1, 0.945])
fig.savefig(OUT / "v2_assembly_views.png", facecolor="white")
print("ok")
