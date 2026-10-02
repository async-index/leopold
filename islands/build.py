#!/usr/bin/env python3
"""Builds images/ + works.json for the islands page from a hand-picked list.

Usage: python3 build.py
Titles/artists/dates come from the grid's collection index (objects.json).
The museum serves no CORS headers, so WebGL can't sample its images directly;
they are downloaded and square-cropped locally instead.
"""
import json, re, shutil, urllib.request
from io import BytesIO
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).parent
BASE = "https://onlinecollection.leopoldmuseum.org"
SIZE = 768  # square: islands crop to cover anyway

PICKS = """
https://onlinecollection.leopoldmuseum.org/en/object/7693-indian-fairytale/
https://onlinecollection.leopoldmuseum.org/en/object/528-self-portrait-with-chinese-lantern-plant/
https://onlinecollection.leopoldmuseum.org/en/object/527-portrait-of-wally-neuzil/
https://onlinecollection.leopoldmuseum.org/en/object/623-tre-croci-dolomite-landscape/
https://onlinecollection.leopoldmuseum.org/en/object/715-mountain-reapers-version-i/
https://onlinecollection.leopoldmuseum.org/en/object/529-caress-cardinal-and-nun/
https://onlinecollection.leopoldmuseum.org/en/object/629-death-and-life/
https://onlinecollection.leopoldmuseum.org/en/object/4328-on-lake-attersee/
https://onlinecollection.leopoldmuseum.org/en/object/622-self-portrait-one-hand-touching-the-face/
https://onlinecollection.leopoldmuseum.org/en/object/2451-moa/
https://onlinecollection.leopoldmuseum.org/en/object/225-marigolds/
""".split()

index = {o["id"]: o for o in json.load(open(ROOT.parent / "grid" / "objects.json"))}
shutil.rmtree(ROOT / "images", ignore_errors=True)
(ROOT / "images").mkdir()

def fetch(url):
    o = index[int(re.search(r"/object/(\d+)", url).group(1))]
    full = BASE + o["p"].replace("-preview.", "-default.")
    name = Path(full).name
    im = Image.open(BytesIO(urllib.request.urlopen(full).read())).convert("RGB")
    # Tall works crop from the top: heads sit high (Moa's would be cut off centred).
    m = min(im.size)
    x, y = (im.width - m) // 2, 0 if im.height > im.width else (im.height - m) // 2
    im = im.crop((x, y, x + m, y + m))
    im.resize((SIZE, SIZE), Image.LANCZOS).save(ROOT / "images" / name, quality=82)
    return {"src": "images/" + name, "title": o["t"], "artist": o["a"], "date": o["d"], "url": url}

with ThreadPoolExecutor(8) as pool:
    out = list(pool.map(fetch, PICKS))
(ROOT / "works.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(len(out), "works")
