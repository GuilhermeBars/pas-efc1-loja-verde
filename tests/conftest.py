"""Fixtures compartilhadas pelos testes."""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from src.main import AppServices, build_services


class RecordingSink:
    """MessageSink de teste: grava todas as mensagens enviadas."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, str, str]] = []

    def send(self, channel: str, recipient: str, message: str) -> None:
        self.messages.append((channel, recipient, message))

    def channels(self) -> list[str]:
        return [channel for channel, _, _ in self.messages]


@pytest.fixture
def sink() -> RecordingSink:
    return RecordingSink()


@pytest.fixture
def app(tmp_path: Path, sink: RecordingSink) -> Iterator[AppServices]:
    """Aplicação sem extensões: reproduz o comportamento legado."""
    services = build_services(
        db_path=str(tmp_path / "loja.db"), sink=sink, enable_extensions=False
    )
    yield services
    services.repository.close()


@pytest.fixture
def app_ext(tmp_path: Path, sink: RecordingSink) -> Iterator[AppServices]:
    """Aplicação com as três extensões ativadas."""
    services = build_services(
        db_path=str(tmp_path / "loja_ext.db"), sink=sink, enable_extensions=True
    )
    yield services
    services.repository.close()
