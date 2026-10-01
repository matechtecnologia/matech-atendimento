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
        if (path === '/admin' || path.startsWith('/admin/')) return '/admin';
        return null;
    }

    // ===== HEADER =====
    function criarHeader() {
        if (document.querySelector('.app-header')) return;
        const header = document.createElement('header');
        header.className = 'app-header';
        header.innerHTML = `
            <a href="/clientes" class="logo-app">
                <span class="dot"></span>
                M.A <em>Tech</em>
            </a>
            <button class="app-help-btn" id="app-help-btn" aria-label="Ajuda" title="Ajuda">
                ${window.ICONE ? window.ICONE('ajuda', { tamanho: 22 }) : '?'}
            </button>
        `;
        document.body.appendChild(header);

        const btn = document.getElementById('app-help-btn');
        if (btn) {
            btn.addEventListener('click', () => {
                if (typeof window.abrirPainelAjuda === 'function') {
                    window.abrirPainelAjuda();
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