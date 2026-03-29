import uuid

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.schemas.api_response import (
    CustomerCollectionResponse,
    CustomerListPayload,
    CustomerSingleResponse,
    PaginationMeta,
)
from app.schemas.customer import CustomerCreate, CustomerPublic
from app.services import customer_service
from app.utils.errors import customer_not_found

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post(
    "",
    response_model=CustomerSingleResponse,
    status_code=201,
)
def create_customer(body: CustomerCreate, db: DbSession) -> CustomerSingleResponse:
    row = customer_service.create_customer(db, body)
    return CustomerSingleResponse(data=CustomerPublic.model_validate(row))


@router.get(
    "/{customer_id}",
    response_model=CustomerSingleResponse,
)
def get_customer(customer_id: uuid.UUID, db: DbSession) -> CustomerSingleResponse:
    row = customer_service.get_customer_by_id(db, customer_id)
    if row is None:
        raise customer_not_found(customer_id)
    return CustomerSingleResponse(data=CustomerPublic.model_validate(row))


@router.get("", response_model=CustomerCollectionResponse)
def list_customers(
    db: DbSession,
    page: int = Query(1, ge=1, description="1-based page index"),
    limit: int = Query(10, ge=1, le=100, description="Page size"),
) -> CustomerCollectionResponse:
    result = customer_service.list_customers_paginated(db, page=page, limit=limit)
    payload = CustomerListPayload(
        items=[CustomerPublic.model_validate(i) for i in result.items],
        pagination=PaginationMeta(
            page=result.page,
            limit=result.limit,
            total=result.total,
            total_pages=result.total_pages,
        ),
    )
    return CustomerCollectionResponse(data=payload)
