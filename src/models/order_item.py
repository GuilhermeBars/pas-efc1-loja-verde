"""Entidade de domínio: item de pedido."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderItem:
    """Item de um pedido.

    `tipo` identifica a categoria de desconto aplicável ao item
    (ex.: ``normal``, ``desc10``, ``desc20``, ``frete_gratis``).
    """

    nome: str
    preco: float
    quantidade: int
    tipo: str = "normal"

    @property
    def subtotal(self) -> float:
        """Valor bruto do item, sem qualquer desconto."""
        return self.preco * self.quantidade
