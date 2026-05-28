"""Testes de integração do repositório SQLite."""
from __future__ import annotations

from pathlib import Path

from src.models.customer import Customer, CustomerType
from src.models.order import Order, OrderStatus
from src.models.order_item import OrderItem
from src.repositories.sqlite_order_repository import SqliteOrderRepository


def _order() -> Order:
    return Order(
        customer=Customer("Joao", CustomerType.VIP),
        items=[OrderItem("p1", 100, 2, "desc10")],
        total=180.0,
        criado_em="2026-05-20 10:00:00",
    )


def test_save_e_get_roundtrip(tmp_path: Path) -> None:
    repo = SqliteOrderRepository(str(tmp_path / "t.db"))
    order_id = repo.save(_order())
    recuperado = repo.get(order_id)
    assert recuperado is not None
    assert recuperado.customer.nome == "Joao"
    assert recuperado.customer.tipo is CustomerType.VIP
    assert recuperado.total == 180.0
    assert recuperado.items[0].tipo == "desc10"
    repo.close()


def test_get_inexistente_retorna_none(tmp_path: Path) -> None:
    repo = SqliteOrderRepository(str(tmp_path / "t.db"))
    assert repo.get(999) is None
    repo.close()


def test_update_status(tmp_path: Path) -> None:
    repo = SqliteOrderRepository(str(tmp_path / "t.db"))
    order_id = repo.save(_order())
    repo.update_status(order_id, OrderStatus.ENVIADO)
    recuperado = repo.get(order_id)
    assert recuperado is not None
    assert recuperado.status is OrderStatus.ENVIADO
    repo.close()


def test_total_by_customer(tmp_path: Path) -> None:
    repo = SqliteOrderRepository(str(tmp_path / "t.db"))
    repo.save(_order())
    repo.save(_order())
    assert repo.total_by_customer("Joao") == 360.0
    assert repo.total_by_customer("Ninguem") == 0.0
    repo.close()


def test_list_all(tmp_path: Path) -> None:
    repo = SqliteOrderRepository(str(tmp_path / "t.db"))
    repo.save(_order())
    repo.save(_order())
    assert len(repo.list_all()) == 2
    repo.close()
