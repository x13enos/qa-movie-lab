import re
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, Field, HttpUrl, StrictInt, StrictStr

PAGE_SIZE = 20


def integer_query(value: object) -> object:
    # FastAPI/Pydantic otherwise accept strings such as "1.0" as integers.
    if isinstance(value, str) and not re.fullmatch(r"[+-]?[0-9]+", value):
        raise ValueError("value must be an integer")
    return value


PageNumber = Annotated[int, Field(ge=1, le=500), BeforeValidator(integer_query)]
MovieId = Annotated[int, Field(ge=1), BeforeValidator(integer_query)]
MinRating = Annotated[float, Field(ge=0, le=10, allow_inf_nan=False)]


class Movie(BaseModel):
    id: StrictInt
    title: Annotated[StrictStr, Field(min_length=1)]
    overview: StrictStr
    release_date: date | None
    rating: Annotated[float, Field(ge=0, le=10, allow_inf_nan=False)]
    vote_count: Annotated[StrictInt, Field(ge=0)]
    poster_url: HttpUrl | None


class MoviePage(BaseModel):
    page: Annotated[StrictInt, Field(ge=1, le=500)]
    page_size: Literal[20] = PAGE_SIZE
    total_results: Annotated[StrictInt, Field(ge=0)]
    total_pages: Annotated[StrictInt, Field(ge=0)]
    results: Annotated[list[Movie], Field(max_length=PAGE_SIZE)]


class Health(BaseModel):
    status: Literal["ok"] = "ok"


class ErrorResponse(BaseModel):
    detail: str
