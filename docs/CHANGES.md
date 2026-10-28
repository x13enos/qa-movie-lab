# Changes

## 0.3.0 — Title search / API contract 1.2

- Optional trimmed `query`: case-insensitive literal title substring in fixture mode, TMDB `/search/movie` in external mode. Search before pagination; preserve correct totals and query during totals recovery.
- Nonblank search and `min_rating` are mutually exclusive (422); blank search preserves existing behavior.
- UI search field, Apply/Reset, explained disabled rating input, URL/pagination/details/back preservation, loading/empty/error recovery.
- Developer regression tests cover fixture search, compatibility and mocked TMDB forwarding/recovery/errors; independent QA tests remain unchanged.

## 0.2.0 — Rating filter and movie details / API contract 1.1

- Optional inclusive `min_rating` (finite 0–10): filter before pagination, recalculate totals, forward `vote_average.gte` to TMDB including totals recovery.
- `GET /api/movies/{movie_id}`: existing movie schema, 404 for missing movies, 422 for invalid IDs, safe upstream errors.
- UI rating input, apply/reset, URL-preserved filter and page; linked titles open a direct `/movies/{movie_id}` page with full overview and metadata, missing-data/error states and return navigation.
- Existing QA-authored tests preserved; no exercise solutions added.
- Developer verification: fixture HTTP boundary/pagination/detail checks, mocked TMDB forwarding/recovery/errors, desktop/mobile Chromium UI smoke checks, and live TMDB catalog/filter/detail/poster/back-navigation checks.
- Known live TMDB limitation: a direct discover request with `vote_average.gte=10` returned a movie whose `vote_average` was 8.0. The documented upstream parameter is used correctly, but the provider currently passes this inconsistency through. Use fixture mode for deterministic filtering assertions; no page-local filtering workaround is applied.

## 0.1.0 — Iteration 1 / API contract 1.0

- FastAPI API: health endpoint and paginated catalog, JSON validation for page 1–500.
- Default offline fixture: 25 fictional movies, stable order, local SVG posters.
- Optional TMDB discover provider: backend Bearer token, timeout, normalization, and safe 502/503/504 responses.
- Minimal responsive frontend: source label, cards, Previous/Next, loading/empty/error states, Credits.
- README, public API_CONTRACT, and a separate backlog.
- No ready-made QA tests were created. Manual checks are recorded separately in SMOKE_CHECK.

Sorting, favorites, controlled failure scenarios and UI automation exercises remain in the backlog.
