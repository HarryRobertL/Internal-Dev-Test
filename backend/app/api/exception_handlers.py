"""Map framework exceptions to the public JSON error envelope."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _status_to_default_code(http_status: int) -> str:
    mapping: dict[int, str] = {
        status.HTTP_400_BAD_REQUEST: "bad_request",
        status.HTTP_401_UNAUTHORIZED: "unauthorized",
        status.HTTP_403_FORBIDDEN: "forbidden",
        status.HTTP_404_NOT_FOUND: "not_found",
        status.HTTP_409_CONFLICT: "conflict",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "validation_error",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "internal_error",
    }
    return mapping.get(http_status, "http_error")


def _normalise_http_detail(detail: Any, http_status: int) -> dict[str, Any]:
    if isinstance(detail, dict):
        code = str(detail.get("code", _status_to_default_code(http_status)))
        message = str(detail.get("message", "Request failed"))
        if "details" in detail:
            extra = detail.get("details")
        elif "fields" in detail:
            extra = detail.get("fields")
        else:
            extra = None
        return {"code": code, "message": message, "details": extra}
    if isinstance(detail, list):
        return {
            "code": _status_to_default_code(http_status),
            "message": "Request failed",
            "details": detail,
        }
    return {
        "code": _status_to_default_code(http_status),
        "message": str(detail),
        "details": None,
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        body = _normalise_http_detail(exc.detail, exc.status_code)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": body},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        _request: Request,
        _exc: Exception,
    ) -> JSONResponse:
        logger.exception("Unhandled server error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred",
                    "details": None,
                }
            },
        )
