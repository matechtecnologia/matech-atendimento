with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# 1. O script carrega as analises no carregamento
# Mas o problema é que ele so carrega UMA VEZ (no setTimeout 2000)
# E se o resultado ainda nao estiver pronto, nao pega nada

# Troca o setTimeout por polling
antigo = '''    carregarStatus();
    setTimeout(carregarAnalise, 2000);'''

novo = '''    carregarStatus();
    
    // Tenta carregar a analise a cada 2s, ate 30s
    let _tentativas = 0;
    const _pollAnalise = setInterval(() => {
        _tentativas++;
        carregarAnalise();
        if (_tentativas >= 15) clearInterval(_pollAnalise);
    }, 2000);'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("OK - polling de analise adicionado")
else:
    print("AVISO - bloco antigo nao achado")

# 2. Corrigir o carregarAnalise pra sempre atualizar
antigo2 = '''    async function carregarAnalise() {
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
    }'''

novo2 = '''    async function carregarAnalise() {
        try {
            const r = await fetch('/api/ia-aprende/analise/' + aid);
            const j = await r.json();
            if (j.ok && j.analise) {
                // Sempre atualiza o progresso
                const total = j.total_analises || 0;
                atualizarDots(total);
                
                // Se inventou, mostra o aviso
                if (j.analise.inventou) {
                    const av = document.getElementById('aviso-ia');
                    if (av) {
                        document.getElementById('aviso-o-que').textContent = j.analise.o_que_a_ia_disse || '—';
                        document.getElementById('aviso-pergunta').textContent = j.analise.pergunta_pro_vendedor || 'Corrigir?';
                        av.style.display = 'block';
                    }
                }
            } else if (j.ok) {
                // Sem analise ainda - atualiza so o progresso
                const st = await fetch('/api/ia-aprende/status');
                const sj = await st.json();
                if (sj.ok) atualizarDots(sj.analises_acumuladas || 0);
            }
        } catch(e) {}
    }'''

if antigo2 in c:
    c = c.replace(antigo2, novo2, 1)
    print("OK - carregarAnalise atualizado")
else:
    print("AVISO - funcao carregarAnalise nao achada")

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
