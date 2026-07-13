const PAGE_SIZE = 6;

const form = document.querySelector("#search-form");
const searchInput = document.querySelector("#search-input");
const categoryFilter = document.querySelector("#category-filter");
const dateFrom = document.querySelector("#date-from");
const dateTo = document.querySelector("#date-to");
const resetButton = document.querySelector("#reset-button");
const grid = document.querySelector("#publication-grid");
const resultCount = document.querySelector("#result-count");
const statusMessage = document.querySelector("#status-message");
const resultsSection = document.querySelector(".results-section");
const loadMoreButton = document.querySelector("#load-more-button");
const cardTemplate = document.querySelector("#publication-card-template");

const dialog = document.querySelector("#article-dialog");
const closeDialogButton = document.querySelector("#close-dialog-button");
const articleContent = document.querySelector("#article-content");
const articleCategory = document.querySelector("#article-category");
const articleTitle = document.querySelector("#article-title");
const articleMeta = document.querySelector("#article-meta");
const articleSummary = document.querySelector("#article-summary");
const articleBody = document.querySelector("#article-body");
const recommendationList = document.querySelector("#recommendation-list");

let offset = 0;
let activeSearch = null;
let activeArticleRequest = null;
let lastFocusedElement = null;

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
}

function formatDate(value) {
  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC"
  }).format(date);
}

async function fetchJson(path, options = {}) {
  const response = await fetch(path, {
    headers: { Accept: "application/json" },
    ...options
  });
  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error("The server returned an unreadable response.");
  }
  if (!response.ok) {
    throw new Error(payload.error || `Request failed (${response.status}).`);
  }
  return payload;
}

function currentFilters() {
  return {
    q: searchInput.value.trim(),
    category: categoryFilter.value,
    date_from: dateFrom.value,
    date_to: dateTo.value
  };
}

function filtersToParams(filters, currentOffset) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value) {
      params.set(key, value);
    }
  }
  params.set("limit", String(PAGE_SIZE));
  params.set("offset", String(currentOffset));
  return params;
}

function updateBrowserUrl(filters) {
  const params = filtersToParams(filters, 0);
  params.delete("limit");
  params.delete("offset");
  const suffix = params.toString();
  window.history.replaceState(null, "", suffix ? `?${suffix}` : window.location.pathname);
}

function createPublicationCard(publication) {
  const fragment = cardTemplate.content.cloneNode(true);
  const card = fragment.querySelector(".publication-card");
  const category = fragment.querySelector(".category-pill");
  const time = fragment.querySelector("time");
  const title = fragment.querySelector("h3");
  const summary = fragment.querySelector(".card-summary");
  const author = fragment.querySelector(".card-author");
  const readButton = fragment.querySelector(".read-button");

  category.textContent = publication.category;
  time.dateTime = publication.publication_date;
  time.textContent = formatDate(publication.publication_date);
  title.textContent = publication.title;
  summary.textContent = publication.summary;
  author.textContent = `By ${publication.author}`;
  readButton.setAttribute("aria-label", `Read ${publication.title}`);
  readButton.addEventListener("click", () => openArticle(publication.publication_id));
  card.dataset.publicationId = String(publication.publication_id);
  return fragment;
}

function renderPublications(items, append) {
  if (!append) {
    grid.replaceChildren();
  }
  const fragment = document.createDocumentFragment();
  for (const publication of items) {
    fragment.append(createPublicationCard(publication));
  }
  grid.append(fragment);
}

async function searchPublications({ append = false } = {}) {
  if (activeSearch) {
    activeSearch.abort();
  }
  activeSearch = new AbortController();
  const filters = currentFilters();
  if (!append) {
    offset = 0;
    updateBrowserUrl(filters);
  }

  resultsSection.setAttribute("aria-busy", "true");
  setStatus(append ? "Loading more publications…" : "Searching publications…");
  loadMoreButton.hidden = true;
  try {
    const params = filtersToParams(filters, offset);
    const data = await fetchJson(`/api/publications?${params}`, {
      signal: activeSearch.signal
    });
    renderPublications(data.items, append);
    offset += data.items.length;
    resultCount.textContent = `${data.total} publication${data.total === 1 ? "" : "s"}`;
    loadMoreButton.hidden = !data.has_more;
    if (data.total === 0) {
      setStatus("No publications match those filters. Try a broader topic or reset the dates.");
    } else {
      setStatus("");
    }
  } catch (error) {
    if (error.name !== "AbortError") {
      if (!append) {
        grid.replaceChildren();
        resultCount.textContent = "Unavailable";
      }
      setStatus(error.message, true);
    }
  } finally {
    resultsSection.setAttribute("aria-busy", "false");
  }
}

