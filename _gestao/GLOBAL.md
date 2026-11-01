# 🌍 GLOBAL - M.A Tech

**Última atualização:** 01/11/2026
**Dono do projeto:** Allan
**Uso:** Este é o documento GLOBAL. TODOS os chats devem ler antes de trabalhar.
**Quem edita:** Só o Allan (com ajuda de algum chat). Nenhum chat edita direto.

---

## 🎯 O QUE É A M.A TECH

- **Marca institucional:** M.A Tech — Tecnologia e Solução
- **Produto principal:** M.A Tech — Atendimento comercial com IA
- **2º produto (em construção):** Gestão (Pessoal + Profissional)

---

## 🗂️ DIVISÃO DE ÁREAS POR CHAT

| Chat | Área | Doc da área |
|------|------|-------------|
| **Chat 1** | Atendimento comercial com IA | `CHAT_1_ATENDIMENTO.md` |
| **Chat 2** | Gestão Pessoal | `CHAT_2_GESTAO_PESSOAL.md` |
| **Chat 3** | Gestão Profissional | `CHAT_3_GESTAO_PROFISSIONAL.md` |
| **Chat 4** | Consultoria IA | `CHAT_4_CONSULTORIA.md` |
| **Chat 5** | Conta + Planos + PIX | `CHAT_5_CONTA_PLANOS.md` |
| **Chat 6** | Admin + Institucional | `CHAT_6_ADMIN_INSTITUCIONAL.md` |
| **Chat 7** | Estrategista (não coda) | — |
| **Chat 8+** | Executor avulso (quando precisar) | — |

**Regra:** cada chat só edita o SEU doc. Nunca o de outro.

---

## 🔧 STACK TÉCNICA

