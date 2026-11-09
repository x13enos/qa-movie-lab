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
    names = data.get("results")
    assert len(names) == 0
    total_pages = data.get('total_pages')
    total_results = data.get('total_results')
    assert total_pages == 0
    assert total_results == 0


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


@pytest.mark.parametrize("query", ["coast", "COAST", "CoAsT", " COAST "])
def test_movies_search_is_case_and_whitespace(query):
    response = requests.get(
        "http://127.0.0.1:8000/api/movies",
        params={"query": query},
        timeout=5,
    )
    assert response.status_code == 200
    data = response.json()
    total_results = data.get('total_results')
    total_pages = data.get('total_pages')
    assert total_results == 1
    assert total_pages == 1
    assert [movie["title"] for movie in response.json()["results"]] == [
        "Where the Coast Ends"
    ]


@pytest.mark.parametrize("min_rating", [0, 8, 10])
def test_movies_search_rating_filter(min_rating):
    response = requests.get("http://127.0.0.1:8000/api/movies", params={"min_rating": min_rating, "query": "coast"}, timeout=5)
    assert response.status_code == 422
    data = response.json()
    assert isinstance(data["detail"], list)


@pytest.mark.parametrize("query", ["", " "])
def test_movies_empty_search_rating_filter(query):
    response = requests.get("http://127.0.0.1:8000/api/movies", params={"min_rating": 8, "query": query}, timeout=5)
    assert response.status_code == 200
    data = response.json()
    results = data.get('results')
    assert (isinstance(results, list))
    assert results
    for movie in results:
        title = movie.get('title')
        rating = movie.get('rating')
        print(f"Проверяется фильм '{title}'. Рейтинг: {rating}")
        assert rating >= 8
    total_pages = data.get('total_pages')
    total_results = data.get('total_results')
    assert total_pages == 1
    assert total_results == 11
    assert len(results) == 11


@pytest.mark.parametrize("page, expected_count, expected_ids", [(1, 20, [1001, 1002, 1003, 1004, 1005, 1007, 1008, 1009, 1010, 1011,
 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1021, 1022]), (2, 2, [1024, 1025]), (3, 0, [])])
def test_movies_one_symbol_search(page, expected_count, expected_ids):
    response = requests.get("http://127.0.0.1:8000/api/movies", params={"query": "e", "page": page}, timeout=5)
    assert response.status_code == 200
    data = response.json()
    actual_ids = [movie["id"] for movie in data["results"]]
    assert actual_ids == expected_ids
    total_pages = data.get('total_pages')
    total_results = data.get('total_results')
    assert total_pages == 2
    assert total_results == 22
    assert len(data["results"]) == expected_count
