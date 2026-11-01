# 💳 CHAT 5 — Conta + Planos + PIX

**Última atualização:** 01/11/2026
**Área:** Cadastro, Login, Onboarding, Planos, PIX Asaas, Indique, Configurações, Suporte
**Quem edita:** Só o Chat 5 e o Allan

---

## 📦 ARQUIVOS QUE ESTE CHAT MEXE

- `asaas.py` — integração PIX
- `templates/signup.html`
- `templates/login.html`
- `templates/onboarding.html`
- `templates/planos.html`
- `templates/assinar.html`
- `templates/pagamento_pix.html`
- `templates/indicar.html`
- `templates/configuracoes.html`
- `templates/bem_vindo.html`

**NÃO MEXE EM:** `gemini.py`, `gestao_*`, `consultor_*`, `templates/admin*`, `templates/clientes.html`

---

## ✅ STATUS ATUAL

**Funcionando:**
- Cadastro + Login (sessão assinada, cookie seguro)
- Onboarding (7 perguntas pra gerar prompt do nicho)
- PIX via Asaas (produção real — cai na conta)
- Planos com limites: 150 / 1.500 / 4.500 / 9.000
- Desconto 1º mês: R$ 47, R$ 147, R$ 297
- Excedente: R$ 0,10 por interação
- Bloqueio: 120% do limite
- Indique e Ganhe (link único por vendedor)
- Configurações (nome, whatsapp, senha, notificações)
- Suporte (link WhatsApp)
- Instagram no rodapé

**Pendente:**
- [ ] Testar fluxo completo do Asaas em produção (assinar → PIX → liberação)
- [ ] Templates de email Asaas (cobrança, confirmação)
- [ ] Melhorar onboarding (tutorial "como usar em 3 passos")
- [ ] Email de boas-vindas (bloqueado — precisa domínio)
- [ ] Revisar textos do "?" das telas desta área

---

## 🐛 BUGS CONHECIDOS

1. **Render gratuito bloqueia SMTP** — não dá pra usar Gmail SMTP
2. **Email de boas-vindas** só funciona com domínio próprio (Resend)

---

## 📅 ÚLTIMAS SESSÕES

**13/10/2026**
- Termos + Privacidade (LGPD)
- Página de obrigado pós-cadastro
- Suporte WhatsApp no menu
- Instagram no rodapé

**01/11/2026**
- Chat 5 oficializado como responsável de Conta + Planos + PIX

---

## 🎯 PRÓXIMO PASSO

Quando Allan abrir este chat, perguntar:
**"O que você quer fazer em Conta/Planos agora?"**

Opções prováveis:
- A) Testar Asaas em produção
- B) Configurar templates de email Asaas
- C) Melhorar onboarding
- D) Outro

---

## 🎨 DECISÕES TOMADAS

- Sessão: cookie assinado `sessao` (HMAC SHA-256)
- Middleware injeta `usuario_id` + `usuario_tipo` como cookies virtuais
- PIX: Asaas produção
- Plano grátis: 1 nicho
- Sem fidelidade
