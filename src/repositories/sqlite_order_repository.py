"""Implementação SQLite do :class:`OrderRepository`."""
from __future__ import annotations

import json
import sqlite3
from typing import Any

from src.models.customer import Customer, CustomerType
from src.models.order import Order, OrderStatus
from src.models.order_item import OrderItem
from src.repositories.interfaces import OrderRepository


class SqliteOrderRepository(OrderRepository):
    """Persiste pedidos em um banco SQLite.

    Toda a conversão entre objetos de domínio e linhas da tabela fica
    confinada aqui; nenhuma outra camada conhece SQL.
    """

    def __init__(self, db_path: str = "loja.db") -> None:
        self._db = sqlite3.connect(db_path)
        self._create_schema()

    def _create_schema(self) -> None:
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS ped (
                id INTEGER PRIMARY KEY, cli TEXT, itens TEXT,
                tot REAL, st TEXT, dt TEXT, tp TEXT)"""
        )
        self._db.commit()

    def save(self, order: Order) -> int:
        cursor = self._db.execute(
            "INSERT INTO ped (cli, itens, tot, st, dt, tp) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                order.customer.nome,
                self._serialize_items(order.items),
                order.total,
                order.status.value,
                order.criado_em,
                order.customer.tipo.value,
            ),
        )
        self._db.commit()
        return int(cursor.lastrowid or 0)

    def get(self, order_id: int) -> Order | None:
        row = self._db.execute(
            "SELECT id, cli, itens, tot, st, dt, tp FROM ped WHERE id=?",
            (order_id,),
        ).fetchone()
        return self._row_to_order(row) if row else None

    def update_status(self, order_id: int, status: OrderStatus) -> None:
        self._db.execute(
            "UPDATE ped SET st=? WHERE id=?", (status.value, order_id)
        )
        self._db.commit()

    def list_all(self) -> list[Order]:
        rows = self._db.execute(
            "SELECT id, cli, itens, tot, st, dt, tp FROM ped"
        ).fetchall()
        return [self._row_to_order(row) for row in rows]

    def total_by_customer(self, customer_name: str) -> float:
        row = self._db.execute(
            "SELECT COALESCE(SUM(tot), 0) FROM ped WHERE cli=?",
            (customer_name,),
        ).fetchone()
        return float(row[0])

    def close(self) -> None:
        self._db.close()

    @staticmethod
    def _serialize_items(items: list[OrderItem]) -> str:
        return json.dumps(
            [
                {
                    "nome": item.nome,
                    "preco": item.preco,
                    "quantidade": item.quantidade,
                    "tipo": item.tipo,
                }
                for item in items
            ]
        )

    @staticmethod
    def _deserialize_items(raw: str) -> list[OrderItem]:
        return [
            OrderItem(
                nome=data["nome"],
                preco=data["preco"],
                quantidade=data["quantidade"],
                tipo=data["tipo"],
            )
            for data in json.loads(raw)
        ]

    def _row_to_order(self, row: tuple[Any, ...]) -> Order:
        return Order(
            id=row[0],
            customer=Customer(nome=row[1], tipo=CustomerType(row[6])),
            items=self._deserialize_items(row[2]),
            total=row[3],
            status=OrderStatus(row[4]),
            criado_em=row[5],
        )
