"""Padrão Observer aplicado a notificações.

O :class:`OrderNotifier` (sujeito) publica :class:`OrderEvent` para os
canais inscritos (observadores). Cada canal decide quais eventos lhe
interessam, sem que a regra de negócio principal saiba quem está ouvindo.

A saída concreta é delegada a um :class:`MessageSink` (DIP): em produção
imprime no console; em testes, grava as mensagens para verificação.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from src.models.order import Order


class OrderEventType(Enum):
    """Tipos de evento de pedido que disparam notificações."""

    CREATED = "created"
    APPROVED = "approved"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


@dataclass(frozen=True)
class OrderEvent:
    """Evento ocorrido em um pedido."""

    type: OrderEventType
    order: Order


class MessageSink(Protocol):
    """Destino de saída das mensagens de notificação."""

    def send(self, channel: str, recipient: str, message: str) -> None:
        ...


class ConsoleSink:
    """Imprime as mensagens no console (uso em produção)."""

    def send(self, channel: str, recipient: str, message: str) -> None:
        print(f"[{channel}] {recipient}: {message}")


class NotificationChannel(ABC):
    """Observador que reage a eventos de pedido."""

    def __init__(self, sink: MessageSink) -> None:
        self._sink = sink

    @abstractmethod
    def update(self, event: OrderEvent) -> None:
        """Reage a um evento de pedido."""
        raise NotImplementedError


class OrderNotifier:
    """Sujeito do padrão Observer: publica eventos aos canais inscritos."""

    def __init__(self) -> None:
        self._channels: list[NotificationChannel] = []

    def subscribe(self, channel: NotificationChannel) -> None:
        self._channels.append(channel)

    def publish(self, event: OrderEvent) -> None:
        for channel in self._channels:
            channel.update(event)


class EmailChannel(NotificationChannel):
    """Envia e-mail em todas as transições relevantes do pedido."""

    _MESSAGES = {
        OrderEventType.CREATED: "Pedido recebido!",
        OrderEventType.APPROVED: "Pedido aprovado!",
        OrderEventType.SHIPPED: "Pedido enviado!",
        OrderEventType.DELIVERED: "Pedido entregue!",
    }

    def update(self, event: OrderEvent) -> None:
        message = self._MESSAGES.get(event.type)
        if message is not None:
            self._sink.send("Email", event.order.customer.nome, message)


class SmsChannel(NotificationChannel):
    """Envia SMS na criação e na aprovação (clientes VIP)."""

    _MESSAGES = {
        OrderEventType.CREATED: "Pedido VIP recebido!",
        OrderEventType.APPROVED: "Pedido aprovado!",
    }

    def update(self, event: OrderEvent) -> None:
        message = self._MESSAGES.get(event.type)
        if message is not None:
            self._sink.send("SMS", event.order.customer.nome, message)


class AccountManagerChannel(NotificationChannel):
    """Notifica o gerente de conta na criação (clientes corporativos)."""

    def update(self, event: OrderEvent) -> None:
        if event.type is OrderEventType.CREATED:
            self._sink.send(
                "GerenteDeConta",
                event.order.customer.nome,
                "Novo pedido corporativo recebido.",
            )


class LoyaltyChannel(NotificationChannel):
    """Concede pontos de fidelidade quando o pedido é entregue."""

    def __init__(self, sink: MessageSink, multiplier: float) -> None:
        super().__init__(sink)
        self._multiplier = multiplier

    def update(self, event: OrderEvent) -> None:
        if event.type is OrderEventType.DELIVERED:
            points = int(event.order.total * self._multiplier)
            self._sink.send(
                "Fidelidade",
                event.order.customer.nome,
                f"Cliente ganhou {points} pontos!",
            )
