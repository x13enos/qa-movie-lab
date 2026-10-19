# Movie QA Lab — public API contract

Version **1.1 / Rating filter and movie details**. The primary reference for independent black-box QA. Base URL: `http://localhost:8000`. All `/api/*` responses, including errors, have `Content-Type: application/json`. Successful responses contain only the documented fields. `GET /` and `/docs` return HTML.

## GET /api/health

Independent of the data source, token, and TMDB availability.

**200 OK**, exact response:

```json
{"status":"ok"}
```

## GET /api/movies

| Query | Type | Default | Constraints |
| --- | --- | --- | --- |
| `page` | integer | `1` | from `1` to `500`, inclusive |

`page` does not accept decimal notation (including `1.0`).

Optional query **`min_rating`**: a finite number from **0 to 10 inclusive**, omitted by default (no filter). Accepts integers and decimals (`8`, `8.0`, `8.1`). Empty, nonnumeric, NaN, infinite and out-of-range values return **422** JSON with a standard `detail` array. `min_rating=0` includes zero-rated movies.

Filter the **entire dataset before pagination**, keeping its original order; include `rating >= min_rating` and recalculate both totals. At 8, exclude 7.9 and include 8.0/8.1. TMDB receives `vote_average.gte`, including when recovering totals; the backend does not filter only the loaded page.

Search and sorting are not available. Unknown query parameters are ignored; this does not imply support for future features. Pass one value per supported parameter.

### 200 OK

Abbreviated fixture example: the full page 1 response contains 20 objects.

```json
{
  "page": 1,
  "page_size": 20,
  "total_results": 25,
  "total_pages": 2,
  "results": [
    {
      "id": 1001,
      "title": "The Last Observatory",
      "overview": "An astronomer discovers a message hidden in the light of a vanished star.",
      "release_date": "2024-01-15",
      "rating": 8.0,
      "vote_count": 120,
      "poster_url": "http://localhost:8000/static/posters/orbit.svg"
    }
  ]
}
```

| Field | Contract |
| --- | --- |
| `page` | integer, requested page |
| `page_size` | integer, always `20` |
| `total_results` | nonnegative integer, size of the entire dataset after any rating filter |
| `total_pages` | integer, `ceil(total_results / 20)`; `0` when there are no results |
| `results` | array of 0 to 20 objects |
| `results[].id` | integer |
| `results[].title` | nonempty string |
| `results[].overview` | string, may be `""` |
| `results[].release_date` | valid `YYYY-MM-DD` date, or `null` for a missing/invalid date |
| `results[].rating` | JSON number, `0 ≤ rating ≤ 10` |
| `results[].vote_count` | nonnegative integer |
| `results[].poster_url` | absolute HTTP(S) image URL or `null` |

The fixture contains 25 fictional movies with unique IDs and a fixed order across restarts. Compare stability using the same base URL: absolute local poster URLs use the request origin.

| Fixture request | HTTP | Number of results | total_results | total_pages |
| --- | --- | --- | --- | --- |
| no page / `page=1` | 200 | 20 | 25 | 2 |
| `page=2` | 200 | 5 | 25 | 2 |
| `page=3` | 200 | 0 | 25 | 2 |
| `page=500` | 200 | 0 | 25 | 2 |

With `min_rating=8`, fixture mode returns 11 movies, `total_results=11`, `total_pages=1`. Page 2 returns an empty array with the same totals. With `min_rating=0`, all 25 movies remain. The table above describes unfiltered requests.

Exact response for unfiltered `page=3`:

```json
{"page":3,"page_size":20,"total_results":25,"total_pages":2,"results":[]}
```

TMDB mode uses the same structure and validation. Movies and totals change in the external service. Selection: non-adult, language en-US, popularity.desc order. A page beyond the dataset returns 200 with empty results and correct totals where possible. If the upstream service rejects the page and totals cannot be retrieved, a safe upstream error is returned, not 500. The TMDB API may limit access to 500 pages even when total_pages is larger; the public page parameter remains limited to 500.

### 422 Unprocessable Entity

Examples: `page=0`, `page=-1`, `page=501`, `page=abc`, `page=1.5`, `page=1.0`, empty `page=`. JSON with a standard `detail` array; error text and additional fields are not part of the stable contract.

Example structure (abbreviated):

```json
{"detail":[{"loc":["query","page"],"msg":"Input should be greater than or equal to 1","type":"greater_than_equal"}]}
```

### TMDB data errors

| Condition | HTTP | Exact body |
| --- | --- | --- |
| Network error, invalid response, upstream HTTP error | 502 | `{"detail":"Movie data is temporarily unavailable"}` |
| TMDB rate limit (429) | 503 | `{"detail":"Movie data is temporarily unavailable"}` |
| Timeout | 504 | `{"detail":"Movie data request timed out"}` |

