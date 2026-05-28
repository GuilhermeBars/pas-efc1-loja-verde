"""Interfaces de persistência (padrão Repository).

A abstração isola o domínio do mecanismo de armazenamento, permitindo
trocar SQLite por outra tecnologia sem afetar os serviços (DIP).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from src.models.order import Order, OrderStatus


class OrderRepository(ABC):
    """Contrato de acesso a pedidos."""

    @abstractmethod
    def save(self, order: Order) -> int:
        """Persiste o pedido e devolve o id gerado."""
        raise NotImplementedError

    @abstractmethod
    def get(self, order_id: int) -> Order | None:
        """Recupera um pedido pelo id, ou ``None`` se não existir."""
        raise NotImplementedError

    @abstractmethod
    def update_status(self, order_id: int, status: OrderStatus) -> None:
        """Atualiza o estado de um pedido."""
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Order]:
        """Lista todos os pedidos."""
        raise NotImplementedError

    @abstractmethod
    def total_by_customer(self, customer_name: str) -> float:
        """Soma o total gasto por um cliente."""
        raise NotImplementedError
