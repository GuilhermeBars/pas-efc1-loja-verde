"""Smoke test: a demonstração de ponta a ponta roda sem erros."""
from __future__ import annotations

from pathlib import Path

import pytest

from src import main as main_module


def test_main_executa_completo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    monkeypatch.chdir(tmp_path)
    main_module.main()
    saida = capsys.readouterr().out
    assert "Pedido 1 criado!" in saida
    assert "RELATORIO DE VENDAS" in saida
    assert "RELATORIO DE CLIENTES" in saida
