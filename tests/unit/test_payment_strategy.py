"""Testes das estratégias de pagamento."""
from __future__ import annotations

from src.models.customer import Customer, CustomerType
from src.models.order import Order
from src.models.order_item import OrderItem
from src.strategies.payment_strategy import (
    BoletoPayment,
    CardPayment,
    PixPayment,
)


def _order(total: float = 100.0) -> Order:
    return Order(
        customer=Customer("Joao", CustomerType.NORMAL),
        items=[OrderItem("p1", total, 1, "normal")],
        total=total,
    )


def test_cartao_aprova_automaticamente() -> None:
    result = CardPayment().charge(_order())
    assert result.success is True
    assert result.auto_approve is True


def test_pix_aprova_automaticamente() -> None:
    result = PixPayment().charge(_order())
    assert result.auto_approve is True


def test_boleto_nao_aprova_automaticamente() -> None:
    result = BoletoPayment().charge(_order())
    assert result.success is True
    assert result.auto_approve is False
