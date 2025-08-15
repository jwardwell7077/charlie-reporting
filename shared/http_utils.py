from __future__ import annotations

"""Minimal HTTP utility stubs with absolute imports only.

Provides request ID helper and timestamp utility. Expand later if needed.
"""

import uuid
from datetime import UTC

from shared.service_logging import configure_logging, get_logger

configure_logging()
_log = get_logger("http_utils")


def create_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"


class Constants:
    HEADER_REQUEST_ID = "X-Request-ID"


class DateTimeUtils:
    @staticmethod
    def utc_now():  # pragma: no cover
        from datetime import datetime
        return datetime.now(UTC)


__all__ = ["create_request_id", "Constants", "DateTimeUtils"]