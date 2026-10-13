with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Troca a funcao atualizarDots
antigo = '''    function atualizarDots(n) {
        const dots = document.getElementById('analises-dots');
        const num = document.getElementById('analises-num');
        if (!dots) return;
        let s = '';
        for (let i = 0; i < 3; i++) {
            s += i < n ? '🟣' : '⚪';
        }
        dots.textContent = s;
        num.textContent = n + '/3';
    }'''

novo = '''    function atualizarDots(n) {
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

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("OK - funcao atualizarDots trocada")
else:
    print("AVISO - funcao antiga nao achada")

# Adiciona classe 'off' no card quando toggle esta off
antigo2 = '''                if (tog) {
                    tog.checked = j.ativo;
                    lbl.textContent = j.ativo ? 'ON' : 'OFF';
                    lbl.style.color = j.ativo ? '#a855f7' : '#8a8a8a';
                }'''

novo2 = '''                if (tog) {
                    tog.checked = j.ativo;
                    const card = document.getElementById('bloco-ia-aprende');
                    if (card) {
                        if (j.ativo) card.classList.remove('off');
                        else card.classList.add('off');
                    }
                }'''

if antigo2 in c:
    c = c.replace(antigo2, novo2, 1)
    print("OK - classe off adicionada")
else:
    print("AVISO - bloco toggle nao achado")

# Atualiza o toggle change pra usar card
antigo3 = '''                const j = await r.json();
                if (j.ok) {
                    const lbl = document.getElementById('toggle-label');
                    lbl.textContent = novo ? 'ON' : 'OFF';
                    lbl.style.color = novo ? '#a855f7' : '#8a8a8a';
                } else {
                    this.checked = !novo;
                }'''

novo3 = '''                const j = await r.json();
                if (j.ok) {
                    const card = document.getElementById('bloco-ia-aprende');
                    if (card) {
                        if (novo) card.classList.remove('off');
                        else card.classList.add('off');
                    }
                } else {
                    this.checked = !novo;
                }'''

if antigo3 in c:
    c = c.replace(antigo3, novo3, 1)
    print("OK - toggle change atualizado")
else:
    print("AVISO - bloco toggle change nao achado")

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
