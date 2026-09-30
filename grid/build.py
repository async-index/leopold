#!/usr/bin/env python3
"""Builds data.js from shape.svg + the Leopold online collection.

Usage: python3 build.py objects.json [count]
objects.json = the collection index (id, t, a, d, p, w, h) pulled from
onlinecollection.leopoldmuseum.org's search API. Preview images are
downloaded once into images/ (local only, not published) to make the square
thumbs/; the page loads larger versions straight from the museum.
"""
import collections, hashlib, json, random, re, sys, urllib.request
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).parent
BASE = "https://onlinecollection.leopoldmuseum.org"

objects = json.load(open(sys.argv[1]))
count = int(sys.argv[2]) if len(sys.argv) > 2 else 800

# Very long/wide objects crop badly to a square tile.
objects = [o for o in objects if 0.5 <= o["h"] / o["w"] <= 2.0]
random.Random(1908).shuffle(objects)

(ROOT / "images").mkdir(exist_ok=True)
(ROOT / "thumbs").mkdir(exist_ok=True)
THUMB = 192  # square grid tile; images/ keeps the full preview for close zoom

def fetch(o):
    dest = ROOT / "images" / Path(o["p"]).name
    if not dest.exists():
        urllib.request.urlretrieve(BASE + o["p"], dest)
    thumb = ROOT / "thumbs" / dest.name
    if not thumb.exists():
        im = Image.open(dest).convert("RGB")
        m = min(im.size)
        im = im.crop(((im.width - m) // 2, (im.height - m) // 2, (im.width + m) // 2, (im.height + m) // 2))
        im.resize((THUMB, THUMB), Image.LANCZOS).save(thumb, quality=82)
    return dest.name

# Works without a photo serve the museum's logo placeholder: an image
# that recurs many times. Fetch extra, drop those, keep the first `count`.
with ThreadPoolExecutor(8) as pool:
    files = list(pool.map(fetch, objects[:int(count * 1.1)]))
digest = [hashlib.md5((ROOT / "images" / f).read_bytes()).hexdigest() for f in files]
seen = collections.Counter(digest)
keep = [i for i, d in enumerate(digest) if seen[d] < 5][:count]
objects = [objects[i] for i in keep]
files = [files[i] for i in keep]

svg = (ROOT / "shape.svg").read_text()
vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
paths = re.findall(r'<path[^>]*\sd="([^"]+)"', svg)

data = {
    "shape": {"viewBox": vb, "paths": paths},
    "works": [
        {"thumb": "thumbs/" + f, "src": BASE + o["p"],
         "full": BASE + o["p"].replace("-preview.", "-default."),
         "title": o["t"], "artist": o["a"], "date": o["d"],
         "url": f"{BASE}/objekt/{o['id']}"}
        for o, f in zip(objects, files)
    ],
}
(ROOT / "data.js").write_text("window.DATA = " + json.dumps(data, ensure_ascii=False) + ";\n")
print(f"{len(files)} works, {len(paths)} path(s), viewBox {vb}")
