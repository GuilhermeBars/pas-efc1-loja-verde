"""Cálculo de preço de pedidos a partir de regras intercambiáveis."""
from __future__ import annotations

from collections.abc import Sequence

from src.models.order_item import OrderItem
from src.strategies.discount_strategy import (
    CustomerDiscountStrategy,
    ItemPricingRule,
)


class PricingService:
    """Aplica uma cadeia de regras por item e o desconto do cliente.

    A lista de regras de item é injetada: a configuração base usa apenas o
    desconto por categoria, mas extensões podem adicionar novas regras
    (ex.: desconto por volume) sem alterar esta classe (OCP).
    """

    def __init__(self, item_rules: Sequence[ItemPricingRule]) -> None:
        self._item_rules: list[ItemPricingRule] = list(item_rules)

    def calculate(
        self, items: Sequence[OrderItem], customer_discount: CustomerDiscountStrategy
    ) -> float:
        subtotal = 0.0
        for item in items:
            subtotal += self._price_of(item)
        return customer_discount.apply(subtotal)

    def _price_of(self, item: OrderItem) -> float:
        price = item.subtotal
        for rule in self._item_rules:
            price = rule.apply(item, price)
        return price
