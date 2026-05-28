# Documento de análise: EFC1 Loja Verde

As referências de linha apontam para `legacy.py`, o código original antes da refatoração.

## (a) Identificação das violações SOLID

### SRP (responsabilidade única)

O método `Sis.add_ped` (linhas 15 a 49) faz quatro coisas ao mesmo tempo: calcula o desconto de cada item, aplica o desconto do cliente, grava o pedido no banco e dispara as notificações. São quatro motivos diferentes para esse método mudar. Se a regra de notificação mudar, o cálculo do total fica exposto ao risco de quebrar junto.

O método `Sis.upd_st` (linhas 59 a 80) tem o mesmo problema. Ele atualiza o estado do pedido, manda e-mail e SMS e ainda calcula os pontos de fidelidade. A classe `Sis` inteira concentra pedido, pagamento, estoque, relatório e notificação, com mais de sete métodos públicos.

### OCP (aberto/fechado)

`Sis.proc_pag` (linhas 116 a 139) decide o pagamento com uma cadeia de `if/elif` sobre `cartao`, `pix` e `boleto`. Para aceitar criptomoeda, é preciso editar o método. `Sis.add_ped` (linhas 18 a 31) repete o padrão para o tipo de desconto do item e o tipo de cliente. Qualquer desconto novo obriga a mexer na classe que já funciona. As três extensões pedidas no trabalho seriam impossíveis sem alterar código existente.

### LSP (substituição de Liskov)

`PedEspecial.upd_st` (linhas 183 a 190) pula direto para qualquer estado e não envia notificação nem concede pontos. Isso contraria o comportamento observável de `Sis.upd_st`. `PedEspecial.add_ped` (linhas 164 a 181) reescreve o cálculo, acrescenta 15% e troca a notificação. Um trecho de código que espera um `Sis` recebe um `PedEspecial` e passa a ter outro resultado sem perceber.

### ISP (segregação de interfaces)

Quem só precisa emitir um relatório depende, através de `Sis`, também de pagamento, estoque e notificação. Não há interfaces separadas por colaboração. A subclasse `PedEspecial` é forçada a herdar toda a superfície de `Sis` para usar apenas parte dela, reimplementando o resto.

### DIP (inversão de dependência)

A regra de negócio fala SQL direto com `sqlite3` (linha 8). Trocar a persistência significa reescrever a classe. As notificações saem por `print`, e o estoque vem de um `dict` fixo com um `# TODO: integrar com sistema externo` (linha 143). O código de alto nível depende de detalhes concretos, o que impede testar em isolamento ou trocar o canal de saída.

## (b) Soluções implementadas

| Violação | Solução | Princípio | Padrão GoF |
|----------|---------|-----------|------------|
| `add_ped`/`upd_st` faziam tudo | Separação em `OrderService`, `PaymentService`, `PricingService` e `ReportService` | SRP | |
| `if/elif` de pagamento | `PaymentStrategy` com dicionário injetado | OCP | Strategy |
| `if/elif` de desconto | `ItemPricingRule` e `CustomerDiscountStrategy` | OCP | Strategy |
| Notificação acoplada à regra | `OrderNotifier` com `NotificationChannel` | SRP, OCP | Observer |
| Criação por tipo de cliente | `OrderFactory` e suas subclasses | OCP | Factory Method |
| `sqlite3` direto na regra | `OrderRepository` (ABC) com `SqliteOrderRepository` | DIP | Repository |
| `print` e estoque fixo | `MessageSink`, `StockService` e `Clock` como abstrações | DIP | |
| Herança `PedEspecial` | Eliminada; o acréscimo vira regra de preço, mesmo tipo `Order` | LSP | |

O caso do pagamento ilustra bem a mudança. Antes:

```python
if m == 'cartao': ...; self.upd_st(id, 'aprovado'); return True
elif m == 'pix':  ...; self.upd_st(id, 'aprovado'); return True
elif m == 'boleto': ...; return True
```

Depois, em `payment_service.py` e `strategies/payment_strategy.py`:

```python
strategy = self._strategies.get(method)        # injetado no construtor
result = strategy.charge(order)
if result.auto_approve:
    self._order_service.advance_status(order.id, OrderStatus.APROVADO)
```

Para aceitar criptomoeda basta uma classe nova, `CryptoPayment`, e uma linha que a registra no composition root. Nenhuma classe antiga muda.

## (c) Diagrama UML de classes

O arquivo `docs/diagrama.puml` tem a fonte em PlantUML, e `docs/loja_verde.png` mostra o resultado renderizado. As camadas aparecem explícitas. As setas de dependência apontam para abstrações, conforme o DIP: os serviços dependem de `OrderRepository`, `PaymentStrategy` e `NotificationChannel`, nunca das classes concretas.

## (d) Melhorias de Clean Code

Os nomes passaram a dizer o que fazem. `Sis` virou `OrderService` e `SqliteOrderRepository`. `add_ped` virou `create_order`, `proc_pag` virou `process` e `upd_st` virou `advance_status`. Os parâmetros `n`, `its` e `t` viraram `customer`, `items` e o tipo do cliente.

Os números mágicos saíram. As multiplicações soltas (`* 0.95`, `* 0.9`, `* 1.15`, `* 2`) viraram estratégias e constantes com nome, como `VipDiscount`, `CRYPTO_FEE_RATE` e `VOLUME_DISCOUNT_FACTOR`. Os métodos ficaram curtos, abaixo de vinte linhas, com uma responsabilidade cada.

A tipagem ficou forte. `CustomerType` e `OrderStatus` são `Enum` no lugar de strings soltas, as entidades são `dataclass` e o `mypy --strict` roda sem erro. O cálculo de total, que aparecia duplicado entre `Sis` e `PedEspecial`, ficou em um lugar só, no `PricingService`.

## (e) Extensões implementadas

As três features são a prova de que o OCP foi cumprido. Dá para auditar pelo `git log` e pelo `git diff`: cada uma é um commit que só adiciona arquivos em `src/extensions/` e nos testes, mais a fiação no composition root (`src/main.py`). Nenhuma classe de domínio foi tocada.

A criptomoeda com taxa de 2% está em `extensions/crypto_payment.py`, como `CryptoPayment(PaymentStrategy)` registrada no dicionário de estratégias. O WhatsApp para todos os clientes está em `extensions/whatsapp_channel.py`, como `WhatsAppChannel(NotificationChannel)` inscrito como canal global. O desconto por volume de 15% para três ou mais unidades está em `extensions/volume_discount.py`, como `VolumeDiscountRule(ItemPricingRule)` anexada à cadeia de regras de preço.

Ficou simples porque as abstrações certas já existiam e são injetadas: estratégia de pagamento, canal de notificação e regra de precificação. A extensão se resume a plugar uma subclasse nova.

## (f) Reflexão metacognitiva

O princípio que eu ainda não domino é o LSP. A violação clássica, a do `PedEspecial`, eu reconheço de cara. O que me trava são os casos sutis: quando uma subclasse aperta a pré-condição em vez de só estender o comportamento. Sem escrever um teste de substituição explícito, ainda não consigo afirmar com segurança se uma hierarquia respeita Liskov.

Usei IA para acelerar a montagem das camadas e a redação dos testes de caracterização. O que funcionou bem foi pedir o mapeamento de cada violação para o padrão correspondente. Discordei em um ponto: a primeira sugestão colocava a escolha dos canais de notificação dentro do `OrderService`, com um `if` por tipo de cliente. Isso recriaria a violação de OCP que eu estava tentando consertar. Movi essa decisão para as fábricas (`OrderFactory`), de modo que o serviço fica fechado para modificação.
