"""Testes da extensão 3: desconto progressivo por volume."""
from __future__ import annotations

from src.extensions.volume_discount import VolumeDiscountRule
from src.main import AppServices
from src.models.customer import Customer, CustomerType
from src.models.order_item import OrderItem


def test_aplica_15_por_cento_a_partir_de_3_unidades() -> None:
    rule = VolumeDiscountRule()
    item = OrderItem("p1", 100, 3, "normal")
    assert rule.apply(item, item.subtotal) == 255.0  # 300 * 0.85


def test_nao_aplica_abaixo_de_3_unidades() -> None:
    rule = VolumeDiscountRule()
    item = OrderItem("p1", 100, 2, "normal")
    assert rule.apply(item, item.subtotal) == 200.0


def test_fluxo_completo_com_desconto_de_volume(app_ext: AppServices) -> None:
    pedido = app_ext.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL),
        [OrderItem("produto1", 100, 5, "normal")],
    )
    # 100 * 5 = 500 ; volume 0.85 -> 425.0 (cliente normal, sem desconto extra)
    assert pedido.total == 425.0


def test_sem_extensao_nao_ha_desconto_de_volume(app: AppServices) -> None:
    pedido = app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL),
        [OrderItem("produto1", 100, 5, "normal")],
    )
    assert pedido.total == 500.0
