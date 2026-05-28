"""Geração de relatórios a partir do repositório de pedidos."""
from __future__ import annotations

from src.repositories.interfaces import OrderRepository


class ReportService:
    """Produz relatórios de vendas e de clientes."""

    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def sales_report(self) -> str:
        orders = self._repository.list_all()
        lines = ["=== RELATORIO DE VENDAS ==="]
        total_geral = 0.0
        for order in orders:
            lines.append(
                f"Pedido #{order.id} - Cliente: {order.customer.nome} - "
                f"Total: R${order.total:.2f} - Status: {order.status.value}"
            )
            total_geral += order.total
        lines.append(f"Total Geral: R${total_geral:.2f}")
        return "\n".join(lines)

    def customers_report(self) -> str:
        lines = ["=== RELATORIO DE CLIENTES ==="]
        for nome, tipo in self._distinct_customers():
            total = self._repository.total_by_customer(nome)
            lines.append(f"Cliente: {nome} ({tipo}) - Total gasto: R${total:.2f}")
        return "\n".join(lines)

    def _distinct_customers(self) -> list[tuple[str, str]]:
        seen: list[tuple[str, str]] = []
        for order in self._repository.list_all():
            pair = (order.customer.nome, order.customer.tipo.value)
            if pair not in seen:
                seen.append(pair)
        return seen
