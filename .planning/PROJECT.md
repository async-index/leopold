# Project

## Overview
Visual explorations around the Leopold Museum: its online collection (onlinecollection.leopoldmuseum.org)
and its website content (leopoldmuseum.org/de). Each idea is a separate page — key visuals for a home
page, ways to browse the collection, and a zoomable grid as an alternative site navigation. The owner
judges every exploration by eye; kept ones stay online, dropped ones are removed from the index.

## Architecture
- Repo root `index.html` = list of live explorations. One folder per exploration, each with `index.html`
  and, where needed, a `build.py` that produces its data/assets.
- Collection data: `grid/objects.json` (3,000-entry index: id, title, artist, date, preview path, w/h),
  `grid/data.js` (1,300 works with thumbs in `grid/thumbs/`). Islands/ring use 11 hand-picked works
  (`islands/works.json`, URLs in `islands/build.py`).
- Site content: `explore/pages.json` (crawl of leopoldmuseum.org/de, 2026-10-02) → `explore/build.py`
  → `items.json` + `images/` (museum originals scaled to 1000px). A snapshot, not live.
- 3D: `figure/figure.glb` (image-to-3D generated), `museum/museum.glb` (hand-built in Blender from
  `blender/build.py`). Artwork projection = triplanar shader in **world space** (see LEARNINGS).
- Live explorations: grid, figure, museum, islands, particles, ring, browse, explore.

## Domain knowledge
- Museum image URLs: `/images/<file>-preview.jpg` (~348px) and `-default.jpg` (~992px long side) —
  the largest available from the collection. Site images: `/media/image/c950x576/<id>.jpg` (fixed crop)
  and `/media/image/original/<id>.jpg` (uncropped, ~4 MB).
- Object links: `onlinecollection.leopoldmuseum.org/en/object/<id>-<slug>/` (ids match `objects.json`).
- The figure's generator licence excludes the EU — `figure/figure.glb` is still that output (residue).

## Decisions (stable)
- Pages stay plain HTML/JS, no framework, no build step for the page itself.
- Shared look: page white `#f9f9f9`, black `#171717`, 9px uppercase monospace; top-left `Leopold` link.
