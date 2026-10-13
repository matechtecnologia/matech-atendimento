with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

antigo = '''        <!-- ERRO -->
        <div id="erro-box" style="display:none;" class="erro">⚠️ <span id="erro-texto"></span></div>'''

novo = '''        <!-- BLOCO 4: IA QUE APRENDE -->
        <div class="bloco bloco-wrap" id="bloco-ia-aprende" style="border-left:4px solid #a855f7; margin-top:20px;">
            <div class="bloco-topo" style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="color:#a855f7;">🧠 IA QUE APRENDE</h2>
                <label style="display:flex; align-items:center; gap:8px; cursor:pointer; user-select:none;">
                    <input type="checkbox" id="toggle-ia-aprende" style="width:44px; height:24px; cursor:pointer; accent-color:#a855f7;">
                    <span id="toggle-label" style="color:#8a8a8a; font-size:13px; font-weight:700;">OFF</span>
                </label>
            </div>
            <div style="margin-top:12px;">
                <p style="color:#8a8a8a; font-size:13px; line-height:1.6; margin:0;">
                    Ligue para a IA melhorar a cada resposta. Custa 1/3 de 1 interação por análise (3 análises = 1 interação).
                </p>
                <div id="analises-status" style="margin-top:12px; display:flex; align-items:center; gap:10px;">
                    <span style="font-family:monospace; font-size:14px; color:#a855f7; font-weight:700;">
                        <span id="analises-dots">⚪⚪⚪</span>
                        <span id="analises-num" style="margin-left:8px;">0/3</span>
                    </span>
                </div>
                <div id="aviso-ia" style="display:none; margin-top:14px; padding:14px; background:#1f0a2a; border-left:4px solid #a855f7; border-radius:8px;">
                    <p style="color:#e8e8e8; font-size:14px; font-weight:700; margin:0 0 8px 0;" id="aviso-titulo">⚠️ A IA usou informação que não estava no cadastro.</p>
                    <p style="color:#8a8a8a; font-size:13px; margin:0 0 6px 0;" id="aviso-o-que">—</p>
                    <p style="color:#a855f7; font-size:13px; font-weight:700; margin:0 0 12px 0;" id="aviso-pergunta">—</p>
                    <button onclick="corrigirIA()" style="background:#a855f7; color:#fff; border:none; padding:10px 20px; border-radius:8px; font-weight:700; cursor:pointer; font-size:13px;">
                        ✓ CORRIGIR AGORA
                    </button>
                </div>
            </div>
        </div>

        <!-- ERRO -->
        <div id="erro-box" style="display:none;" class="erro">⚠️ <span id="erro-texto"></span></div>'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    with open("templates/resultado.html", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - bloco IA que Aprende adicionado")
else:
    print("ERRO - nao achei o bloco")
