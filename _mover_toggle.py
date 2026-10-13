with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Adiciona o toggle no cabecalho
antigo_header = '''        <div class="topo">
            <h1>M.A Tech</h1>
            <div class="usuario-info">
                <span>{{ usuario_nome }}</span>
                <a href="/clientes">Clientes</a>
                {% if usuario_tipo == 'admin' %}<a href="/admin">Admin</a>{% endif %}
                <a href="/logout">Sair</a>
            </div>
        </div>'''

novo_header = '''        <div class="topo">
            <h1>M.A Tech</h1>
            <div class="usuario-info">
                <!-- TOGGLE IA QUE APRENDE -->
                <div class="ia-toggle-header" id="ia-toggle-wrap">
                    <span class="ia-toggle-icone">🧠</span>
                    <span class="ia-toggle-label">IA Aprende</span>
                    <label class="ia-mini-switch">
                        <input type="checkbox" id="toggle-ia-aprende">
                        <span class="ia-mini-slider"></span>
                    </label>
                    <span class="ia-toggle-status" id="ia-toggle-status">OFF</span>
                </div>
                <span>{{ usuario_nome }}</span>
                <a href="/clientes">Clientes</a>
                {% if usuario_tipo == 'admin' %}<a href="/admin">Admin</a>{% endif %}
                <a href="/logout">Sair</a>
            </div>
        </div>'''

if antigo_header in c:
    c = c.replace(antigo_header, novo_header, 1)
    print("OK - toggle adicionado no cabecalho")
else:
    print("AVISO - cabecalho nao achado")

# 2. Remove o bloco antigo (o grandão roxo) - deixa so o aviso
inicio = c.find('<!-- BLOCO 4: IA QUE APRENDE -->')
fim = c.find('<!-- ERRO -->')

if inicio != -1 and fim != -1:
    novo_bloco = '''<!-- AVISO IA QUE APRENDE (aparece so quando a IA inventa) -->
        <div class="ia-aviso" id="aviso-ia" style="display:none;">
            <div class="ia-aviso-topo">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                <span>A IA usou informação que não estava no cadastro</span>
            </div>
            <div class="ia-aviso-conteudo">
                <div class="ia-aviso-linha">
                    <span class="ia-aviso-chave">O que ela disse</span>
                    <span class="ia-aviso-valor" id="aviso-o-que">—</span>
                </div>
                <div class="ia-aviso-linha">
                    <span class="ia-aviso-chave">O que falta</span>
                    <span class="ia-aviso-valor" id="aviso-pergunta">—</span>
                </div>
            </div>
            <button class="ia-btn-corrigir" onclick="corrigirIA()">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                </svg>
                Corrigir agora
            </button>
        </div>

        <style>
        /* TOGGLE NO CABECALHO */
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
        }
        /* AVISO */
        .ia-aviso {
            background: linear-gradient(180deg, #1f0a2a 0%, #1a0a24 100%);
            border: 1px solid rgba(168, 85, 247, 0.3);
            border-left: 4px solid #a855f7;
            border-radius: 12px;
            padding: 16px 18px;
            margin-top: 20px;
        }
        .ia-aviso-topo {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #d8b4fe;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 14px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(168, 85, 247, 0.15);
        }
        .ia-aviso-topo svg { color: #f59e0b; flex-shrink: 0; }
        .ia-aviso-conteudo {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 14px;
        }
        .ia-aviso-linha { display: flex; flex-direction: column; gap: 4px; }
        .ia-aviso-chave {
            font-size: 10px;
            color: #8080a0;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
        }
        .ia-aviso-valor {
            font-size: 13px;
            color: #e8e8f0;
            line-height: 1.5;
        }
        .ia-btn-corrigir {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
            color: #fff;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: 700;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
            box-shadow: 0 4px 14px rgba(124, 58, 237, 0.4);
            font-family: inherit;
        }
        .ia-btn-corrigir:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(124, 58, 237, 0.55);
        }
        @media (max-width: 600px) {
            .ia-toggle-label { display: none; }
            .ia-toggle-header { padding: 4px 10px; }
        }
        </style>

        '''
    c = c[:inicio] + novo_bloco + c[fim:]
    print("OK - bloco antigo substituido por aviso limpo")

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
