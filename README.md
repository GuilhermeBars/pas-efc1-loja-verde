# Loja Verde: refatoração SOLID, Clean Code e GoF (EFC1)

Refatoração do sistema legado de pedidos da Loja Verde, guiada por testes de
caracterização (Golden Master), princípios SOLID, Clean Code e padrões GoF.

## Integrantes

| Nome | RA |
|------|----|
| Felipe Cosmo Granziol | 24021602 |
| Guilherme Bars | 24014122 |
| Gustavo Kurten | 24008150 |
| Henrique Gambin | 24013762 |
| João Celso | 24012463 |
| Pedro Tiezo Sales Shimizu | 24005158 |
| Vitor Hugo Barbosa | 24018852 |

Não entramos em grupo separado para esta disciplina porque nosso grupo de
Projeto Integrador tem 7 integrantes, uma exceção autorizada pela professora
de Projeto Integrador. Mantivemos o mesmo grupo aqui.

## Estrutura

```
legacy.py                  # código original (o "antes"), mantido como referência
src/
├── models/                # entidades de domínio (Customer, Order, OrderItem)
├── repositories/          # padrão Repository (interface + SQLite)
├── strategies/            # padrão Strategy (descontos e pagamentos)
├── observers/             # padrão Observer (notificações)
├── factories/             # padrão Factory Method (criação de pedidos)
├── services/              # camada de aplicação (orquestração + DI)
├── extensions/            # 3 features novas, 100% aditivas (prova de OCP)
└── main.py                # composition root (injeção de dependências)
tests/
├── golden_master/         # caracterização + equivalência com o legado
├── unit/                  # testes de unidade
├── integration/           # testes de integração
└── extensions/            # testes das 3 extensões
docs/                      # análise textual e diagrama UML
```

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate
pip install pytest pytest-cov ruff mypy radon

make test         # roda os testes
make cov          # cobertura
make lint         # ruff
make type         # mypy --strict
make complexity   # radon
make all          # tudo
make run          # executa a demonstração (src/main.py)
```

## Padrões GoF aplicados

| Padrão          | Onde                                              |
|-----------------|---------------------------------------------------|
| Strategy        | `strategies/`: descontos e pagamentos  |
| Repository      | `repositories/`: isolamento do SQLite            |
| Observer        | `observers/`: notificações desacopladas          |
| Factory Method  | `factories/`: criação de pedidos por tipo        |

## As três extensões (OCP empírico)

Todas em `src/extensions/`, sem modificar **nenhuma** classe existente,
apenas novas classes registradas no composition root (`src/main.py`):

1. `crypto_payment.py`: pagamento em criptomoeda com taxa de 2%.
2. `whatsapp_channel.py`: canal de notificação WhatsApp para todos.
3. `volume_discount.py`: 15% de desconto extra para 3+ unidades do item.

## Métricas (verificadas)

- Cobertura de testes: **98%** (mínimo 85%)
- `ruff check`: **sem erros**
- `mypy --strict`: **sem erros**
- Complexidade ciclomática (radon): **média A**, todos os blocos ≤ B
