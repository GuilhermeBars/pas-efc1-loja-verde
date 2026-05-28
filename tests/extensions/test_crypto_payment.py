"""Testes da extensão 1: pagamento em criptomoeda."""
from __future__ import annotations

from src.extensions.crypto_payment import CryptoPayment
from src.main import AppServices
from src.models.customer import Customer, CustomerType
from src.models.order import Order, OrderStatus
from src.models.order_item import OrderItem


def test_taxa_de_2_por_cento() -> None:
    order = Order(
        customer=Customer("Joao", CustomerType.NORMAL),
        items=[OrderItem("p1", 100, 1, "normal")],
        total=100.0,
    )
    result = CryptoPayment().charge(order)
    assert result.amount_charged == 102.0
    assert result.auto_approve is True


def test_cripto_aprova_pedido_no_fluxo_completo(app_ext: AppServices) -> None:
    pedido = app_ext.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL),
        [OrderItem("p1", 100, 1, "normal")],
    )
    assert pedido.id is not None
    assert app_ext.payment_service.process(pedido.id, "cripto", 200) is True
    recuperado = app_ext.repository.get(pedido.id)
    assert recuperado is not None
    assert recuperado.status is OrderStatus.APROVADO
