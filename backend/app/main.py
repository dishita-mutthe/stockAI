"""FastAPI entrypoint for the StockAI backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, health
from app.config import get_settings
from app.db import init_db
from app.utils.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="StockAI",
        version="0.1.0",
        description="Multi-agent stock sentiment platform.",
    )

    ## Allows the frontend running on localhost:5173 to make requests to the FastAPI backend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Vite dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(analysis.router, prefix="/api")

    #initialize database when backend starts
    @app.on_event("startup")
    def _startup() -> None:
        init_db()

    return app


app = create_app()
