from __future__ import annotations

from typing import Any


def assert_error_envelope(
    body: dict[str, Any],
    *,
    code: str | None = None,
    has_details: bool | None = None,
) -> dict[str, Any]:
    assert "data" in body, f"expected 'data' key, got keys={body.keys()}"
    assert "meta" in body, f"expected 'meta' key, got keys={body.keys()}"
    assert "error" in body, f"expected error envelope, got keys={body.keys()}"
    assert body["data"] is None
    assert body["meta"] is None
    err = body["error"]
    assert isinstance(err, dict)
    assert "code" in err and "message" in err
    if code is not None:
        assert err["code"] == code, err
    if has_details is True:
        assert "details" in err
        assert err["details"] is not None
    if has_details is False:
        assert err.get("details") is None
    return err


def assert_success_data(body: dict[str, Any]) -> Any:
    assert "error" in body, body
    assert "meta" in body, body
    assert "data" in body, body
    assert body["error"] is None
    return body["data"]
