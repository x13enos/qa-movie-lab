from typing import Annotated

from fastapi import APIRouter, Path, Query, Request
from fastapi.exceptions import RequestValidationError

from app.models import ErrorResponse, MinRating, Movie, MovieId, MoviePage, PageNumber

router = APIRouter(prefix="/api", tags=["Movies"])


@router.get("/movies", response_model=MoviePage, responses={
    502: {"model": ErrorResponse, "description": "Upstream or network failure"},
    503: {"model": ErrorResponse, "description": "Upstream rate limit"},
    504: {"model": ErrorResponse, "description": "Upstream timeout"},
})
async def movies(
    request: Request,
    page: Annotated[PageNumber, Query()] = 1,
    min_rating: Annotated[MinRating | None, Query()] = None,
    query: Annotated[str | None, Query(description="Title search; cannot be combined with min_rating.")] = None,
):
    if query is not None:
        query = query.strip() or None
    if query is not None and min_rating is not None:
        raise RequestValidationError([{
            "type": "value_error",
            "loc": ("query", "query"),
            "msg": "Title search cannot be combined with min_rating",
            "input": query,
        }])
    return await request.app.state.movie_provider.movies(
        page, str(request.base_url), min_rating, query
    )


@router.get("/movies/{movie_id}", response_model=Movie, responses={
    404: {"model": ErrorResponse, "description": "Movie not found"},
    502: {"model": ErrorResponse, "description": "Upstream or network failure"},
    503: {"model": ErrorResponse, "description": "Upstream rate limit"},
    504: {"model": ErrorResponse, "description": "Upstream timeout"},
})
async def movie(request: Request, movie_id: Annotated[MovieId, Path()]):
    return await request.app.state.movie_provider.movie(movie_id, str(request.base_url))
