"""Hidden-line orthographic + isometric views generated from the real solids."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from build123d import *
from lumon_blockout import (p, OUTER_HOUSING, DISPLAY_REFERENCE, PRINTER_REFERENCE,
                            PI_REFERENCE, PSU_REFERENCE, OUT)

INK = "#1b1f23"
REF = "#c0392b"
HID = "#9aa0a6"
DIM = "#2e6fb7"

parts = [(OUTER_HOUSING, INK, 1.1),
         (DISPLAY_REFERENCE, REF, 0.9),
         (PRINTER_REFERENCE, REF, 0.9),
         (PI_REFERENCE, "#7a7a7a", 0.6),
         (PSU_REFERENCE, "#7a7a7a", 0.6)]


def polylines(shape, origin, up, look_at):
    vis, hid = shape.project_to_viewport(origin, up, look_at)
    out = []
    for grp, kind in ((vis, "v"), (hid, "h")):
        for e in grp:
            n = 2 if e.geom_type == GeomType.LINE else 32
            pts = np.array([[(e @ (i / (n - 1))).X, (e @ (i / (n - 1))).Y]
                            for i in range(n)])
            out.append((pts, kind))
    return out


def draw(ax, origin, up, look_at, title):
    for shape, col, lw in parts:
        for pts, kind in polylines(shape, origin, up, look_at):
            ax.plot(pts[:, 0], pts[:, 1],
                    color=col if kind == "v" else HID,
                    lw=lw if kind == "v" else 0.4,
                    ls="-" if kind == "v" else (0, (4, 3)),
                    solid_capstyle="round", zorder=3 if kind == "v" else 1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=9.5, color=INK, family="monospace", y=-0.16)


def dim(ax, x0, y0, x1, y1, label, off=0, vertical=False):
    ax.annotate("", (x1, y1), (x0, y0),
                arrowprops=dict(arrowstyle="<->", color=DIM, lw=0.8))
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    ax.text(mx, my + (0 if vertical else 4), label, color=DIM, fontsize=7.5,
            family="monospace", ha="center", va="bottom",
            rotation=90 if vertical else 0)


c = (p.W / 2, p.D / 2, p.H / 2)
FAR = 1500

fig = plt.figure(figsize=(15, 10.5), dpi=150)
fig.patch.set_facecolor("white")

# ---- FRONT (looking along +Y)
ax = fig.add_subplot(2, 2, 1)
draw(ax, (c[0], c[1] - FAR, c[2]), (0, 0, 1), c, "FRONT ELEVATION")
y = -p.H / 2 - 14
dim(ax, -p.W / 2, y, p.W / 2, y, f"{p.W:.1f}")
yd = -p.H / 2 - 30
dx0 = -p.W / 2 + p.wall + p.display_clear
dim(ax, dx0, yd, dx0 + p.display_w, yd, f"display {p.display_w:.2f}")
px0 = -p.W / 2 + p.printer_x
dim(ax, px0, yd, px0 + p.printer_w, yd, f"printer {p.printer_w:.0f}")
dim(ax, p.W / 2 + 14, -p.H / 2, p.W / 2 + 14, p.H / 2, f"{p.H:.0f}", vertical=True)
ax.text(0, p.H / 2 + 22,
        f"width ratio {p.printer_w/p.display_w:.1%}   height ratio {p.printer_h/p.display_h:.1%}",
        ha="center", fontsize=8, color=DIM, family="monospace")

# ---- SIDE (looking along -X, from the right)
ax = fig.add_subplot(2, 2, 2)
draw(ax, (c[0] + FAR, c[1], c[2]), (0, 0, 1), c, "SIDE ELEVATION (from right)")
y = -p.H / 2 - 14
dim(ax, -p.D / 2, y, p.D / 2, y, f"depth {p.D:.0f}")
dim(ax, p.D / 2 + 14, -p.H / 2, p.D / 2 + 14, p.H / 2, f"{p.H:.0f}", vertical=True)
ax.text(0, p.H / 2 + 18, f"printer depth {p.printer_d:.0f}  |  rear cavity {p.rear_cavity:.0f}",
        ha="center", fontsize=8, color=DIM, family="monospace")

# ---- TOP
ax = fig.add_subplot(2, 2, 3)
draw(ax, (c[0], c[1], c[2] + FAR), (0, 1, 0), c, "TOP VIEW  (printer aperture = clamshell lid)")

# ---- ISO
ax = fig.add_subplot(2, 2, 4)
draw(ax, (c[0] - FAR, c[1] - FAR * 1.1, c[2] + FAR * 0.8), (0, 0, 1), c,
     "ISOMETRIC  (red = physical reference bodies)")

fig.suptitle("LUMON_TERMINAL  -  MILESTONE 1 BLOCKOUT  -  no cosmetic geometry",
             fontsize=12, family="monospace", color=INK, y=0.97)
fig.text(0.5, 0.02,
         "printer envelope 142 x 122 x 122 UNVERIFIED - confirm with calipers before Milestone 2",
         ha="center", fontsize=8, color=REF, family="monospace")
fig.tight_layout(rect=[0, 0.04, 1, 0.95])
fig.savefig(OUT / "blockout_views.png", facecolor="white")
print("ok")
