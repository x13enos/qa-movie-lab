import json
from pathlib import Path

from app.models import Movie, MoviePage, PAGE_SIZE
from app.services.movie_service import MovieNotFoundError


class FixtureProvider:
    def __init__(self, path: Path):
        self.records = json.loads(path.read_text(encoding="utf-8"))
        ids = [item["id"] for item in self.records]
        if len(set(ids)) != len(ids):
            raise ValueError("Fixture movie IDs must be unique")

    @staticmethod
    def normalize(record: dict, base_url: str) -> Movie:
        item = dict(record)
        if item["poster_url"] is not None:
            item["poster_url"] = base_url.rstrip("/") + item["poster_url"]
        return Movie.model_validate(item)

    async def movie(self, movie_id: int, base_url: str) -> Movie:
        for record in self.records:
            if record["id"] == movie_id:
                return self.normalize(record, base_url)
        raise MovieNotFoundError()

    async def movies(self, page: int, base_url: str,
                     min_rating: float | None = None,
                     query: str | None = None) -> MoviePage:
        records = [record for record in self.records
                   if (min_rating is None or record["rating"] >= min_rating)
                   and (query is None or query.casefold() in record["title"].casefold())]
        start = (page - 1) * PAGE_SIZE
        movies = [self.normalize(record, base_url)
                  for record in records[start:start + PAGE_SIZE]]
        total = len(records)
        return MoviePage(page=page, total_results=total,
                         total_pages=(total + PAGE_SIZE - 1) // PAGE_SIZE,
                         results=movies)
