#!/usr/bin/env python3
"""Builds atlas.jpg + works.json for the colour page from the grid's thumbs.

Usage: python3 build.py [tile=64] [mode=hue|pca]
Each thumb's mean colour (CIELAB) is placed in 2D, then every work is assigned
to one cell of a 52×25 grid (linear assignment), so neighbours share colour.
The atlas is written in grid order: it is the field itself.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).parent
GRID = ROOT.parent / "grid"
COLS, ROWS = 52, 25
tile = int(sys.argv[1]) if len(sys.argv) > 1 else 64
mode = sys.argv[2] if len(sys.argv) > 2 else "hue"

js = (GRID / "data.js").read_text()
works = json.loads(js[js.index("{"):js.rindex("}") + 1])["works"][:COLS * ROWS]
assert len(works) == COLS * ROWS, len(works)

def lab(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = c @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T
    xyz /= [0.95047, 1.0, 1.08883]
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)

thumbs = [Image.open(GRID / w["thumb"]).convert("RGB") for w in works]
cols = np.array([lab(np.asarray(t.resize((24, 24)), float)).reshape(-1, 3).mean(0) for t in thumbs])

def rank(v):  # spread evenly over [0, 1]
    r = np.empty(len(v)); r[np.argsort(v)] = np.arange(len(v)); return r / (len(v) - 1)

if mode == "pca":
    x = cols - cols.mean(0)
    _, _, vt = np.linalg.svd(x, full_matrices=False)
    p = x @ vt[:2].T
    px, py = rank(p[:, 0]), rank(p[:, 1])
else:
    hue = np.arctan2(cols[:, 2], cols[:, 1])
    px, py = rank(hue), rank(-cols[:, 0])

gx, gy = np.meshgrid((np.arange(COLS) + 0.5) / COLS, (np.arange(ROWS) + 0.5) / ROWS)
g = np.stack([gx.ravel(), gy.ravel()], 1)
cost = (px[:, None] - g[None, :, 0]) ** 2 + (py[:, None] - g[None, :, 1]) ** 2
item, cell = linear_sum_assignment(cost)
order = item[np.argsort(cell)]  # order[c] = work in cell c

# Smooth: swap neighbours while it lowers total Lab difference to adjacent cells.
def energy(o, c):
    r, k = divmod(c, COLS); e = 0
    for dr, dk in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        rr, kk = r + dr, k + dk
        if 0 <= rr < ROWS and 0 <= kk < COLS:
            e += np.sum((cols[o[c]] - cols[o[rr * COLS + kk]]) ** 2)
    return e
rng = np.random.default_rng(1908)
for _ in range(60000):
    a = rng.integers(COLS * ROWS); r, k = divmod(a, COLS)
    b = a + (1 if k + 1 < COLS and rng.random() < 0.5 else COLS if r + 1 < ROWS else -1)
    if not 0 <= b < COLS * ROWS: continue
    before = energy(order, a) + energy(order, b)
    order[a], order[b] = order[b], order[a]
    if energy(order, a) + energy(order, b) > before: order[a], order[b] = order[b], order[a]

atlas = Image.new("RGB", (COLS * tile, ROWS * tile))
for c, i in enumerate(order):
    atlas.paste(thumbs[i].resize((tile, tile), Image.LANCZOS), ((c % COLS) * tile, (c // COLS) * tile))
atlas.save(ROOT / "atlas.jpg", quality=80)
out = {"cols": COLS, "rows": ROWS, "tile": tile,
       "works": [{k: works[i][k] for k in ("thumb", "title", "artist", "date", "url")} for i in order]}
(ROOT / "works.json").write_text(json.dumps(out, ensure_ascii=False))
print(mode, atlas.size, round((ROOT / "atlas.jpg").stat().st_size / 1e6, 2), "MB")
