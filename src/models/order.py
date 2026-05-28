"""Entidade de domínio: pedido."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.models.customer import Customer
from src.models.order_item import OrderItem


class OrderStatus(Enum):
    """Estados possíveis do ciclo de vida de um pedido."""

    PENDENTE = "pendente"
    APROVADO = "aprovado"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


@dataclass
class Order:
    """Pedido da Loja Verde.

    O total já vem calculado pela camada de serviço (via estratégias de
    desconto); a entidade apenas o armazena junto do estado atual.
    """

    customer: Customer
    items: list[OrderItem]
    total: float
    status: OrderStatus = OrderStatus.PENDENTE
    criado_em: str = ""
    id: int | None = None
