import json
from pathlib import Path

from app.models import Movie, MoviePage, PAGE_SIZE


class FixtureProvider:
    def __init__(self, path: Path):
        self.records = json.loads(path.read_text(encoding="utf-8"))
        ids = [item["id"] for item in self.records]
        if len(set(ids)) != len(ids):
            raise ValueError("Fixture movie IDs must be unique")

    async def movies(self, page: int, base_url: str) -> MoviePage:
        start = (page - 1) * PAGE_SIZE
        movies = []
        for record in self.records[start:start + PAGE_SIZE]:
            item = dict(record)
            if item["poster_url"] is not None:
                item["poster_url"] = base_url.rstrip("/") + item["poster_url"]
            movies.append(Movie.model_validate(item))
        total = len(self.records)
        return MoviePage(page=page, total_results=total,
                         total_pages=(total + PAGE_SIZE - 1) // PAGE_SIZE,
                         results=movies)
