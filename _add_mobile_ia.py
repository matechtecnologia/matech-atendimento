with open("static/app-mobile.js", "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona o botao IA Aprende antes do help-btn
antigo = '''            <button class="app-help-btn" id="app-help-btn" aria-label="Ajuda" title="Ajuda">
                ${window.ICONE ? window.ICONE('ajuda', { tamanho: 22 }) : '?'}'''

novo = '''            <button class="app-ia-btn" id="app-ia-btn" aria-label="IA Aprende" title="IA Aprende: ligar/desligar">
                <span class="app-ia-icone">🧠</span>
                <span class="app-ia-dot" id="app-ia-dot"></span>
            </button>
            <button class="app-help-btn" id="app-help-btn" aria-label="Ajuda" title="Ajuda">
                ${window.ICONE ? window.ICONE('ajuda', { tamanho: 22 }) : '?'}'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("OK - botao IA adicionado no header mobile")
else:
    print("ERRO - nao achei o botao help")

# Adiciona o CSS do botao
antigo_css = '''            .app-header .app-menu-btn svg,
            .app-header .app-help-btn svg {'''

novo_css = '''            .app-header .app-ia-btn {
                background: transparent !important;
                border: 1px solid rgba(168, 85, 247, 0.35) !important;
                border-radius: 100px !important;
                padding: 6px 10px !important;
                cursor: pointer !important;
                display: inline-flex !important;
                align-items: center !important;
                gap: 5px !important;
                transition: all 0.25s !important;
                position: relative !important;
                height: 36px !important;
                box-sizing: border-box !important;
            }
            .app-header .app-ia-btn .app-ia-icone {
                font-size: 16px !important;
                line-height: 1 !important;
                filter: grayscale(1) opacity(0.5) !important;
                transition: all 0.25s !important;
            }
            .app-header .app-ia-btn .app-ia-dot {
                width: 6px !important;
                height: 6px !important;
                border-radius: 50% !important;
                background: #4a4a5e !important;
                transition: all 0.25s !important;
            }
            .app-header .app-ia-btn.on {
                background: linear-gradient(135deg, rgba(124, 58, 237, 0.25) 0%, rgba(168, 85, 247, 0.25) 100%) !important;
                border-color: #a855f7 !important;
                box-shadow: 0 0 16px rgba(168, 85, 247, 0.4) !important;
            }
            .app-header .app-ia-btn.on .app-ia-icone {
                filter: grayscale(0) opacity(1) !important;
            }
            .app-header .app-ia-btn.on .app-ia-dot {
                background: #a855f7 !important;
                box-shadow: 0 0 8px #a855f7 !important;
                animation: pulse-ia 1.5s ease-in-out infinite !important;
            }
            @keyframes pulse-ia {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.4; }
            }
            .app-header .app-menu-btn svg,
            .app-header .app-help-btn svg {'''

if antigo_css in c:
    c = c.replace(antigo_css, novo_css, 1)
    print("OK - CSS do botao IA adicionado")
else:
    print("AVISO - CSS nao achado")

with open("static/app-mobile.js", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
