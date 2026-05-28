"""Testes de bordas em serviços auxiliares."""
from __future__ import annotations

import re

from src.models.customer import CustomerType
from src.models.order_item import OrderItem
from src.services.clock import SystemClock
from src.services.order_service import OrderService
from src.services.stock_service import InMemoryStockService


def test_system_clock_formato() -> None:
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", SystemClock().now())


def test_estoque_indisponivel_para_item_inexistente() -> None:
    service = InMemoryStockService({"p1": 10})
    assert service.is_available([OrderItem("p1", 1, 1)]) is True
    assert service.is_available([OrderItem("desconhecido", 1, 1)]) is False
    assert service.is_available([OrderItem("p1", 1, 50)]) is False


def test_order_service_sem_fabrica_para_o_tipo() -> None:
    from typing import cast

    from src.repositories.interfaces import OrderRepository

    service = OrderService(
        repository=cast(OrderRepository, object()),
        factories={},
        clock=SystemClock(),
    )
    try:
        service._factory_for(CustomerType.NORMAL)
    except ValueError as exc:
        assert "fábrica" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("esperava ValueError")
