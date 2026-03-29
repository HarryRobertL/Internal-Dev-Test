#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${TEST_DATABASE_URL:-}" ]]; then
  echo "TEST_DATABASE_URL is required (postgresql+psycopg://...)"
  exit 1
fi

if [[ "${TEST_DATABASE_URL}" != postgresql+psycopg://* ]]; then
  echo "TEST_DATABASE_URL must start with postgresql+psycopg://"
  exit 1
fi

export DATABASE_URL="${TEST_DATABASE_URL}"
export APP_ENV=test

alembic upgrade head
pytest -q tests/test_postgres_integration.py
