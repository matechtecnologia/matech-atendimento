with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Troca o toggle por um botao grande LIGAR/DESLIGAR
antigo = '''                <!-- TOGGLE IA QUE APRENDE -->
                <div class="ia-toggle-header" id="ia-toggle-wrap">
                    <span class="ia-toggle-icone">🧠</span>
                    <span class="ia-toggle-label">IA Aprende</span>
                    <label class="ia-mini-switch">
                        <input type="checkbox" id="toggle-ia-aprende">
                        <span class="ia-mini-slider"></span>
                    </label>
                    <span class="ia-toggle-status" id="ia-toggle-status">OFF</span>
                </div>'''

novo = '''                <!-- TOGGLE IA QUE APRENDE -->
                <button type="button" class="ia-btn-header" id="ia-btn-header">
                    <span class="ia-btn-icone">🧠</span>
                    <span class="ia-btn-texto">IA Aprende</span>
                    <span class="ia-btn-estado" id="ia-btn-estado">DESLIGADA</span>
                </button>
                <input type="checkbox" id="toggle-ia-aprende" style="display:none;">'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("OK - botao trocado")

# 2. Troca o CSS do toggle
antigo_css = '''        /* TOGGLE NO CABECALHO */
        .ia-toggle-header {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            background: linear-gradient(180deg, #14141f 0%, #111119 100%);
            border: 1px solid #1e1e2e;
            border-radius: 100px;
            margin-right: 12px;
        }
        .ia-toggle-icone { font-size: 14px; }
        .ia-toggle-label {
            font-size: 11px;
            font-weight: 700;
            color: #a855f7;
            letter-spacing: 0.3px;
        }
        .ia-mini-switch {
            position: relative;
            display: inline-block;
            width: 34px;
            height: 20px;
            flex-shrink: 0;
        }
        .ia-mini-switch input { opacity: 0; width: 0; height: 0; }
        .ia-mini-slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background: #2a2a3e;
            transition: 0.25s;
            border-radius: 20px;
            border: 1px solid #1e1e2e;
        }
        .ia-mini-slider:before {
            position: absolute;
            content: "";
            height: 14px;
            width: 14px;
            left: 2px;
            bottom: 2px;
            background: #8080a0;
            transition: 0.25s;
            border-radius: 50%;
        }
        .ia-mini-switch input:checked + .ia-mini-slider {
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
            border-color: #a855f7;
            box-shadow: 0 0 12px rgba(168, 85, 247, 0.5);
        }
        .ia-mini-switch input:checked + .ia-mini-slider:before {
            transform: translateX(14px);
            background: #fff;
        }
        .ia-toggle-status {
            font-size: 10px;
            font-weight: 800;
            color: #8080a0;
            letter-spacing: 0.5px;
            min-width: 26px;
            text-align: right;
        }
        .ia-toggle-status.on {
            color: #a855f7;
            text-shadow: 0 0 8px rgba(168, 85, 247, 0.6);
        }'''

novo_css = '''        /* BOTAO IA QUE APRENDE NO CABECALHO */
        .ia-btn-header {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            background: #14141f;
            border: 1px solid #2a2a3e;
            border-radius: 100px;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.2s;
            margin-right: 10px;
        }
        .ia-btn-header:hover {
            border-color: #a855f7;
            transform: translateY(-1px);
        }
        .ia-btn-header.on {
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
            border-color: #a855f7;
            box-shadow: 0 4px 16px rgba(168, 85, 247, 0.4);
        }
        .ia-btn-icone {
            font-size: 16px;
            line-height: 1;
        }
        .ia-btn-texto {
            font-size: 12px;
            font-weight: 700;
            color: #a855f7;
            letter-spacing: 0.3px;
            white-space: nowrap;
        }
        .ia-btn-header.on .ia-btn-texto {
            color: #fff;
        }
        .ia-btn-estado {
            font-size: 10px;
            font-weight: 800;
            padding: 2px 8px;
            border-radius: 100px;
            background: #2a2a3e;
            color: #8080a0;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }
        .ia-btn-header.on .ia-btn-estado {
            background: rgba(255,255,255,0.25);
            color: #fff;
        }'''

if antigo_css in c:
    c = c.replace(antigo_css, novo_css, 1)
    print("OK - CSS trocado")

# 3. Remove o @media que esconde no mobile
antigo_media = '''        @media (max-width: 600px) {
            .ia-toggle-label { display: none; }
            .ia-toggle-header { padding: 4px 10px; }
        }'''

novo_media = '''        @media (max-width: 600px) {
            .ia-btn-header {
                padding: 6px 10px;
                gap: 6px;
            }
            .ia-btn-texto { font-size: 11px; }
            .ia-btn-estado { font-size: 9px; padding: 2px 6px; }
        }'''

if antigo_media in c:
    c = c.replace(antigo_media, novo_media, 1)
    print("OK - media query corrigida")

# 4. Atualiza o script do toggle
antigo_js = '''    // Toggle ON/OFF
    const tog = document.getElementById('toggle-ia-aprende');
    if (tog) {
        tog.addEventListener('change', async function() {
            const novo = this.checked;
            try {
                const r = await fetch('/api/ia-aprende/toggle', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ativo: novo})
                });
                const j = await r.json();
                if (j.ok) {
                    const st = document.getElementById('ia-toggle-status');
                    if (st) {
                        st.textContent = novo ? 'ON' : 'OFF';
                        if (novo) st.classList.add('on');
                        else st.classList.remove('on');
                    }
                } else {
                    this.checked = !novo;
                }
            } catch(e) {
                this.checked = !novo;
            }
        });
    }'''

novo_js = '''    // Botao IA Aprende
    const btn = document.getElementById('ia-btn-header');
    const togHidden = document.getElementById('toggle-ia-aprende');
    if (btn && togHidden) {
        btn.addEventListener('click', async function() {
            const novo = !togHidden.checked;
            try {
                const r = await fetch('/api/ia-aprende/toggle', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ativo: novo})
                });
                const j = await r.json();
                if (j.ok) {
                    togHidden.checked = novo;
                    const estado = document.getElementById('ia-btn-estado');
                    if (novo) {
                        btn.classList.add('on');
                        if (estado) estado.textContent = 'LIGADA';
                    } else {
                        btn.classList.remove('on');
                        if (estado) estado.textContent = 'DESLIGADA';
                    }
                }
            } catch(e) {}
        });
    }'''

if antigo_js in c:
    c = c.replace(antigo_js, novo_js, 1)
    print("OK - script do botao atualizado")

# 5. Atualiza o carregamento do status
antigo_carregar = '''                if (tog) {
                    tog.checked = j.ativo;
                    const st = document.getElementById('ia-toggle-status');
                    if (st) {
                        st.textContent = j.ativo ? 'ON' : 'OFF';
                        if (j.ativo) st.classList.add('on');
                        else st.classList.remove('on');
                    }
                }'''

novo_carregar = '''                if (togHidden) {
                    togHidden.checked = j.ativo;
                    if (btn) {
                        const estado = document.getElementById('ia-btn-estado');
                        if (j.ativo) {
                            btn.classList.add('on');
                            if (estado) estado.textContent = 'LIGADA';
                        } else {
                            btn.classList.remove('on');
                            if (estado) estado.textContent = 'DESLIGADA';
                        }
                    }
                }'''

if antigo_carregar in c:
    c = c.replace(antigo_carregar, novo_carregar, 1)
    print("OK - carregar status atualizado")

# 6. Remove o atualizarDots antigo e troca
antigo_dots = '''    function atualizarDots(n) {
        // Atualiza o status no cabecalho
        const st = document.getElementById('ia-toggle-status');
        if (st) {
            st.textContent = n + '/3';
            if (n > 0) st.classList.add('on');
        }
    }'''

novo_dots = '''    function atualizarDots(n) {
        // Sem barra de progresso visivel agora (fica escondido no botao)
        // Mas atualiza o title do botao
        const btn = document.getElementById('ia-btn-header');
        if (btn) {
            btn.title = 'IA Aprende: ' + n + '/3 analises';
        }
    }'''

if antigo_dots in c:
    c = c.replace(antigo_dots, novo_dots, 1)
    print("OK - atualizarDots adaptado")

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
