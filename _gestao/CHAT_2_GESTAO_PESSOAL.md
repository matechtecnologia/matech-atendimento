# 💰 CHAT 2 — Gestão Pessoal

**Última atualização:** 01/11/2026
**Área:** Gestão Pessoal (2º produto — ramo pessoal)
**Quem edita:** Só o Chat 2 e o Allan

---

## 📦 ARQUIVOS QUE ESTE CHAT MEXE

- `gestao_pessoal_db.py` — tabelas
- `gestao_pessoal_rotas.py` — rotas
- `templates/gestao.html` — hub com Pessoal | Profissional
- `templates/gestao_pessoal.html` — lista de áreas
- `templates/gestao_pessoal_financeira.html` — painel
- `templates/gestao_pessoal_lancar.html` — form lançar
- `templates/gestao_pessoal_extrato.html` — extrato

**NÃO MEXE EM:** `gemini.py`, `consultor_*`, `asaas.py`, `templates/admin*`, `templates/clientes.html`

---

## ✅ STATUS ATUAL

**Funcionando (FASE 2 completa):**
- Tabelas: `gestao_pessoal_lancamentos`, `gestao_pessoal_metas`, `gestao_pessoal_reserva`
- Painel: `/gestao/pessoal/financeira` (saldo + últimos + metas + reserva)
- Lançar: `/gestao/pessoal/financeira/lancar` (entrada/saída + categoria + essencial)
- Extrato: `/gestao/pessoal/financeira/extrato` (lista com filtro)

**Categorias:**
- Entradas: Salário, Freelance, Investimento, Venda, Outros
- Saídas essenciais: Moradia, Alimentação, Transporte, Saúde, Educação
- Saídas não-essenciais: Lazer, Roupas, Eletrônicos, Assinaturas

**Áreas que existem mas estão "em breve":**
- Agenda
- Metas Pessoais (tela existe? falta criar)
- Estudos
- Saúde
- Casa/Família
- Bens

**Pendente:**
- [ ] FASE 3 — IA de análise (analisa gastos, sugere cortes, projeta mês)
- [ ] Tela de Metas (CRUD completo)
- [ ] Tela de Reserva de emergência
- [ ] Tela de Dívidas (em breve)
- [ ] Tela de Investimentos (em breve)
- [ ] Tela de Indicadores (em breve)
- [ ] Atualizar textos do "?" das telas de Gestão Pessoal

---

## 🐛 BUGS CONHECIDOS

Nenhum no momento.

---

## 📅 ÚLTIMAS SESSÕES

**13/10/2026**
- Árvore de Gestão criada (`/gestao` → Pessoal | Profissional)
- FASE 2 da Gestão Pessoal Financeira:
  - 3 tabelas
  - Painel + Lançar + Extrato
  - Rotas registradas no `app.py`

**01/11/2026**
- Chat 2 oficializado como responsável da Gestão Pessoal

---

## 🎯 PRÓXIMO PASSO

Quando Allan abrir este chat, perguntar:
**"O que você quer fazer na Gestão Pessoal agora?"**

Opções prováveis:
- A) FASE 3 (IA analisa gastos)
- B) Tela de Metas (CRUD)
- C) Tela de Reserva
- D) Outro

---

## 🎨 DECISÕES TOMADAS

- Cada nível é uma ESCOLHA do cliente
- Tudo acessível pelo `/hub`
- Gestão Pessoal e Profissional são IGUAIS em peso
- Áreas "em breve" devem aparecer na lista (cria expectativa)
- IA só na FASE 3
