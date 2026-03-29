"""Customer persistence and queries. Normalisation is applied here as the canonical gate before ORM."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import (
    NAME_MAX_LEN,
    PHONE_MAX_LEN,
    REQUEST_DETAILS_MAX_LEN,
    RESPONSE_DATA_MAX_LEN,
    CustomerCreate,
)
from app.utils.text_sanitize import (
    clean_multiline,
    clean_optional_blob,
    clean_phone,
    clean_single_line,
    normalise_email,
)


@dataclass(frozen=True, slots=True)
class CustomerListResult:
    items: list[Customer]
    total: int
    page: int
    limit: int
    total_pages: int


def _normalised_fields(payload: CustomerCreate) -> dict[str, object]:
    """Defence-in-depth normalisation after Pydantic validation."""
    return {
        "name": clean_single_line(payload.name, max_len=NAME_MAX_LEN),
        "email": normalise_email(str(payload.email)),
        "phone": clean_phone(payload.phone, max_len=PHONE_MAX_LEN),
        "request_details": clean_multiline(
            payload.request_details, max_len=REQUEST_DETAILS_MAX_LEN
        ),
        "response_data": clean_optional_blob(
            payload.response_data, max_len=RESPONSE_DATA_MAX_LEN
        ),
    }


def create_customer(db: Session, payload: CustomerCreate) -> Customer:
    fields = _normalised_fields(payload)
    row = Customer(
        name=str(fields["name"]),
        email=str(fields["email"]),
        phone=str(fields["phone"]),
        request_details=str(fields["request_details"]),
        response_data=fields["response_data"],  # str | None
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_customer_by_id(db: Session, customer_id: uuid.UUID) -> Customer | None:
    return db.get(Customer, customer_id)


def list_customers_paginated(
    db: Session,
    *,
    page: int,
    limit: int,
) -> CustomerListResult:
    safe_page = max(1, page)
    safe_limit = min(max(1, limit), 100)

    total = int(db.scalar(select(func.count()).select_from(Customer)) or 0)
    total_pages = (total + safe_limit - 1) // safe_limit if total > 0 else 0
    offset = (safe_page - 1) * safe_limit

    stmt = (
        select(Customer)
        # Stable ordering prevents record jitter across pages when created_at ties.
        .order_by(Customer.created_at.desc(), Customer.id.desc())
        .offset(offset)
        .limit(safe_limit)
    )
    items = list(db.scalars(stmt).all())

    return CustomerListResult(
        items=items,
        total=total,
        page=safe_page,
        limit=safe_limit,
        total_pages=total_pages,
    )
