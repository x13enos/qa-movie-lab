from typing import Annotated

from fastapi import APIRouter, Query, Request

from app.models import ErrorResponse, MoviePage, PageNumber

router = APIRouter(prefix="/api", tags=["Movies"])


@router.get("/movies", response_model=MoviePage, responses={
    502: {"model": ErrorResponse, "description": "Upstream or network failure"},
    503: {"model": ErrorResponse, "description": "Upstream rate limit"},
    504: {"model": ErrorResponse, "description": "Upstream timeout"},
})
async def movies(request: Request, page: Annotated[PageNumber, Query()] = 1):
    return await request.app.state.movie_provider.movies(page, str(request.base_url))
