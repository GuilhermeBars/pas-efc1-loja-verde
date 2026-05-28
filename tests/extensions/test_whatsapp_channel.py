"""Testes da extensão 2: canal WhatsApp."""
from __future__ import annotations

from src.main import AppServices
from src.models.customer import Customer, CustomerType
from src.models.order_item import OrderItem
from tests.conftest import RecordingSink


def test_whatsapp_notifica_cliente_normal(
    app_ext: AppServices, sink: RecordingSink
) -> None:
    app_ext.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL),
        [OrderItem("p1", 100, 1, "normal")],
    )
    assert "WhatsApp" in sink.channels()


def test_whatsapp_disponivel_para_todos_os_tipos(
    app_ext: AppServices, sink: RecordingSink
) -> None:
    for tipo in CustomerType:
        app_ext.order_service.create_order(
            Customer(f"cliente-{tipo.value}", tipo),
            [OrderItem("p1", 100, 1, "normal")],
        )
    whatsapp = [m for m in sink.messages if m[0] == "WhatsApp"]
    assert len(whatsapp) == len(list(CustomerType))


def test_whatsapp_ausente_sem_extensoes(
    app: AppServices, sink: RecordingSink
) -> None:
    app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL),
        [OrderItem("p1", 100, 1, "normal")],
    )
    assert "WhatsApp" not in sink.channels()
