"""Serviço de processamento de pagamentos."""
from __future__ import annotations

from collections.abc import Mapping

from src.models.order import OrderStatus
from src.observers.notification_observer import MessageSink
from src.repositories.interfaces import OrderRepository
from src.services.order_service import OrderService
from src.strategies.payment_strategy import PaymentStrategy


class PaymentService:
    """Processa pagamentos delegando o algoritmo a uma estratégia.

    O dicionário de estratégias é injetado: novos meios de pagamento
    (ex.: criptomoeda) são registrados na composição da aplicação, sem
    alterar este serviço (OCP).
    """

    def __init__(
        self,
        repository: OrderRepository,
        strategies: Mapping[str, PaymentStrategy],
        order_service: OrderService,
        sink: MessageSink,
    ) -> None:
        self._repository = repository
        self._strategies = dict(strategies)
        self._order_service = order_service
        self._sink = sink

    def process(self, order_id: int, method: str, amount: float) -> bool:
        order = self._repository.get(order_id)
        if order is None:
            return False
        if amount < order.total:
            self._sink.send("Pagamento", order.customer.nome, "Valor insuficiente!")
            return False
        strategy = self._strategies.get(method)
        if strategy is None:
            self._sink.send(
                "Pagamento", order.customer.nome, "Metodo de pagamento invalido!"
            )
            return False
        result = strategy.charge(order)
        self._sink.send("Pagamento", order.customer.nome, result.message)
        if result.auto_approve and order.id is not None:
            self._order_service.advance_status(order.id, OrderStatus.APROVADO)
        return result.success
