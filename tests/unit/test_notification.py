"""Testes do mecanismo de notificação (Observer)."""
from __future__ import annotations

from src.models.customer import Customer, CustomerType
from src.models.order import Order
from src.models.order_item import OrderItem
from src.observers.notification_observer import (
    EmailChannel,
    LoyaltyChannel,
    OrderEvent,
    OrderEventType,
    OrderNotifier,
    SmsChannel,
)


class _Sink:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str, str]] = []

    def send(self, channel: str, recipient: str, message: str) -> None:
        self.messages.append((channel, recipient, message))


def _order(total: float = 100.0) -> Order:
    return Order(
        customer=Customer("Joao", CustomerType.NORMAL),
        items=[OrderItem("p1", total, 1, "normal")],
        total=total,
    )


def test_email_channel_reage_a_criacao() -> None:
    sink = _Sink()
    notifier = OrderNotifier()
    notifier.subscribe(EmailChannel(sink))
    notifier.publish(OrderEvent(OrderEventType.CREATED, _order()))
    assert sink.messages == [("Email", "Joao", "Pedido recebido!")]


def test_sms_ignora_eventos_de_entrega() -> None:
    sink = _Sink()
    notifier = OrderNotifier()
    notifier.subscribe(SmsChannel(sink))
    notifier.publish(OrderEvent(OrderEventType.DELIVERED, _order()))
    assert sink.messages == []


def test_loyalty_concede_pontos_na_entrega() -> None:
    sink = _Sink()
    notifier = OrderNotifier()
    notifier.subscribe(LoyaltyChannel(sink, 2.0))
    notifier.publish(OrderEvent(OrderEventType.DELIVERED, _order(100.0)))
    assert sink.messages == [("Fidelidade", "Joao", "Cliente ganhou 200 pontos!")]


def test_loyalty_so_dispara_na_entrega() -> None:
    sink = _Sink()
    notifier = OrderNotifier()
    notifier.subscribe(LoyaltyChannel(sink, 1.0))
    notifier.publish(OrderEvent(OrderEventType.APPROVED, _order()))
    assert sink.messages == []
