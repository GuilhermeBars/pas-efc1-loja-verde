"""Validação de estoque, isolada atrás de uma interface (ISP/DIP)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from src.models.order_item import OrderItem


class StockService(ABC):
    """Contrato de verificação de disponibilidade de estoque."""

    @abstractmethod
    def is_available(self, items: Sequence[OrderItem]) -> bool:
        """Indica se há estoque para todos os itens."""
        raise NotImplementedError


class InMemoryStockService(StockService):
    """Estoque em memória (placeholder do sistema externo futuro)."""

    def __init__(self, stock: dict[str, int]) -> None:
        self._stock = dict(stock)

    def is_available(self, items: Sequence[OrderItem]) -> bool:
        return all(
            item.nome in self._stock and self._stock[item.nome] >= item.quantidade
            for item in items
        )
