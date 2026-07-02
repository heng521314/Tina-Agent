from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.gateway.routers import models, suggestions, uploads, skills


def create_app() -> FastAPI:
    app = FastAPI(
        title="Tina-Agent application backend",
        description="a Tina-Agent assistant gateway",
        version="0.0.1",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins="*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(models.router)
    app.include_router(suggestions.router)
    app.include_router(uploads.router)
    app.include_router(skills.router)

    @app.get("/health")
    async def health_check() -> dict:
        return {"status": "healthy", "service": "Tina-Agent gateway"}

    return app


app = create_app()
