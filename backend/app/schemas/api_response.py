"""Shared API response envelopes for consistent OpenAPI and JSON bodies."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.customer import CustomerPublic


class PaginationMeta(BaseModel):
    page: int = Field(..., ge=1, description="Current page (1-based)")
    limit: int = Field(..., ge=1, description="Page size")
    total: int = Field(..., ge=0, description="Total rows matching the query")
    total_pages: int = Field(..., ge=0, description="Total pages for this limit")


class CustomerListPayload(BaseModel):
    items: list[CustomerPublic]
    pagination: PaginationMeta


class CustomerSingleResponse(BaseModel):
    data: CustomerPublic


class CustomerCollectionResponse(BaseModel):
    data: CustomerListPayload


class ErrorInfo(BaseModel):
    code: str
    message: str
    details: object | None = None


class ErrorResponse(BaseModel):
    error: ErrorInfo
