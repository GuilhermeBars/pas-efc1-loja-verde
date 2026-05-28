"""Testes de integração do serviço de pagamento."""
from __future__ import annotations

from src.main import AppServices
from src.models.customer import Customer, CustomerType
from src.models.order_item import OrderItem
from tests.conftest import RecordingSink


def _pedido_id(app: AppServices) -> int:
    pedido = app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL),
        [OrderItem("p1", 100, 1, "normal")],
    )
    assert pedido.id is not None
    return pedido.id


def test_metodo_invalido_retorna_false(
    app: AppServices, sink: RecordingSink
) -> None:
    order_id = _pedido_id(app)
    assert app.payment_service.process(order_id, "cheque", 100) is False
    assert ("Pagamento", "Joao", "Metodo de pagamento invalido!") in sink.messages


def test_pagamento_pedido_inexistente(app: AppServices) -> None:
    assert app.payment_service.process(999, "cartao", 100) is False


def test_valor_insuficiente_avisa(
    app: AppServices, sink: RecordingSink
) -> None:
    order_id = _pedido_id(app)
    assert app.payment_service.process(order_id, "cartao", 10) is False
    assert ("Pagamento", "Joao", "Valor insuficiente!") in sink.messages
