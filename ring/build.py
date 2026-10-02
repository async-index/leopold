#!/usr/bin/env python3
"""Builds images/ + works.json for the ring page from the islands picks.

Usage: python3 build.py
Same works as islands, but uncropped (cards keep each work's own proportions).
The museum serves no CORS headers, so WebGL can't sample its images directly.
"""
import json, re, urllib.request
from io import BytesIO
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).parent
BASE = "https://onlinecollection.leopoldmuseum.org"
LONG = 1024

picks = json.load(open(ROOT.parent / "islands" / "works.json"))
index = {o["id"]: o for o in json.load(open(ROOT.parent / "grid" / "objects.json"))}
(ROOT / "images").mkdir(exist_ok=True)

def fetch(w):
    o = index[int(re.search(r"/object/(\d+)", w["url"]).group(1))]
    full = BASE + o["p"].replace("-preview.", "-default.")
    name = Path(full).name
    im = Image.open(BytesIO(urllib.request.urlopen(full).read())).convert("RGB")
    im.thumbnail((LONG, LONG), Image.LANCZOS)
    im.save(ROOT / "images" / name, quality=84)
    return {**w, "src": "images/" + name, "w": im.width, "h": im.height}

with ThreadPoolExecutor(8) as pool:
    out = list(pool.map(fetch, picks))
(ROOT / "works.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(len(out), "works")
