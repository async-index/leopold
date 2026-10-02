#!/usr/bin/env python3
"""Builds works.json for the browse page from the grid's works + collection index.

Usage: python3 build.py
Images load straight from the museum as <img> (no CORS needed outside WebGL);
this only adds each work's proportions so the grid can lay out uncropped.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).parent
js = (ROOT.parent / "grid" / "data.js").read_text()
works = json.loads(js[js.index("{"):js.rindex("}") + 1])["works"]
index = {o["id"]: o for o in json.load(open(ROOT.parent / "grid" / "objects.json"))}

out = []
for w in works:
    o = index.get(int(re.search(r"/objekt/(\d+)", w["url"]).group(1)))
    if not o: continue
    out.append({"src": w["src"], "full": w["full"], "title": w["title"], "artist": w["artist"],
                "date": w["date"], "url": w["url"], "r": round(o["w"] / o["h"], 3)})
(ROOT / "works.json").write_text(json.dumps(out, ensure_ascii=False))
print(len(out), "of", len(works), "works")
