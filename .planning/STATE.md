# State

## Current Phase
Phase 2 — Explore (zoomable grid as site navigation).

## Current Focus
Explore is live: 52 content cards, figure + museum visuals (hover skew), search with "Häufig gesucht"
suggestions, category/search resetting each other, overview with category + title, opens on PREMIERE!.
Latest round reviewed as "ok for a first version" for the (now removed) logo view; no open requests.
Next: owner's next direction for Explore — candidates are in Postponed.

## Decided
- Islands/Ring/Particles use the 11 hand-picked works (`islands/build.py`) — the random collection
  sample was rejected ("not happy with the artwork selection").
- Explore: click opens the item at every zoom step (no click-to-zoom); search resets the category to
  Alle and picking a category clears the search (Explore + Browse); filtered sets centre in the window;
  zoom steps 1.4 / 1 / 0.23; overview shows category + title; zoom buttons grey out at the limits; no
  text selection while dragging.
- Explore visuals: no post text, bigger, placed apart (figure left, museum right of centre); figure
  starts black ("Keine Projektion"); museum plain with shadows; slight skew toward the cursor only while
  hovered (camera moves, projection stays put). No drag-rotate — it fought the page's drag-to-pan;
  no mouse-follow when not hovered.
- Explore search: on focus, "Häufig gesucht" suggestions (tickets, hours, current/upcoming exhibitions,
  tours, kids, directions, café, shop, accessibility, contact).
- Ring: clicked work flies out of the ring to the centre, ring stops and fades; Escape/click returns.
- Repo stays public and low-profile: pages get `noindex`, docs describe the work only.

## Postponed
- **Logo overview for Explore** — built and removed 2026-10-02, kept as an option. The overview step
  becomes the logo from `grid/shape.svg` tiled (32 columns) with the posts' images; the page loads on it,
  then zooms into PREMIERE!. Restore: `git revert 54c7c0d` (re-applies commit 3ab0e05; resolve
  conflicts in `explore/index.html` if Explore changed since) — revisit when asked for "the logo view".
- Building pale on white — shadows added; darker material if it still reads too faint.
- Overview captions (2 lines) touch the card below in a few places — 1-line titles if it shows.
- Same zoom steps / 3D on Browse — only if asked.

## Rejected
- Fluid paint, pixel sort — "remove fluid and sort" — 2026-10-02
- Hoffmann squares, flip tiles, louvres — "i dont like them" — 2026-10-02
- Coral growth (reaction-diffusion) — removed — 2026-10-02
- Colour field (1,300 thumbs by hue) — removed — 2026-10-02
- Schiele-based ideas (process, life, letters…) — "abandon that idea" — 2026-10-02
- Open idea list: time stream, mosaic, globe/ring of thumbs, card stack, stroke rebuild, hanging
  canvases, ribbed glass, torch reveal, halftone, letters, similarity galaxy, 2.5D parallax,
  zoom-through — "dont like any of those" — 2026-10-02

## Open Issues
- Explore content is a 2026-10-02 snapshot; events/dates will go stale (re-run scrape + build).
- `figure/figure.glb` is output of a generator whose licence excludes the EU.

## Session Log
### 2026-10-02
Built islands, particles, ring, browse, explore (+ removed fluid, sort, hoffmann, tiles, louvres,
coral, colour). Project files created; Blender sources moved in from the Desktop. Explore iterated:
3D visuals (projection fixed to world space, black default, shadows, hover skew), search suggestions,
filter/search reset, logo overview built then parked (see Postponed). Next: owner's next direction.
