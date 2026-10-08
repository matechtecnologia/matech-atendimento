with open("templates/consultoria.html", "r", encoding="utf-8") as f:
    c = f.read()

antigo = """function adicionarTyping() {
    const box = document.getElementById('chat-mensagens');
    if (!box) return;
    const linha = document.createElement('div');
    linha.className = 'consult-linha';
    linha.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'consult-avatar-mini ia';
    const img = document.createElement('img');
    img.src = LOGO_URL;
    img.alt = 'M.A Tech';
    avatar.appendChild(img);

    const bolha = document.createElement('div');
    bolha.className = 'consult-msg consultor consult-typing';
    bolha.innerHTML = '<span></span><span></span><span></span>';

    linha.appendChild(avatar);
    linha.appendChild(bolha);
    box.appendChild(linha);
    box.scrollTop = box.scrollHeight;
}"""

novo = """function adicionarTyping() {
    const box = document.getElementById('chat-mensagens');
    if (!box) return;
    const linha = document.createElement('div');
    linha.className = 'consult-linha';
    linha.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'consult-avatar-mini ia';
    const img = document.createElement('img');
    img.src = LOGO_URL;
    img.alt = 'M.A Tech';
    avatar.appendChild(img);

    const bolha = document.createElement('div');
    bolha.className = 'consult-msg consultor consult-typing';
    bolha.innerHTML = '<span></span><span></span><span></span><span id="typing-tempo" style="margin-left:8px;color:#8a8a8a;font-size:12px;"></span>';

    linha.appendChild(avatar);
    linha.appendChild(bolha);
    box.appendChild(linha);
    box.scrollTop = box.scrollHeight;

    // Contador de tempo
    const inicio = Date.now();
    const tempoEl = document.getElementById('typing-tempo');
    if (window.typingInterval) clearInterval(window.typingInterval);
    window.typingInterval = setInterval(() => {
        if (!document.getElementById('typing-tempo')) {
            clearInterval(window.typingInterval);
            return;
        }
        const s = Math.floor((Date.now() - inicio) / 1000);
        tempoEl.textContent = s + 's';
    }, 500);
}"""

if antigo in c:
    c = c.replace(antigo, novo)
    with open("templates/consultoria.html", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - contador de tempo adicionado")
else:
    print("ERRO - nao achei o bloco")
