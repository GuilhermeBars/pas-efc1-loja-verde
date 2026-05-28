"""Raiz de composição da aplicação (Composition Root).

Aqui, e somente aqui, as dependências concretas são instanciadas e
injetadas. As extensões obrigatórias (criptomoeda, WhatsApp e desconto por
volume) são ativadas apenas adicionando classes novas a esta montagem,
sem alterar nenhuma classe existente.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.extensions.crypto_payment import CryptoPayment
from src.extensions.volume_discount import VolumeDiscountRule
from src.extensions.whatsapp_channel import WhatsAppChannel
from src.factories.order_factory import (
    CorporateOrderFactory,
    NormalOrderFactory,
    OrderFactory,
    VipOrderFactory,
)
from src.models.customer import Customer, CustomerType
from src.models.order import OrderStatus
from src.models.order_item import OrderItem
from src.observers.notification_observer import (
    ConsoleSink,
    MessageSink,
    NotificationChannel,
)
from src.repositories.sqlite_order_repository import SqliteOrderRepository
from src.services.clock import SystemClock
from src.services.order_service import OrderService
from src.services.payment_service import PaymentService
from src.services.pricing_service import PricingService
from src.services.report_service import ReportService
from src.services.stock_service import InMemoryStockService
from src.strategies.discount_strategy import ItemPricingRule, TypeDiscountRule
from src.strategies.payment_strategy import (
    BoletoPayment,
    CardPayment,
    PaymentStrategy,
    PixPayment,
)


@dataclass
class AppServices:
    """Conjunto de serviços já montados e prontos para uso."""

    repository: SqliteOrderRepository
    order_service: OrderService
    payment_service: PaymentService
    report_service: ReportService
    stock_service: InMemoryStockService


def build_services(
    db_path: str = "loja.db",
    sink: MessageSink | None = None,
    enable_extensions: bool = True,
) -> AppServices:
    """Monta a aplicação injetando todas as dependências.

    `enable_extensions` liga/desliga as três features novas; os Golden
    Master Tests montam com elas desligadas para reproduzir o legado.
    """
    sink = sink if sink is not None else ConsoleSink()

    item_rules: list[ItemPricingRule] = [TypeDiscountRule()]
    payment_strategies: dict[str, PaymentStrategy] = {
        "cartao": CardPayment(),
        "pix": PixPayment(),
        "boleto": BoletoPayment(),
    }
    global_channels: list[NotificationChannel] = []

    if enable_extensions:
        item_rules.append(VolumeDiscountRule())
        payment_strategies["cripto"] = CryptoPayment()
        global_channels.append(WhatsAppChannel(sink))

    pricing = PricingService(item_rules)
    repository = SqliteOrderRepository(db_path)
    factories: dict[CustomerType, OrderFactory] = {
        CustomerType.NORMAL: NormalOrderFactory(pricing, sink),
        CustomerType.VIP: VipOrderFactory(pricing, sink),
        CustomerType.CORPORATIVO: CorporateOrderFactory(pricing, sink),
    }
    order_service = OrderService(
        repository, factories, SystemClock(), global_channels
    )
    payment_service = PaymentService(
        repository, payment_strategies, order_service, sink
    )
    report_service = ReportService(repository)
    stock_service = InMemoryStockService(
        {"produto1": 100, "produto2": 50, "produto3": 75}
    )
    return AppServices(
        repository=repository,
        order_service=order_service,
        payment_service=payment_service,
        report_service=report_service,
        stock_service=stock_service,
    )


def main() -> None:
    app = build_services()
    order_service = app.order_service

    its1 = [
        OrderItem("produto1", 100, 2, "normal"),
        OrderItem("produto2", 50, 1, "desc10"),
    ]
    if app.stock_service.is_available(its1):
        pedido1 = order_service.create_order(
            Customer("Joao Silva", CustomerType.NORMAL), its1
        )
        print(f"Pedido {pedido1.id} criado!")
        assert pedido1.id is not None
        app.payment_service.process(pedido1.id, "cartao", 250)
        order_service.advance_status(pedido1.id, OrderStatus.ENVIADO)
        order_service.advance_status(pedido1.id, OrderStatus.ENTREGUE)

    its2 = [OrderItem("produto3", 200, 1, "desc20")]
    if app.stock_service.is_available(its2):
        pedido2 = order_service.create_order(
            Customer("Maria Santos", CustomerType.VIP), its2
        )
        assert pedido2.id is not None
        app.payment_service.process(pedido2.id, "pix", 160)

    its3 = [OrderItem("produto1", 100, 5, "normal")]
    if app.stock_service.is_available(its3):
        pedido3 = order_service.create_order(
            Customer("Empresa XYZ", CustomerType.CORPORATIVO), its3
        )
        assert pedido3.id is not None
        app.payment_service.process(pedido3.id, "cripto", 600)

    print()
    print(app.report_service.sales_report())
    print()
    print(app.report_service.customers_report())
    app.repository.close()


if __name__ == "__main__":
    main()
