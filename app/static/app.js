"use strict";

const status = document.querySelector("#status");
const query = new URLSearchParams(window.location.search);

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function placeholder(container) {
  container.replaceChildren(element("span", "poster-placeholder", "No poster available"));
}

function moviePoster(movie) {
  const poster = element("div", "poster");
  if (movie.poster_url) {
    const image = element("img");
    image.alt = `Poster for ${movie.title}`;
    image.loading = "lazy";
    image.decoding = "async";
    image.addEventListener("error", () => placeholder(poster), { once: true });
    image.src = movie.poster_url;
    poster.append(image);
  } else {
    placeholder(poster);
  }
  return poster;
}

async function loadMovieDetail() {
  const detail = document.querySelector("#movie-detail");
  const back = document.querySelector("#back-to-catalog");
  const context = new URLSearchParams();
  for (const name of ["page", "min_rating"]) {
    if (query.has(name)) context.set(name, query.get(name));
  }
  back.href = context.size ? `/?${context}` : "/";
  const id = window.location.pathname.split("/").pop();
  try {
    const response = await fetch(`/api/movies/${encodeURIComponent(id)}`, {
      headers: { Accept: "application/json" },
    });
    if (response.status === 404) {
      status.textContent = "Movie not found. Return to the catalog to choose another movie.";
      document.title = "Movie not found · Movie QA Lab";
      return;
    }
    if (response.status === 422) {
      status.className = "status error";
      status.textContent = "Invalid movie ID. Return to the catalog to choose a movie.";
      return;
    }
    if (!response.ok) throw new Error("Movie request failed");
    const movie = await response.json();
    document.title = `${movie.title} · Movie QA Lab`;
    document.querySelector("#detail-heading").textContent = movie.title;
    const content = element("div", "detail-content");
    const facts = element("dl", "movie-facts");
    for (const [label, value] of [
      ["Movie ID", movie.id],
      ["Release date", movie.release_date || "Not available"],
      ["Rating", `${movie.rating.toFixed(1)} / 10`],
      ["Votes", movie.vote_count],
    ]) {
      const fact = element("div");
      fact.append(element("dt", "", label), element("dd", "", String(value)));
      facts.append(fact);
    }
    content.append(facts, element("h3", "", "Overview"),
      element("p", "detail-overview", movie.overview || "No description available."));
    detail.replaceChildren(moviePoster(movie), content);
    status.hidden = true;
  } catch {
    status.className = "status error";
    status.textContent = "Failed to load movie. Reload the page to retry, or return to the catalog.";
  } finally {
    detail.setAttribute("aria-busy", "false");
  }
}

function startCatalog() {
  const grid = document.querySelector("#movies");
  const summary = document.querySelector("#summary");
  const previous = document.querySelector("#previous");
  const next = document.querySelector("#next");
  const pageLabel = document.querySelector("#page-label");
  const form = document.querySelector("#rating-filter");
  const ratingInput = document.querySelector("#min-rating");
  const apply = document.querySelector("#apply-filter");
  const reset = document.querySelector("#reset-filter");
  let currentPage = 1;
  let totalPages = 0;
  let loading = false;
  let minRating = query.get("min_rating");
  ratingInput.value = minRating ?? "";

  function catalogQuery(page) {
    const params = new URLSearchParams({ page });
    if (minRating !== null) params.set("min_rating", minRating);
    return params;
  }

  function movieCard(movie) {
    const card = element("article", "movie-card");
    const title = element("h3");
    const link = element("a", "", movie.title);
    link.href = `/movies/${movie.id}?${catalogQuery(currentPage)}`;
    title.append(link);
    const meta = element("div", "movie-meta");
    meta.append(element("span", "year", movie.release_date ? movie.release_date.slice(0, 4) : ""));
    meta.append(element("span", "rating", `${movie.rating.toFixed(1)} / 10`));
    card.append(moviePoster(movie), title, meta,
      element("p", "overview", movie.overview || "No description available."));
    return card;
  }

  function updateNavigation() {
    previous.disabled = loading || currentPage <= 1;
    next.disabled = loading || currentPage >= totalPages || currentPage >= 500;
    ratingInput.disabled = loading;
    apply.disabled = loading;
    reset.disabled = loading;
  }

  async function loadMovies(page) {
    if (loading) return;
    loading = true;
    updateNavigation();
    grid.setAttribute("aria-busy", "true");
    grid.replaceChildren();
    status.hidden = false;
    status.className = "status";
    status.textContent = "Loading";
    summary.textContent = "Loading movies…";
    try {
      const response = await fetch(`/api/movies?${catalogQuery(page)}`, {
        headers: { Accept: "application/json" },
      });
      if (response.status === 422) {
        status.className = "status error";
        status.textContent = "Invalid page or rating. Choose a rating from 0 to 10 and apply the filter to start at page 1.";
        summary.textContent = "Check the catalog parameters.";
        totalPages = 0;
        return;
      }
      if (!response.ok) throw new Error("Movie request failed");
      const data = await response.json();
      currentPage = data.page;
      totalPages = data.total_pages;
      history.replaceState(null, "", `/?${catalogQuery(currentPage)}`);
      grid.replaceChildren(...data.results.map(movieCard));
      status.textContent = data.results.length ? "" : "No movies found. Try a lower minimum rating or reset the filter.";
      status.hidden = data.results.length > 0;
      pageLabel.textContent = totalPages ? `Page ${currentPage} of ${totalPages}` : `Page ${currentPage}`;
      const filterLabel = minRating === null ? "" : ` · minimum rating ${minRating}`;
      summary.textContent = `${data.total_results} movies · ${data.results.length} on this page${filterLabel}`;
    } catch {
      status.className = "status error";
      status.textContent = "Failed to load movies. Check that the server is running, then reload the page or apply the filter to retry.";
      summary.textContent = "Movie data is unavailable.";
    } finally {
      loading = false;
      grid.setAttribute("aria-busy", "false");
      updateNavigation();
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    minRating = ratingInput.value === "" ? null : ratingInput.value;
    currentPage = 1;
    totalPages = 0;
    loadMovies(1);
  });
  reset.addEventListener("click", () => {
    ratingInput.value = "";
    minRating = null;
    currentPage = 1;
    totalPages = 0;
    loadMovies(1);
  });
  previous.addEventListener("click", () => loadMovies(currentPage - 1));
  next.addEventListener("click", () => loadMovies(currentPage + 1));
  loadMovies(query.get("page") ?? 1);
}

if (document.querySelector("#movie-detail")) {
  loadMovieDetail();
} else {
  startCatalog();
}
