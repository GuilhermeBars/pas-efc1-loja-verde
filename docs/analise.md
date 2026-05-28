# Documento de Análise : EFC1 Loja Verde (inicial, Sprint 0)

> Análise textual das violações SOLID no código legado (`legacy.py`).
> As seções de solução, diagrama e reflexão serão preenchidas nos sprints
> seguintes.

## (a) Identificação das Violações SOLID

### SRP : Single Responsibility Principle
- `Sis.add_ped` (linhas 15 a 49): calcula descontos, persiste e notifica num
  único método. *Impacto:* mudar notificação arrisca quebrar o cálculo.
- `Sis.upd_st` (linhas 59 a 80): mistura atualização de estado, e-mail/SMS e
  pontos de fidelidade.

### OCP : Open/Closed Principle
- `Sis.proc_pag` (116 a 139): `if/elif` por método de pagamento; novo meio
  exige editar o método.
- `Sis.add_ped` (18 a 31): `if/elif` por tipo de desconto/cliente.

### LSP : Liskov Substitution Principle
- `PedEspecial.upd_st` (183 a 190): pula estados e não notifica, quebrando o
  contrato de `Sis.upd_st`.
- `PedEspecial.add_ped` (164 a 181): muda o cálculo e a notificação.

### ISP : Interface Segregation Principle
- `Sis` é uma classe gorda (pedido, pagamento, estoque, relatório).
- `PedEspecial` é forçada a herdar toda a superfície de `Sis`.

### DIP : Dependency Inversion Principle
- Dependência direta de `sqlite3` (linha 8).
- Notificação via `print` e estoque *hardcoded* (linha 143, com `# TODO`).
