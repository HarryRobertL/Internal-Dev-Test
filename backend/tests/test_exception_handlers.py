"""Behaviour of the global exception handlers registered on the FastAPI app."""

from __future__ import annotations

import uuid

import app.api.customers as customers_api
from tests.support.assertions import assert_error_envelope


def test_unhandled_exception_returns_internal_error_envelope(client, monkeypatch) -> None:
    def boom(_db, _cid: uuid.UUID):
        raise RuntimeError("deliberate failure for 500 handler")

    monkeypatch.setattr(customers_api.customer_service, "get_customer_by_id", boom)

    response = client.get(f"/api/customers/{uuid.uuid4()}")
    assert response.status_code == 500
    err = assert_error_envelope(
        response.json(),
        code="internal_error",
        has_details=False,
    )
    assert err["message"] == "An unexpected error occurred"
