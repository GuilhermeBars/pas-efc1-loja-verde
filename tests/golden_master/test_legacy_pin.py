"""Golden Master fixando o comportamento direto do legado (`legacy.Sis`).

Capturado no Sprint 0, antes de qualquer refatoração. Estes valores são a
"verdade" contra a qual a refatoração é validada. Não depende de fixtures
do pacote refatorado. Roda isolando o banco em diretório temporário.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from legacy import Sis


@pytest.fixture
def sis(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    s = Sis()
    yield s
    s.close()


def test_pedido_normal_calcula_total(sis: Sis) -> None:
    itens = [
        {"nome": "produto1", "p": 100, "q": 2, "tipo": "normal"},
        {"nome": "produto2", "p": 50, "q": 1, "tipo": "desc10"},
    ]
    pid = sis.add_ped("Joao Silva", itens, "normal")
    assert sis.get_ped(pid)["tot"] == pytest.approx(245.0)
    assert sis.get_ped(pid)["st"] == "pendente"


def test_pedido_vip_desconto_5(sis: Sis) -> None:
    itens = [{"nome": "p1", "p": 100, "q": 1, "tipo": "normal"}]
    pid = sis.add_ped("Maria", itens, "vip")
    assert sis.get_ped(pid)["tot"] == pytest.approx(95.0)


def test_pagamento_insuficiente_falha(sis: Sis) -> None:
    itens = [{"nome": "p1", "p": 100, "q": 1, "tipo": "normal"}]
    pid = sis.add_ped("Joao", itens, "normal")
    assert sis.proc_pag(pid, "cartao", 50) is False


def test_pix_aprova_automaticamente(sis: Sis) -> None:
    itens = [{"nome": "p1", "p": 100, "q": 1, "tipo": "normal"}]
    pid = sis.add_ped("Joao", itens, "normal")
    sis.proc_pag(pid, "pix", 100)
    assert sis.get_ped(pid)["st"] == "aprovado"


def test_boleto_nao_aprova(sis: Sis) -> None:
    itens = [{"nome": "p1", "p": 100, "q": 1, "tipo": "normal"}]
    pid = sis.add_ped("Joao", itens, "normal")
    sis.proc_pag(pid, "boleto", 100)
    assert sis.get_ped(pid)["st"] == "pendente"
