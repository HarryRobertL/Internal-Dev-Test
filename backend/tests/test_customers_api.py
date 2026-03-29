"""HTTP contract tests — isolated DB per test via ``client`` fixture."""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from tests.support.assertions import assert_error_envelope, assert_success_data
from tests.support.factories import customer_json


def _post_customer(client, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/api/customers", json=payload)
    assert response.status_code == 201, response.text
    body = response.json()
    data = assert_success_data(body)
    assert "id" in data and "created_at" in data
    return data


@pytest.mark.parametrize(
    "field",
    ["name", "email", "phone", "request_details"],
)
def test_post_validation_missing_required_field(client, field: str) -> None:
    payload = customer_json()
    del payload[field]
    response = client.post("/api/customers", json=payload)
    assert response.status_code == 422
    err = assert_error_envelope(response.json(), code="validation_error", has_details=True)
    assert isinstance(err["details"], list)
    locs = {tuple(d.get("loc", ())) for d in err["details"]}
    assert any("body" in loc and field in loc for loc in locs)


def test_post_validation_invalid_email(client) -> None:
    response = client.post(
        "/api/customers",
        json=customer_json(email="not-an-email"),
    )
    assert response.status_code == 422
    assert_error_envelope(response.json(), code="validation_error", has_details=True)


def test_post_trims_and_normalises_input(client) -> None:
    data = _post_customer(
        client,
        customer_json(
            name="  Alex  \t Lee ",
            email=" Alex@EXAMPLE.com ",
            phone=" +1  415 \n 555-0100 ",
            request_details="  first line\nsecond line  ",
            response_data="  snapshot  ",
        ),
    )
    assert data["name"] == "Alex Lee"
    assert data["email"] == "alex@example.com"
    assert data["phone"] == "+1 415 555-0100"
    assert data["request_details"] == "first line\nsecond line"
    assert data["response_data"] == "snapshot"


def test_post_response_data_null_when_empty_string(client) -> None:
    data = _post_customer(client, customer_json(response_data="   "))
    assert data["response_data"] is None


def test_get_by_id_round_trip(client) -> None:
    created = _post_customer(client, customer_json())
    cid = created["id"]
    response = client.get(f"/api/customers/{cid}")
    assert response.status_code == 200
    data = assert_success_data(response.json())
    assert data["id"] == cid
    assert data["email"] == "jordan.smith@example.com"


def test_get_by_id_not_found(client) -> None:
    missing = uuid.uuid4()
    response = client.get(f"/api/customers/{missing}")
    assert response.status_code == 404
    err = assert_error_envelope(response.json(), code="not_found", has_details=False)
    assert err["details"] is None
    assert str(missing) in err["message"]


def test_list_pagination_first_page_and_metadata(client) -> None:
    for i in range(25):
        _post_customer(client, customer_json(email=f"user{i}@example.com"))

    r1 = client.get("/api/customers", params={"page": 1, "limit": 10})
    assert r1.status_code == 200
    outer = assert_success_data(r1.json())
    assert "items" in outer and "pagination" in outer
    pag = outer["pagination"]
    assert pag == {
        "page": 1,
        "limit": 10,
        "total": 25,
        "total_pages": 3,
    }
    assert len(outer["items"]) == 10


def test_list_pagination_last_page_partial(client) -> None:
    for i in range(25):
        _post_customer(client, customer_json(email=f"u{i}@example.com"))

    r3 = client.get("/api/customers", params={"page": 3, "limit": 10})
    assert r3.status_code == 200
    outer = assert_success_data(r3.json())
    assert len(outer["items"]) == 5
    assert outer["pagination"]["page"] == 3


def test_list_empty_collection(client) -> None:
    response = client.get("/api/customers", params={"page": 1, "limit": 10})
    assert response.status_code == 200
    outer = assert_success_data(response.json())
    assert outer["items"] == []
    assert outer["pagination"] == {
        "page": 1,
        "limit": 10,
        "total": 0,
        "total_pages": 0,
    }


def test_list_validation_limit_too_large(client) -> None:
    response = client.get("/api/customers", params={"page": 1, "limit": 101})
    assert response.status_code == 422
    assert_error_envelope(response.json(), code="validation_error")


def test_list_validation_page_below_one(client) -> None:
    response = client.get("/api/customers", params={"page": 0, "limit": 10})
    assert response.status_code == 422
    assert_error_envelope(response.json(), code="validation_error")
