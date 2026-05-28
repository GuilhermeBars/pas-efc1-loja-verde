"""Testes das fábricas de pedido (Factory Method)."""
from __future__ import annotations

from src.factories.order_factory import (
    CorporateOrderFactory,
    NormalOrderFactory,
    VipOrderFactory,
)
from src.observers.notification_observer import (
    AccountManagerChannel,
    EmailChannel,
    SmsChannel,
)
from src.services.pricing_service import PricingService
from src.strategies.discount_strategy import (
    CorporateDiscount,
    NoCustomerDiscount,
    TypeDiscountRule,
    VipDiscount,
)


class _Sink:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str, str]] = []

    def send(self, channel: str, recipient: str, message: str) -> None:
        self.messages.append((channel, recipient, message))


def _pricing() -> PricingService:
    return PricingService([TypeDiscountRule()])


def test_normal_factory_usa_desconto_neutro() -> None:
    factory = NormalOrderFactory(_pricing(), _Sink())
    assert isinstance(factory.discount_strategy(), NoCustomerDiscount)


def test_vip_factory_inclui_sms() -> None:
    factory = VipOrderFactory(_pricing(), _Sink())
    assert isinstance(factory.discount_strategy(), VipDiscount)
    tipos = [type(c) for c in factory.notification_channels()]
    assert SmsChannel in tipos
    assert EmailChannel in tipos


def test_corporate_factory_inclui_gerente() -> None:
    factory = CorporateOrderFactory(_pricing(), _Sink())
    assert isinstance(factory.discount_strategy(), CorporateDiscount)
    tipos = [type(c) for c in factory.notification_channels()]
    assert AccountManagerChannel in tipos
