# DIARIO DE PRODUCAO - 08/10/2026

## O QUE FOI FEITO HOJE

### 1. CONSULTORIA EMPRESARIAL - IA v3 (Prompt Profissional)
- [x] Prompt 2 profissional (80 partes) implementado em consultor.py
- [x] Dossie expandido: nichos detalhados + clientes concretos
- [x] Multiplos nichos suportados (nao so 1)
- [x] Prompt enxuto para caber no limite Groq (8000 tokens/min)
- [x] Regras agressivas: 1 pergunta por resposta, fechamento rapido
- [x] Regra de "nao sei": assume diagnostico apos 2 respostas vagas
- [x] Regra de nicho: sempre citar nicho do cliente
- [x] Regra de nao indicar ferramenta antes do diagnostico

### 2. CONSULTORIA - Painel do Admin
- [x] Tela "EM DESENVOLVIMENTO" (cliente ve isso) - consultor_em_breve.py
- [x] Guard: /consultoria so admin acessa (cliente vai pra /consultoria-premium)
- [x] Rota /api/eh-admin para detectar admin
- [x] Hub aponta pra /consultoria-premium
- [x] Contador admin (99999) funcionando
- [x] Bug do botao enviar (multiplas mensagens) - CORRIGIDO
- [x] Contador de tempo no typing (Xs)

### 3. BANCO DE DADOS
- [x] Tabelas criadas: consultoria_passos, consultorias.vista_em
- [x] 3 passos salvos automaticamente pela IA
- [x] Gargalo detectado: "Respostas lentas e follow-up desorganizado"
- [x] Servico indicado: "atendimento_ia"
- [x] Erro cosmetico "strategic_plans already exists" - CORRIGIDO

### 4. VISUAL / UX
- [x] Loading global (aparece em todas as telas do cliente)
- [x] Menu lateral reorganizado em 4 grupos (PAINEL, PRODUTO, OPERACAO, SISTEMA)
- [x] Consultor_painel.js bump v4

### 5. DOCUMENTACAO
- [x] _projeto_consultoria.md (visao completa do produto)
- [x] Registro de integrações futuras (WhatsApp, Meta Ads, etc)

---

## O QUE ESTA FUNCIONANDO

- Chat da Consultoria (admin) - IA responde com dados reais
- Painel da Consultoria (gargalo, servico, passos)
- Consultoria em desenvolvimento (cliente ve tela premium)
- Plano M.A Tech (17 telas) - populado e funcional
- Atendimento IA - funcionando
- PIX Asaas - sandbox funcionando
- Login + admin - OK

---

## O QUE AINDA FALTA (PROXIMA SESSAO)

### PRIORIDADE ALTA (proximas horas)

1. **Testar o prompt reescrito** - confirmar que:
   - IA faz 1 pergunta (nao 3)
   - Depois de 2 "nao sei", assume diagnostico
   - Cita o nicho especifico
   - NAO entra em loop

2. **Se o teste passar** - subir pro Render
   - `git add .; git commit -m "Prompt hard"; git push`

3. **Se o teste falhar** - mais ajustes no prompt
   - Reduzir ainda mais (15 partes)
   - Mudar temperatura do Groq

### PRIORIDADE MEDIA (proximos dias)

4. **Acesso do consultor aos dados completos**
   - Historico de conversas (cliente final)
   - Atendimentos IA (mensagem + resposta)
   - Follow-ups detalhados
   - Financeiro (receitas, custos)

5. **Calculos automaticos** no dossie
   - Faturamento, margem, conversao, ticket
   - A IA recebe os numeros ja calculados

6. **Memoria de longo prazo**
   - Consultor lembra de consultorias anteriores
   - Comparar semana a semana

### PRIORIDADE BAIXA (futuro)

7. **Integracoes do cliente** (a porta pra Gestao)
   - Google Calendar
   - WhatsApp Business
   - Meta Ads / Google Ads
   - Gmail/Outlook

8. **Permissao LGPD** (checkbox)
9. **Email resumo executivo**
10. **Notificacao proativa**

---

## ESTADO DO BANCO

- vendedor_id=3 e o admin (matechtecnologia01@gmail.com)
- 20 consultorias criadas (13, 14, 15, 16, 17, 18, 19, 20)
- Gargalo/servico/passos: ainda sendo testados
- Consultorias #13-19: teste antigo (com bugs)
- Consultoria #20: teste mais recente

---

## PROBLEMAS CONHECIDOS

1. **IA pergunta em loop** (o bug principal)
   - Causa: prompt com 80 partes tem regras conflitantes
   - Solucao: prompt reescrito hoje (teste pendente)

2. **Painel mostra "0/5 gratis" ao abrir nova consultoria**
   - Causa: cache do consultor_painel.js
   - Solucao: bump v4 (feito, mas pode voltar)

3. **Groq free tier limite 8000 tokens/min**
   - Solucao: prompt enxuto (feito) ou pagar Dev Tier

---

## COMANDOS UTEIS

Testar local:
  python -m uvicorn app:app --reload

Ver consultorias do admin:
  python _ver_consult.py

Ver vendedor do admin:
  python _ver_vend.py

Testar _get_plano:
  python _test_plano.py

---

## ARQUIVOS PRINCIPAIS

- consultor.py - IA consultora (prompt + funcao Groq)
- consultor_rotas.py - Rotas da Consultoria
- consultor_core.py - Dossie do vendedor
- consultor_db.py - Tabelas da Consultoria
- consultor_install.py - Amarra no app.py
- consultor_em_breve.py - Tela "em desenvolvimento"
- consultor_loading.py - Tela de loading
- _projeto_consultoria.md - Visao completa do produto

---

## PROXIMA SESSAO - COMECAR POR AQUI

1. Allan abre o chat
2. Cola o resultado de: python -m uvicorn app:app --reload
3. Testa /consultoria (admin) com "oi" + "nao sei" + "nao sei"
4. Ve se a IA:
   - Faz 1 pergunta so
   - Assume diagnostico apos 2 "nao sei"
   - Cita o nicho
5. Reporta o que aconteceu
6. Continua o ajuste OU sobe pro Render

---

**REGISTRADO EM:** 08/10/2026
**PROXIMA REVISAO:** quando Allan voltar
