"""Developer regression checks; independent QA HTTP tests remain unchanged."""
import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("DATA_SOURCE", "fixture")
    with TestClient(app) as client:
        yield client


def test_search_matches_titles_before_pagination(client):
    catalog = []
    for page in (1, 2):
        catalog.extend(client.get("/api/movies", params={"page": page}).json()["results"])
    for query in ("the", "  THE  ", "coast", "The Last Observatory", "' OR 1=1", "不存在"):
        expected = [m for m in catalog if query.strip().casefold() in m["title"].casefold()]
        for page in (1, 2):
            response = client.get("/api/movies", params={"query": query, "page": page})
            assert response.status_code == 200
            data = response.json()
            assert data["results"] == expected[(page - 1) * 20:page * 20]
            assert data["total_results"] == len(expected)
            assert data["total_pages"] == (len(expected) + 19) // 20


def test_empty_search_and_incompatible_parameters(client):
    for query in ("", "   "):
        assert client.get("/api/movies", params={"query": query}).json() == client.get("/api/movies").json()
        assert client.get("/api/movies", params={"query": query, "min_rating": 8}).json() == client.get("/api/movies?min_rating=8").json()
    response = client.get("/api/movies", params={"query": "coast", "min_rating": 0})
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
    assert response.json()["detail"][0]["loc"] == ["query", "query"]


def test_tmdb_search_forwarding_and_totals_recovery(monkeypatch):
    calls = []

    def upstream(request):
        calls.append(request)
        assert request.url.path == "/3/search/movie"
        assert request.url.params["query"] == "Coast & tide"
        assert request.url.params["language"] == "en-US"
        assert request.url.params["include_adult"] == "false"
        assert "vote_average.gte" not in request.url.params
        assert "sort_by" not in request.url.params
        assert request.headers["authorization"] == "Bearer test-token"
        if request.url.params["page"] == "2":
            return httpx.Response(422)
        return httpx.Response(200, json={"total_results": 1, "results": [{
            "id": 42, "title": "Coast & tide", "vote_average": 8,
            "vote_count": 12, "release_date": "2020-01-01", "poster_path": None,
        }]})

    async_client = httpx.AsyncClient
    monkeypatch.setenv("DATA_SOURCE", "tmdb")
    monkeypatch.setenv("TMDB_READ_TOKEN", "test-token")
    monkeypatch.setattr("app.main.httpx.AsyncClient", lambda **kwargs: async_client(
        transport=httpx.MockTransport(upstream), **kwargs))
    with TestClient(app) as client:
        first = client.get("/api/movies", params={"query": "  Coast & tide  "})
        assert first.status_code == 200
        assert first.json()["results"][0]["id"] == 42
        assert first.json()["total_results"] == 1
        second = client.get("/api/movies", params={"query": "Coast & tide", "page": 2})
        assert second.status_code == 200
        assert second.json() == {"page": 2, "page_size": 20, "total_results": 1,
                                 "total_pages": 1, "results": []}
        assert client.get("/api/movies?query=coast&min_rating=8").status_code == 422
    assert [r.url.params["page"] for r in calls] == ["1", "2", "1"]


@pytest.mark.parametrize("upstream_status,expected", [(429, 503), (500, 502)])
def test_tmdb_search_errors(monkeypatch, upstream_status, expected):
    async_client = httpx.AsyncClient
    monkeypatch.setenv("DATA_SOURCE", "tmdb")
    monkeypatch.setenv("TMDB_READ_TOKEN", "test-token")
    monkeypatch.setattr("app.main.httpx.AsyncClient", lambda **kwargs: async_client(
        transport=httpx.MockTransport(lambda request: httpx.Response(upstream_status)), **kwargs))
    with TestClient(app) as client:
        response = client.get("/api/movies?query=coast")
        assert response.status_code == expected
        assert response.json() == {"detail": "Movie data is temporarily unavailable"}
