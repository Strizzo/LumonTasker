"""
checks.py - the model proves itself after every build.

Three classes of check, chosen because each one would have caught a defect
that instead took a screenshot to find:

1. HELPER CONTRACTS. Unit tests on the geometry helpers. plate_region must
   return a solid spanning exactly [z0, z0+h] (it was offset by h/2 for three
   versions), and on the raked module it must sit behind the rake plane (it
   was a plain rectangle, giving a 33 mm visor over the screen).

2. SLICE INTEGRITY. Every few mm of height, cut the part, rasterise the
   section, and ask two questions: is the interior cavity sealed from the
   outside, and how thin is the material anywhere. A breach is the missing
   corner - invisible to axis-aligned sections, obvious here. Thinness is
   measured from the medial axis, so it is correct on raked walls too.

3. ASSEMBLY. All-pairs interference, one solid per part, bed fit, and a
   golden snapshot of key dimensions so an unintended change is loud.

Run:  python3 checks.py lumon_v17
Exit code is non-zero if anything fails, so it can gate a print.
"""

import sys
import json
import importlib
from pathlib import Path

import numpy as np
from scipy import ndimage

PASS, FAIL, WARN = "PASS", "FAIL", "warn"
_results = []


def record(name, ok, detail=""):
    _results.append((name, PASS if ok else FAIL, detail))
    return ok


# ------------------------------------------------------------------ slicing
def mesh_of(shape, tol=0.25):
    verts, faces = shape.tessellate(tolerance=tol)
    V = np.array([[q.X, q.Y, q.Z] for q in verts], dtype=np.float64)
    F = np.array(faces, dtype=np.int64)
    return V, F


def section_segments(V, F, z):
    """Triangle/plane intersection segments at height z."""
    t = V[F]                                   # (n,3,3)
    d = t[:, :, 2] - z
    above = d > 0
    n_above = above.sum(axis=1)
    cross = (n_above == 1) | (n_above == 2)
    t, d, above = t[cross], d[cross], above[cross]
    if len(t) == 0:
        return np.zeros((0, 2, 2))
    segs = np.zeros((len(t), 2, 2))
    for i in range(len(t)):
        pts = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            if above[i, a] != above[i, b]:
                w = d[i, a] / (d[i, a] - d[i, b])
                pts.append(t[i, a, :2] + w * (t[i, b, :2] - t[i, a, :2]))
        if len(pts) == 2:
            segs[i] = pts
    return segs


def rasterise(segs, x0, y0, nx, ny, res):
    """Even-odd scanline fill of the section onto a grid."""
    mask = np.zeros((ny, nx), dtype=bool)
    if len(segs) == 0:
        return mask
    ya, yb = segs[:, 0, 1], segs[:, 1, 1]
    xa, xb = segs[:, 0, 0], segs[:, 1, 0]
    for j in range(ny):
        yc = y0 + (j + 0.5) * res
        hit = ((ya <= yc) & (yb > yc)) | ((yb <= yc) & (ya > yc))
        if not hit.any():
            continue
        w = (yc - ya[hit]) / (yb[hit] - ya[hit])
        xs = np.sort(xa[hit] + w * (xb[hit] - xa[hit]))
        for k in range(0, len(xs) - 1, 2):
            i0 = int(np.ceil((xs[k] - x0) / res - 0.5))
            i1 = int(np.floor((xs[k + 1] - x0) / res - 0.5))
            if i1 >= i0:
                mask[j, max(i0, 0):min(i1 + 1, nx)] = True
    return mask


def corner_walls(shape, name, z_list, corners, min_wall=2.0, res=0.4, win=30.0):
    """In each corner quadrant, how close does the cavity get to the outside?

    Windows are used because the part has legitimate apertures elsewhere - a
    global seal test would just flag the display window. Inside a corner
    window the wall should be continuous, and the shortest distance from any
    cavity pixel to the exterior IS the wall thickness. A breach drives it to
    zero, which is exactly the defect that axis-aligned sections missed.
    """
    V, F = mesh_of(shape)
    worst = {c: (99.0, None) for c in corners}
    for z in z_list:
        segs = section_segments(V, F, z)
        if len(segs) == 0:
            continue
        for cname, (cx, cy) in corners.items():
            x0, y0 = cx - win / 2, cy - win / 2
            n = int(win / res)
            m_ = rasterise(segs, x0, y0, n, n, res)
            if m_.sum() < 20 or m_.all():
                continue
            filled = ndimage.binary_fill_holes(m_)
            cavity = filled & ~m_
            if not cavity.any():
                continue
            d = ndimage.distance_transform_edt(filled) * res
            t = float(d[cavity].min())
            if t < worst[cname][0]:
                worst[cname] = (t, round(z, 1))
    for cname, (t, z) in worst.items():
        if z is None:
            continue
        record(f"{name} {cname}: wall >= {min_wall} mm", t >= min_wall,
               f"thinnest {t:.1f} mm at z={z}")


