with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Encontra e substitui o bloco antigo inteiro
inicio = c.find('<!-- BLOCO 4: IA QUE APRENDE -->')
fim = c.find('<!-- ERRO -->')

if inicio != -1 and fim != -1:
    novo_bloco = '''<!-- BLOCO 4: IA QUE APRENDE -->
        <div class="ia-aprende-card" id="bloco-ia-aprende">
            <!-- HEADER -->
            <div class="ia-header">
                <div class="ia-header-esquerda">
                    <div class="ia-icone">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 2a7 7 0 0 0-7 7c0 2 1 3 1 4v3a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-3c0-1 1-2 1-4a7 7 0 0 0-7-7z"/>
                            <path d="M9 21v-1"/>
                            <path d="M15 21v-1"/>
                        </svg>
                    </div>
                    <div>
                        <h3 class="ia-titulo">IA que Aprende</h3>
                        <p class="ia-subtitulo">Sua IA fica mais inteligente a cada resposta</p>
                    </div>
                </div>
                <label class="ia-switch" id="ia-switch-label">
                    <input type="checkbox" id="toggle-ia-aprende">
                    <span class="ia-switch-slider"></span>
                </label>
            </div>

            <!-- PROGRESSO -->
            <div class="ia-progresso-wrap" id="ia-progresso-wrap">
                <div class="ia-progresso-header">
                    <span class="ia-progresso-label">Progresso do ciclo</span>
                    <span class="ia-progresso-custo" id="ia-progresso-custo">0/3 · 1 interação a cada 3 análises</span>
                </div>
                <div class="ia-progresso-barras">
                    <div class="ia-bar" id="ia-bar-1"></div>
                    <div class="ia-bar" id="ia-bar-2"></div>
                    <div class="ia-bar" id="ia-bar-3"></div>
                </div>
            </div>

            <!-- AVISO DE CORRECAO -->
            <div class="ia-aviso" id="aviso-ia">
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
        </div>

        <style>
        .ia-aprende-card {
            background: linear-gradient(180deg, #14141f 0%, #111119 100%);
            border: 1px solid #1e1e2e;
            border-radius: 16px;
            padding: 22px;
            margin-top: 24px;
            position: relative;
            overflow: hidden;
        }
        .ia-aprende-card::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, #7c3aed, #a855f7, #00d97e);
            opacity: 0.6;
        }
        .ia-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            margin-bottom: 20px;
        }
        .ia-header-esquerda {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .ia-icone {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            flex-shrink: 0;
            box-shadow: 0 4px 16px rgba(124, 58, 237, 0.35);
        }
        .ia-titulo {
            font-size: 15px;
            font-weight: 700;
            color: #fff;
            margin: 0 0 2px;
            letter-spacing: -0.2px;
        }
        .ia-subtitulo {
            font-size: 12px;
            color: #8080a0;
            margin: 0;
        }
        /* SWITCH */
        .ia-switch {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 28px;
            flex-shrink: 0;
        }
        .ia-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        .ia-switch-slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background: #2a2a3e;
            transition: 0.25s;
            border-radius: 28px;
            border: 1px solid #1e1e2e;
        }
        .ia-switch-slider:before {
            position: absolute;
            content: "";
            height: 20px;
            width: 20px;
            left: 3px;
            bottom: 3px;
            background: #8080a0;
            transition: 0.25s;
            border-radius: 50%;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        }
        .ia-switch input:checked + .ia-switch-slider {
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
            border-color: #a855f7;
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.4);
        }
        .ia-switch input:checked + .ia-switch-slider:before {
            transform: translateX(22px);
            background: #fff;
        }
        /* PROGRESSO */
        .ia-progresso-wrap {
            padding: 16px;
            background: rgba(124, 58, 237, 0.06);
            border: 1px solid rgba(124, 58, 237, 0.15);
            border-radius: 12px;
            margin-bottom: 16px;
        }
        .ia-progresso-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 8px;
        }
        .ia-progresso-label {
            font-size: 11px;
            color: #8080a0;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
        }
        .ia-progresso-custo {
            font-size: 11px;
            color: #a78bfa;
            font-family: monospace;
            font-weight: 700;
        }
        .ia-progresso-barras {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 8px;
        }
        .ia-bar {
            height: 6px;
            background: #1e1e2e;
            border-radius: 3px;
            overflow: hidden;
            position: relative;
            transition: all 0.4s ease;
        }
        .ia-bar::after {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(90deg, #7c3aed, #a855f7);
            border-radius: 3px;
            opacity: 0;
            transition: opacity 0.4s;
        }
        .ia-bar.ativa::after {
            opacity: 1;
            box-shadow: 0 0 12px rgba(168, 85, 247, 0.6);
        }
        /* AVISO */
        .ia-aviso {
            display: none;
            background: linear-gradient(180deg, #1f0a2a 0%, #1a0a24 100%);
            border: 1px solid rgba(168, 85, 247, 0.3);
            border-radius: 12px;
            padding: 16px;
            margin-top: 16px;
        }
        .ia-aviso-topo {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #d8b4fe;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 14px;
            padding-bottom: 14px;
            border-bottom: 1px solid rgba(168, 85, 247, 0.15);
        }
        .ia-aviso-topo svg {
            color: #f59e0b;
            flex-shrink: 0;
        }
        .ia-aviso-conteudo {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 14px;
        }
        .ia-aviso-linha {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
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
        /* ESCONDE PROGRESSO QUANDO OFF */
        .ia-aprende-card.off .ia-progresso-wrap {
            opacity: 0.4;
        }
        </style>

        '''
    
    c = c[:inicio] + novo_bloco + c[fim:]
    with open("templates/resultado.html", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - visual premium aplicado")
else:
    print("ERRO - nao achei o bloco antigo")
