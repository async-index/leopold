# State

## Current Phase
Phase 2 — Explore (zoomable grid as site navigation).

## Current Focus
Explore is live with 52 content cards plus the figure and museum visuals. Waiting on the owner's eye for
the latest round (smaller visuals, black default figure, museum shadows). Next: whatever comes back from review.

## Decided
- Islands/Ring/Particles use the 11 hand-picked works (`islands/build.py`) — the random collection
  sample was rejected ("not happy with the artwork selection").
- Explore: click opens the item at every zoom step (no click-to-zoom); search ignores the category
  filter (resets it to Alle); filtered sets centre in the window; zoom steps 1.4 / 1 / 0.23; overview
  shows category + title; zoom buttons grey out at the limits; no text selection while dragging.
- Explore visuals: no post text, bigger, placed apart (figure left, museum right of centre); figure
  starts black ("Keine Projektion"); museum plain with shadows; rotate by dragging (OrbitControls, as
  in their own pages) — no mouse-follow effect.
- Explore search: on focus, "Häufig gesucht" suggestions (tickets, hours, current/upcoming exhibitions,
  tours, kids, directions, café, shop, accessibility, contact).
- Ring: clicked work flies out of the ring to the centre, ring stops and fades; Escape/click returns.
- Repo stays public and low-profile: pages get `noindex`, docs describe the work only.

## Postponed
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
coral, colour). Project files created; Blender sources moved in from the Desktop. Next: owner's
review of Explore's 3D visuals.