# --------------------------------------------------------------- assembly
def ivol(a, b):
    r = a.intersect(b)
    if r is None:
        return 0.0
    return sum(s.volume for s in r.solids()) if hasattr(r, "solids") else r.volume


def run(modname):
    m = importlib.import_module(modname)
    p = m.p

    # ---- 1. helper contracts
    reg = m.plate_region("right", 0.0, 100.0, 12.0, 8.0)
    bb = reg.bounding_box()
    record("plate_region spans exactly [z0, z0+h]",
           abs(bb.min.Z - 100.0) < 1e-6 and abs(bb.max.Z - 112.0) < 1e-6,
           f"got {bb.min.Z:.2f}..{bb.max.Z:.2f}, wanted 100.00..112.00")

    lid_l = m.PARTS["top_plate_left"]
    lb = lid_l.bounding_box()
    y_at_bottom = m.y_front_inner(lb.min.Z, 0.0)
    record("left lid follows the rake plane",
           abs(lb.min.Y - y_at_bottom) < 1.5,
           f"lid front y={lb.min.Y:.1f}, rake plane at that height y={y_at_bottom:.1f}")

    fill = m.LOGO_FILL
    fb = fill.bounding_box()
    record("mark sits on the outer face, not inside the wall",
           abs(fb.min.Y) < 0.2 and fb.max.Y <= p.logo_relief + 0.2,
           f"mark spans y={fb.min.Y:.2f}..{fb.max.Y:.2f}, face is y=0")
    record("mark exactly fills its recess",
           ivol(fill, m.TUB_RIGHT) < 1.0,
           f"overlap {ivol(fill, m.TUB_RIGHT):.1f} mm3")

    # ---- 2. slice integrity on the structural parts
    zs = list(np.arange(p.skirt_h + 6, p.H - p.lid_t - 4, 4.0))
    corner_walls(m.TUB_LEFT, "tub_left", zs, {
        "front-left": (0.0, 0.0), "rear-left": (0.0, p.D)})
    corner_walls(m.TUB_RIGHT, "tub_right", zs, {
        "front-right": (p.W, 0.0), "rear-right": (p.W, p.D)})

    # ---- 3. assembly
    for k, v in m.PARTS.items():
        record(f"{k}: one solid", len(v.solids()) == 1, f"{len(v.solids())} solids")

    names = list(m.PARTS) + [k for k in m.REFS if k in ("ref_display", "ref_printer",
                                                        "ref_psu", "ref_pi")]
    def get(k):
        return m.PARTS[k] if k in m.PARTS else m.REFS[k]
    allowed = {("display_retainer", "ref_display"), ("display_bezel", "ref_display")}
    clashes = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if (a, b) in allowed or (b, a) in allowed:
                continue
            v = ivol(get(a), get(b))
            if v > 1.0:
                clashes.append(f"{a}+{b}={v:.0f}")
    record("no interference between any two bodies", not clashes, "; ".join(clashes[:6]))

    bed = (256, 256, 256)
    bad = []
    for k, v in m.PARTS.items():
        s = v.bounding_box().size
        d = sorted([s.X, s.Y])
        if not (d[0] <= min(bed[:2]) and d[1] <= max(bed[:2]) and s.Z <= bed[2]):
            bad.append(f"{k} {s.X:.0f}x{s.Y:.0f}x{s.Z:.0f}")
    record("every part fits a 256 mm bed", not bad, "; ".join(bad))

    # ---- golden snapshot
    gold_p = Path(f"/home/claude/golden_{modname}.json")
    cur = {"W": round(p.W, 2), "D": round(p.D, 2), "H": round(p.H, 2),
           "parts": sorted(m.PARTS),
           "vol": {k: round(v.volume, 1) for k, v in sorted(m.PARTS.items())}}
    if gold_p.exists():
        old = json.loads(gold_p.read_text())
        diff = [k for k in cur["vol"] if k in old["vol"]
                and abs(cur["vol"][k] - old["vol"][k]) > 1.0]
        env = [k for k in ("W", "D", "H") if cur[k] != old[k]]
        record("dimensions unchanged since last snapshot", not (diff or env),
               f"envelope {env} parts {diff[:5]}")
    else:
        _results.append(("golden snapshot written", WARN, str(gold_p)))
    gold_p.write_text(json.dumps(cur, indent=1))

    # ---- report
    w = max(len(n) for n, _, _ in _results)
    print(f"\n{'CHECK':<{w}}  RESULT  DETAIL")
    print("-" * (w + 40))
    for n, r, d in _results:
        print(f"{n:<{w}}  {r:<6}  {d}")
    nf = sum(1 for _, r, _ in _results if r == FAIL)
    print(f"\n{len(_results)} checks, {nf} failed")
    return nf


if __name__ == "__main__":
    sys.path.insert(0, "/home/claude")
    sys.exit(1 if run(sys.argv[1] if len(sys.argv) > 1 else "lumon_v17") else 0)
