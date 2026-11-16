// ============================================
// M.A Tech — App Mobile (header + bandeja + busca)
// ============================================

(function() {
    'use strict';

    function isMobile() {
        return window.matchMedia('(max-width: 768px)').matches;
    }

    function getUsuario() {
        const span = document.querySelector('.usuario-info span');
        return span ? span.textContent.trim() : 'Usuário';
    }

    function isAdmin() {
        if (document.querySelector('.usuario-info a[href="/admin"]')) return true;
        if (document.body && document.body.dataset && document.body.dataset.isAdmin === 'true') return true;
        const meta = document.querySelector('meta[name="usuario-tipo"]');
        if (meta && meta.content === 'admin') return true;
        return false;
    }

    function getNomeTela() {
        const path = window.location.pathname;
        if (path === '/clientes' || path === '/bem_vindo' || path.startsWith('/cliente/')) return 'Atendimento';
        if (path === '/gestao/pessoal/financeira') return 'Gestão Pessoal Financeira';
        if (path === '/gestao/pessoal/tempo') return 'Gestão do Tempo';
        if (path === '/gestao/pessoal') return 'Gestão Pessoal';
        if (path === '/gestao') return 'Gestão';
        if (path === '/planos' || path === '/assinar' || path.startsWith('/pagamento/')) return 'Planos';
        if (path === '/followups') return 'Follow-ups';
        if (path === '/relatorios') return 'Relatórios';
        if (path === '/configuracoes') return 'Configurações';
        if (path === '/meus_nichos' || path === '/novo_nicho') return 'Nichos';
        if (path === '/indicar') return 'Indique e Ganhe';
        if (path === '/notas') return 'Notas';
        if (path === '/consultoria') return 'Consultoria';
        if (path === '/socio') return 'Sócio IA';
        if (path === '/termos') return 'Termos de Uso';
        if (path === '/privacidade') return 'Privacidade';
        if (path === '/plano' || path.startsWith('/plano/')) return 'Plano M.A Tech';
        if (path === '/admin/dashboard') return 'Dashboard';
        if (path === '/admin/leads') return 'Leads';
        if (path === '/admin' || path.startsWith('/admin/')) return 'Admin';
        return 'M.A Tech';
    }

    function rotaAtiva() {
        return window.location.pathname;
    }

    // ===== CSS =====
    function injetarCSSHeader() {
        if (document.getElementById('app-header-premium')) return;
        const st = document.createElement('style');
        st.id = 'app-header-premium';
        st.textContent = `
            .app-header {
                display: grid !important;
                grid-template-columns: 42px 1fr 42px 42px !important;
                align-items: center !important;
                gap: 8px !important;
                padding: 10px 12px !important;
                padding-top: calc(10px + env(safe-area-inset-top, 0px)) !important;
                background: linear-gradient(180deg, rgba(15,15,15,0.98) 0%, rgba(15,15,15,0.88) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border-bottom: 1px solid rgba(0,217,126,0.12) !important;
                position: sticky !important;
                top: 0 !important;
                z-index: 9900 !important;
                box-shadow: 0 2px 20px rgba(0,0,0,0.5) !important;
            }
            html[data-tema="claro"] .app-header {
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.88) 100%) !important;
                border-bottom-color: rgba(0,217,126,0.2) !important;
            }
            .app-header .app-menu-btn,
            .app-header .app-help-btn,
            .app-header .app-config-btn {
                width: 42px !important;
                height: 42px !important;
                padding: 0 !important;
                border-radius: 12px !important;
                background: rgba(0,217,126,0.08) !important;
                border: 1px solid rgba(0,217,126,0.25) !important;
                color: #00d97e !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                cursor: pointer !important;
                transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
                text-decoration: none !important;
            }
            .app-header .app-menu-btn:hover,
            .app-header .app-help-btn:hover,
            .app-header .app-config-btn:hover {
                border-color: rgba(0,217,126,0.6) !important;
                box-shadow: 0 0 20px rgba(0,217,126,0.2) !important;
            }
            .app-header .app-menu-btn:active,
            .app-header .app-help-btn:active,
            .app-header .app-config-btn:active {
                transform: scale(0.92) !important;
            }
            .app-header .app-menu-btn svg,
            .app-header .app-help-btn svg,
            .app-header .app-config-btn svg {
                width: 20px !important;
                height: 20px !important;
            }
            .app-header .logo-app {
                display: inline-flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 2px !important;
                text-decoration: none !important;
                margin: 0 auto !important;
                padding: 0 4px !important;
                max-width: 100% !important;
            }
            .app-header .logo-img {
                height: 32px !important;
                width: auto !important;
                display: block !important;
                filter: drop-shadow(0 0 12px rgba(0,217,126,0.35)) !important;
            }
            .app-header .logo-nome-tela {
                font-size: 10px !important;
                font-weight: 700 !important;
                color: #8a8a8a !important;
                letter-spacing: 0.06em !important;
                text-transform: uppercase !important;
                white-space: nowrap !important;
                line-height: 1 !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
                max-width: 100% !important;
            }
            html[data-tema="claro"] .app-header .logo-nome-tela {
                color: #4a4a4a !important;
            }

            /* BANDEJA */
            .app-bandeja {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                height: 100vh !important;
                height: 100dvh !important;
                width: 86vw !important;
                max-width: 360px !important;
                background: #0f0f0f !important;
                border-right: 1px solid rgba(0,217,126,0.15) !important;
                transform: translateX(-100%) !important;
                transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
                z-index: 9950 !important;
                display: flex !important;
                flex-direction: column !important;
                padding-top: env(safe-area-inset-top, 0px) !important;
                overflow: hidden !important;
            }
            .app-bandeja.aberto { transform: translateX(0) !important; }
            html[data-tema="claro"] .app-bandeja { background: #ffffff !important; }

            .app-bandeja-header {
                padding: 14px 16px 10px !important;
                border-bottom: 1px solid rgba(0,217,126,0.12) !important;
                flex-shrink: 0 !important;
            }
            .app-bandeja-header .avatar {
                width: 40px !important;
                height: 40px !important;
                border-radius: 50% !important;
                background: rgba(0,217,126,0.15) !important;
                color: #00d97e !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-weight: 800 !important;
                font-size: 16px !important;
                margin-bottom: 6px !important;
            }
            .app-bandeja-header .nome {
                font-weight: 800 !important;
                font-size: 14px !important;
                color: #fff !important;
            }
            .app-bandeja-header .papel {
                font-size: 11px !important;
                color: #8a8a8a !important;
                margin-top: 2px !important;
            }
            html[data-tema="claro"] .app-bandeja-header .nome { color: #0a0a0a !important; }

            .app-bandeja-busca {
                padding: 10px 14px !important;
                flex-shrink: 0 !important;
                border-bottom: 1px solid rgba(0,217,126,0.08) !important;
                background: #0f0f0f !important;
            }
            html[data-tema="claro"] .app-bandeja-busca { background: #fff !important; }
            .app-bandeja-busca input {
                width: 100% !important;
                padding: 10px 12px !important;
                border-radius: 10px !important;
                border: 1px solid rgba(0,217,126,0.2) !important;
                background: rgba(0,217,126,0.05) !important;
                color: #fff !important;
                font-size: 14px !important;
                outline: none !important;
                box-sizing: border-box !important;
                font-family: inherit !important;
            }
            .app-bandeja-busca input::placeholder { color: #6a6a6a !important; }
            .app-bandeja-busca input:focus {
                border-color: rgba(0,217,126,0.6) !important;
                box-shadow: 0 0 0 3px rgba(0,217,126,0.1) !important;
            }
            html[data-tema="claro"] .app-bandeja-busca input {
                color: #0a0a0a !important;
                background: #f5f5f5 !important;
            }

            .app-bandeja-lista {
                flex: 1 1 auto !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                padding: 6px 8px 20px !important;
                -webkit-overflow-scrolling: touch !important;
                overscroll-behavior: contain !important;
                min-height: 0 !important;
            }
            .app-bandeja-lista::-webkit-scrollbar { width: 4px !important; }
            .app-bandeja-lista::-webkit-scrollbar-thumb {
                background: rgba(0,217,126,0.3) !important;
                border-radius: 4px !important;
            }

            .app-bandeja-secao-titulo {
                font-size: 10px !important;
                font-weight: 800 !important;
                color: #5a5a5a !important;
                letter-spacing: 0.15em !important;
                text-transform: uppercase !important;
                padding: 12px 12px 6px !important;
            }

            .app-bandeja-item {
                display: flex !important;
                align-items: center !important;
                gap: 10px !important;
                padding: 11px 12px !important;
                border-radius: 10px !important;
                color: #e0e0e0 !important;
                text-decoration: none !important;
                font-size: 14px !important;
                font-weight: 600 !important;
                transition: background 0.15s !important;
            }
            .app-bandeja-item:hover,
            .app-bandeja-item.menu-ativo {
                background: rgba(0,217,126,0.12) !important;
                color: #00d97e !important;
            }
            html[data-tema="claro"] .app-bandeja-item { color: #2a2a2a !important; }
            .app-bandeja-item .emoji {
                font-size: 18px !important;
                width: 24px !important;
                text-align: center !important;
                flex-shrink: 0 !important;
            }
            .app-bandeja-item .nome-item {
                flex: 1 !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }
            .app-bandeja-item .seta {
                color: #5a5a5a !important;
                font-size: 16px !important;
            }
            .app-bandeja-vazio {
                padding: 24px 16px !important;
                text-align: center !important;
                color: #5a5a5a !important;
                font-size: 13px !important;
            }

            /* OVERLAY */
            .app-overlay {
                position: fixed !important;
                inset: 0 !important;
                background: rgba(0,0,0,0.6) !important;
                opacity: 0 !important;
                pointer-events: none !important;
                transition: opacity 0.25s !important;
                z-index: 9940 !important;
            }
            .app-overlay.aberto {
                opacity: 1 !important;
                pointer-events: auto !important;
            }
        `;
        document.head.appendChild(st);

        if (!document.getElementById('app-container-pad')) {
            const st2 = document.createElement('style');
            st2.id = 'app-container-pad';
            st2.textContent = `
                @media (max-width: 768px) {
                    body.drawer-aberto { overflow: hidden !important; }
                }
            `;
            document.head.appendChild(st2);
        }
    }

    // ===== HEADER =====
    function criarHeader() {
        injetarCSSHeader();
        if (document.querySelector('.app-header')) return;
        const nomeTela = getNomeTela();
        const header = document.createElement('header');
        header.className = 'app-header';
        header.innerHTML = `
            <button class="app-menu-btn" id="app-menu-btn" aria-label="Bandeja de apps" title="Bandeja">
                ${window.ICONE ? window.ICONE('menu', { tamanho: 22 }) : '☰'}
            </button>
            <a href="/clientes" class="logo-app">
                <img src="/static/logo.png" alt="M.A Tech" class="logo-img">
                <span class="logo-nome-tela">${nomeTela}</span>
            </a>
            <button class="app-help-btn" id="app-help-btn" aria-label="Ajuda" title="Ajuda">
                ${window.ICONE ? window.ICONE('ajuda', { tamanho: 22 }) : '?'}
            </button>
            <a href="/configuracoes" class="app-config-btn" aria-label="Configurações" title="Configurações">
                ${window.ICONE ? window.ICONE('configuracoes', { tamanho: 22 }) : '⚙️'}
            </a>
        `;
        const containerAtual = document.querySelector('.container-atendimento');
        if (containerAtual && containerAtual.parentNode) {
            containerAtual.parentNode.insertBefore(header, containerAtual);
        } else {
            document.body.insertBefore(header, document.body.firstChild);
        }

        const btn = document.getElementById('app-help-btn');
        if (btn) {
            btn.addEventListener('click', () => {
                if (typeof window.abrirPainelAjuda === 'function') {
                    window.abrirPainelAjuda();
                }
            });
        }

        const menuBtn = document.getElementById('app-menu-btn');
        if (menuBtn) {
            menuBtn.addEventListener('click', () => {
                if (typeof window.abrirBandejaApp === 'function') {
                    window.abrirBandejaApp();
                }
            });
        }
    }

    // ===== OVERLAY =====
    function criarOverlay() {
        if (document.querySelector('.app-overlay')) return;
        const overlay = document.createElement('div');
        overlay.className = 'app-overlay';
        overlay.id = 'app-overlay';
        document.body.appendChild(overlay);
    }

    // ===== DADOS DA BANDEJA =====
    function getTelasBandeja() {
        const admin = isAdmin();

        const secoes = [];

        secoes.push({
            titulo: 'Atendimento',
            itens: [
                { href: '/clientes',   emoji: '👥', nome: 'Atendimento' },
                { href: '/followups',  emoji: '📞', nome: 'Follow-ups' },
                { href: '/relatorios', emoji: '📊', nome: 'Relatórios' },
                { href: '/meus_nichos',emoji: '🙋', nome: 'Meus Nichos' },
                { href: '/novo_nicho', emoji: '➕', nome: 'Novo Nicho' },
            ]
        });

        secoes.push({
            titulo: 'Gestão',
            itens: [
                { href: '/gestao',                       emoji: '💼', nome: 'Gestão' },
                { href: '/gestao/pessoal',               emoji: '👤', nome: 'Gestão Pessoal' },
                { href: '/gestao/pessoal/financeira',    emoji: '💰', nome: 'Gestão Pessoal Financeira' },
                { href: '/gestao/pessoal/tempo',         emoji: '⏰', nome: 'Gestão do Tempo' },
                { href: '/gestao/pessoal/tempo/planejado', emoji: '📋', nome: 'Planejado Tempo' },
                { href: '/gestao/pessoal/tempo/rotinas', emoji: '🔄', nome: 'Rotinas Tempo' },
                { href: '/gestao/pessoal/tempo/foco',    emoji: '🎯', nome: 'Foco Tempo' },
                { href: '/gestao/pessoal/tempo/config',  emoji: '⚙️', nome: 'Config Tempo' },
                { href: '/gestao/profissional',          emoji: '🏢', nome: 'Gestão Profissional' },
            ]
        });

        secoes.push({
            titulo: 'Consultoria',
            itens: [
                { href: '/consultoria', emoji: '🧠', nome: 'Consultoria' },
                { href: '/socio',       emoji: '🧠', nome: 'Sócio IA' },
            ]
        });

        secoes.push({
            titulo: 'Conta',
            itens: [
                { href: '/planos',       emoji: '💳', nome: 'Planos' },
                { href: '/indicar',      emoji: '🎁', nome: 'Indique e Ganhe' },
                { href: '/configuracoes',emoji: '⚙️', nome: 'Configurações' },
                { href: '/notas',        emoji: '📝', nome: 'Notas' },
                { href: '/termos',       emoji: '🔐', nome: 'Termos de Uso' },
                { href: '/privacidade',  emoji: '🔒', nome: 'Privacidade' },
            ]
        });

        if (admin) {
            secoes.push({
                titulo: 'Admin',
                itens: [
                    { href: '/plano',           emoji: '🧭', nome: 'Plano M.A Tech' },
                    { href: '/admin/dashboard', emoji: '📈', nome: 'Dashboard' },
                    { href: '/admin/leads',     emoji: '🎯', nome: 'Leads' },
                    { href: '/admin',           emoji: '🔧', nome: 'Admin' },
                ]
            });
        }

        secoes.push({
            titulo: 'Ações',
            itens: [
                { href: 'https://wa.me/5512997291583', emoji: '💬', nome: 'Suporte WhatsApp', externo: true },
                { href: '/logout',                     emoji: '🚪', nome: 'Sair' },
            ]
        });

        return secoes;
    }

    // ===== RENDER BANDEJA =====
    function renderizarListaBandeja(filtro) {
        const lista = document.getElementById('app-bandeja-lista');
        if (!lista) return;
        const ativa = rotaAtiva();
        const secoes = getTelasBandeja();
        const q = (filtro || '').toLowerCase().trim();

        let html = '';
        let totalMostrado = 0;

        for (const secao of secoes) {
            const itens = secao.itens.filter(it => {
                if (!q) return true;
                return it.nome.toLowerCase().includes(q);
            });
            if (itens.length === 0) continue;

            html += `<div class="app-bandeja-secao-titulo">${secao.titulo}</div>`;
            for (const it of itens) {
                const ativo = (it.href === ativa) ? 'menu-ativo' : '';
                const attrs = it.externo ? ' target="_blank" rel="noopener"' : '';
                html += `<a href="${it.href}" class="app-bandeja-item ${ativo}"${attrs}>
                    <span class="emoji">${it.emoji}</span>
                    <span class="nome-item">${it.nome}</span>
                    <span class="seta">→</span>
                </a>`;
                totalMostrado++;
            }
        }

        if (totalMostrado === 0) {
            html = `<div class="app-bandeja-vazio">Nenhuma tela encontrada pra "<strong>${filtro}</strong>"</div>`;
        }

        lista.innerHTML = html;

        document.querySelectorAll('#app-bandeja-lista .app-bandeja-item').forEach(link => {
            link.addEventListener('click', () => {
                fecharBandeja();
            });
        });
    }

    // ===== BANDEJA =====
    function criarBandeja() {
        if (document.querySelector('.app-bandeja')) return;
        const nome = getUsuario();
        const admin = isAdmin();
        const primeiraLetra = nome.charAt(0).toUpperCase();

        const bandeja = document.createElement('aside');
        bandeja.className = 'app-bandeja';
        bandeja.id = 'app-bandeja';
        bandeja.innerHTML = `
            <div class="app-bandeja-header">
                <div class="avatar" id="app-bandeja-avatar">${primeiraLetra}</div>
                <div class="nome">${nome}</div>
                <div class="papel">${admin ? 'Administrador' : 'Vendedor'}</div>
            </div>
            <div class="app-bandeja-busca">
                <input type="text" id="app-bandeja-busca-input" placeholder="Pesquisar tela..." autocomplete="off">
            </div>
            <nav class="app-bandeja-lista" id="app-bandeja-lista"></nav>
        `;
        document.body.appendChild(bandeja);

        renderizarListaBandeja('');
        carregarFotoBandeja();

        const input = document.getElementById('app-bandeja-busca-input');
        if (input) {
            input.addEventListener('input', (e) => {
                renderizarListaBandeja(e.target.value);
            });
        }
    }

    function carregarFotoBandeja() {
        fetch('/api/usuario/foto').then(r => r.json()).then(d => {
            if (!d.foto_url) return;
            const av = document.getElementById('app-bandeja-avatar');
            if (!av) return;
            av.innerHTML = '<img src="' + d.foto_url + '" alt="" style="width:100%; height:100%; object-fit:cover; border-radius:50%;">';
            av.style.padding = '0';
            av.style.overflow = 'hidden';
        }).catch(() => {});
    }

    // ===== ABRIR / FECHAR =====
    function abrirBandeja() {
        const bandeja = document.getElementById('app-bandeja');
        const overlay = document.getElementById('app-overlay');
        if (bandeja) bandeja.classList.add('aberto');
        if (overlay) overlay.classList.add('aberto');
        document.body.classList.add('drawer-aberto');
        setTimeout(() => {
            const input = document.getElementById('app-bandeja-busca-input');
            if (input) input.focus();
        }, 300);
    }

    function fecharBandeja() {
        const bandeja = document.getElementById('app-bandeja');
        const overlay = document.getElementById('app-overlay');
        if (bandeja) bandeja.classList.remove('aberto');
        if (overlay) overlay.classList.remove('aberto');
        document.body.classList.remove('drawer-aberto');
        const input = document.getElementById('app-bandeja-busca-input');
        if (input) input.value = '';
    }

    // ===== EVENTOS =====
    function ligarEventos() {
        const overlay = document.getElementById('app-overlay');
        if (overlay) overlay.addEventListener('click', fecharBandeja);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') fecharBandeja();
        });
    }

    window.abrirBandejaApp = abrirBandeja;
    window.fecharBandejaApp = fecharBandeja;

    function init() {
        const path = window.location.pathname;
        if (path === '/' || path === '/login' || path === '/signup' || path === '/ver-landing') return;
        if (!document.querySelector('.usuario-info')) return;
        if (!isMobile()) return;

        criarHeader();
        criarOverlay();
        criarBandeja();
        ligarEventos();

        window.addEventListener('resize', () => {
            if (!isMobile()) {
                fecharBandeja();
                const header = document.querySelector('.app-header');
                if (header) header.style.display = 'none';
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
