# DOCUMENTO DE TRANSFERENCIA - M.A TECH

**Data:** 13/10/2026
**Uso:** Colar no proximo chat pra continuar o trabalho
**Autor:** Allan + Chat 8

---

## ESTADO ATUAL

### Funcionando em producao
- Landing page com Pixel Meta (ID: 1797761131556226)
- Cadastro + Login + Onboarding
- Atendimento IA (Gemini 3.5 Flash)
- Plano M.A Tech (17 telas)
- PIX via Asaas (producao)
- Consultoria IA (admin only, em dev)
- Limites: 150 / 1.500 / 4.500 / 9.000
- Desconto 1o mes: R$ 47, R$ 147, R$ 297
- Excedente: R$ 0,10 por interacao
- Termos de Uso + Politica de Privacidade (LGPD)
- Pagina de obrigado pos-cadastro
- Suporte WhatsApp (landing + menu ☰)
- Instagram no rodape
- Logo "Tech" verde em 25 arquivos
- Textos do "?" em 19 telas
- Bottom nav novo: Gestao | Consultoria | Atendimento | Follow-ups | Relatorios
- Menu ☰: Nichos | Planos | Indique e ganhe | Configuracoes | Suporte | Sair
- Arvore de Gestao: /gestao (Pessoal | Profissional) navegaveis
- Gestao Pessoal Financeira (FASE 2):
  - Tabelas: gestao_pessoal_lancamentos, gestao_pessoal_metas, gestao_pessoal_reserva
  - Painel: /gestao/pessoal/financeira
  - Lancar: /gestao/pessoal/financeira/lancar
  - Extrato: /gestao/pessoal/financeira/extrato

### O que foi consertado (nao mexer)
- Modelo Gemini corrigido: gemini-3.5-flash (era gemini-3.5-flash-lite que nao existe)
- gemini.py limpo (retry removido por enquanto)
- app.min.js renomeado pra app.min2.js (forca cache fresh)
- Card Gestao Empresarial virou "Gestao" (leva pra /gestao)

### PENDENTE IMEDIATO
- [ ] Ativar billing pago do Gemini (SEMANA QUE VEM) - resolve 503
- [ ] Rodar anuncio Meta Ads (R$ 10/dia)
- [ ] Conseguir os primeiros 10 clientes gratis

### PENDENTE MEDIO
- [ ] Meta Ads - montar campanha (publico, criativo, texto, orcamento)
- [ ] Testar Asaas em producao (assinar plano, ver PIX, ver liberacao)
- [ ] Melhorar landing (prova social, copy)
- [ ] Onboarding do cliente (tutorial "como usar em 3 passos")
- [ ] Asaas templates (emails de cobranca)
- [ ] FASE 3 da Gestao Pessoal (IA analisa gastos, sugere cortes, projeta mes)
- [ ] FASE 2 da Gestao Profissional (financeira, CRM, vendas, estoque)
- [ ] Revisar textos "?" das novas telas de Gestao
- [ ] Terminar "IA que Aprende" (botao mobile)

### PENDENTE FUTURO
- [ ] Integracoes (Google Calendar, WhatsApp API)
- [ ] Modulo CRM, Trafego, Automacao
- [ ] Email de boas-vindas (precisa dominio proprio)
- [ ] Gestao Empresarial completa

---

## MODELO DE NEGOCIO

| Plano | Preco | 1o mes | Interacoes/mes |
|-------|-------|--------|----------------|
| Gratis | R$ 0 | R$ 0 | 150 |
| Basico | R$ 97 | R$ 47 | 1.500 |
| Pro | R$ 297 | R$ 147 | 4.500 |
| Empresarial | R$ 597 | R$ 297 | 9.000 |

- Excedente: R$ 0,10/interacao
- Bloqueio: so em 120% do limite
- Desconto 1o mes: 50%

### Custo real (Gemini)
- Gemini 3.5 Flash: ~R$ 0,035 por resposta
- Custo por cliente Basico usando tudo: ~R$ 53/mes
- Lucro por cliente: R$ 44 a R$ 82

### Meta
- 30 dias: 10 clientes gratis
- 90 dias: 5 clientes pagantes

---

## SOBRE O ALLAN

- Nao e programador. Cola comando no PowerShell.
- Impaciente. Quer resultado rapido.
- Cansado. Trabalhou dias seguidos.
- Direto. Fala o que pensa.

### Como trabalhar com ele
1. Codigo pronto pra colar (nunca "voce pode tentar X")
2. 1 coisa por vez
3. Se der erro, pedir o print
4. Se voce errar, admitir e consertar rapido
5. Nao explicar demais. Ele entende rapido.
6. NAO mandar 2 perguntas na mesma msg
7. Se ele disser que nao entendeu, para tudo e explica simples

---

## CREDENCIAIS (nao colar no chat, so pra saber que existem)

- Render: dashboard.render.com (plano gratuito - bloqueia SMTP)
- Supabase: supabase.com
- Gemini: aistudio.google.com (chave no .env + Render)
- Asaas: asaas.com (producao ativa)
- Meta Ads: business.facebook.com (Pixel ID: 1797761131556226)
- GitHub: github.com/matechtecnologia/matech-atendimento

---

## ARQUIVOS PRINCIPAIS

- app.py (servidor)
- gemini.py (IA Atendimento)
- consultor.py + consultor_rotas.py (IA Consultoria)
- auditor_ia.py (IA que Aprende)
- limites_mensais.py (planos)
- gestao_pessoal_db.py (tabelas Gestao Pessoal)
- gestao_pessoal_rotas.py (rotas Gestao Pessoal)
- templates/ (40+ HTML)
- static/ (JS/CSS, app.min2.js)

---

## REGRAS DE OURO

1. Arquivo inteiro, nunca patch
2. 1 passo por vez - esperar resposta
3. Testar local antes de push
4. Rodar regen.py depois de mexer em .js
5. Ctrl+Shift+R depois de mudanca
6. Aguardar 2-3 min apos push pro Render
7. Nunca colar senha no chat
8. Sempre %s (nao ?) em queries
9. Sempre commit apos INSERT/UPDATE
10. Nunca apagar tabela sem autorizacao

---

## LICOES APRENDIDAS

1. Gemini gratis funciona mas da 503 em picos (Google recusa)
2. Modelo gemini-3.5-flash-lite NAO existe - usar gemini-3.5-flash
3. Render gratuito bloqueia SMTP (nao da pra usar Gmail SMTP)
4. app.min.js em producao tem cache CDN forte - renomear pra .min2.js resolve
5. Sempre testar em modo anonimo antes de achar que e cache
6. git checkout HEAD -- arquivo salva quando quebra
7. Sempre rodar regen.py depois de mexer em JS
8. Nao inventar dado - se nao viu, pergunta
9. Nao fazer 2 perguntas na mesma msg
10. NUNCA dizer "tudo uma merda" pra ele
11. Backend FastAPI usa Cookie(None) + middleware injeta usuario_id
12. ler_sessao retorna tupla (uid, tipo), nao uid direto
13. Sublinhado em "_" so vale pra variavel local - Allan copiou e colou literal

---

## PROXIMO PASSO

Allan vai escolher:
A) Rodar anuncio Meta Ads
B) Continuar FASE 3 da Gestao Pessoal (IA analise)
C) Testar Asaas producao
D) Outro

Pergunta o que ele quer. Nao assume.

---

**FIM DO DOCUMENTO**

**Proximo chat:** voce e o Chat 9. Boa sorte.
