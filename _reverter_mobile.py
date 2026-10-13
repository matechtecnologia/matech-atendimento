with open("static/app-mobile.js", "r", encoding="utf-8") as f:
    c = f.read()

# Volta o grid pra 3 colunas
c = c.replace(
    'grid-template-columns: 44px 1fr 44px 44px !important;',
    'grid-template-columns: 44px 1fr 44px !important;'
)

# Remove o botao IA do HTML
antigo = '''            <button class="app-ia-btn" id="app-ia-btn" aria-label="IA Aprende" title="IA Aprende: ligar/desligar">
                <span class="app-ia-icone">🧠</span>
                <span class="app-ia-dot" id="app-ia-dot"></span>
            </button>
            <button class="app-help-btn" id="app-help-btn" aria-label="Ajuda" title="Ajuda">
                ${window.ICONE ? window.ICONE('ajuda', { tamanho: 22 }) : '?'}
            </button>'''

novo = '''            <button class="app-help-btn" id="app-help-btn" aria-label="Ajuda" title="Ajuda">
                ${window.ICONE ? window.ICONE('ajuda', { tamanho: 22 }) : '?'}
            </button>'''

c = c.replace(antigo, novo)

# Remove o CSS do botao IA
import re
c = re.sub(r'\.app-header \.app-ia-btn[^}]*\}', '', c)
c = re.sub(r'\.app-header \.app-ia-btn \.app-ia-icone[^}]*\}', '', c)
c = re.sub(r'\.app-header \.app-ia-btn \.app-ia-dot[^}]*\}', '', c)
c = re.sub(r'\.app-header \.app-ia-btn\.on[^}]*\}', '', c)
c = re.sub(r'\.app-header \.app-ia-btn\.on \.app-ia-icone[^}]*\}', '', c)
c = re.sub(r'\.app-header \.app-ia-btn\.on \.app-ia-dot[^}]*\}', '', c)
c = re.sub(r'@keyframes pulse-ia[^}]*\}[^}]*\}', '', c)

# Remove o clique do botao IA
antigo_js = '''        // ===== BOTAO IA APRENDE =====
        const iaBtn = document.getElementById('app-ia-btn');
        if (iaBtn) {
            // Carrega status
            fetch('/api/ia-aprende/status')
                .then(r => r.json())
                .then(j => {
                    if (j.ok && j.ativo) {
                        iaBtn.classList.add('on');
                    }
                })
                .catch(() => {});

            // Clique
            iaBtn.addEventListener('click', async () => {
                const estaLigado = iaBtn.classList.contains('on');
                const novo = !estaLigado;
                try {
                    const r = await fetch('/api/ia-aprende/toggle', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ativo: novo})
                    });
                    const j = await r.json();
                    if (j.ok) {
                        if (novo) iaBtn.classList.add('on');
                        else iaBtn.classList.remove('on');
                    }
                } catch(e) {}
            });
        }
    }'''

novo_js = '''    }'''

c = c.replace(antigo_js, novo_js)

with open("static/app-mobile.js", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - app-mobile.js revertido")
