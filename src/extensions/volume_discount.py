"""Extensão 3: desconto progressivo por volume.

3 ou mais unidades do mesmo item recebem 15% de desconto adicional.

Adicionada SEM modificar nenhuma classe existente: é apenas uma nova
:class:`ItemPricingRule`, anexada à cadeia de regras do ``PricingService``
na composição da aplicação.
"""
from __future__ import annotations

from src.models.order_item import OrderItem
from src.strategies.discount_strategy import ItemPricingRule

VOLUME_THRESHOLD = 3
VOLUME_DISCOUNT_FACTOR = 0.85


class VolumeDiscountRule(ItemPricingRule):
    """Aplica 15% de desconto adicional a itens com 3+ unidades."""

    def apply(self, item: OrderItem, current_price: float) -> float:
        if item.quantidade >= VOLUME_THRESHOLD:
            return current_price * VOLUME_DISCOUNT_FACTOR
        return current_price