The same upstream errors apply to movie details. A missing/invalid token in TMDB mode results in 502 for the catalog and details. Tokens, tracebacks, and secrets never appear in client responses. There are no random errors, special fault injection endpoints, or fallback to demo data.

## GET /api/movies/{movie_id}

`movie_id`: positive integer, with no page-related upper limit. Decimal notation (`1001.0`), text, zero and negative IDs return **422** JSON with a standard `detail` array.

**200 OK**: a single movie object, not a page wrapper, with exactly the same fields and types as `results[]`: `id`, `title`, `overview`, `release_date`, `rating`, `vote_count`, `poster_url`. The full description is returned. Fixture IDs 1001–1025 exist and match the list data for the same base URL. Details are independent of list filters and pagination.

**404 Not Found** for a valid but nonexistent ID, exact body:

```json
{"detail":"Movie not found"}
```

TMDB mode calls `/3/movie/{movie_id}` with `language=en-US`, normalizes the response to the same movie schema and maps upstream 404 to this 404. Other upstream failures use the 502/503/504 table above. Tokens remain server-side. TMDB details may change independently of an earlier list response.

## UI and documentation

- `GET /` → **200 HTML**, “Movie QA Lab”, source `Demo data` or `TMDB`.
- Cards: linked title, year when a date is available, rating, short description, poster or placeholder. An empty description does not break the UI.
- Minimum rating: labelled optional number input (0–10), Apply filter and Reset. Both actions start at page 1; pagination keeps the applied filter. Controls are disabled while loading. Blank input means no filter.
- The catalog URL stores `page` and optional `min_rating`; loading/sharing it restores those parameters. Invalid URL parameters show a recoverable validation message.
- Linked titles open `/movies/{movie_id}`: full description, ID, release date, rating, votes, poster, and missing-data fallbacks. Back to catalog preserves the page and applied filter, including after a details reload.
- The detail HTML route returns a 200 shell; the API request determines loading/success/not-found/invalid-ID/error states. Errors offer reload/back recovery.
- `Previous` / `Next`, page number. Previous is disabled on the first page; Next is disabled on the last page, for an empty dataset, and on page 500. Both buttons are disabled while loading.
- States: `Loading`, `No movies found`, `Failed to load movies`, successful grid. The error includes advice to reload the page.
- The UI retrieves the list through `/api/movies` and details through `/api/movies/{movie_id}`. Credits identify the fictional demo data and TMDB as a source without false attribution.
- `GET /docs` → **200 HTML**, standard Swagger UI.
- `GET /openapi.json` → **200 JSON**, machine-readable contract. Swagger uses standard CDN assets.
- `/static/*` — local CSS, JS, and SVG frontend assets, not API endpoints.

## Iteration 1 acceptance criteria

1. After installation and startup as documented, fixture mode works without a token or external network access.
2. Health: exact 200 and `{"status":"ok"}`, independent of TMDB.
3. Movies: 200, documented types/fields; the fixture is stable across repeated requests and restarts.
4. Fixture pages 1/2/3: 20/5/0 objects respectively, totals 25 and 2.
5. Invalid page: 422 JSON, not 500.
6. The UI is responsive, displays cards/navigation, and correctly handles missing posters/descriptions and loading/empty/error states.
7. TMDB with valid credentials retrieves real movies through the backend only and normalizes them to the same contract; errors match the table.
8. README includes installation, startup, shutdown, variables, mode switching, and curl examples.
9. This document is available to QA without requiring implementation knowledge.
10. Ready-made QA automated tests are not supplied: QA creates them independently.

## Rating filter and details acceptance criteria

1. Omitting `min_rating` and using `min_rating=0` preserve the original fixture list and pagination.
2. At 8, exclude 7.9 and include 8.0/8.1 across the whole dataset; fixture totals are 11 and 1. Pages beyond the filtered dataset return 200, empty results and unchanged totals.
3. Invalid ratings return 422 JSON, not 500; finite boundary values 0 and 10 are valid.
4. Every fixture movie is retrievable by ID with the documented fields; nonexistent positive IDs return the exact 404 body, malformed/nonpositive IDs return 422.
5. TMDB filters before pagination and supports details with safe documented upstream errors.
6. UI filtering, reset, pagination, direct details, missing data and back navigation work on desktop and mobile.
7. Swagger/OpenAPI describe both additions; QA tests remain independently authored.

Search, sorting, favorites and authorization are outside this contract. Changes require a new version of this document.
