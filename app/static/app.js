"use strict";

const grid = document.querySelector("#movies");
const status = document.querySelector("#status");
const summary = document.querySelector("#summary");
const previous = document.querySelector("#previous");
const next = document.querySelector("#next");
const pageLabel = document.querySelector("#page-label");
let currentPage = 1;
let totalPages = 0;
let loading = false;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function placeholder(container) {
  container.replaceChildren(element("span", "poster-placeholder", "No poster available"));
}

function movieCard(movie) {
  const card = element("article", "movie-card");
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
  const meta = element("div", "movie-meta");
  meta.append(element("span", "year", movie.release_date ? movie.release_date.slice(0, 4) : ""));
  meta.append(element("span", "rating", `${movie.rating.toFixed(1)} / 10`));
  card.append(poster, element("h3", "", movie.title), meta);
  card.append(element("p", "overview", movie.overview || "No description available."));
  return card;
}

function updateNavigation() {
  previous.disabled = loading || currentPage <= 1;
  next.disabled = loading || currentPage >= totalPages || currentPage >= 500;
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
    const response = await fetch(`/api/movies?page=${page}`, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("Movie request failed");
    const data = await response.json();
    currentPage = data.page;
    totalPages = data.total_pages;
    grid.replaceChildren(...data.results.map(movieCard));
    status.textContent = data.results.length ? "" : "No movies found";
    status.hidden = data.results.length > 0;
    pageLabel.textContent = totalPages ? `Page ${currentPage} of ${totalPages}` : `Page ${currentPage}`;
    summary.textContent = `${data.total_results} movies · ${data.results.length} on this page`;
  } catch {
    status.className = "status error";
    status.textContent = "Failed to load movies. Check that the server is running, then reload the page.";
    summary.textContent = "Movie data is unavailable.";
    // Keep the previous page as the navigation anchor, so a failed Next can be retried.
  } finally {
    loading = false;
    grid.setAttribute("aria-busy", "false");
    updateNavigation();
  }
}

previous.addEventListener("click", () => loadMovies(currentPage - 1));
next.addEventListener("click", () => loadMovies(currentPage + 1));
loadMovies(1);
