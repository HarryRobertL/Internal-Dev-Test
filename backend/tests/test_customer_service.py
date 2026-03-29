"""Service-layer behaviour without going through HTTP."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate
from app.services.customer_service import (
    CustomerListResult,
    create_customer,
    get_customer_by_id,
    list_customers_paginated,
)


def _make_payload(**kwargs) -> CustomerCreate:
    base = {
        "name": "Service User",
        "email": "service.user@example.com",
        "phone": "+1 555 0001",
        "request_details": "Internal service test record.",
    }
    base.update(kwargs)
    return CustomerCreate.model_validate(base)


def test_create_persists_normalised_row(db_session: Session) -> None:
    row = create_customer(
        db_session,
        _make_payload(
            name="  Pat  ",
            email="Pat@Example.COM",
        ),
    )
    assert row.id is not None
    assert row.name == "Pat"
    assert row.email == "pat@example.com"
    assert row.response_data is None


def test_get_by_id_returns_none_when_missing(db_session: Session) -> None:
    assert get_customer_by_id(db_session, uuid.uuid4()) is None


def test_list_empty_yields_zero_totals(db_session: Session) -> None:
    result = list_customers_paginated(db_session, page=1, limit=10)
    assert isinstance(result, CustomerListResult)
    assert result.items == []
    assert result.total == 0
    assert result.total_pages == 0
    assert result.page == 1
    assert result.limit == 10


def test_limit_clamped_to_max(db_session: Session) -> None:
    result = list_customers_paginated(db_session, page=1, limit=500)
    assert result.limit == 100


def test_page_below_one_coerced(db_session: Session) -> None:
    create_customer(db_session, _make_payload(email="one@example.com"))
    result = list_customers_paginated(db_session, page=0, limit=10)
    assert result.page == 1
    assert len(result.items) == 1


def test_ordering_newest_first(db_session: Session) -> None:
    first = create_customer(db_session, _make_payload(email="older@example.com"))
    second = create_customer(db_session, _make_payload(email="newer@example.com"))

    # Tie-break: same created_at resolution on SQLite — set explicit timestamps if needed
    older_ts = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    newer_ts = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    r_first = db_session.get(Customer, first.id)
    r_second = db_session.get(Customer, second.id)
    assert r_first is not None and r_second is not None
    r_first.created_at = older_ts
    r_second.created_at = newer_ts
    db_session.commit()

    page = list_customers_paginated(db_session, page=1, limit=10)
    assert [c.id for c in page.items] == [second.id, first.id]


def test_total_pages_math(db_session: Session) -> None:
    for i in range(7):
        create_customer(db_session, _make_payload(email=f"math{i}@example.com"))
    r = list_customers_paginated(db_session, page=1, limit=3)
    assert r.total == 7
    assert r.total_pages == 3
