"""
render3d.py - shaded previews without a GPU.

Tessellates build123d solids, projects them through a perspective camera and
rasterises with a numpy z-buffer. Flat shading plus a soft key/fill/rim rig,
supersampled and downsampled for anti-aliasing.

    from render3d import Scene
    s = Scene(1600, 1100)
    s.add(part, "#DEE9EE")
    s.look_at(eye=(...), target=(...))
    s.save("out.png")
"""

import numpy as np
from PIL import Image


def _hex(c):
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], dtype=float) / 255.0


class Scene:
    def __init__(self, w=1600, h=1100, ss=2, bg_top="#9aa7b2", bg_bot="#6f7b87",
                 exposure=1.0):
        self.w, self.h, self.ss = w, h, ss
        self.bg = (bg_top, bg_bot)
        self.exposure = exposure
        self.tris = []          # (N,3,3) vertex arrays
        self.cols = []          # (N,3) colours

    def add(self, shape, colour, tol=0.12):
        verts, faces = shape.tessellate(tolerance=tol)
        v = np.array([[p.X, p.Y, p.Z] for p in verts], dtype=float)
        f = np.array(faces, dtype=int)
        if len(f) == 0:
            return
        self.tris.append(v[f])
        self.cols.append(np.tile(_hex(colour), (len(f), 1)))

    # ------------------------------------------------------------ camera
    def look_at(self, eye, target, up=(0, 0, 1), fov=32.0):
        self.eye = np.array(eye, float)
        f = np.array(target, float) - self.eye
        f /= np.linalg.norm(f)
        u = np.array(up, float)
        r = np.cross(f, u); r /= np.linalg.norm(r)
        u = np.cross(r, f)
        self.R = np.stack([r, u, -f])          # world -> camera
        self.fov = np.radians(fov)

    # ------------------------------------------------------------ render
    def _background(self, W, H):
        top, bot = _hex(self.bg[0]), _hex(self.bg[1])
        t = np.linspace(0, 1, H)[:, None, None]
        return top[None, None, :] * (1 - t) + bot[None, None, :] * t + np.zeros((H, W, 3))

    def render(self):
        W, H = self.w * self.ss, self.h * self.ss
        img = self._background(W, H)
        zbuf = np.full((H, W), np.inf)

        tris = np.concatenate(self.tris, axis=0)
        cols = np.concatenate(self.cols, axis=0)

        # camera space
        cam = (tris - self.eye) @ self.R.T
        # cull triangles behind the camera
        keep = (cam[:, :, 2] < -1e-6).all(axis=1)
        cam, cols, tris = cam[keep], cols[keep], tris[keep]

        # perspective projection
        focal = (H / 2) / np.tan(self.fov / 2)
        z = -cam[:, :, 2]
        sx = cam[:, :, 0] * focal / z + W / 2
        sy = -cam[:, :, 1] * focal / z + H / 2
        scr = np.stack([sx, sy], axis=-1)

        # flat shading
        e1 = tris[:, 1] - tris[:, 0]
        e2 = tris[:, 2] - tris[:, 0]
        n = np.cross(e1, e2)
        ln = np.linalg.norm(n, axis=1, keepdims=True)
        ln[ln == 0] = 1
        n = n / ln
        # face the normal toward the camera so orientation errors don't matter
        view = self.eye - tris.mean(axis=1)
        view /= np.linalg.norm(view, axis=1, keepdims=True)
        n *= np.sign((n * view).sum(axis=1, keepdims=True))

        key = np.array([-0.45, -0.75, 0.62]); key /= np.linalg.norm(key)
        fill = np.array([0.8, -0.35, 0.25]); fill /= np.linalg.norm(fill)
        rim = np.array([0.1, 0.9, 0.35]); rim /= np.linalg.norm(rim)
        # Energy must sum to 1 with the ambient term, or every lit face clips
        # to white and the albedo - the actual brand colour - is lost.
        AMB, KEY, FILL, RIM = 0.34, 0.44, 0.15, 0.07
        lam = (AMB
               + KEY * np.clip((n * key).sum(1), 0, 1)
               + FILL * np.clip((n * fill).sum(1), 0, 1)
               + RIM * np.clip((n * rim).sum(1), 0, 1))
        half = (key + view) / np.linalg.norm(key + view, axis=-1, keepdims=True)
        spec = 0.05 * np.clip((n * half).sum(1), 0, 1) ** 32
        lit = (cols * lam[:, None] + spec[:, None]) * self.exposure
        # soft shoulder instead of a hard clamp, so highlights roll off
        shade = lit / (1.0 + np.clip(lit - 0.86, 0, None) * 2.2)
        shade = np.clip(shade, 0, 1)

        # painter-free z-buffer rasterisation, triangle by triangle
        order = np.argsort(-z.mean(axis=1))          # far to near helps cache
        for i in order:
            p = scr[i]
            zz = z[i]
            x0 = max(int(np.floor(p[:, 0].min())), 0)
            x1 = min(int(np.ceil(p[:, 0].max())) + 1, W)
            y0 = max(int(np.floor(p[:, 1].min())), 0)
            y1 = min(int(np.ceil(p[:, 1].max())) + 1, H)
            if x1 <= x0 or y1 <= y0:
                continue
            xs = np.arange(x0, x1) + 0.5
            ys = np.arange(y0, y1) + 0.5
            gx, gy = np.meshgrid(xs, ys)
            d = ((p[1, 1] - p[2, 1]) * (p[0, 0] - p[2, 0])
                 + (p[2, 0] - p[1, 0]) * (p[0, 1] - p[2, 1]))
            if abs(d) < 1e-12:
                continue
            l0 = ((p[1, 1] - p[2, 1]) * (gx - p[2, 0])
                  + (p[2, 0] - p[1, 0]) * (gy - p[2, 1])) / d
            l1 = ((p[2, 1] - p[0, 1]) * (gx - p[2, 0])
                  + (p[0, 0] - p[2, 0]) * (gy - p[2, 1])) / d
            l2 = 1.0 - l0 - l1
            m = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
            if not m.any():
                continue
            zi = 1.0 / np.clip(l0 / zz[0] + l1 / zz[1] + l2 / zz[2], 1e-9, None)
            sub = zbuf[y0:y1, x0:x1]
            hit = m & (zi < sub)
            if not hit.any():
                continue
            sub[hit] = zi[hit]
            img[y0:y1, x0:x1][hit] = shade[i]

        out = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        im = Image.fromarray(out)
        if self.ss > 1:
            im = im.resize((self.w, self.h), Image.LANCZOS)
        return im

    def save(self, path):
        self.render().save(path)
        return path
