# 🧠 CHAT 4 — Consultoria IA

**Última atualização:** 01/11/2026
**Área:** Consultoria Empresarial com IA (produto 3)
**Quem edita:** Só o Chat 4 e o Allan

---

## 📦 ARQUIVOS QUE ESTE CHAT MEXE

- `consultor.py` — lógica da IA consultora
- `consultor_rotas.py` — rotas
- `consultor_db.py` (se existir)
- `templates/consultoria.html`
- `templates/consultoria_loading.html`
- `templates/consultoria_em_breve.html`

**NÃO MEXE EM:** `gemini.py`, `gestao_*`, `asaas.py`, `templates/admin*`, `templates/clientes.html`

---

## ✅ STATUS ATUAL

**Funcionando (admin only, em desenvolvimento):**
- Rota de loading
- Rota "em breve"
- Rota eh-admin
- Rotas registradas no `app.py`
- IA consultora responde (via `consultor.py`)

**Como funciona:**
- Analisa dados reais do vendedor
- Detecta gargalo
- Sugere plano de ação
- Histórico salvo (o cliente sai e volta de onde parou)
- Limite diário por plano

**Pendente:**
- [ ] Liberar pra todos (hoje só admin vê)
- [ ] Redesenhar tela premium
- [ ] Testar fluxo completo em produção
- [ ] IA sugerir cortes de gasto (integração com Gestão Pessoal)

---

## 🐛 BUGS CONHECIDOS

Nenhum no momento.

---

## 📅 ÚLTIMAS SESSÕES

**13/10/2026**
- Consultoria em desenvolvimento (admin only)
- Cliente comum vê tela "em breve"

**01/11/2026**
- Chat 4 oficializado como responsável da Consultoria

---

## 🎯 PRÓXIMO PASSO

Quando Allan abrir este chat, perguntar:
**"O que você quer fazer na Consultoria agora?"**

Opções prováveis:
- A) Liberar pra todos (tirar do admin only)
- B) Redesenhar tela premium
- C) Testar fluxo completo
- D) Outro

---

## 🎨 DECISÕES TOMADAS

- Consultoria é o 1º passo pra vender Gestão e CRM no futuro
- Limite diário por plano
- Histórico persistente
- Hoje: admin only
