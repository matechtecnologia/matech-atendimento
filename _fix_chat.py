import re

with open("templates/consultoria.html", "r", encoding="utf-8") as f:
    content = f.read()

antigo = """async function enviarMensagem() {
    if (enviando) return;
    const texto = (inputMsg.value || '').trim();
    if (!texto) return;

    if (usado >= limite) {
        mostrarErro('Voce atingiu o limite de hoje. Volta amanha ou faz upgrade.');
        return;
    }

    enviando = true;
    btnEnviar.disabled = true;
    inputMsg.disabled = true;
    inputMsg.value = '';
    inputMsg.style.height = '52px';

    adicionarMensagem(texto, 'cliente');
    adicionarTyping();

    try {
        const r = await fetch('/consultoria/mensagem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mensagem: texto })
        });
        removerTyping();
        const j = await r.json();

        if (j.ok) {
            adicionarMensagem(j.resposta, 'consultor');
            usado = j.usado;
            limite = j.limite;
            atualizarContador();
            if (window.ConsultorPainel && j.status) {
                window.ConsultorPainel.atualizarStatus(j.status);
            }
        } else if (j.erro === 'limite_diario') {
            mostrarErro(j.mensagem);
        } else {
            mostrarErro('Erro: ' + (j.erro || 'falha'));
            adicionarMensagem('[Erro ao gerar resposta. Tenta de novo.]', 'consultor');
        }
    } catch (e) {
        removerTyping();
        mostrarErro('Erro de rede: ' + e.message);
    } finally {
        btnEnviar.disabled = false;
        inputMsg.disabled = false;
        inputMsg.focus();
    }
}"""

novo = """async function enviarMensagem() {
    if (enviando) return;
    const texto = (inputMsg.value || '').trim();
    if (!texto) return;

    if (usado >= limite) {
        mostrarErro('Voce atingiu o limite de hoje. Volta amanha ou faz upgrade.');
        return;
    }

    enviando = true;
    btnEnviar.disabled = true;
    inputMsg.disabled = true;
    inputMsg.value = '';
    inputMsg.style.height = '52px';

    adicionarMensagem(texto, 'cliente');
    adicionarTyping();

    try {
        const r = await fetch('/consultoria/mensagem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mensagem: texto })
        });
        removerTyping();
        
        let j = null;
        try {
            j = await r.json();
        } catch (ejson) {
            mostrarErro('Erro ao ler resposta do servidor.');
            adicionarMensagem('[Erro ao gerar resposta. Tenta de novo.]', 'consultor');
            return;
        }

        if (j.ok) {
            adicionarMensagem(j.resposta, 'consultor');
            usado = j.usado;
            limite = j.limite;
            atualizarContador();
            if (window.ConsultorPainel && j.status) {
                window.ConsultorPainel.atualizarStatus(j.status);
            }
        } else if (j.erro === 'limite_diario') {
            mostrarErro(j.mensagem);
        } else {
            mostrarErro('Erro: ' + (j.erro || 'falha'));
            adicionarMensagem('[Erro ao gerar resposta. Tenta de novo.]', 'consultor');
        }
    } catch (e) {
        removerTyping();
        mostrarErro('Erro de rede: ' + e.message);
    } finally {
        enviando = false;
        btnEnviar.disabled = false;
        inputMsg.disabled = false;
        inputMsg.focus();
    }
}"""

if antigo in content:
    content = content.replace(antigo, novo)
    with open("templates/consultoria.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("OK - enviarMensagem corrigida")
else:
    print("ERRO - nao achei o bloco")
