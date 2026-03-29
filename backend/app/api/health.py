from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db.database import get_engine
from app.schemas.api_response import ErrorInfo, HealthDatabasePayload, HealthPayload, HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse | JSONResponse:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        payload = HealthResponse(
            data=None,
            error=ErrorInfo(
                code="service_unavailable",
                message="Database connectivity check failed",
                details=None,
            ),
            meta=None,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=payload.model_dump(mode="json"),
        )

    return HealthResponse(
        data=HealthPayload(
            status="ok",
            database=HealthDatabasePayload(status="ok"),
        ),
        error=None,
        meta=None,
    )
