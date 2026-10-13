with open("static/app-mobile.js", "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona clique do botao IA apos o menuBtn
antigo = '''        const menuBtn = document.getElementById('app-menu-btn');
        if (menuBtn) {
            menuBtn.addEventListener('click', () => {
                if (typeof window.abrirDrawerApp === 'function') {
                    window.abrirDrawerApp();
                }
            });
        }
    }'''

novo = '''        const menuBtn = document.getElementById('app-menu-btn');
        if (menuBtn) {
            menuBtn.addEventListener('click', () => {
                if (typeof window.abrirDrawerApp === 'function') {
                    window.abrirDrawerApp();
                }
            });
        }

        // ===== BOTAO IA APRENDE =====
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

if antigo in c:
    c = c.replace(antigo, novo, 1)
    with open("static/app-mobile.js", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - clique do botao IA adicionado")
else:
    print("ERRO - nao achei o bloco menuBtn")
