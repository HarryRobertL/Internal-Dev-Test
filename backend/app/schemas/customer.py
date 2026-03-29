from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.utils.text_sanitize import (
    clean_multiline,
    clean_optional_blob,
    clean_phone,
    clean_single_line,
    normalise_email,
)

NAME_MAX_LEN = 255
PHONE_MAX_LEN = 64
REQUEST_DETAILS_MAX_LEN = 50_000
RESPONSE_DATA_MAX_LEN = 65_535


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=NAME_MAX_LEN)
    email: EmailStr
    phone: str = Field(..., min_length=1, max_length=PHONE_MAX_LEN)
    request_details: str = Field(..., min_length=1, max_length=REQUEST_DETAILS_MAX_LEN)
    response_data: str | None = Field(default=None, max_length=RESPONSE_DATA_MAX_LEN)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: object) -> object:
        if isinstance(value, str):
            return clean_single_line(value, max_len=NAME_MAX_LEN)
        return value

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: object) -> object:
        if isinstance(value, str):
            return normalise_email(value)
        return value

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, value: object) -> object:
        if isinstance(value, str):
            return clean_phone(value, max_len=PHONE_MAX_LEN)
        return value

    @field_validator("request_details", mode="before")
    @classmethod
    def validate_request_details(cls, value: object) -> object:
        if isinstance(value, str):
            return clean_multiline(value, max_len=REQUEST_DETAILS_MAX_LEN)
        return value

    @field_validator("response_data", mode="before")
    @classmethod
    def validate_response_data(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            return clean_optional_blob(value, max_len=RESPONSE_DATA_MAX_LEN)
        return value


class CustomerPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    name: str
    email: str
    phone: str
    request_details: str
    response_data: str | None
