import requests
import pytest

def test_movies_name_search():
    response = requests.get("http://127.0.0.1:8000/api/movies", params={"query": "The Last Observatory"}, timeout=5)
    assert response.status_code == 200
    data = response.json()
    names = data.get('results', [])
    assert len(names) > 0
    for name in names:
        title = name.get('title')
        print(f"Соответствующие совпадения '{title}'.")
        assert title == "The Last Observatory"

@pytest.mark.parametrize("query", ["coast", "the last", "coa", "c"])
def test_movies_part_name_search(query):
    response = requests.get("http://127.0.0.1:8000/api/movies", params={"query": query}, timeout=5)
    assert response.status_code == 200
    data = response.json()
    names = data.get('results', [])
    assert len(names) > 0
    for name in names:
        title = name.get('title')
        correct_id = name.get('id')
        print(f"Проверяем фильм: '{title}' (ID: {correct_id})")
        assert query.lower() in title.lower()
        ##assert correct_id == 1025

@pytest.mark.parametrize("query", ["", "   "])
def test_movies_empty_query(query: str):
    response_1 = requests.get("http://127.0.0.1:8000/api/movies", timeout=5)
    response_2 = requests.get("http://127.0.0.1:8000/api/movies", params={"query": query}, timeout=5)
    assert response_1.status_code == 200
    assert response_2.status_code == 200
    assert response_1.json() == response_2.json()

@pytest.mark.parametrize("query", ["$", "@", "&", "*"])
def test_movies_part_special_symbol(query):
    response = requests.get("http://127.0.0.1:8000/api/movies", params={"query": query}, timeout=5)
    assert response.status_code == 200
    data = response.json()
    names = data.get('results', [])
    assert len(names) == 0


@pytest.mark.parametrize("page", [0, "abc"])
def test_movies_search_invalid_page(page):
    response = requests.get(
        "http://127.0.0.1:8000/api/movies",
        params={"query": "coast", "page": page},
        timeout=5,
    )
    assert response.status_code == 422
    assert any(error["loc"] == ["query", "page"] for error in response.json()["detail"])


@pytest.mark.parametrize("query", ["1001", "2024"], ids=["movie-id", "release-year"])
def test_movies_search_by_digits(query):
    response = requests.get(
        "http://127.0.0.1:8000/api/movies",
        params={"query": query},
        timeout=5,
    )
    assert response.status_code == 200
    assert response.json()["results"] == []


@pytest.mark.parametrize("query", ["coast", "COAST", "CoAsT"])
def test_movies_search_is_case_insensitive(query):
    response = requests.get(
        "http://127.0.0.1:8000/api/movies",
        params={"query": query},
        timeout=5,
    )
    assert response.status_code == 200
    assert [movie["title"] for movie in response.json()["results"]] == [
        "Where the Coast Ends"
    ]
