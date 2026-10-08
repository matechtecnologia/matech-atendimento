# ESTADO DO PROJETO M.A TECH
# Este arquivo e a memoria do Chat 7 (gestor).
# Atualizado em: 07/10/2026

## STATUS ATUAL
- Sistema em producao no Render (matech-novo.onrender.com)
- 4 usuarios cadastrados (1 admin, 4 atendentes)
- 32 tabelas no banco (todas do Plano existem)
- 15 das 17 telas do Plano registradas
- 2 telas faltam: /plano/pendencias e /plano/proximos
- Todas as telas do Plano estao VAZIAS (sem conteudo)

## O QUE JA FOI FEITO (sessoes anteriores)
- Etapa 3: extracao de gargalo/servico (max_tokens 1500)
- Painel roxo da Consultoria (drawer + historico)
- Etapa 4A: tabela consultoria_passos + prompt 2 reescrito
- Etapa 4B: badge de pendencias (vista_em + /api/consultoria-pendente)

## O QUE ESTA PENDENTE (proximas tarefas)
1. Popular tabelas do Plano com conteudo real (em andamento)
2. Criar 2 telas faltantes (/plano/pendencias, /plano/proximos)
3. Resolver bug de login em /plano (mostra login mesmo logado como admin)
4. Limpar duplicacao: plano_rotas.py esta morto (plano_ui.py venceu)

## PROBLEMAS CONHECIDOS
- Boot imprime "Plano DB erro: relation strategic_plans already exists" (cosmetico)
- plano_install.py tem blocos duplicados (ROI e comerciais aparecem 2x)

## ARQUIVOS-CHAVE
- app.py (3000+ linhas)
- plano_ui.py (rotas /plano vencedoras - HTML inline)
- plano_ui2.py, plano_ui3.py, plano_roi.py (rotas extras)
- plano_rotas.py (morto - duplicado)
- plano_install.py (orquestra registro das rotas)
- plano_db.py, plano_estrategico.py (criam tabelas)
- consultor_*.py (Consultoria IA)

## ESTRUTURA DE TRABALHO
- Chat 7 (eu) e o gestor do sistema
- Eu escrevo o conteudo, Allan roda, Plano reflete
- Allan nao gerencia o Plano, eu gerencio
- Cada sessao termina com atualizacao deste arquivo

## PROXIMA SESSAO
- Allan cola este arquivo no comeco
- Chat 7 le e continua de onde parou
