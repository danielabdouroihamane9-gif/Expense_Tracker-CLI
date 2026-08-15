"""Runtime providers used by application and domain services."""

from datetime import datetime
from typing import Protocol, runtime_checkable
from uuid import UUID, uuid4


@runtime_checkable
class Clock(Protocol):
    """Provide the current local, timezone-aware date and time."""

    def now(self) -> datetime: ...


@runtime_checkable
class UUIDGenerator(Protocol):
    """Provide new stable identifiers for domain entities."""

    def new_uuid(self) -> UUID: ...


class SystemClock:
    """Production clock backed by the operating system."""

    def now(self) -> datetime:
        return datetime.now().astimezone()


class SystemUUIDGenerator:
    """Production UUID generator backed by UUID version 4."""

    def new_uuid(self) -> UUID:
        return uuid4()
