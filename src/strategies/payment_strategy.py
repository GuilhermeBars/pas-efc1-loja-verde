"""Padrão Strategy aplicado a métodos de pagamento."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.models.order import Order


@dataclass(frozen=True)
class PaymentResult:
    """Resultado de uma tentativa de cobrança.

    `auto_approve` indica se o pedido deve transitar automaticamente para
    o estado ``aprovado`` (cartão e PIX aprovam; boleto não).
    """

    success: bool
    auto_approve: bool
    amount_charged: float
    message: str


class PaymentStrategy(ABC):
    """Algoritmo de cobrança intercambiável."""

    @abstractmethod
    def charge(self, order: Order) -> PaymentResult:
        """Processa o pagamento do pedido e devolve o resultado."""
        raise NotImplementedError


class CardPayment(PaymentStrategy):
    """Pagamento com cartão: aprova automaticamente."""

    def charge(self, order: Order) -> PaymentResult:
        return PaymentResult(
            success=True,
            auto_approve=True,
            amount_charged=order.total,
            message="Cartao validado!",
        )


class PixPayment(PaymentStrategy):
    """Pagamento via PIX: aprova automaticamente."""

    def charge(self, order: Order) -> PaymentResult:
        return PaymentResult(
            success=True,
            auto_approve=True,
            amount_charged=order.total,
            message="PIX recebido!",
        )


class BoletoPayment(PaymentStrategy):
    """Pagamento via boleto: gerado, mas não aprova de imediato."""

    def charge(self, order: Order) -> PaymentResult:
        return PaymentResult(
            success=True,
            auto_approve=False,
            amount_charged=order.total,
            message="Boleto gerado!",
        )
