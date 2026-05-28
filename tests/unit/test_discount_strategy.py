"""Testes das estratégias de desconto."""
from __future__ import annotations

import pytest

from src.models.order_item import OrderItem
from src.strategies.discount_strategy import (
    CorporateDiscount,
    NoCustomerDiscount,
    TypeDiscountRule,
    VipDiscount,
)


@pytest.mark.parametrize(
    "tipo, esperado",
    [
        ("normal", 200.0),
        ("desc10", 180.0),
        ("desc20", 160.0),
        ("frete_gratis", 200.0),
        ("desconhecido", 200.0),
    ],
)
def test_type_discount_rule(tipo: str, esperado: float) -> None:
    item = OrderItem("x", 100, 2, tipo)
    rule = TypeDiscountRule()
    assert rule.apply(item, item.subtotal) == esperado


def test_no_customer_discount() -> None:
    assert NoCustomerDiscount().apply(100.0) == 100.0


def test_vip_discount() -> None:
    assert VipDiscount().apply(100.0) == 95.0


def test_corporate_discount() -> None:
    assert CorporateDiscount().apply(100.0) == 90.0
