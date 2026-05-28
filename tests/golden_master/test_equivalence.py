"""Equivalência legado x refatorado.

Roda o sistema legado (``legacy.Sis``) e o refatorado sobre as mesmas
entradas e exige que os totais e estados sejam idênticos. É a rede de
segurança que garante que a refatoração preservou o comportamento.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from legacy import Sis
from src.main import build_services
from src.models.customer import Customer, CustomerType
from src.models.order_item import OrderItem

CASOS = [
    (
        "normal",
        CustomerType.NORMAL,
        [
            {"nome": "produto1", "p": 100, "q": 2, "tipo": "normal"},
            {"nome": "produto2", "p": 50, "q": 1, "tipo": "desc10"},
        ],
    ),
    (
        "vip",
        CustomerType.VIP,
        [{"nome": "produto3", "p": 200, "q": 1, "tipo": "desc20"}],
    ),
    (
        "corporativo",
        CustomerType.CORPORATIVO,
        [{"nome": "produto1", "p": 100, "q": 1, "tipo": "normal"}],
    ),
]


@pytest.mark.parametrize("tp_legacy, tp_novo, itens_raw", CASOS)
def test_total_identico_ao_legado(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    tp_legacy: str,
    tp_novo: CustomerType,
    itens_raw: list,
) -> None:
    monkeypatch.chdir(tmp_path)
    legado = Sis()
    id_legado = legado.add_ped("Cliente", itens_raw, tp_legacy)
    total_legado = legado.get_ped(id_legado)["tot"]
    legado.close()

    app = build_services(
        db_path=str(tmp_path / "novo.db"), enable_extensions=False
    )
    itens = [
        OrderItem(i["nome"], i["p"], i["q"], i["tipo"]) for i in itens_raw
    ]
    pedido = app.order_service.create_order(Customer("Cliente", tp_novo), itens)
    app.repository.close()

    assert pedido.total == pytest.approx(total_legado)
