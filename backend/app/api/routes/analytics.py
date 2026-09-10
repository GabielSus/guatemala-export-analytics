from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas.analytics import ExportSummaryResponse
from app.application.use_cases.get_export_summary import GetExportSummary
from app.core.database import get_db
from app.infrastructure.repositories.sqlalchemy_export_repository import (
    SQLAlchemyExportRepository,
)


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=ExportSummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    repository = SQLAlchemyExportRepository(db)
    use_case = GetExportSummary(repository)

    try:
        summary = use_case.execute()
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return ExportSummaryResponse(**summary.__dict__)
