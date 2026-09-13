from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analytics import router as analytics_router
from app.api.routes.forecast import router as forecast_router
from app.api.routes.health import router as health_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Analytics API for historical Guatemalan exports by tariff item. "
        "Source: Banco de Guatemala dataset loaded through a validated ETL pipeline."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_origin,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(analytics_router)
app.include_router(forecast_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "project": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "dashboard": settings.frontend_origin,
    }
