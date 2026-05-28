"""Abstração de relógio, para desacoplar o domínio de ``datetime.now``."""
from __future__ import annotations

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Fornece o instante atual já formatado."""

    def now(self) -> str:
        ...


class SystemClock:
    """Relógio real do sistema."""

    def now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
