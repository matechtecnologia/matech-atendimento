# DIARIO DE PRODUCAO - 12 e 13/10/2026

## O QUE FOI FEITO

### 1. IA DE ATENDIMENTO MIGROU PRO GEMINI
- [x] Gemini 3.5 Flash-Lite rodando
- [x] SDK novo (google-genai)
- [x] Funcao universal (_chamar_ia) - troca IA mudando 1 linha
- [x] Prompt grande funcionando (1M tokens de contexto)
- [x] Testado em producao - IA respondendo MUITO bem

### 2. LIMITES E PLANOS ATUALIZADOS
- [x] Gratis: 150 interacoes/mes
- [x] Basico: 1.500 interacoes (R$ 97)
- [x] Pro: 4.500 interacoes (R$ 297)
- [x] Empresarial: 9.000 interacoes (R$ 597)
- [x] Desconto 1o mes: R$ 47, R$ 147, R$ 297
- [x] Excedente: R$ 0,10 por interacao
- [x] Bloqueio so em 120% (da margem)
- [x] Tabela primeira_cobranca criada

### 3. NICHO ATUALIZADO
- [x] Nicho 14 atualizado com dados reais
- [x] Precos corretos
- [x] Prompt regenerado

### 4. PIXEL META ADS INSTALADO
- [x] Pixel ID: 1797761131556226
- [x] PageView na landing
- [x] PageView no login
- [x] Evento Lead quando alguem se cadastra
- [x] Testado com Meta Pixel Helper

### 5. LANDING PAGE ATUALIZADA
- [x] Hero ajustado ("A IA te ajuda a atender...")
- [x] Valores dos planos corretos
- [x] Desconto 1o mes visivel
- [x] FAQ atualizado (excedente R$ 0,10)
- [x] Botao Empresarial "Assinar" (nao mais "falar com vendas")

### 6. IA QUE APRENDE (EM DESENVOLVIMENTO)
- [x] Codigo do auditor criado (auditor_ia.py)
- [x] Tabelas: analises_ia, nicho_campos_extras
- [x] Colunas: vendedores.ia_aprende_ativo, analises_acumuladas
- [x] Rotas API: /api/ia-aprende/status, /toggle, /analise/{id}, /corrigir
- [x] Auditoria automatica funcionando (testado)
- [x] Modelo de cobranca: 1/3 de interacao por analise
- [x] Cobranca automatica: 3 analises = 1 interacao
- [x] REVERTIDO o botao no header mobile (fica pra depois)

### 7. OUTRAS CORRECOES
- [x] Hub: "Bem-vindo de volta" -> "Bem-vindo"
- [x] Consultoria: tela "Em Desenvolvimento" pra cliente
- [x] Consultoria: guard admin (so admin acessa chat)
- [x] Plano M.A Tech (17 telas) populado
- [x] Menu do Plano reorganizado em 4 grupos
- [x] Erro cosmetico "strategic_plans" corrigido
- [x] plano_rotas.py removido (codigo morto)

---

## O QUE ESTA FUNCIONANDO

- IA de Atendimento respondendo com Gemini (MUITO bom)
- Landing com Pixel Meta pronto pra anunciar
- Cadastro + Onboarding + Hub
- Planos com PIX funcionando em producao
- Consultoria (admin only)
- Plano M.A Tech (17 telas)

---

## O QUE ESTA PENDENTE

### IMPORTANTE (proximo)
- [ ] Rodar anuncio Meta Ads (R$ 10/dia)
- [ ] Acompanhar metricas (CTR, CPC, CPL)
- [ ] Conseguir primeiros 10 clientes gratis
- [ ] Coletar feedback

### MEDIO PRAZO
- [ ] Corrigir botao IA que Aprende no header mobile
- [ ] Terminar visual do bloco IA que Aprende
- [ ] Configurar billing pago no Gemini (quando tiver 20+ clientes)

### FUTURO
- [ ] Integracoes (Google Calendar, WhatsApp API)
- [ ] Modulo Gestao
- [ ] Modulo CRM
- [ ] Modulo Trafego
- [ ] Modulo Automacao

---

## ARQUIVOS IMPORTANTES

### Modificados
- gemini.py - migrado pra Gemini
- app.py - limites, desconto, auditoria
- consultor_rotas.py - limites mensais
- consultor_em_breve.py - tela em desenvolvimento
- templates/landing.html - atualizada + Pixel
- templates/signup.html - Pixel
- templates/login.html - Pixel + Lead tracking
- templates/resultado.html - (botao IA revertido)

### Criados
- auditor_ia.py - IA que audita respostas
- limites_mensais.py - logica de planos
- consultor_em_breve.py - tela em dev
- consultor_loading.py - loading da consultoria

### Removidos
- plano_rotas.py (codigo morto)

---

## CREDENCIAIS / ACESSOS

### Render
- Projeto: matech-novo
- URL: matech-novo.onrender.com
- Branch: main
- Auto-deploy: sim

### Supabase
- Region: Sao Paulo
- Plano: Free

### Gemini (Google AI Studio)
- Chave: no .env local + Render Environment
- Plano: FREE (1.500 req/dia)
- Billing: pendente (Google bloqueou upgrade com OR_BACR2_59)

### Asaas
- Modo: PRODUCAO
- PIX: cai na conta real

### Meta Ads
- Pixel ID: 1797761131556226
- Conta de anuncios: 28214431881510391

---

## PROXIMA SESSAO - COMECAR POR AQUI

1. Allan abre o chat
2. Cola:
   "Le o _mestre.md e _diario_producao.md e continua"
3. Chat 7 le, sabe o contexto
4. Decide proximo passo:
   - Se o foco for vender: criar campanha Meta Ads
   - Se o foco for produto: terminar IA que Aprende

---

## LICOES APRENDIDAS

1. Gemini grátis funciona pra comecar (1.500 req/dia)
2. Google bloqueia upgrade em contas novas (OR_BACR2_59)
3. Groq grátis nao aguenta prompt grande (8k tokens)
4. CSS forcado quebra layout mobile - cuidado
5. Sempre testar em modo anonimo antes de achar que e cache
6. Git checkout salva a vida quando quebra

---

**Registrado em:** 13/10/2026
**Local:** _diario_producao.md
