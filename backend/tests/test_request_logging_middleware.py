"""Request logging middleware behaviour."""

from __future__ import annotations

import logging
import uuid
from unittest.mock import patch


def test_adds_request_id_header_when_missing(client) -> None:
    response = client.get("/health")
    request_id = response.headers.get("X-Request-ID")
    assert request_id is not None
    uuid.UUID(request_id)


def test_preserves_incoming_request_id_header(client) -> None:
    response = client.get("/health", headers={"X-Request-ID": "test-request-id"})
    assert response.headers.get("X-Request-ID") == "test-request-id"


def test_logs_method_path_status_duration_and_request_id(client, caplog) -> None:
    with (
        caplog.at_level(logging.INFO, logger="app.middleware.request_logging"),
        patch("app.middleware.request_logging.logger.info") as info_mock,
    ):
        response = client.get("/health", headers={"X-Request-ID": "req-123"})
    assert response.status_code == 200

    info_mock.assert_called_once()
    template, method, path, status, duration_ms, request_id = info_mock.call_args.args
    assert "method=%s path=%s status=%s duration_ms=%s request_id=%s" in template
    assert method == "GET"
    assert path == "/health"
    assert status == 200
    assert isinstance(duration_ms, float)
    assert request_id == "req-123"
