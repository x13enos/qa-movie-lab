# Movie QA Lab — Title search, rating filter and movie details

A learning catalog for black-box QA over HTTP. FastAPI serves the API and a minimal HTML/CSS/JavaScript frontend from the same origin. Implemented: a paginated movie catalog, title search, an inclusive minimum-rating filter, and movie details with direct UI links. QA writes their own tests using `pytest` and `requests`; no ready-made QA tests or exercise solutions are included.

## Installation and startup

Requires **Python 3.12+**. Run commands from the repository root. Installing dependencies requires access to PyPI; once installed, fixture mode works without an external network connection, an API token, or external UI assets.

macOS / Linux:

```bash
cd /path/to/qa-movie-lab
python3 --version  # Must be 3.12 or newer; use python3.12 if needed.
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- UI: http://localhost:8000/
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
- Stop the server with **Ctrl+C**. Run `deactivate` to leave the virtual environment if needed.
- Add `--reload` during development if desired. For HTTP checks, run without reload.
- `/docs` uses the standard Swagger UI CDN assets: its HTML and the OpenAPI schema are available locally, but the interactive interface requires a network connection or cached assets. The catalog itself is fully local in fixture mode.

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `DATA_SOURCE` | `fixture` | `fixture` or `tmdb`; other values cause a startup error |
| `TMDB_READ_TOKEN` | empty | TMDB API Read Access Token; required only for `tmdb` |

Variables are read at startup. `.env` is **not loaded automatically**. To use it:

```bash
cp .env.example .env
# Edit .env as needed; do not publish it.
python -m uvicorn app.main:app --env-file .env --host 127.0.0.1 --port 8000
```

Existing environment variables take precedence over `.env`. Do not commit the token or put it in URLs or frontend code.

### Switching to TMDB

1. Create an account on [TMDB](https://www.themoviedb.org/).
2. Request API access in [Settings → API](https://www.themoviedb.org/settings/api) and copy the **API Read Access Token** (Bearer), not the `API Key`.
3. Stop the server. In `.env`, set `DATA_SOURCE=tmdb` and `TMDB_READ_TOKEN=<your full token>`, without the `Bearer` prefix.
4. Start the server using the `--env-file .env` command above. A valid token and access to the TMDB API and image service are required.
5. To return to demo mode, stop the server, set `DATA_SOURCE=fixture`, and start it again. You may remove the token.

Alternatively, configure the current shell without saving the token in shell history (macOS / Linux):

```bash
export DATA_SOURCE=tmdb
read -r -s TMDB_READ_TOKEN
export TMDB_READ_TOKEN
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# After Ctrl+C:
unset DATA_SOURCE TMDB_READ_TOKEN
```

The backend calls TMDB `GET /3/discover/movie` with `include_adult=false`, `language=en-US`, `sort_by=popularity.desc`, and the requested page. An optional `min_rating` is forwarded as `vote_average.gte` before pagination. A nonblank `query` instead uses `/3/search/movie` with the trimmed title query, `include_adult=false`, `language=en-US` and the requested page. Search cannot be combined with `min_rating` (422); blank queries mean no search. TMDB controls its search matching and order, whereas fixture mode uses a case-insensitive literal title substring. Details use `GET /3/movie/{movie_id}` with `language=en-US`. The token is sent only in the server-side Authorization header. The HTTP timeout is 10 seconds per upstream request; recovering totals for a rejected page may require a second request. Without a token in TMDB mode, `/api/movies` returns a safe `502`, while `/api/health` continues to return `200`. There is no automatic fallback to fixture data.

## Endpoints and manual examples

The primary reference for QA is **[docs/API_CONTRACT.md](docs/API_CONTRACT.md)**.

```bash
curl -i http://localhost:8000/api/health             # 200, {"status":"ok"}
curl -i http://localhost:8000/api/movies             # 200, 20 movies in fixture mode
curl -i 'http://localhost:8000/api/movies?min_rating=8' # 200, 11 fixture movies
curl -i 'http://localhost:8000/api/movies?min_rating=11' # 422
curl -i 'http://localhost:8000/api/movies?query=coast'  # 200, fixture movie 1025
curl -i 'http://localhost:8000/api/movies?query=coast&min_rating=8' # 422, incompatible
curl -i http://localhost:8000/api/movies/1001        # 200, single movie object
curl -i http://localhost:8000/api/movies/999999      # 404
curl -i http://localhost:8000/api/movies/abc         # 422
curl -i 'http://localhost:8000/api/movies?page=2'     # 200, 5 movies in fixture mode
curl -i 'http://localhost:8000/api/movies?page=3'     # 200, results=[] in fixture mode
curl -i 'http://localhost:8000/api/movies?page=0'     # 422
curl -i 'http://localhost:8000/api/movies?page=501'   # 422
curl -i 'http://localhost:8000/api/movies?page=abc'   # 422
curl -i 'http://localhost:8000/api/movies?page=1.5'   # 422
curl -I http://localhost:8000/static/style.css       # 200
curl -i http://localhost:8000/docs                   # 200, HTML
```

Fixture mode contains exactly 25 fictional movies in a fixed order, with IDs 1001–1025. It includes ratings of `0`, `7.9`, `8.0`, `8.1`, and `10.0`, missing dates, a missing poster, and an empty description. Local posters require no network connection. Absolute poster URLs use the current request's origin; compare data stability using the same base URL.

### Using the new UI

Enter a title in **Search by title** and choose **Apply**. While the search field is nonblank, the rating input is disabled with an explanation; applying the search clears any rating. Clear the search to enable rating again. **Reset** clears both fields. Search is submitted only on Apply/Enter, not while typing.

Alternatively, set **Minimum rating** (0–10) and choose **Apply**. Leave it blank or choose **Reset** for all ratings. Applying or resetting starts at page 1; pagination retains the applied search or rating filter. Click a movie title to open its full description, ID, release date, rating and vote count. **Back to catalog** restores the applied search or rating filter and page. Catalog URLs and `/movies/1001` can be shared or opened directly.

## Repository structure

```text
app/
  main.py                 # Application, configuration, frontend
  models.py               # Public response schemas
  routes/movies.py         # Catalog and movie details HTTP endpoints
  providers/
    fixture_provider.py
    tmdb_provider.py
  services/movie_service.py
  static/
    index.html
    movie.html            # Direct movie details page
    style.css
    app.js
    tmdb-logo.svg
    posters/              # Five local SVG illustrations
