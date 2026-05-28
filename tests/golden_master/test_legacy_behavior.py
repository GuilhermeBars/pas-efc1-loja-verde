"""Golden Master Tests.

Caracterizam o comportamento observável do sistema legado. As mesmas
asserções (valores esperados) devem continuar verdadeiras no sistema
refatorado, provando ausência de regressão. A aplicação é montada SEM
extensões para reproduzir exatamente o legado.
"""
from __future__ import annotations

from src.main import AppServices
from src.models.customer import Customer, CustomerType
from src.models.order import OrderStatus
from src.models.order_item import OrderItem


def test_pedido_normal_calcula_total_corretamente(app: AppServices) -> None:
    itens = [
        OrderItem("produto1", 100, 2, "normal"),
        OrderItem("produto2", 50, 1, "desc10"),
    ]
    pedido = app.order_service.create_order(
        Customer("Joao Silva", CustomerType.NORMAL), itens
    )
    assert pedido.total == 245.0
    assert pedido.status is OrderStatus.PENDENTE


def test_pedido_vip_aplica_desconto_de_5_por_cento(app: AppServices) -> None:
    itens = [OrderItem("p1", 100, 1, "normal")]
    pedido = app.order_service.create_order(
        Customer("Maria", CustomerType.VIP), itens
    )
    assert pedido.total == 95.0


def test_pedido_corporativo_aplica_desconto_de_10_por_cento(
    app: AppServices,
) -> None:
    itens = [OrderItem("p1", 100, 1, "normal")]
    pedido = app.order_service.create_order(
        Customer("Empresa", CustomerType.CORPORATIVO), itens
    )
    assert pedido.total == 90.0


def test_desc20_no_item(app: AppServices) -> None:
    itens = [OrderItem("produto3", 200, 1, "desc20")]
    pedido = app.order_service.create_order(
        Customer("Maria Santos", CustomerType.VIP), itens
    )
    # 200 * 0.8 = 160 ; VIP * 0.95 = 152.0
    assert pedido.total == 152.0


def test_pagamento_insuficiente_falha(app: AppServices) -> None:
    itens = [OrderItem("p1", 100, 1, "normal")]
    pedido = app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL), itens
    )
    assert pedido.id is not None
    assert app.payment_service.process(pedido.id, "cartao", 50) is False


def test_pix_aprova_pedido_automaticamente(app: AppServices) -> None:
    itens = [OrderItem("p1", 100, 1, "normal")]
    pedido = app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL), itens
    )
    assert pedido.id is not None
    app.payment_service.process(pedido.id, "pix", 100)
    recuperado = app.repository.get(pedido.id)
    assert recuperado is not None
    assert recuperado.status is OrderStatus.APROVADO


def test_cartao_aprova_pedido_automaticamente(app: AppServices) -> None:
    itens = [OrderItem("p1", 100, 1, "normal")]
    pedido = app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL), itens
    )
    assert pedido.id is not None
    app.payment_service.process(pedido.id, "cartao", 100)
    recuperado = app.repository.get(pedido.id)
    assert recuperado is not None
    assert recuperado.status is OrderStatus.APROVADO


def test_boleto_nao_aprova_automaticamente(app: AppServices) -> None:
    itens = [OrderItem("p1", 100, 1, "normal")]
    pedido = app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL), itens
    )
    assert pedido.id is not None
    app.payment_service.process(pedido.id, "boleto", 100)
    recuperado = app.repository.get(pedido.id)
    assert recuperado is not None
    assert recuperado.status is OrderStatus.PENDENTE


def test_atualizacao_de_status(app: AppServices) -> None:
    itens = [OrderItem("p1", 100, 1, "normal")]
    pedido = app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL), itens
    )
    assert pedido.id is not None
    app.order_service.advance_status(pedido.id, OrderStatus.ENVIADO)
    recuperado = app.repository.get(pedido.id)
    assert recuperado is not None
    assert recuperado.status is OrderStatus.ENVIADO


def test_cancelamento(app: AppServices) -> None:
    itens = [OrderItem("p1", 100, 1, "normal")]
    pedido = app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL), itens
    )
    assert pedido.id is not None
    app.order_service.cancel_order(pedido.id)
    recuperado = app.repository.get(pedido.id)
    assert recuperado is not None
    assert recuperado.status is OrderStatus.CANCELADO


def test_geracao_de_relatorios(app: AppServices) -> None:
    app.order_service.create_order(
        Customer("Joao", CustomerType.NORMAL),
        [OrderItem("p1", 100, 1, "normal")],
    )
    app.order_service.create_order(
        Customer("Maria", CustomerType.VIP),
        [OrderItem("p1", 100, 1, "normal")],
    )
    vendas = app.report_service.sales_report()
    clientes = app.report_service.customers_report()
    assert "RELATORIO DE VENDAS" in vendas
    assert "Total Geral: R$195.00" in vendas
    assert "Joao" in clientes
    assert "Maria" in clientes
