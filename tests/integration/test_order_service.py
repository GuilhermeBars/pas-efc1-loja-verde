"""Testes de integração do fluxo de pedido ponta a ponta."""
from __future__ import annotations

from src.main import AppServices
from src.models.customer import Customer, CustomerType
from src.models.order import OrderStatus
from src.models.order_item import OrderItem
from tests.conftest import RecordingSink


def test_criacao_vip_dispara_email_e_sms(
    app: AppServices, sink: RecordingSink
) -> None:
    app.order_service.create_order(
        Customer("Maria", CustomerType.VIP),
        [OrderItem("p1", 100, 1, "normal")],
    )
    assert "Email" in sink.channels()
    assert "SMS" in sink.channels()


def test_criacao_corporativa_notifica_gerente(
    app: AppServices, sink: RecordingSink
) -> None:
    app.order_service.create_order(
        Customer("Empresa", CustomerType.CORPORATIVO),
        [OrderItem("p1", 100, 1, "normal")],
    )
    assert "GerenteDeConta" in sink.channels()


def test_entrega_concede_pontos_de_fidelidade(
    app: AppServices, sink: RecordingSink
) -> None:
    pedido = app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL),
        [OrderItem("p1", 100, 1, "normal")],
    )
    assert pedido.id is not None
    app.order_service.advance_status(pedido.id, OrderStatus.ENTREGUE)
    assert "Fidelidade" in sink.channels()


def test_advance_status_pedido_inexistente(app: AppServices) -> None:
    assert app.order_service.advance_status(999, OrderStatus.ENVIADO) is None


def test_cancelar_pedido_inexistente(app: AppServices) -> None:
    assert app.order_service.cancel_order(999) is None
