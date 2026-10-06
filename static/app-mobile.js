// ============================================
// M.A Tech — App Mobile (header + 2 drawers + swipes)
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
        return !!document.querySelector('.usuario-info a[href="/admin"]');
    }

    function getFollowups() {
        return window.__followups_total_cache || 0;
    }

    function rotaAtiva() {
        const path = window.location.pathname;
        if (path === '/clientes' || path === '/bem_vindo' || path.startsWith('/cliente/')) return '/clientes';
        if (path === '/relatorios') return '/relatorios';
        if (path === '/followups') return '/followups';
        if (path === '/meus_nichos' || path === '/novo_nicho') return '/meus_nichos';
        if (path === '/planos' || path === '/assinar' || path.startsWith('/pagamento/')) return '/planos';
        if (path === '/configuracoes') return '/configuracoes';
        if (path === '/indicar') return '/indicar';
        if (path === '/plano' || path.startsWith('/plano/')) return '/plano';
        if (path === '/admin' || path.startsWith('/admin/')) return '/admin';
        return null;
    }

    // ===== CSS INLINE ? HEADER PREMIUM =====
    function injetarCSSHeader() {
        if (document.getElementById('app-header-premium')) return;
        const st = document.createElement('style');
        st.id = 'app-header-premium';
        st.textContent = `
            .app-header {
                display: grid !important;
                grid-template-columns: 44px 1fr 44px !important;
                align-items: center !important;
                gap: 10px !important;
                padding: 12px 16px !important;
                padding-top: calc(12px + env(safe-area-inset-top, 0px)) !important;
                background: linear-gradient(180deg, rgba(15,15,15,0.98) 0%, rgba(15,15,15,0.88) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border-bottom: 1px solid rgba(0,217,126,0.12) !important;
                position: sticky !important;
                top: 0 !important;
                z-index: 9996 !important;
                box-shadow: 0 2px 20px rgba(0,0,0,0.5) !important;
            }
            html[data-tema="claro"] .app-header {
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.88) 100%) !important;
                border-bottom-color: rgba(0,217,126,0.2) !important;
            }
            .app-header .app-menu-btn,
            .app-header .app-help-btn {
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
            }
            .app-header .app-menu-btn:hover,
            .app-header .app-help-btn:hover {
                border-color: rgba(0,217,126,0.6) !important;
                box-shadow: 0 0 20px rgba(0,217,126,0.2) !important;
            }
            .app-header .app-menu-btn:active,
            .app-header .app-help-btn:active {
                transform: scale(0.92) !important;
            }
            .app-header .app-menu-btn svg,
            .app-header .app-help-btn svg {
                width: 20px !important;
                height: 20px !important;
            }
            .app-header .logo-app {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 9px !important;
                font-size: 18px !important;
                font-weight: 800 !important;
                color: #ffffff !important;
                text-decoration: none !important;
                letter-spacing: -0.02em !important;
                white-space: nowrap !important;
                margin: 0 auto !important;
            }
            .app-header .logo-app em {
                font-style: normal !important;
                color: #00d97e !important;
                text-shadow: 0 0 20px rgba(0,217,126,0.35) !important;
            }
            .app-header .logo-app .dot {
                display: inline-block !important;
                width: 8px !important;
                height: 8px !important;
                background: #00d97e !important;
                border-radius: 50% !important;
                box-shadow: 0 0 10px #00d97e, 0 0 20px rgba(0,217,126,0.5) !important;
                animation: pulso-logo 2s ease-in-out infinite !important;
            }
            @keyframes pulso-logo {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.7; transform: scale(0.85); }
            }
            html[data-tema="claro"] .app-header .logo-app { color: #0a0a0a !important; }
        `;
        document.head.appendChild(st);

        // CSS do logo + slogan
        if (!document.getElementById('app-logo-style')) {
            const st2 = document.createElement('style');
            st2.id = 'app-logo-style';
            st2.textContent = `
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
                    height: 38px !important;
                    width: auto !important;
                    display: block !important;
                    filter: drop-shadow(0 0 12px rgba(0,217,126,0.35)) !important;
                }
                .app-header .logo-slogan {
                    font-size: 8px !important;
                    font-weight: 700 !important;
                    color: #8a8a8a !important;
                    letter-spacing: 0.12em !important;
                    text-transform: uppercase !important;
                    white-space: nowrap !important;
                    line-height: 1 !important;
                }
                html[data-tema="claro"] .app-header .logo-slogan {
                    color: #4a4a4a !important;
                }
            `;
            document.head.appendChild(st2);
        }

        // CSS adicional: forca container a descer (vence qualquer coisa)
        if (!document.getElementById('app-container-pad')) {
            const st2 = document.createElement('style');
            st2.id = 'app-container-pad';
            st2.textContent = `
                @media (max-width: 768px) {
                    html body .container-atendimento,
                    html body div.container-atendimento,
                    body > .container-atendimento {
                        padding-top: 90px !important;
                    }
                }
            `;
            document.head.appendChild(st2);
        }
    }

    // ===== HEADER =====
    function criarHeader() {
        injetarCSSHeader();
        injetarCSSHeader();
        if (document.querySelector('.app-header')) return;
        const header = document.createElement('header');
        header.className = 'app-header';
        header.innerHTML = `
            <button class="app-menu-btn" id="app-menu-btn" aria-label="Menu" title="Menu">
                ${window.ICONE ? window.ICONE('menu', { tamanho: 22 }) : '?'}
            </button>
            <a href="/clientes" class="logo-app">
                <img src="/static/logo.png" alt="M.A Tech" class="logo-img">
                <span class="logo-slogan">Tecnologia e Solu&ccedil;&atilde;o</span>
            </a>
            <button class="app-help-btn" id="app-help-btn" aria-label="Ajuda" title="Ajuda">
                ${window.ICONE ? window.ICONE('ajuda', { tamanho: 22 }) : '?'}
            </button>
        `;
        // INSERIR ANTES do container-atendimento (nao no final do body)
        const containerAtual = document.querySelector('.container-atendimento');
        if (containerAtual && containerAtual.parentNode) {
            containerAtual.parentNode.insertBefore(header, containerAtual);
        } else {
            document.body.insertBefore(header, document.body.firstChild);
        }

        // FORCA o container a descer pra nao ficar embaixo do header
        const container = document.querySelector('.container-atendimento');
        if (container) {
        }

            const btn = document.getElementById('app-help-btn');
    if (btn) {
        btn.addEventListener('click', () => {
            // Se estiver na tela da Consultoria, abre o modal especifico
            if (window.location.pathname === '/consultoria' && typeof window.abrirModalAjudaConsultoria === 'function') {
                window.abrirModalAjudaConsultoria();
                return;
            }
            // Senao, painel generico
            if (typeof window.abrirPainelAjuda === 'function') {
                window.abrirPainelAjuda();
            }
        });
    }

        const menuBtn = document.getElementById('app-menu-btn');
        if (menuBtn) {
            menuBtn.addEventListener('click', () => {
                if (typeof window.abrirDrawerApp === 'function') {
                    window.abrirDrawerApp();
                }
            });
        }
    }

    // ===== OVERLAY (um só pros 2 drawers) =====
    function criarOverlay() {
        if (document.querySelector('.app-overlay')) return;
        const overlay = document.createElement('div');
        overlay.className = 'app-overlay';
        overlay.id = 'app-overlay';
        document.body.appendChild(overlay);
    }

    // ===== DRAWER ESQUERDO (menu) =====
    function criarDrawer() {
        if (document.querySelector('.app-drawer')) return;
        const nome = getUsuario();
        const admin = isAdmin();
        const ativa = rotaAtiva();
        const total = getFollowups();
        const primeiraLetra = nome.charAt(0).toUpperCase();

        const links = [
            { href: '/planos', rota: '/planos', icone: 'planos', texto: 'Planos' },
            { href: '/indicar', rota: '/indicar', icone: 'indicar', texto: 'Indique e ganhe' },
            { href: '/configuracoes', rota: '/configuracoes', icone: 'configuracoes', texto: 'Configurações' },
        ];
        if (admin) {
            links.push({ href: '/plano', rota: '/plano', icone: 'dashboard', texto: '🧭 Plano M.A Tech' });
            links.push({ href: '/admin/dashboard', rota: '/admin/dashboard', icone: 'dashboard', texto: 'Dashboard' });
            links.push({ href: '/admin/leads', rota: '/admin/leads', icone: 'leads', texto: 'Leads' });
            links.push({ href: '/admin', rota: '/admin', icone: 'admin', texto: 'Admin' });
        }

        let linksHTML = '';
        for (const l of links) {
            const ativo = (l.rota === ativa) ? 'menu-ativo' : '';
            const badge = l.badge > 0 ? `<span class="badge-menu">${l.badge > 99 ? '99+' : l.badge}</span>` : '';
            const svgIcon = window.ICONE ? window.ICONE(l.icone, { tamanho: 20 }) : '';
            linksHTML += `<a href="${l.href}" class="${ativo}">
                <span class="icone">${svgIcon}</span>
                <span class="texto">${l.texto}${badge}</span>
            </a>`;
        }

        const drawer = document.createElement('aside');
        drawer.className = 'app-drawer';
        drawer.id = 'app-drawer';
        drawer.innerHTML = `
            <div class="app-drawer-header">
                <div class="avatar">${primeiraLetra}</div>
                <div class="nome">${nome}</div>
                <div class="papel">${admin ? 'Administrador' : 'Vendedor'}</div>
            </div>
            <nav class="app-drawer-lista">${linksHTML}</nav>
            <div class="app-drawer-footer">
                <a href="/logout">
                    <span class="icone">${window.ICONE ? window.ICONE('sair', { tamanho: 20 }) : ''}</span>
                    Sair da conta
                </a>
            </div>
        `;
        document.body.appendChild(drawer);
    }

    // ===== DRAWER DIREITO (follow-ups rápidos) =====
    function criarDrawerRight() {
        if (document.querySelector('.app-drawer-right')) return;

        const drawer = document.createElement('aside');
        drawer.className = 'app-drawer-right';
        drawer.id = 'app-drawer-right';
        drawer.innerHTML = `
            <div class="app-drawer-header">
                <div class="avatar">⚡</div>
                <div class="nome">Follow-ups rápidos</div>
                <div class="papel">quem falar hoje</div>
            </div>
            <div style="flex:1;overflow-y:auto;padding:12px 14px;" id="fr-lista">
                <div class="fr-vazio"><div class="ok">...</div>Carregando...</div>
            </div>
            <div class="app-drawer-footer">
                <a href="/followups" style="color:#f59e0b;">
                    <span class="icone">${window.ICONE ? window.ICONE('followups', { tamanho: 20 }) : ''}</span>
                    Ver todos os follow-ups
                </a>
            </div>
        `;
        document.body.appendChild(drawer);

        // Carrega follow-ups via API
        carregarFollowupsDrawer();
    }

    function carregarFollowupsDrawer() {
        const lista = document.getElementById('fr-lista');
        if (!lista) return;

        fetch('/api/total-followups').then(r => r.json()).then(d => {
            const total = d.total || 0;
            if (total === 0) {
                lista.innerHTML = '<div class="fr-vazio"><div class="ok">✓</div>Tudo em dia!<br><span style="color:#5a5a5a;font-size:12px;">Ninguém precisa de atenção agora</span></div>';
                return;
            }
            // Busca os follow-ups reais
            return fetch('/api/followups-rapidos').then(r => r.json()).then(f => {
                const itens = f.itens || [];
                if (itens.length === 0) {
                    lista.innerHTML = '<div class="fr-vazio"><div class="ok">✓</div>Tudo em dia!</div>';
                    return;
                }
                let html = '';
                itens.forEach(i => {
                    const cls = i.urgencia || 'atencao';
                    const letra = (i.nome || 'S').charAt(0).toUpperCase();
                    html += `<a href="/cliente/${i.id}/atender" class="fr-card ${cls}">
                        <div class="avatar-mini">${letra}</div>
                        <div class="fr-info">
                            <div class="fr-nome">${i.nome || 'Sem nome'}</div>
                            <div class="fr-dias">${i.dias_sem_contato}d sem contato</div>
                        </div>
                        <span class="fr-seta">›</span>
                    </a>`;
                });
                lista.innerHTML = html;
            });
        }).catch(() => {
            lista.innerHTML = '<div class="fr-vazio">Erro ao carregar</div>';
        });
    }

    // ===== ABRIR / FECHAR =====
    function abrirDrawer() {
        const drawer = document.getElementById('app-drawer');
        const right = document.getElementById('app-drawer-right');
        const overlay = document.getElementById('app-overlay');
        if (right) right.classList.remove('aberto');
        if (drawer) drawer.classList.add('aberto');
        if (overlay) overlay.classList.add('aberto');
        document.body.classList.add('drawer-aberto');
    }

    function abrirDrawerRight() {
        // Redireciona direto pra página de follow-ups
        window.location.href = '/followups';
    }

    function fecharDrawer() {
        const drawer = document.getElementById('app-drawer');
        const right = document.getElementById('app-drawer-right');
        const overlay = document.getElementById('app-overlay');
        if (drawer) drawer.classList.remove('aberto');
        if (right) right.classList.remove('aberto');
        if (overlay) overlay.classList.remove('aberto');
        document.body.classList.remove('drawer-aberto');
    }

    // ===== EVENTOS =====
    function ligarEventos() {
        const overlay = document.getElementById('app-overlay');
        if (overlay) overlay.addEventListener('click', fecharDrawer);

        document.querySelectorAll('.app-drawer a').forEach(link => {
            link.addEventListener('click', () => {
                fecharDrawer();
                document.body.style.overflow = '';
                document.body.style.position = '';
                document.body.style.width = '';
            });
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') fecharDrawer();
        });

        }

    // Expõe
    window.abrirDrawerApp = abrirDrawer;
    window.abrirDrawerRightApp = abrirDrawerRight;
    window.fecharDrawerApp = fecharDrawer;

    function init() {
        const path = window.location.pathname;
        if (path === '/' || path === '/login' || path === '/signup' || path === '/ver-landing') return;
        if (!document.querySelector('.usuario-info')) return;
        if (!isMobile()) return;

        criarHeader();
        criarOverlay();
        criarDrawer();
        // criarDrawerRight();
        ligarEventos();

        window.addEventListener('resize', () => {
            if (!isMobile()) {
                fecharDrawer();
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