"""Normalise inbound text: trim, strip control characters, collapse whitespace where appropriate."""

from __future__ import annotations

import re

_NULL = "\x00"


def strip_null_bytes(value: str) -> str:
    return value.replace(_NULL, "")


def clean_single_line(value: str, *, max_len: int) -> str:
    """Trim ends, remove NULs, collapse internal whitespace to single spaces, enforce max length."""
    s = strip_null_bytes(value).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:max_len]


def clean_multiline(value: str, *, max_len: int) -> str:
    """Trim ends, remove NULs, normalise line endings; cap length for storage safety."""
    s = strip_null_bytes(value).strip()
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return s[:max_len]


def clean_optional_blob(value: str | None, *, max_len: int) -> str | None:
    if value is None:
        return None
    s = strip_null_bytes(value).strip()
    if not s:
        return None
    return s[:max_len]


def normalise_email(value: str) -> str:
    return strip_null_bytes(value).strip().lower()


def clean_phone(value: str, *, max_len: int) -> str:
    """Allow typical phone characters; collapse internal whitespace."""
    s = strip_null_bytes(value).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:max_len]
