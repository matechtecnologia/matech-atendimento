with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Atualiza o script pra usar os novos IDs
antigo = '''    function atualizarDots(n) {
        // Atualiza as 3 barras de progresso
        for (let i = 1; i <= 3; i++) {
            const bar = document.getElementById('ia-bar-' + i);
            if (bar) {
                if (i <= n) {
                    bar.classList.add('ativa');
                } else {
                    bar.classList.remove('ativa');
                }
            }
        }
        const custo = document.getElementById('ia-progresso-custo');
        if (custo) {
            custo.textContent = n + '/3 · 1 interação a cada 3 análises';
        }
    }'''

novo = '''    function atualizarDots(n) {
        // Atualiza o status no cabecalho
        const st = document.getElementById('ia-toggle-status');
        if (st) {
            st.textContent = n + '/3';
            if (n > 0) st.classList.add('on');
        }
    }'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("OK - atualizarDots adaptado")

# Atualiza o toggle change
antigo2 = '''                if (tog) {
                    tog.checked = j.ativo;
                    const card = document.getElementById('bloco-ia-aprende');
                    if (card) {
                        if (j.ativo) card.classList.remove('off');
                        else card.classList.add('off');
                    }
                }'''

novo2 = '''                if (tog) {
                    tog.checked = j.ativo;
                    const st = document.getElementById('ia-toggle-status');
                    if (st) {
                        st.textContent = j.ativo ? 'ON' : 'OFF';
                        if (j.ativo) st.classList.add('on');
                        else st.classList.remove('on');
                    }
                }'''

if antigo2 in c:
    c = c.replace(antigo2, novo2, 1)
    print("OK - toggle carregamento adaptado")

antigo3 = '''                const j = await r.json();
                if (j.ok) {
                    const card = document.getElementById('bloco-ia-aprende');
                    if (card) {
                        if (novo) card.classList.remove('off');
                        else card.classList.add('off');
                    }
                } else {
                    this.checked = !novo;
                }'''

novo3 = '''                const j = await r.json();
                if (j.ok) {
                    const st = document.getElementById('ia-toggle-status');
                    if (st) {
                        st.textContent = novo ? 'ON' : 'OFF';
                        if (novo) st.classList.add('on');
                        else st.classList.remove('on');
                    }
                } else {
                    this.checked = !novo;
                }'''

if antigo3 in c:
    c = c.replace(antigo3, novo3, 1)
    print("OK - toggle change adaptado")

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
