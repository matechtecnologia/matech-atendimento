with open("plano_ui.py", "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona a rota /plano/socio antes de @app.post("/plano/sync")
antigo = '''    @app.post("/plano/sync")'''

novo = '''    # ============================================================
    # SOCIO — conceito estrategico
    # ============================================================
    @app.get("/plano/socio", response_class=HTMLResponse)
    def plano_socio(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")

        corpo = f"""
        {_topo("socio")}
        <div class="container">
            <div class="bloco" style="border-left:4px solid #a855f7; background:linear-gradient(180deg,#14141f 0%,#111119 100%);">
                <div class="badge b-cinza" style="float:right;">CONCEITO</div>
                <h2 style="color:#a855f7; font-size:22px; margin:0;">🧠 O SÓCIO</h2>
                <p style="color:#e8e8e8; font-size:15px; margin-top:12px; line-height:1.7;">
                    <strong>Não é uma ferramenta. Não é SaaS. Não é "CEO".</strong><br>
                    É um <strong style="color:#a855f7;">SÓCIO</strong>.
                </p>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:20px;">
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border:1px solid #2a2a3e;">
                        <div style="color:#8a8a9a; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">CEO (o que existe)</div>
                        <ul style="color:#8a8a9a; font-size:13px; margin:0; padding-left:18px; line-height:1.8;">
                            <li>Espera você pedir</li>
                            <li>Mostra números</li>
                            <li>Responde pergunta</li>
                            <li>Concorda</li>
                            <li>É ferramenta</li>
                        </ul>
                    </div>
                    <div style="background:#1a0a2a; padding:14px; border-radius:8px; border:1px solid #a855f7;">
                        <div style="color:#a855f7; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">SÓCIO (o que ninguém fez)</div>
                        <ul style="color:#e8e8e8; font-size:13px; margin:0; padding-left:18px; line-height:1.8;">
                            <li>Te procura sozinho</li>
                            <li>Diz o que fazer</li>
                            <li>Questiona decisão</li>
                            <li>Discorda quando errado</li>
                            <li>É parceiro</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="bloco">
                <h2>AS 5 BASES DO SÓCIO</h2>
                <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin-top:14px;">
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:3px solid #a855f7;">
                        <div style="color:#a855f7; font-weight:700; margin-bottom:6px;">1. Memória longa</div>
                        <div style="color:#8a8a9a; font-size:12px;">Lembra de decisões passadas, promoções que falharam, padrões do negócio.</div>
                    </div>
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:3px solid #a855f7;">
                        <div style="color:#a855f7; font-weight:700; margin-bottom:6px;">2. Banco unificado</div>
                        <div style="color:#8a8a9a; font-size:12px;">Conecta CRM + Gestão + Agenda + Atendimento num só contexto.</div>
                    </div>
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:3px solid #a855f7;">
                        <div style="color:#a855f7; font-weight:700; margin-bottom:6px;">3. Notificação ativa</div>
                        <div style="color:#8a8a9a; font-size:12px;">Ele te procura. Não espera você perguntar.</div>
                    </div>
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:3px solid #a855f7;">
                        <div style="color:#a855f7; font-weight:700; margin-bottom:6px;">4. Autonomia</div>
                        <div style="color:#8a8a9a; font-size:12px;">Regras do que ele pode fazer sozinho (responder, agendar, cobrar).</div>
                    </div>
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:3px solid #a855f7;">
                        <div style="color:#a855f7; font-weight:700; margin-bottom:6px;">5. Aprendizado</div>
                        <div style="color:#8a8a9a; font-size:12px;">Fica mais inteligente a cada uso. Evolui com você.</div>
                    </div>
                </div>
            </div>

            <div class="bloco">
                <h2>COMO O SÓCIO FUNCIONA</h2>
                <div style="background:#0a0a0f; padding:16px; border-radius:8px; margin-top:12px; font-family:monospace; font-size:12px; color:#8a8a9a; line-height:1.8;">
                    ┌──────────────────────────────┐<br>
                    │      SÓCIO (Maestro)         │<br>
                    └──────────────┬───────────────┘<br>
                           ┌──────┴──────┐<br>
                           ▼             ▼<br>
                    ┌──────────┐  ┌──────────┐<br>
                    │Atendimento│ │Consultoria│<br>
                    │    IA    │ │    IA    │<br>
                    └──────────┘  └──────────┘<br>
                           ▼             ▼<br>
                    ┌──────────┐  ┌──────────┐<br>
                    │  Gestão  │  │  Agenda  │<br>
                    │    IA    │  │    IA    │<br>
                    └──────────┘  └──────────┘<br>
                           ▼             ▼<br>
                    ┌──────────────────────┐<br>
                    │  Banco Unificado     │<br>
                    │  (One Context)       │<br>
                    └──────────────────────┘
                </div>
                <p style="color:#8a8a9a; font-size:13px; margin-top:14px;">
                    O Maestro não faz nada sozinho. Ele <strong style="color:#a855f7;">coordena</strong> as outras IAs.
                </p>
            </div>

            <div class="bloco">
                <h2>EXEMPLOS DE USO</h2>
                <div style="display:flex; flex-direction:column; gap:10px; margin-top:12px;">
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:3px solid #22c55e;">
                        <div style="color:#22c55e; font-size:11px; font-weight:700; letter-spacing:1px; margin-bottom:4px;">ELE TE PROCURA</div>
                        <div style="color:#e8e8e8; font-size:13px; line-height:1.6;">"Bom dia, Allan. Faturamento caiu 15% essa semana. 3 clientes que compravam toda semana não compraram. Quer que eu mande mensagem pra eles?"</div>
                    </div>
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:3px solid #f59e0b;">
                        <div style="color:#f59e0b; font-size:11px; font-weight:700; letter-spacing:1px; margin-bottom:4px;">ELE QUESTIONA</div>
                        <div style="color:#e8e8e8; font-size:13px; line-height:1.6;">Allan: "Vou contratar funcionário."<br>SÓCIO: "Antes disso, margem caiu 8% esse mês. Tem certeza que é hora de aumentar custo fixo?"</div>
                    </div>
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:3px solid #ff5555;">
                        <div style="color:#ff5555; font-size:11px; font-weight:700; letter-spacing:1px; margin-bottom:4px;">ELE DISCORDA</div>
                        <div style="color:#e8e8e8; font-size:13px; line-height:1.6;">Allan: "Vou fazer promoção de 30%."<br>SÓCIO: "Não recomendo. Sua margem é 22%. Com 30% você vende no prejuízo."</div>
                    </div>
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:3px solid #a855f7;">
                        <div style="color:#a855f7; font-size:11px; font-weight:700; letter-spacing:1px; margin-bottom:4px;">ELE APRENDE</div>
                        <div style="color:#e8e8e8; font-size:13px; line-height:1.6;">"Lembra da promoção de 30% em setembro? Não funcionou. Por isso estou sugerindo 15% agora."</div>
                    </div>
                </div>
            </div>

            <div class="bloco">
                <h2>ROADMAP DO SÓCIO</h2>
                <div style="display:flex; flex-direction:column; gap:12px; margin-top:14px;">
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:4px solid #22c55e;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="color:#22c55e; font-weight:700;">FASE 1 — AGORA (3-6 meses)</div>
                            <span class="badge b-verde">EM CURSO</span>
                        </div>
                        <div style="color:#8a8a9a; font-size:12px; margin-top:6px;">Construir as áreas (Atendimento, Consultoria, Gestão). Sem SÓCIO. Ainda é SaaS.</div>
                    </div>
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:4px solid #f59e0b;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="color:#f59e0b; font-weight:700;">FASE 2 — BASE DO SÓCIO (6-12 meses)</div>
                            <span class="badge b-amarelo">PLANEJADO</span>
                        </div>
                        <div style="color:#8a8a9a; font-size:12px; margin-top:6px;">Banco unificado + memória de longo prazo. SÓCIO começa a aparecer.</div>
                    </div>
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:4px solid #a855f7;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="color:#a855f7; font-weight:700;">FASE 3 — SÓCIO ATIVO (12-24 meses)</div>
                            <span class="badge b-cinza">PLANEJADO</span>
                        </div>
                        <div style="color:#8a8a9a; font-size:12px; margin-top:6px;">Notificações proativas + autonomia. SÓCIO vira produto.</div>
                    </div>
                    <div style="background:#0a0a0f; padding:14px; border-radius:8px; border-left:4px solid #7c3aed;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="color:#a78bfa; font-weight:700;">FASE 4 — SÓCIO SUPREMO (24-36 meses)</div>
                            <span class="badge b-cinza">PLANEJADO</span>
                        </div>
                        <div style="color:#8a8a9a; font-size:12px; margin-top:6px;">Ele decide, executa, conecta, aprende. Monopólio de categoria.</div>
                    </div>
                </div>
            </div>

            <div class="bloco">
                <h2>POR QUE É DIFÍCIL DE COPIAR</h2>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:14px;">
                    <div style="background:#1f0a0a; padding:14px; border-radius:8px; border-left:3px solid #ff5555;">
                        <div style="color:#ff5555; font-weight:700; font-size:12px; margin-bottom:8px;">CONCORRENTE COPIA</div>
                        <ul style="color:#8a8a9a; font-size:12px; margin:0; padding-left:18px; line-height:1.8;">
                            <li>Feature de IA</li>
                            <li>Dashboard bonito</li>
                            <li>Integração WhatsApp</li>
                            <li>Preço</li>
                        </ul>
                    </div>
                    <div style="background:#0a1f15; padding:14px; border-radius:8px; border-left:3px solid #22c55e;">
                        <div style="color:#22c55e; font-weight:700; font-size:12px; margin-bottom:8px;">CONCORRENTE NÃO COPIA</div>
                        <ul style="color:#8a8a9a; font-size:12px; margin:0; padding-left:18px; line-height:1.8;">
                            <li>Histórico de aprendizado (leva tempo)</li>
                            <li>Contexto unificado (produto completo)</li>
                            <li>Memória de longo prazo (meses de uso)</li>
                            <li>Proatividade real (confiança)</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="bloco" style="background:linear-gradient(180deg,#1a0a2a 0%,#0f0a1a 100%); border-left:4px solid #a855f7;">
                <h2 style="color:#a855f7;">PREÇO DO SÓCIO</h2>
                <p style="color:#e8e8e8; font-size:18px; margin-top:12px; line-height:1.6;">
                    "Um consultor custa <strong>R$ 5.000/mês</strong>.<br>
                    Um sócio custa <strong style="color:#a855f7;">R$ 297/mês</strong>."
                </p>
            </div>

            <div class="bloco">
                <h2>DECISÃO</h2>
                <ul style="color:#8a8a9a; font-size:13px; margin:0; padding-left:20px; line-height:2;">
                    <li>Registrar como norte estratégico ✅</li>
                    <li>Continuar plano de 7 dias (Gestão + anúncio) ⏳</li>
                    <li>Construir SÓCIO depois dos primeiros clientes ⏳</li>
                    <li>Reposicionar landing quando tiver tração ⏳</li>
                </ul>
            </div>
        </div>
        """
        return HTMLResponse(_html("Sócio", corpo))

    @app.post("/plano/sync")'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    with open("plano_ui.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - rota /plano/socio adicionada")
else:
    print("ERRO - nao achei @app.post(\"/plano/sync\")")
