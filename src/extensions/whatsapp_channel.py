"""Extensão 2: canal de notificação WhatsApp (todos os clientes).

Adicionada SEM modificar nenhuma classe existente: é apenas um novo
:class:`NotificationChannel`, inscrito como canal global na composição da
aplicação, ficando disponível para qualquer tipo de cliente.
"""
from __future__ import annotations

from src.observers.notification_observer import (
    NotificationChannel,
    OrderEvent,
    OrderEventType,
)


class WhatsAppChannel(NotificationChannel):
    """Envia mensagem de WhatsApp em todas as transições do pedido."""

    _MESSAGES = {
        OrderEventType.CREATED: "Recebemos seu pedido!",
        OrderEventType.APPROVED: "Pagamento aprovado!",
        OrderEventType.SHIPPED: "Seu pedido foi enviado!",
        OrderEventType.DELIVERED: "Seu pedido foi entregue!",
    }

    def update(self, event: OrderEvent) -> None:
        message = self._MESSAGES.get(event.type)
        if message is not None:
            self._sink.send("WhatsApp", event.order.customer.nome, message)
