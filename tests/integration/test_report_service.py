"""Testes de integração do serviço de relatórios."""
from __future__ import annotations

from src.main import AppServices
from src.models.customer import Customer, CustomerType
from src.models.order_item import OrderItem


def _popula(app: AppServices) -> None:
    app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL),
        [OrderItem("p1", 100, 1, "normal")],
    )
    app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL),
        [OrderItem("p1", 50, 1, "normal")],
    )
    app.order_service.create_order(
        Customer("Maria", CustomerType.VIP),
        [OrderItem("p1", 100, 1, "normal")],
    )


def test_relatorio_de_vendas(app: AppServices) -> None:
    _popula(app)
    relatorio = app.report_service.sales_report()
    assert "RELATORIO DE VENDAS" in relatorio
    # 100 + 50 + (100 * 0.95) = 245.00
    assert "Total Geral: R$245.00" in relatorio


def test_relatorio_de_clientes_sem_duplicar(app: AppServices) -> None:
    _popula(app)
    relatorio = app.report_service.customers_report()
    assert relatorio.count("Cliente: Joao") == 1
    assert "Total gasto: R$150.00" in relatorio
    assert "Maria" in relatorio
