"""
logo_from_image.py - turn a bitmap into CAD geometry for the moulded mark.

Takes any image with the artwork in dark on light (or the reverse), traces the
outlines, works out which loops are holes, and returns a build123d sketch
scaled to a target width. Use it when you have the mark as a PNG or a crop of
a render rather than as an SVG.

    from logo_from_image import sketch_from_image
    art = sketch_from_image("logo.png", target_w=58)

Print-safety: min_feature_mm reports the narrowest stroke after scaling, so
you know whether the artwork survives a 0.4 nozzle before you print it.
"""

import numpy as np
from PIL import Image
from matplotlib.path import Path as MplPath
from skimage import measure
from build123d import *


def _binary(path, invert=None, threshold=None):
    im = Image.open(path).convert("L")
    a = np.asarray(im, dtype=float) / 255.0
    if threshold is None:
        try:
            from skimage.filters import threshold_otsu
            threshold = threshold_otsu(a)
        except Exception:
            threshold = 0.5
    mask = a < threshold                      # dark pixels are the artwork
    if invert is None:                        # guess: artwork is the minority
        invert = mask.mean() > 0.5
    if invert:
        mask = ~mask
    return mask


def _loops(mask, simplify_px=0.8):
    padded = np.pad(mask.astype(float), 1)
    out = []
    for c in measure.find_contours(padded, 0.5):
        c = measure.approximate_polygon(c, tolerance=simplify_px)
        if len(c) < 4:
            continue
        pts = [(float(col), float(-row)) for row, col in c]   # image -> CAD
        if pts[0] != pts[-1]:
            pts.append(pts[0])
        out.append(np.array(pts))
    return out


def _area(poly):
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * abs(np.dot(x[:-1], y[1:]) - np.dot(x[1:], y[:-1]))


def sketch_from_image(path, target_w=58.0, invert=None, threshold=None,
                      simplify_px=0.8, report=True):
    mask = _binary(path, invert, threshold)
    loops = sorted(_loops(mask, simplify_px), key=_area, reverse=True)
    if not loops:
        raise ValueError(f"no outlines found in {path}")

    # Odd nesting depth means a hole. Loops must be applied largest first so
    # an island sitting inside a hole is added after that hole is cut, not
    # before - otherwise the cut erases it.
    def face_of(poly):
        return make_face(Polyline(*[(x, y) for x, y in poly[:-1]], close=True))

    art = None
    n_face = n_hole = 0
    for i, poly in enumerate(loops):
        depth = sum(1 for j in range(i)
                    if MplPath(loops[j]).contains_point(poly[0]))
        f = face_of(poly)
        if depth % 2:
            art, n_hole = art - f, n_hole + 1
        else:
            art, n_face = (f if art is None else art + f), n_face + 1
    faces = [None] * n_face
    holes = [None] * n_hole

    bb = art.bounding_box()
    art = scale(art, by=target_w / bb.size.X)
    bb = art.bounding_box()
    art = Pos(-bb.center().X, -bb.center().Y) * art

    if report:
        px_per_mm = mask.shape[1] / target_w
        # stroke width = twice the inscribed radius along the medial axis
        from skimage.morphology import medial_axis
        skel, dist = medial_axis(mask, return_distance=True)
        vals = dist[skel]
        thin_px = 2 * np.percentile(vals, 5) if vals.size else 0.0
        print(f"[{path}] traced {len(faces)} outline(s), {len(holes)} hole(s)")
        print(f"  scaled to {target_w:.0f} mm wide x "
              f"{art.bounding_box().size.Y:.1f} mm tall")
        print(f"  thinnest stroke ~= {thin_px / px_per_mm:.2f} mm "
              f"({'OK' if thin_px / px_per_mm >= 0.8 else 'TOO FINE for a 0.4 nozzle'})")
    return art


if __name__ == "__main__":
    import sys
    sketch_from_image(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 58.0)
