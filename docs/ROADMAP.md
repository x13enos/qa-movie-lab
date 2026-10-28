# Roadmap

Implemented through 0.3.0: minimum-rating filter (original Iteration 2), title search (Iteration 3) and movie details (original Iteration 5), including UI. Remaining items below are not implemented.

Each iteration requires a separate PR, a new version of `API_CONTRACT.md`, an entry in `CHANGES.md`, and independent black-box tests written by QA. Incomplete features must not appear as working UI controls.

- **Iteration 4 — Sorting:** sort by rating and date; agree on the contract.
- **Iteration 6 — Favorites:** local add/remove operations; a database requires a separate decision.
- **Iteration 7 — Failure scenarios:** controlled external responses/errors for black-box testing.
- **Iteration 8 — UI automation:** a separate Playwright stage, with tests written by QA.

CI/GitHub Actions comes later, after the first QA tests are added. The MVP does not include a database, authentication, Docker, cloud infrastructure, or microservices.
