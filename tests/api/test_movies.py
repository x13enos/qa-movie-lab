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

