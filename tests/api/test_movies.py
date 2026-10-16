import requests
def test_movies_api_available():
    response = requests.get("http://127.0.0.1:8000/api/movies", timeout=5)
    assert response.status_code == 200
