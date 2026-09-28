// ============================================
// M.A TECH — Funções globais de UX
// ============================================

// Toast — notificação bonita que aparece no canto
function toast(mensagem, tipo = 'sucesso') {
    const cores = {
        sucesso: { bg: '#0a1f15', border: '#00d97e', cor: '#00d97e', icone: '✓' },
        erro:    { bg: '#1f0a0a', border: '#ff3b3b', cor: '#ff3b3b', icone: '⚠' },
        aviso:   { bg: '#1f1a0a', border: '#f59e0b', cor: '#f59e0b', icone: 'ℹ' },
        info:    { bg: '#0a1a1f', border: '#00d97e', cor: '#00d97e', icone: 'ℹ' }
    };
    const c = cores[tipo] || cores.sucesso;

    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const t = document.createElement('div');
    t.className = 'toast';
    t.style.background = c.bg;
    t.style.borderColor = c.border;
    t.style.color = c.cor;
    t.innerHTML = `<span class="toast-icone">${c.icone}</span><span>${mensagem}</span>`;

    container.appendChild(t);

    requestAnimationFrame(() => t.classList.add('toast-show'));

    setTimeout(() => {
        t.classList.remove('toast-show');
        setTimeout(() => t.remove(), 300);
    }, 3000);
}

// Copiar texto pro clipboard com toast de feedback
function copiarTexto(id, botao) {
    const el = document.getElementById(id);
    if (!el) return;
    const texto = el.innerText || el.textContent;
    navigator.clipboard.writeText(texto).then(() => {
        if (botao) {
            const original = botao.innerText;
            botao.innerText = '✓ COPIADO!';
            botao.style.color = '#00d97e';
            botao.style.borderColor = '#00d97e';
            setTimeout(() => {
                botao.innerText = original;
                botao.style.color = '';
                botao.style.borderColor = '';
            }, 1500);
        }
        toast('Copiado pra área de transferência', 'sucesso');
    }).catch(() => toast('Não foi possível copiar', 'erro'));
}

// Botão com loading interno (evita duplo clique)
function ligarLoadingEmForms() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            const btn = form.querySelector('button[type="submit"]');
            if (btn && !btn.disabled) {
                btn.disabled = true;
                btn.dataset.originalText = btn.innerText;
                btn.innerHTML = '<span class="btn-spinner"></span> Processando...';
                btn.style.opacity = '0.7';
                btn.style.cursor = 'wait';
            }
        });
    });
}

// Confirmação antes de sair de páginas importantes
function confirmarSaida(mensagem) {
    document.querySelectorAll('a[href="/logout"]').forEach(link => {
        link.addEventListener('click', (e) => {
            if (!confirm(mensagem || 'Tem certeza que quer sair?')) {
                e.preventDefault();
            }
        });
    });
}

// Confirmação em botões com atributo data-confirmar
function ligarConfirmacoes() {
    document.querySelectorAll('[data-confirmar]').forEach(el => {
        el.addEventListener('click', (e) => {
            if (!confirm(el.dataset.confirmar)) e.preventDefault();
        });
    });
}

// Inicializa tudo quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    ligarLoadingEmForms();
    ligarConfirmacoes();
});

// Alias pra manter compatibilidade com templates antigos
function copiar(id, botao) { copiarTexto(id, botao); }
