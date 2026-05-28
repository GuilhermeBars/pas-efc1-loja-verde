"""Serviço de aplicação para o ciclo de vida de pedidos."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from src.factories.order_factory import OrderFactory
from src.models.customer import Customer, CustomerType
from src.models.order import Order, OrderStatus
from src.models.order_item import OrderItem
from src.observers.notification_observer import (
    NotificationChannel,
    OrderEvent,
    OrderEventType,
    OrderNotifier,
)
from src.repositories.interfaces import OrderRepository
from src.services.clock import Clock


class OrderService:
    """Cria pedidos, avança seu estado e dispara as notificações.

    Recebe todas as dependências por construtor (injeção explícita): não
    instancia repositórios, fábricas nem canais concretos.
    """

    _STATUS_EVENTS = {
        OrderStatus.APROVADO: OrderEventType.APPROVED,
        OrderStatus.ENVIADO: OrderEventType.SHIPPED,
        OrderStatus.ENTREGUE: OrderEventType.DELIVERED,
    }

    def __init__(
        self,
        repository: OrderRepository,
        factories: Mapping[CustomerType, OrderFactory],
        clock: Clock,
        global_channels: Sequence[NotificationChannel] = (),
    ) -> None:
        self._repository = repository
        self._factories = dict(factories)
        self._clock = clock
        self._global_channels = list(global_channels)

    def create_order(
        self, customer: Customer, items: Sequence[OrderItem]
    ) -> Order:
        factory = self._factory_for(customer.tipo)
        order = factory.create_order(customer, items, self._clock.now())
        order.id = self._repository.save(order)
        self._notify(order, OrderEventType.CREATED)
        return order

    def advance_status(
        self, order_id: int, status: OrderStatus
    ) -> Order | None:
        order = self._repository.get(order_id)
        if order is None:
            return None
        self._repository.update_status(order_id, status)
        order.status = status
        event_type = self._STATUS_EVENTS.get(status)
        if event_type is not None:
            self._notify(order, event_type)
        return order

    def cancel_order(self, order_id: int) -> Order | None:
        return self._set_status(order_id, OrderStatus.CANCELADO)

    def _set_status(
        self, order_id: int, status: OrderStatus
    ) -> Order | None:
        order = self._repository.get(order_id)
        if order is None:
            return None
        self._repository.update_status(order_id, status)
        order.status = status
        return order

    def _notify(self, order: Order, event_type: OrderEventType) -> None:
        notifier = OrderNotifier()
        for channel in self._factory_for(order.customer.tipo).notification_channels():
            notifier.subscribe(channel)
        for channel in self._global_channels:
            notifier.subscribe(channel)
        notifier.publish(OrderEvent(event_type, order))

    def _factory_for(self, tipo: CustomerType) -> OrderFactory:
        factory = self._factories.get(tipo)
        if factory is None:
            raise ValueError(f"Sem fábrica para o tipo de cliente: {tipo}")
        return factory
