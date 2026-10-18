# Iteration 1 smoke check results

Checks were performed locally on macOS with Python **3.14.5** (requirement: 3.12+), FastAPI 0.143.0, Uvicorn 0.54.0, and httpx 0.28.1. Check commands and temporary browser tools are **not included as a QA suite** and were not added to the project dependencies.

## HTTP: real local server

| Check | Result |
| --- | --- |
| `/api/health` | 200, exact `{"status":"ok"}`, application/json |
| `/api/movies`, `page=1` | 200, 20 records, page_size=20, totals=25/2 |
| `page=2` | 200, 5 records, totals=25/2 |
| `page=3`, `page=500` | 200, 0 records, totals=25/2 |
| `page=0,-1,501,abc,1.5,1.0` and empty page | 422, application/json |
| Repeated fixture requests | Identical JSON responses |
| Fixture restart | Page 1 response matched the original byte for byte |
| Fixture IDs | 25 unique IDs, 1001–1025 |
| `min_rating=8` in the MVP | Unknown parameter ignored; filtering is not implemented |
| `/`, `/docs` | 200, HTML |
| `/openapi.json` | 200, JSON |
| CSS, JS, local poster, TMDB logo | 200, appropriate content type |
| TMDB mode without a token: health | 200, independent of credentials |
| TMDB mode without a token: movies | 502, exact safe detail |

## Browser smoke

Checked in Chromium at desktop 1280×900 and mobile 390×844:

- Page 1: 20 cards, Previous disabled.
- Next → page 2: 5 cards, Next disabled.
- Previous → page 1 works.
- Mobile: no horizontal overflow.
- No JavaScript errors; no external network requests in fixture mode.
- Loading/empty/error states were visually checked by temporarily replacing the HTTP response **in the browser**, not through special application features.
- Loading appears during a delay; an empty dataset shows `No movies found`, with both buttons disabled.
- A substituted 502 response shows `Failed to load movies` with advice to reload.

Desktop/mobile screenshots were reviewed. Visual review verdict: **ship** within the scope of the minimal light MVP. An independent subagent was unavailable, so the visual review was performed in the current session.

### Visual review record

- **persistence:** PRODUCT.md and the design direction contract in HTML are present; DESIGN.md records the actual implementation.
- **fidelity:** TYPE — the system font suits the operating UI; MATERIAL — local SVGs suit the fictional demo; GROUND — a light neutral background; the grid, metadata, Credits, and navigation match the MVP.
- **ceiling:** the chosen minimal catalog design has been achieved; a more complex visual concept and motion are not required.
- **material_fixes:** none within the checked viewports.
- **keep:** preserve the visible mode, clear identification of fictional data, and simple native buttons.

The automated UI detector returned an empty list but ran in degraded regex mode (without HTML/CSS parser modules), so this is **not** full accessibility certification.

## Additional checks

- `python -m pip check`: No broken requirements found.
- Python compileall: passed.
- `node --check app/static/app.js`: passed.

## Check limitations

- **Real TMDB movies were not checked:** no valid TMDB_READ_TOKEN was provided.
- 503 rate limit, 504 timeout, and malformed upstream responses were not reproduced against the real TMDB service. Handlers are implemented; a live integration smoke check remains a separate check requiring credentials.
- This is a basic smoke check, not a ready-made QA test suite, exhaustive regression testing, or cross-browser certification.