- Python 3.14 + FastAPI
- PostgreSQL (Supabase)
- Google Gemini 3.5 Flash (`gemini-3.5-flash`)
- Render (produção — plano gratuito)
- Asaas (PIX em produção)
- Meta Pixel: 1797761131556226
- GitHub: matechtecnologia/matech-atendimento
- Local: `C:\Users\luis gustavos\Desktop\ma_tech_atendimento\`

---

## 📁 ARQUIVOS PRINCIPAIS POR ÁREA

| Área | Arquivos |
|------|----------|
| Atendimento IA | `gemini.py`, `auditor_ia.py`, `limites_mensais.py`, `templates/atendimento_*.html`, `templates/clientes.html`, `templates/resultado.html`, `templates/followups.html`, `templates/meus_nichos.html`, `templates/relatorios.html` |
| Gestão Pessoal | `gestao_pessoal_db.py`, `gestao_pessoal_rotas.py`, `templates/gestao_pessoal_*.html`, `templates/gestao.html`, `templates/gestao_pessoal.html` |
| Gestão Profissional | `templates/gestao_profissional.html` (+ futuros) |
| Consultoria IA | `consultor.py`, `consultor_rotas.py`, `templates/consultoria.html` |
| Conta + Planos | `templates/signup.html`, `templates/login.html`, `templates/onboarding.html`, `templates/planos.html`, `templates/assinar.html`, `templates/pagamento_pix.html`, `templates/indicar.html`, `templates/configuracoes.html`, `asaas.py` |
| Admin + Institucional | `templates/admin*.html`, `templates/landing.html`, `templates/termos.html`, `templates/privacidade.html`, `templates/obrigado.html` |

---

## ✅ O QUE ESTÁ FUNCIONANDO EM PRODUÇÃO

- Landing page com Pixel Meta
- Cadastro + Login + Onboarding
- Atendimento IA (Gemini)
- Plano M.A Tech (17 telas)
- PIX via Asaas (produção real)
- Consultoria IA (admin only, em dev)
- Termos + Privacidade (LGPD)
- Página de obrigado pós-cadastro
- Suporte WhatsApp (landing + menu ☰)
- Instagram no rodapé
- Logo "Tech" verde em 25 arquivos
- Textos do "?" em 19 telas
- Bottom nav: Gestão | Consultoria | Atendimento | Follow-ups | Relatórios
- Menu ☰: Nichos | Planos | Indique e ganhe | Configurações | Suporte | Sair
- Árvore de Gestão: `/gestao` (Pessoal | Profissional)
- Gestão Pessoal Financeira (FASE 2): tabelas + 3 telas + rotas
- Card de clientes redesenhado
- Filtro dentro da busca (clientes)

---

## ⚠️ PROBLEMAS CONHECIDOS

1. **Gemini grátis dá 503 em picos** — resolver com billing pago (semana que vem)
2. **Render gratuito bloqueia SMTP** — email de boas-vindas precisa domínio próprio
3. **`app.min.js` tem cache CDN forte** — renomeado pra `app.min2.js`

---

## 📝 PENDÊNCIAS GLOBAIS

**IMEDIATO:**
- [ ] Ativar billing Gemini
- [ ] Rodar anúncio Meta Ads (R$ 10/dia)
- [ ] Conseguir os primeiros 10 clientes grátis

**MÉDIO:**
- [ ] Meta Ads — montar campanha
- [ ] Testar Asaas em produção
- [ ] Melhorar landing (prova social)
- [ ] Onboarding do cliente (tutorial 3 passos)
- [ ] Asaas templates (emails de cobrança)
- [ ] FASE 3 Gestão Pessoal (IA analisa gastos)
- [ ] FASE 2 Gestão Profissional
- [ ] Terminar "IA que Aprende"

**FUTURO:**
- [ ] Integrações (Google Calendar, WhatsApp API)
- [ ] CRM, Tráfego, Automação
- [ ] Email de boas-vindas (precisa domínio)

---

## 💰 MODELO DE NEGÓCIO

| Plano | Preço | 1º mês | Interações/mês |
|-------|-------|--------|----------------|
| Grátis | R$ 0 | R$ 0 | 150 |
| Básico | R$ 97 | R$ 47 | 1.500 |
| Pro | R$ 297 | R$ 147 | 4.500 |
| Empresarial | R$ 597 | R$ 297 | 9.000 |

- Excedente: R$ 0,10/interação
- Bloqueio: 120% do limite
- Desconto 1º mês: 50%

---

## 📏 REGRAS DE OURO (todos os chats)

1. Arquivo inteiro, nunca patch
2. 1 passo por vez — esperar resposta do Allan
3. Testar local antes de push
4. Rodar `regen.py` depois de mexer em `.js`
5. Ctrl+Shift+R depois de mudança
6. Aguardar 2-3 min após push pro Render
7. Nunca colar senha no chat
8. Sempre `%s` (não `?`) em queries
9. Sempre commit após INSERT/UPDATE
10. Nunca apagar tabela sem autorização

---

## 🔄 COMO TRABALHAR COM O ALLAN

- Não é programador. Cola comando no PowerShell.
- Impaciente. Quer resultado rápido.
- Direto. Fala o que pensa.
- Cansado com frequência.

**Como responder:**
1. Código pronto pra colar (nunca "você pode tentar X")
2. 1 coisa por vez
3. Se der erro, pedir o print
4. Se errar, admitir e consertar rápido
5. Não explicar demais
6. NUNCA 2 perguntas na mesma msg

---

## 📅 CHANGELOG GLOBAL

**01/11/2026**
- Criado sistema de transferência multi-chat
- Documentos: GLOBAL + 6 chats

**29/10/2026**
- Card de clientes redesenhado
- Filtro dentro da busca
- Gestão Pessoal Financeira FASE 2 completa

**13/10/2026**
- Textos do "?" em 19 telas
- Suporte WhatsApp
- Instagram no rodapé
- Termos + Privacidade
- Página de obrigado
- Bottom nav novo
- Árvore de Gestão criada
