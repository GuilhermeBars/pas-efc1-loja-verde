"""Extensão 1: pagamento em criptomoeda (taxa de 2%).

Adicionada SEM modificar nenhuma classe existente: é apenas uma nova
:class:`PaymentStrategy`, registrada no dicionário de meios de pagamento
na composição da aplicação.
"""
from __future__ import annotations

from src.models.order import Order
from src.strategies.payment_strategy import PaymentResult, PaymentStrategy

CRYPTO_FEE_RATE = 0.02


class CryptoPayment(PaymentStrategy):
    """Pagamento em criptomoeda com taxa de 2% sobre o valor do pedido."""

    def charge(self, order: Order) -> PaymentResult:
        fee = order.total * CRYPTO_FEE_RATE
        charged = order.total + fee
        return PaymentResult(
            success=True,
            auto_approve=True,
            amount_charged=charged,
            message=f"Cripto confirmada! Taxa de 2% (R${fee:.2f}) aplicada.",
        )
