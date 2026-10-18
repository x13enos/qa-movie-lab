# Backlog — not implemented in the MVP

Each iteration requires a separate PR, a new version of `API_CONTRACT.md`, an entry in `CHANGES.md`, and independent black-box tests written by QA. Incomplete features must not appear as working UI controls.

- **Iteration 2 — Rating filter:** `min_rating` — an optional number from 0 to 10, with an inclusive boundary. Filter the entire dataset **before** pagination and recalculate totals. At 8, exclude 7.9 and include 8.0 and 8.1. For TMDB, use `vote_average.gte` for discover rather than filtering the 20 records already loaded. Invalid values → 422.
- **Iteration 3 — Search:** search by title; agree on the contract separately, using TMDB `/search/movie`.
- **Iteration 4 — Sorting:** sort by rating and date; agree on the contract.
- **Iteration 5 — Movie details:** `GET /api/movies/{id}`, including 404.
- **Iteration 6 — Favorites:** local add/remove operations; a database requires a separate decision.
- **Iteration 7 — Failure scenarios:** controlled external responses/errors for black-box testing.
- **Iteration 8 — UI automation:** a separate Playwright stage, with tests written by QA.

CI/GitHub Actions comes later, after the first QA tests are added. The MVP does not include a database, authentication, Docker, cloud infrastructure, or microservices.
