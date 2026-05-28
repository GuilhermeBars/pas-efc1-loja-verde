"""Padrão Strategy aplicado a descontos.

Há dois eixos de desconto independentes:

* desconto por item, via :class:`ItemPricingRule`;
* desconto por cliente, via :class:`CustomerDiscountStrategy`.

Ambos são abertos para extensão: novas regras são novas classes, sem
necessidade de tocar nas existentes (OCP).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from src.models.order_item import OrderItem


class ItemPricingRule(ABC):
    """Regra de precificação aplicada a um único item.

    Recebe o preço corrente (já possivelmente ajustado por regras
    anteriores) e devolve o novo preço, permitindo encadear regras.
    """

    @abstractmethod
    def apply(self, item: OrderItem, current_price: float) -> float:
        """Devolve o preço do item após aplicar a regra."""
        raise NotImplementedError


class TypeDiscountRule(ItemPricingRule):
    """Desconto baseado na categoria (``tipo``) do item."""

    _FACTORS = {
        "normal": 1.0,
        "desc10": 0.9,
        "desc20": 0.8,
        "frete_gratis": 1.0,
    }

    def apply(self, item: OrderItem, current_price: float) -> float:
        factor = self._FACTORS.get(item.tipo, 1.0)
        return current_price * factor


class CustomerDiscountStrategy(ABC):
    """Desconto aplicado sobre o subtotal, conforme o tipo de cliente."""

    @abstractmethod
    def apply(self, subtotal: float) -> float:
        """Devolve o total após o desconto do cliente."""
        raise NotImplementedError


class NoCustomerDiscount(CustomerDiscountStrategy):
    """Cliente comum: sem desconto adicional."""

    def apply(self, subtotal: float) -> float:
        return subtotal


class VipDiscount(CustomerDiscountStrategy):
    """Cliente VIP: 5% de desconto sobre o subtotal."""

    def apply(self, subtotal: float) -> float:
        return subtotal * 0.95


class CorporateDiscount(CustomerDiscountStrategy):
    """Cliente corporativo: 10% de desconto sobre o subtotal."""

    def apply(self, subtotal: float) -> float:
        return subtotal * 0.90
