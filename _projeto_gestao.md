# PROJETO GESTAO EMPRESARIAL M.A TECH

**Status:** EM IMPLEMENTACAO (13/10/2026)
**Prioridade:** ALTA (Allan decidiu fazer agora)
**Versao:** 0.1

---

## VISAO

A Gestao e o segundo produto da M.A Tech.
Onde o Atendimento IA ajuda a VENDER, a Gestao ajuda a ADMINISTRAR.

O cliente que vende precisa saber:
- Quanto entrou
- Quanto saiu
- Quanto sobrou
- Quanto tem a receber
- Quanto tem a pagar
- Se esta lucrando ou so girando

A Gestao resolve isso com telas simples + IA de analise.

---

## TELAS DO MODULO

1. Dashboard        - visao geral (receita, custo, lucro)
2. Receitas         - o que entrou
3. Despesas         - o que saiu
4. Contas a Pagar   - o que tem que pagar
5. Contas a Receber - o que tem que receber
6. DRE Simplificado - demonstrativo de resultado
7. Fluxo de Caixa   - entrada x saida no tempo
8. Metas            - objetivo do mes
9. Indicadores      - margem, ticket medio, ponto de equilibrio
10. Configuracoes   - categorias, contas, preferencias

---

## DADOS QUE MANIPULA

- Receitas (descricao, valor, categoria, data, cliente)
- Despesas (descricao, valor, categoria, data, fornecedor)
- Contas a pagar (valor, vencimento, status)
- Contas a receber (valor, vencimento, status)
- Categorias (receita e despesa)
- Contas bancarias
- Metas mensais
- KPIs calculados (margem, lucro, ROI, ponto de equilibrio)

---

## TABELAS EXISTENTES

Ja criadas no banco:
- gestao_empresas
- gestao_modulos
- custos_mensais

A DEFINIR:
- gestao_receitas
- gestao_despesas
- gestao_contas_pagar
- gestao_contas_receber
- gestao_categorias
- gestao_metas
- gestao_indicadores

---

## CONEXAO COM O ATENDIMENTO IA









A Consultoria e a porta de entrada pra Gestao.

---

## MODELO DE NEGOCIO

### Preco sugerido

- Add-on Gestao: R$ 47/mes
- OU incluso no plano Pro+ (R$ 297+)
- OU incluso no plano Empresarial (R$ 597)

### Meta

- Fase 1: cliente no Atendimento ve que precisa
- Fase 2: ativa Gestao por R$ 47/mes
- Fase 3: upsell de CRM, Trafego, Automacao

---

## ROADMAP

### Fase 1 — Estrutura (1-2 dias)
- [ ] Criar tabelas de receita, despesa, contas, categorias, metas
- [ ] Criar dashboard com metricas basicas
- [ ] Criar tela de lancamento de receita
- [ ] Criar tela de lancamento de despesa

### Fase 2 — DRE + Fluxo (3-4 dias)
- [ ] DRE simplificado
- [ ] Fluxo de caixa
- [ ] Contas a pagar/receber
- [ ] Categorias personalizadas

### Fase 3 — IA de Analise (5-7 dias)
- [ ] IA analisa dados e sugere acoes
- [ ] Deteccao de anomalias
- [ ] Relatorio automatico mensal
- [ ] Indicadores calculados

### Fase 4 — Integracao (futuro)
- [ ] Conexao automatica com Atendimento IA
- [ ] Venda fechada vira receita
- [ ] Consultoria IA sugere Gestao
- [ ] Dashboard unificado (Atendimento + Gestao)

---

## PRIORIDADE

**DECISAO ALLAN (13/10):** Fazer agora.

Ordem:
1. Gestao primeiro (proximo)
2. Depois anúncios

Motivo: Allan quer o modulo pronto pra oferecer quando o cliente pedir.

---

## REGRAS TECNICAS

- Novo arquivo: gestao_rotas.py
- Novo arquivo: gestao_db.py
- Novo arquivo: gestao_core.py
- Novos templates: gestao_*.html
- Registrar em app.py
- Menu no hub: adicionar card Gestao
- Testar local antes de subir

---

**Registrado em:** 13/10/2026
**Local:** _projeto_gestao.md