function renderRecommendations(items) {
  recommendationList.replaceChildren();
  if (items.length === 0) {
    const empty = document.createElement("p");
    empty.textContent = "No related publications are available yet.";
    recommendationList.append(empty);
    return;
  }

  for (const item of items) {
    const button = document.createElement("button");
    const title = document.createElement("strong");
    const meta = document.createElement("span");
    button.type = "button";
    button.className = "recommendation-button";
    title.textContent = item.title;
    meta.textContent = `${item.category} · ${formatDate(item.publication_date)}`;
    button.append(title, meta);
    button.addEventListener("click", () => openArticle(item.publication_id, false));
    recommendationList.append(button);
  }
}

async function openArticle(publicationId, rememberFocus = true) {
  if (activeArticleRequest) {
    activeArticleRequest.abort();
  }
  activeArticleRequest = new AbortController();
  if (rememberFocus) {
    lastFocusedElement = document.activeElement;
  }

  articleCategory.textContent = "Loading publication";
  articleTitle.textContent = "Loading…";
  articleMeta.textContent = "";
  articleSummary.textContent = "";
  articleBody.replaceChildren();
  recommendationList.replaceChildren();
  if (!dialog.open) {
    dialog.showModal();
  }

  try {
    const [publication, recommendations] = await Promise.all([
      fetchJson(`/api/publications/${publicationId}`, {
        signal: activeArticleRequest.signal
      }),
      fetchJson(`/api/publications/${publicationId}/recommendations?limit=3`, {
        signal: activeArticleRequest.signal
      })
    ]);
    articleCategory.textContent = publication.category;
    articleTitle.textContent = publication.title;
    articleMeta.textContent = `By ${publication.author} · ${formatDate(publication.publication_date)}`;
    articleSummary.textContent = publication.summary;
    const bodyParagraph = document.createElement("p");
    bodyParagraph.textContent = publication.content;
    articleBody.replaceChildren(bodyParagraph);
    renderRecommendations(recommendations.items);
    articleContent.focus();
  } catch (error) {
    if (error.name !== "AbortError") {
      articleCategory.textContent = "Unable to load";
      articleTitle.textContent = "Publication unavailable";
      articleSummary.textContent = error.message;
    }
  }
}

async function loadCategories() {
  try {
    const data = await fetchJson("/api/categories");
    for (const item of data.items) {
      const option = document.createElement("option");
      option.value = item.name;
      option.textContent = `${item.name} (${item.publication_count})`;
      categoryFilter.append(option);
    }
  } catch (error) {
    setStatus(`Categories could not be loaded: ${error.message}`, true);
  }
}

function hydrateFiltersFromUrl() {
  const params = new URLSearchParams(window.location.search);
  searchInput.value = params.get("q") || "";
  categoryFilter.value = params.get("category") || "";
  dateFrom.value = params.get("date_from") || "";
  dateTo.value = params.get("date_to") || "";
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  searchPublications();
});

resetButton.addEventListener("click", () => {
  form.reset();
  searchInput.focus();
  searchPublications();
});

loadMoreButton.addEventListener("click", () => {
  searchPublications({ append: true });
});

closeDialogButton.addEventListener("click", () => dialog.close());

dialog.addEventListener("click", (event) => {
  if (event.target === dialog) {
    dialog.close();
  }
});

dialog.addEventListener("close", () => {
  if (activeArticleRequest) {
    activeArticleRequest.abort();
  }
  if (lastFocusedElement instanceof HTMLElement) {
    lastFocusedElement.focus();
  }
});

async function initialize() {
  await loadCategories();
  hydrateFiltersFromUrl();
  await searchPublications();
}

initialize();

