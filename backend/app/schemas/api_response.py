"""Shared API response envelopes for consistent OpenAPI and JSON bodies."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.customer import CustomerPublic


class PaginationMeta(BaseModel):
    page: int = Field(..., ge=1, description="Current page (1-based)")
    limit: int = Field(..., ge=1, description="Page size")
    total: int = Field(..., ge=0, description="Total rows matching the query")
    total_pages: int = Field(..., ge=0, description="Total pages for this limit")


class ErrorInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    details: object | None = None


class ResponseMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pagination: PaginationMeta | None = None


class HealthDatabasePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str


class HealthPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    database: HealthDatabasePayload


class CustomerSingleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: CustomerPublic | None = None
    error: ErrorInfo | None = None
    meta: ResponseMeta | None = None


class CustomerCollectionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: list[CustomerPublic] | None = None
    error: ErrorInfo | None = None
    meta: ResponseMeta | None = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: None = None
    error: ErrorInfo
    meta: None = None


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: HealthPayload | None = None
    error: ErrorInfo | None = None
    meta: ResponseMeta | None = None
