#!/usr/bin/env python3
"""Builds items.json + images/ for the explore page from pages.json.

pages.json comes from scrape.mjs (Playwright, run from a folder with
`playwright` installed): exhibitions, programme and section pages of
leopoldmuseum.org/de. Repeated events are merged into their next date;
images are the museum's uncropped originals, scaled down locally.
"""
import json, re, urllib.request
from io import BytesIO
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).parent
BASE = "https://www.leopoldmuseum.org"
LONG = 1000
# List/overview pages that only repeat other items.
SKIP = {"ausstellungen", "ausstellungen/aktuell", "ausstellungen/vorschau", "besuch/programm", "besuch/programm/",
        "besuch", "museum", "presse", "presse/presseunterlagen", "presse/news", "engagement", "museum/team-und-kontakte",
        "vermietung/infos"}
NAMES = {"besuch": "Besuch", "sammlung": "Sammlung", "ausstellungen": "Ausstellungen", "museum": "Museum",
         "forschung": "Forschung", "engagement": "Engagement", "vermietung": "Vermietung", "presse": "Presse"}

def short(t, n=170):
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + " …"

pages = json.load(open(ROOT / "pages.json"))
items, seen = [], {}
for p in pages:
    path = p["url"].split("/de/", 1)[1].rstrip("/") if "/de/" in p["url"] else ""
    if path in SKIP: continue
    segs = [s.strip() for s in p["doctitle"].split("|")]
    title = p["title"] or segs[0]
    top = path.split("/")[0]
    if "/programm/" in path:
        cat, kicker = "Programm", p["cat"]
        key = (title, p["cat"])
        if key in seen: seen[key]["more"] += 1; continue
    elif re.match(r"ausstellungen/\d+", path):
        cat, kicker = "Ausstellungen", segs[1] if len(segs) > 2 else ""
    else:
        cat, kicker = NAMES.get(top, "Info"), ""
    m = re.search(r"/(\d+)\.jpg$", p["img"])
    it = {"cat": cat, "kicker": kicker, "title": title.strip(), "sub": p["sub"], "when": p["when"],
          "text": short(p["para"]), "url": p["url"], "img": m.group(1) if m else "", "more": 0}
    if "/programm/" in path: seen[(title, p["cat"])] = it
    items.append(it)

(ROOT / "images").mkdir(exist_ok=True)
def fetch(id):
    dest = ROOT / "images" / f"{id}.jpg"
    if not dest.exists():
        try: data = urllib.request.urlopen(f"{BASE}/media/image/original/{id}.jpg").read()
        except Exception: data = urllib.request.urlopen(f"{BASE}/media/image/c950x576/{id}.jpg").read()
        im = Image.open(BytesIO(data)).convert("RGB"); im.thumbnail((LONG, LONG), Image.LANCZOS); im.save(dest, quality=82)
    with Image.open(dest) as im: return id, round(im.width / im.height, 3)
with ThreadPoolExecutor(6) as pool:
    ratio = dict(pool.map(fetch, sorted({i["img"] for i in items if i["img"]})))
for it in items:
    it["r"] = ratio.get(it["img"], 0.75)
    it["img"] = f"images/{it['img']}.jpg" if it["img"] else ""
(ROOT / "items.json").write_text(json.dumps(items, ensure_ascii=False, indent=1))
print(len(items), "items,", len(ratio), "images")
