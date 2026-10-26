import pytest
import requests


def test_movies_api_available():
    response = requests.get("http://127.0.0.1:8000/api/movies", timeout=5)
    assert response.status_code == 200


def test_movies_response_body():
    response = requests.get("http://127.0.0.1:8000/api/movies", timeout=5)
    assert response.status_code == 200
    data = response.json()

    page = data.get('page')
    assert page == 1

    page_size = data.get('page_size')
    assert page_size == 20

    results = data.get('results')
    assert (isinstance(results, list))
    assert len(results) == 20


def test_movies_rating_filter():
    response = requests.get("http://127.0.0.1:8000/api/movies", params={"min_rating": 8}, timeout=5)
    data = response.json()
    movies = data.get('results', [])
    for movie in movies:
        title = movie.get('title')
        rating = movie.get('rating')
        print(f"Проверяется фильм '{title}'. Рейтинг: {rating}")
        assert movie.get('rating') >= 8

def test_total_results_filter():
    response = requests.get("http://127.0.0.1:8000/api/movies", params={"min_rating": 8}, timeout=5)
    data = response.json()
    total_results = data.get('total_results')
    total_pages = data.get('total_pages')
    print(f"Всего фильмов: {total_results}")
    print(f"Всего страниц: {total_pages}")
    assert total_results == 11
    assert total_pages == 1

def test_second_page():
    response = requests.get("http://127.0.0.1:8000/api/movies", params={"min_rating": 8, "page": 2}, timeout=5)
    data = response.json()
    total_results = data.get('total_results')
    total_pages = data.get('total_pages')
    result = data.get('results')
    assert result == []
    assert total_results == 11
    assert total_pages == 1

def test_boundary_values_zero():
    response = requests.get("http://127.0.0.1:8000/api/movies", params={"min_rating": 0}, timeout=5)
    assert response.status_code == 200

def test_boundary_values_ten():
    response = requests.get("http://127.0.0.1:8000/api/movies", params={"min_rating": 10}, timeout=5)
    assert response.status_code == 200

@pytest.mark.parametrize("rating", [100, -1, "test"])
def test_unprocessable_content(rating):
    response = requests.get("http://127.0.0.1:8000/api/movies", params={"min_rating": rating}, timeout=5)
    assert response.status_code == 422

def test_movies_api_id():
    response = requests.get("http://127.0.0.1:8000/api/movies/1025", timeout=5)
    print(response.json())
    assert response.status_code == 200

def test_movies_api_id_nonexistent():
    response = requests.get("http://127.0.0.1:8000/api/movies/999999", timeout=5)
    print(response.json())
    assert response.status_code == 404

def test_movies_api_id_invalid():
    response = requests.get("http://127.0.0.1:8000/api/movies/abc", timeout=5)
    print(response.json())
    assert response.status_code == 422