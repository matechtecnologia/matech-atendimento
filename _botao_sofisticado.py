with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Troca o cabecalho inteiro
antigo = '''    <div class="container-atendimento">
        <div class="topo">
            <h1>M.A Tech</h1>
            <div class="usuario-info">
                <!-- TOGGLE IA QUE APRENDE -->
                <button type="button" class="ia-btn-header" id="ia-btn-header">
                    <span class="ia-btn-icone">🧠</span>
                    <span class="ia-btn-texto">IA Aprende</span>
                    <span class="ia-btn-estado" id="ia-btn-estado">DESLIGADA</span>
                </button>
                <input type="checkbox" id="toggle-ia-aprende" style="display:none;">
                <span>{{ usuario_nome }}</span>
                <a href="/clientes">Clientes</a>
                {% if usuario_tipo == 'admin' %}<a href="/admin">Admin</a>{% endif %}
                <a href="/logout">Sair</a>
            </div>
        </div>'''

novo = '''    <div class="container-atendimento">
        <div class="topo">
            <h1>M.A Tech</h1>
            <div class="usuario-info">
                <input type="checkbox" id="toggle-ia-aprende" style="display:none;">
                <button type="button" class="btn-ia" id="ia-btn-header" title="IA Aprende: ligar/desligar">
                    <span class="btn-ia-icone">🧠</span>
                    <span class="btn-ia-txt">IA Aprende</span>
                    <span class="btn-ia-status">
                        <span class="dot"></span>
                        <span id="ia-btn-estado">OFF</span>
                    </span>
                </button>
                <span class="usuario-nome">{{ usuario_nome }}</span>
                <a href="/clientes">Clientes</a>
                {% if usuario_tipo == 'admin' %}<a href="/admin">Admin</a>{% endif %}
                <a href="/logout">Sair</a>
            </div>
        </div>'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("OK - cabecalho reescrito")

# Substitui todo o CSS do botao + media
inicio_css = c.find('        /* BOTAO IA QUE APRENDE NO CABECALHO */')
fim_css = c.find('        @media (max-width: 600px) {', inicio_css)

if inicio_css != -1 and fim_css != -1:
    novo_css = '''        /* BOTAO IA APRENDE - DESIGN SOFISTICADO */
        .btn-ia {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px 6px 10px;
            background: rgba(124, 58, 237, 0.08);
            border: 1px solid rgba(124, 58, 237, 0.25);
            border-radius: 100px;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            margin-right: 12px;
            position: relative;
            overflow: hidden;
        }
        .btn-ia::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 0;
        }
        .btn-ia > * {
            position: relative;
            z-index: 1;
        }
        .btn-ia:hover {
            border-color: #a855f7;
            background: rgba(124, 58, 237, 0.15);
            transform: translateY(-1px);
        }
        .btn-ia.on {
            border-color: transparent;
            box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4);
        }
        .btn-ia.on::before {
            opacity: 1;
        }
        .btn-ia-icone {
            font-size: 14px;
            line-height: 1;
            filter: grayscale(1);
            opacity: 0.6;
            transition: all 0.25s;
        }
        .btn-ia.on .btn-ia-icone {
            filter: grayscale(0);
            opacity: 1;
            text-shadow: 0 0 10px rgba(255,255,255,0.5);
        }
        .btn-ia-txt {
            font-size: 11px;
            font-weight: 700;
            color: #a78bfa;
            letter-spacing: 0.3px;
            white-space: nowrap;
            transition: color 0.25s;
        }
        .btn-ia.on .btn-ia-txt {
            color: #fff;
        }
        .btn-ia-status {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 9px;
            font-weight: 800;
            color: #6a6a80;
            letter-spacing: 0.5px;
            background: rgba(0,0,0,0.3);
            padding: 3px 7px;
            border-radius: 100px;
            transition: all 0.25s;
        }
        .btn-ia-status .dot {
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: #6a6a80;
            transition: all 0.25s;
        }
        .btn-ia.on .btn-ia-status {
            color: #fff;
            background: rgba(255,255,255,0.2);
        }
        .btn-ia.on .btn-ia-status .dot {
            background: #0f0;
            box-shadow: 0 0 8px #0f0;
            animation: pulse-dot 1.5s ease-in-out infinite;
        }
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        '''
    c = c[:inicio_css] + novo_css + c[fim_css:]
    print("OK - CSS reescrito")

# Corrige a media query mobile
antigo_media = '''        @media (max-width: 600px) {
            .ia-btn-header {
                padding: 6px 10px;
                gap: 6px;
            }
            .ia-btn-texto { font-size: 11px; }
            .ia-btn-estado { font-size: 9px; padding: 2px 6px; }
        }'''

novo_media = '''        @media (max-width: 600px) {
            .topo {
                padding: 10px 12px !important;
                flex-wrap: wrap;
                gap: 8px;
            }
            .topo h1 {
                font-size: 14px !important;
            }
            .usuario-info {
                gap: 6px !important;
                font-size: 11px !important;
                flex-wrap: wrap;
            }
            .usuario-nome {
                display: none;
            }
            .btn-ia {
                padding: 5px 10px 5px 8px;
                margin-right: 0;
                gap: 6px;
            }
            .btn-ia-icone { font-size: 12px; }
            .btn-ia-txt { font-size: 10px; }
            .btn-ia-status {
                font-size: 8px;
                padding: 2px 6px;
                gap: 3px;
            }
            .btn-ia-status .dot {
                width: 4px;
                height: 4px;
            }
        }'''

if antigo_media in c:
    c = c.replace(antigo_media, novo_media, 1)
    print("OK - media query reescrita")

# Atualiza o JavaScript
antigo_js = '''    // Botao IA Aprende
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
                        if (estado) estado.textContent = 'ON';
                    } else {
                        btn.classList.remove('on');
                        if (estado) estado.textContent = 'OFF';
                    }
                }
            } catch(e) {}
        });
    }'''

if antigo_js in c:
    c = c.replace(antigo_js, novo_js, 1)
    print("OK - JS atualizado")

# Atualiza o carregamento do status
antigo_carregar = '''                if (togHidden) {
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

novo_carregar = '''                if (togHidden) {
                    togHidden.checked = j.ativo;
                    if (btn) {
                        const estado = document.getElementById('ia-btn-estado');
                        if (j.ativo) {
                            btn.classList.add('on');
                            if (estado) estado.textContent = 'ON';
                        } else {
                            btn.classList.remove('on');
                            if (estado) estado.textContent = 'OFF';
                        }
                    }
                }'''

if antigo_carregar in c:
    c = c.replace(antigo_carregar, novo_carregar, 1)
    print("OK - carregamento status atualizado")

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
