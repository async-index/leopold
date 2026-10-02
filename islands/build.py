#!/usr/bin/env python3
"""Builds images/ + works.json for the islands page from the grid's collection.

Usage: python3 build.py [count]
The museum serves no CORS headers, so WebGL can't sample its images directly;
a seeded pick of the grid's works is downloaded and resized locally instead.
"""
import json, random, sys, urllib.request
from io import BytesIO
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).parent
count = int(sys.argv[1]) if len(sys.argv) > 1 else 30
SIZE = 768  # square: islands crop to cover anyway

js = (ROOT.parent / "grid" / "data.js").read_text()
works = json.loads(js[js.index("{"):js.rindex("}") + 1])["works"]
works = random.Random(1918).sample(works, count)
(ROOT / "images").mkdir(exist_ok=True)

def fetch(w):
    name = Path(w["full"]).name
    dest = ROOT / "images" / name
    if not dest.exists():
        im = Image.open(BytesIO(urllib.request.urlopen(w["full"]).read())).convert("RGB")
        m = min(im.size)
        im = im.crop(((im.width - m) // 2, (im.height - m) // 2, (im.width + m) // 2, (im.height + m) // 2))
        im.resize((SIZE, SIZE), Image.LANCZOS).save(dest, quality=80)
    return {"src": "images/" + name, "title": w["title"], "artist": w["artist"], "date": w["date"], "url": w["url"]}

with ThreadPoolExecutor(8) as pool:
    out = list(pool.map(fetch, works))
(ROOT / "works.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(len(out), "works")
