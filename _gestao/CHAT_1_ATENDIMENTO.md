# 🤖 CHAT 1 — Atendimento comercial com IA

**Última atualização:** 01/11/2026
**Área:** Atendimento comercial com IA (produto principal)
**Quem edita:** Só o Chat 1 e o Allan

---

## 📦 ARQUIVOS QUE ESTE CHAT MEXE

- `gemini.py` — IA principal
- `auditor_ia.py` — IA que Aprende
- `limites_mensais.py` — limites por plano
- `templates/atendimento_cliente.html`
- `templates/clientes.html`
- `templates/resultado.html`
- `templates/followups.html`
- `templates/meus_nichos.html`
- `templates/novo_nicho.html`
- `templates/relatorios.html`
- `templates/cliente_detalhe.html`
- `templates/novo_cliente.html`

**NÃO MEXE EM:** `app.py` (só nas rotas de atendimento, anotando linhas), `gestao_*`, `consultor_*`, `asaas.py`, `templates/admin*`, `templates/landing.html`

---

## ✅ STATUS ATUAL

**Funcionando:**
- Atendimento com Gemini 3.5 Flash
- Histórico por cliente
- Geração de resposta em 3 blocos (áudio/texto/estágio)
- Follow-ups com badge
- Nichos configuráveis
- Relatórios (funil, top clientes, top nichos)
- Card de clientes redesenhado (avatar + nome + meta + status)
- Filtro dentro da busca
- Modo instrução
- Limites por plano (150/1500/4500/9000)

**Pendente:**
- [ ] Terminar "IA que Aprende" (botão mobile)
- [ ] FASE 3 (IA analisa gastos — se for do atendimento)
- [ ] Redesenhar tela de atendimento (Allan pediu, mas reverso)
- [ ] Textos do "?" das novas telas

---

## 🐛 BUGS CONHECIDOS

1. **Gemini 503 em picos** — não é bug, é Google. Solução: billing pago (semana que vem)
2. **Modelo `gemini-3.5-flash-lite` não existe mais** — usar `gemini-3.5-flash`

---

## 📅 ÚLTIMAS SESSÕES

**13/10/2026**
- Corrigido modelo Gemini (era flash-lite inexistente)
- Card de clientes atualizado (avatar+nome+meta+status)
- Filtro movido pra dentro da busca
- Textos do "?" revisados

**29/10/2026**
- Card de clientes redesenhado
- Filtro embutido na busca

**01/11/2026**
- Criado sistema multi-chat
- Chat 1 oficializado como responsável do Atendimento

---

## 🎯 PRÓXIMO PASSO

Quando Allan abrir este chat, perguntar:
**"O que você quer fazer no Atendimento agora?"**

Opções prováveis:
- A) Terminar "IA que Aprende"
- B) Melhorar tela de atendimento
- C) Ajustar textos do "?"
- D) Outro

---

## 🎨 DECISÕES TOMADAS

- Modelo: `gemini-3.5-flash`
- Sem retry automático (por enquanto)
- Bottom nav: Gestão | Consultoria | Atendimento | Follow-ups | Relatórios
- Modo instrução marcado por checkbox
