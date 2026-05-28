"""Padrão Factory Method para criação de pedidos por tipo de cliente.

Cada fábrica concreta sabe montar a *família* de colaboradores de um tipo
de cliente: sua estratégia de desconto e seus canais de notificação. Novos
tipos de cliente entram como novas fábricas, sem alterar as existentes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from src.models.customer import Customer
from src.models.order import Order
from src.models.order_item import OrderItem
from src.observers.notification_observer import (
    AccountManagerChannel,
    EmailChannel,
    LoyaltyChannel,
    MessageSink,
    NotificationChannel,
    SmsChannel,
)
from src.services.pricing_service import PricingService
from src.strategies.discount_strategy import (
    CorporateDiscount,
    CustomerDiscountStrategy,
    NoCustomerDiscount,
    VipDiscount,
)


class OrderFactory(ABC):
    """Cria pedidos e a família de colaboradores de um tipo de cliente."""

    def __init__(self, pricing: PricingService, sink: MessageSink) -> None:
        self._pricing = pricing
        self._sink = sink

    @abstractmethod
    def discount_strategy(self) -> CustomerDiscountStrategy:
        """Estratégia de desconto do cliente."""
        raise NotImplementedError

    @abstractmethod
    def notification_channels(self) -> list[NotificationChannel]:
        """Canais de notificação próprios deste tipo de cliente."""
        raise NotImplementedError

    def create_order(
        self, customer: Customer, items: Sequence[OrderItem], criado_em: str
    ) -> Order:
        total = self._pricing.calculate(items, self.discount_strategy())
        return Order(
            customer=customer,
            items=list(items),
            total=total,
            criado_em=criado_em,
        )


class NormalOrderFactory(OrderFactory):
    """Pedido de cliente comum: e-mail e fidelidade simples."""

    def discount_strategy(self) -> CustomerDiscountStrategy:
        return NoCustomerDiscount()

    def notification_channels(self) -> list[NotificationChannel]:
        return [EmailChannel(self._sink), LoyaltyChannel(self._sink, 1.0)]


class VipOrderFactory(OrderFactory):
    """Pedido VIP: e-mail, SMS e fidelidade em dobro."""

    def discount_strategy(self) -> CustomerDiscountStrategy:
        return VipDiscount()

    def notification_channels(self) -> list[NotificationChannel]:
        return [
            EmailChannel(self._sink),
            SmsChannel(self._sink),
            LoyaltyChannel(self._sink, 2.0),
        ]


class CorporateOrderFactory(OrderFactory):
    """Pedido corporativo: e-mail, gerente de conta e fidelidade 1.5x."""

    def discount_strategy(self) -> CustomerDiscountStrategy:
        return CorporateDiscount()

    def notification_channels(self) -> list[NotificationChannel]:
        return [
            EmailChannel(self._sink),
            AccountManagerChannel(self._sink),
            LoyaltyChannel(self._sink, 1.5),
        ]
