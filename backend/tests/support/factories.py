"""Stable request payloads for API and service tests."""

from __future__ import annotations

from typing import Any


def customer_json(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": "Jordan Smith",
        "email": "jordan.smith@example.com",
        "phone": "+44 20 7946 0958",
        "request_details": "Need updated billing contact for our account.",
    }
    payload.update(overrides)
    return payload
