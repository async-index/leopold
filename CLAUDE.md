# CLAUDE.md — leopold

Design explorations around the Leopold Museum's online collection and website content: one
self-contained page per idea, published together on GitHub Pages. Self-contained project — no
vault entry; state, decisions and learnings all live in `.planning/`.

## Build & Run
- Serve locally: `python3 -m http.server 8808` in the repo root → `http://localhost:8808/<folder>/`
- Deploy: push `main` → GitHub Pages (`https://async-index.github.io/leopold/`). Wait for
  `gh api repos/async-index/leopold/pages/builds/latest --jq '.status+" "+.commit'` = `built <sha>`,
  then curl the live page.
- Data builders (run inside the folder): `grid/build.py`, `islands/build.py`, `ring/build.py`,
  `browse/build.py`, `explore/build.py` (+ `explore/scrape.mjs`, needs `playwright`).
  Blender museum model: `blender/build.py` (usage in its header).

## Key Rules
- **Public repo, kept low-profile**: docs, commits and pages describe the work only — no names of
  people or organisations behind it, no statement of what it is for, nothing personal. Every page carries `<meta name="robots" content="noindex, nofollow">`.
- **The museum's servers send no CORS headers**: `<img>` may hotlink, WebGL may not — anything
  sampled in a shader needs a local copy (see `islands/images/`, `ring/images/`).
- Each exploration = one folder with its own `index.html`; plain JS, no build step; three.js only via
  importmap (jsdelivr `three@0.170.0`). Top-left `Leopold` link to `../` on every page; add the
  folder to the root `index.html` list; remove it from that list when an exploration is dropped.
- Shared look: `--white #f9f9f9`, `--black #171717`, 9px uppercase monospace (`ui-monospace`).
- Verify visually before pushing: headless screenshots + measured checks (see LEARNINGS).

## Build order
UI-first, one exploration at a time. Verify headless, then push — the owner reviews on the live Pages
site — and iterate on what comes back.

## Session start
Read `.planning/STATE.md`. Before touching an area, check `.planning/LEARNINGS.md`.

## Project Context (read on demand)
- `.planning/PROJECT.md` · `ROADMAP.md` · `STATE.md` · `NOTES.md` · `LEARNINGS.md`
- End sessions with the `wrap` skill (learnings go to `.planning/LEARNINGS.md`, not the vault).
