with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Script pra IA que aprende
script = """
<script>
(function() {
    const aid = {{ atendimento_id }};
    
    // Carrega status do toggle
    async function carregarStatus() {
        try {
            const r = await fetch('/api/ia-aprende/status');
            const j = await r.json();
            if (j.ok) {
                const tog = document.getElementById('toggle-ia-aprende');
                const lbl = document.getElementById('toggle-label');
                if (tog) {
                    tog.checked = j.ativo;
                    lbl.textContent = j.ativo ? 'ON' : 'OFF';
                    lbl.style.color = j.ativo ? '#a855f7' : '#8a8a8a';
                }
                atualizarDots(j.analises_acumuladas || 0);
            }
        } catch(e) {}
    }
    
    function atualizarDots(n) {
        const dots = document.getElementById('analises-dots');
        const num = document.getElementById('analises-num');
        if (!dots) return;
        let s = '';
        for (let i = 0; i < 3; i++) {
            s += i < n ? '🟣' : '⚪';
        }
        dots.textContent = s;
        num.textContent = n + '/3';
    }
    
    // Toggle ON/OFF
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
                    const lbl = document.getElementById('toggle-label');
                    lbl.textContent = novo ? 'ON' : 'OFF';
                    lbl.style.color = novo ? '#a855f7' : '#8a8a8a';
                } else {
                    this.checked = !novo;
                }
            } catch(e) {
                this.checked = !novo;
            }
        });
    }
    
    // Carrega analise desse atendimento (se existir)
    async function carregarAnalise() {
        try {
            const r = await fetch('/api/ia-aprende/analise/' + aid);
            const j = await r.json();
            if (j.ok && j.analise && j.analise.inventou) {
                const av = document.getElementById('aviso-ia');
                document.getElementById('aviso-o-que').textContent = 'IA disse: ' + (j.analise.o_que_a_ia_disse || '—');
                document.getElementById('aviso-pergunta').textContent = '⚠️ ' + (j.analise.pergunta_pro_vendedor || 'Corrigir?');
                av.style.display = 'block';
            }
        } catch(e) {}
    }
    
    function corrigirIA() {
        const campo = prompt('Qual o campo que está faltando?\\n\\nEx: endereco, telefone, horario');
        if (!campo) return;
        const valor = prompt('Qual o valor correto pra esse campo?');
        if (!valor) return;
        
        fetch('/api/ia-aprende/corrigir', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({atendimento_id: aid, campo: campo, valor: valor})
        }).then(r => r.json()).then(j => {
            if (j.ok) {
                alert('✓ IA melhorada! Próxima resposta será melhor.');
                document.getElementById('aviso-ia').style.display = 'none';
            } else {
                alert('Erro: ' + (j.erro || 'falha'));
            }
        });
    }
    
    window.corrigirIA = corrigirIA;
    
    carregarStatus();
    setTimeout(carregarAnalise, 2000);
})();
</script>
"""

if "toggle-ia-aprende" in c and "/api/ia-aprende/status" not in c:
    c = c.replace("</body>", script + "\n</body>", 1)
    with open("templates/resultado.html", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - script IA que Aprende adicionado")
else:
    print("AVISO - ja tem ou falta o bloco")