data/movies.json
docs/API_CONTRACT.md
docs/ROADMAP.md
docs/CHANGES.md
docs/SMOKE_CHECK.md
tests/
  api/                    # QA-authored API tests
  developer/              # Developer regression checks with fixture/mocked upstream
  ui/.gitkeep             # Placeholder for QA-authored UI tests
PRODUCT.md
DESIGN.md
.impeccable/design.json   # Documentation of implemented UI patterns
.env.example
.gitignore
pyproject.toml
README.md
```

Empty `__init__.py` files identify Python packages. Install the project in editable mode from the cloned repository; running a wheel outside the repository is not a supported MVP use case.

## Collaboration

QA uses the public contract, HTTP API, and UI. The `tests/api/` and `tests/ui/` directories are placeholders; QA adds their own dependencies and tests. Use fixture mode for deterministic checks and TMDB for external integration smoke checks. Bug reports should include the environment, reproduction steps, expected and actual results, and the HTTP response. The developer submits small PRs with acceptance criteria; QA independently adds regression coverage.

Sorting, favorites, and authorization are **not implemented**. Each future iteration requires a separate PR and updates to API_CONTRACT and CHANGES; see the [ROADMAP](docs/ROADMAP.md).

## Credits / About

Demo movies and SVG posters are fictional and created for this project; they are not TMDB data.

In TMDB mode, movie data and posters come from [The Movie Database (TMDB)](https://www.themoviedb.org/).

**This product uses the TMDB API but is not endorsed or certified by TMDB.**

The official, unmodified logo is bundled locally as `app/static/tmdb-logo.svg`. Source: https://files.readme.io/29c6fee-blue_short.svg (the logo used in the official TMDB documentation). It appears in Credits less prominently than the application name, with its original proportions and colors preserved.

Official resources:
- [Discover movie](https://developer.themoviedb.org/reference/discover-movie)
- [Application authentication](https://developer.themoviedb.org/docs/authentication-application)
- [FAQ: attribution requirements](https://developer.themoviedb.org/docs/faq)
- [Approved logos and attribution](https://www.themoviedb.org/about/logos-attribution)

Before using TMDB beyond this learning project, review its current terms and licensing requirements.
