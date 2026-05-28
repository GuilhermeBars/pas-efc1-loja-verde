"""Entidade de domínio: cliente."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CustomerType(Enum):
    """Categorias de cliente reconhecidas pela Loja Verde."""

    NORMAL = "normal"
    VIP = "vip"
    CORPORATIVO = "corporativo"


@dataclass(frozen=True)
class Customer:
    """Cliente que realiza um pedido.

    Imutável: a identidade do cliente não muda ao longo do pedido.
    """

    nome: str
    tipo: CustomerType
