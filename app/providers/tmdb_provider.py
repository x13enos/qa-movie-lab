import re
from datetime import date

import httpx
from pydantic import ValidationError

from app.models import Movie, MoviePage, PAGE_SIZE
from app.services.movie_service import MovieDataError, MovieNotFoundError


class TMDBProvider:
    def __init__(self, client: httpx.AsyncClient, token: str):
        self.client = client
        self.token = token

    async def request(self, path: str, params: dict) -> httpx.Response:
        if not self.token:
            raise MovieDataError()
        try:
            return await self.client.get(
                f"https://api.themoviedb.org/3/{path}",
                headers={"Authorization": f"Bearer {self.token}"},
                params=params,
            )
        except httpx.TimeoutException:
            raise MovieDataError(504) from None
        except httpx.RequestError:
            raise MovieDataError() from None

    async def discover(self, page: int, min_rating: float | None) -> httpx.Response:
        params = {"include_adult": "false", "language": "en-US",
                  "sort_by": "popularity.desc", "page": page}
        if min_rating is not None:
            params["vote_average.gte"] = min_rating
        return await self.request("discover/movie", params)

    @staticmethod
    def decode_object(response: httpx.Response) -> dict:
        if response.status_code == 429:
            raise MovieDataError(503)
        if response.status_code != 200:
            raise MovieDataError()
        try:
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError()
            return data
        except (ValueError, KeyError, TypeError):
            raise MovieDataError() from None

    @classmethod
    def decode(cls, response: httpx.Response) -> dict:
        data = cls.decode_object(response)
        try:
            total = data["total_results"]
            results = data["results"]
            if type(total) is not int or total < 0:
                raise ValueError()
            if not isinstance(results, list) or len(results) > PAGE_SIZE:
                raise ValueError()
            return data
        except (ValueError, KeyError, TypeError):
            raise MovieDataError() from None

    @staticmethod
    def normalize(record: dict) -> Movie:
        release = record.get("release_date")
        valid_date = None
        if isinstance(release, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", release):
            try:
                valid_date = date.fromisoformat(release)
            except ValueError:
                pass
        poster = record.get("poster_path")
        if poster is not None and poster != "":
            if not isinstance(poster, str) or not re.fullmatch(r"/[A-Za-z0-9_.-]+", poster):
                raise ValueError()
            poster_url = "https://image.tmdb.org/t/p/w500" + poster
        else:
            poster_url = None
        rating = record["vote_average"]
        if type(rating) not in (int, float):
            raise ValueError()
        return Movie(
            id=record["id"], title=record["title"],
            overview="" if record.get("overview") is None else record["overview"],
            release_date=valid_date, rating=rating,
            vote_count=record["vote_count"], poster_url=poster_url,
        )

    async def movie(self, movie_id: int, base_url: str) -> Movie:
        response = await self.request(f"movie/{movie_id}", {"language": "en-US"})
        if response.status_code == 404:
            raise MovieNotFoundError()
        data = self.decode_object(response)
        try:
            movie = self.normalize(data)
            if movie.id != movie_id:
                raise ValueError()
            return movie
        except (ValidationError, ValueError, KeyError, TypeError, AttributeError):
            raise MovieDataError() from None

    async def movies(self, page: int, base_url: str,
                     min_rating: float | None = None) -> MoviePage:
        response = await self.discover(page, min_rating)
        # Some upstreams reject an out-of-range page. Recover totals from page 1,
        # but do not mask other 4xx errors or introduce extra calls on success.
        if page > 1 and response.status_code in (400, 422):
            first = self.decode(await self.discover(1, min_rating))
            total = first["total_results"]
            total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
            if page > total_pages:
                return MoviePage(page=page, total_results=total,
                                 total_pages=total_pages, results=[])
            raise MovieDataError()
        data = self.decode(response)
        total = data["total_results"]
        total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
        try:
            movies = [self.normalize(record) for record in data["results"]]
            return MoviePage(page=page, total_results=total,
                             total_pages=total_pages,
                             results=movies if page <= total_pages else [])
        except (ValidationError, ValueError, KeyError, TypeError, AttributeError):
            raise MovieDataError() from None
