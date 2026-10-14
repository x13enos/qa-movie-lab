import os
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.models import Health
from app.providers.fixture_provider import FixtureProvider
from app.providers.tmdb_provider import TMDBProvider
from app.routes.movies import router
from app.services.movie_service import MovieDataError

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "app" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    source = os.getenv("DATA_SOURCE", "fixture").strip().lower()
    if source not in ("fixture", "tmdb"):
        raise ValueError("DATA_SOURCE must be fixture or tmdb")
    app.state.data_source = source
    if source == "fixture":
        app.state.movie_provider = FixtureProvider(ROOT / "data" / "movies.json")
        yield
    else:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            app.state.movie_provider = TMDBProvider(
                client, os.getenv("TMDB_READ_TOKEN", "").strip()
            )
            yield


app = FastAPI(title="Movie QA Lab", version="0.1.0", lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.exception_handler(MovieDataError)
async def movie_data_error(request: Request, exc: MovieDataError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/api/health", response_model=Health, tags=["Health"])
async def health():
    return Health()


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    source = request.app.state.data_source
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html.replace("{{DATA_SOURCE}}", source).replace(
        "{{MODE_LABEL}}", "Demo data" if source == "fixture" else "TMDB"
    ))
