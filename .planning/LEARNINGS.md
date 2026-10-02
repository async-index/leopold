# Learnings

Hard-won, project-specific. Kept here instead of the vault (self-contained project, decided 2026-10-02).

## Museum data & assets
- **No CORS on either museum server** — `curl -sI -H "Origin: …" <image>` shows no
  `access-control-allow-origin`. `<img>` works; a WebGL texture from the same URL fails. Bundle local
  copies for anything shader-sampled. `[tested 2026-10-02]`
- **leopoldmuseum.org scraping**: pages are JS-rendered (plain curl gets ~nothing) → use Playwright.
  The cookie banner's `<p>` text pollutes naive paragraph grabs — filter `/Cookie/`. Exhibition pages:
  `.precontent-h1` / `.precontent-h2` / `.precontent-p` (title / subtitle / dates). Event pages: `p.cat`,
  `h1`, `p.eventdate`; `document.title` = `DATE - TITLE | Programm | BESUCH | …`. Only the `c950x576`
  crop and `original` sizes exist under `/media/image/`. `[tested 2026-10-02]`

## 3D
- **Triplanar projection is in world space** (`modelMatrix` in the shader, as in `figure/`): rotating the
  model makes the artwork slide over the body. Keep the model still and orbit the camera. `[tested 2026-10-02]`
- A canvas inside a CSS-scaled container must be re-rendered at the scale
  (`renderer.setPixelRatio(dpr * scale)`) or it blurs/wastes pixels. `[tested 2026-10-02]`

## Interaction
- `setPointerCapture` on the pan container sends the `click` to the container, not to buttons inside
  it — resolve buttons via `document.elementsFromPoint()` in `pointerup`. `[tested 2026-10-02]`
- Centring a filtered set: sort cells by their centre (not top-left corner — that biased the set
  down-right), then centre the view on the bounding box of what is visible. `[tested 2026-10-02]`

## Verification
- **Headless WebGL**: the shared Playwright MCP browser collides with parallel agents, and
  `chrome --headless --screenshot` hangs on always-animating pages. A standalone Playwright works:
  `npm i playwright && npx playwright install chromium`, launch with
  `['--use-angle=metal','--enable-gpu','--ignore-gpu-blocklist']`. `[tested 2026-10-02]`
- Prefer measured checks over eyeballing for checkable claims (offset from centre in px, overlap of
  boxes, canvas sizes, fps over rAF) — and run each new check once against a known-bad version first
  (the overlap and text-selection checks both caught the bug before passing the fix). `[tested 2026-10-02]`
