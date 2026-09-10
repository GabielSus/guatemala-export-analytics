from fastapi import FastAPI

from app.api.routes.analytics import router as analytics_router
from app.api.routes.health import router as health_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Analytics API for historical Guatemalan export data.",
)

app.include_router(health_router)
app.include_router(analytics_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": settings.app_name,
        "docs": "/docs",
    }
