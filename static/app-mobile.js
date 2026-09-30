// ============================================
// M.A TECH — App Mobile (header + drawer)
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
        const el = document.querySelector('.usuario-info a[href="/followups"] span');
        if (el) {
            const n = parseInt(el.textContent.trim());
            return isNaN(n) ? 0 : n;
        }
        return 0;
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

    // Cria o header fixo (logo + botão ajuda)
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

        const helpBtn = document.getElementById('app-help-btn');
        if (helpBtn) {
            helpBtn.addEventListener('click', () => {
                if (typeof window.abrirPainelAjuda === 'function') {
                    window.abrirPainelAjuda();
                }
            });
        }
    }

    function criarOverlay() {
        if (document.querySelector('.app-overlay')) return;
        const overlay = document.createElement('div');
        overlay.className = 'app-overlay';
        overlay.id = 'app-overlay';
        document.body.appendChild(overlay);
    }

    function criarDrawer() {
        if (document.querySelector('.app-drawer')) return;

        const nome = getUsuario();
        const admin = isAdmin();
        const ativa = rotaAtiva();
        const total = getFollowups();
        const primeiraLetra = nome.charAt(0).toUpperCase();

        const links = [
            { href: '/clientes', rota: '/clientes', icone: 'clientes', texto: 'Clientes' },
            { href: '/followups', rota: '/followups', icone: 'followups', texto: 'Follow-ups', badge: total },
            { href: '/relatorios', rota: '/relatorios', icone: 'relatorios', texto: 'Relatórios' },
            { href: '/meus_nichos', rota: '/meus_nichos', icone: 'nichos', texto: 'Meus Nichos' },
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
            <nav class="app-drawer-lista">
                ${linksHTML}
            </nav>
            <div class="app-drawer-footer">
                <a href="/logout">
                    <span class="icone">${window.ICONE ? window.ICONE('sair', { tamanho: 20 }) : ''}</span>
                    Sair da conta
                </a>
            </div>
        `;
        document.body.appendChild(drawer);
    }

    function abrirDrawer() {
        const drawer = document.getElementById('app-drawer');
        const overlay = document.getElementById('app-overlay');
        if (drawer) drawer.classList.add('aberto');
        if (overlay) overlay.classList.add('aberto');
        document.body.classList.add('drawer-aberto');
    }

    function fecharDrawer() {
        const drawer = document.getElementById('app-drawer');
        const overlay = document.getElementById('app-overlay');
        if (drawer) drawer.classList.remove('aberto');
        if (overlay) overlay.classList.remove('aberto');
        document.body.classList.remove('drawer-aberto');
    }

    function ligarEventos() {
        const overlay = document.getElementById('app-overlay');
        if (overlay) {
            overlay.addEventListener('click', fecharDrawer);
        }

        const drawer = document.getElementById('app-drawer');
        if (drawer) {
            drawer.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    fecharDrawer();
                    document.body.classList.remove('drawer-aberto');
                    document.body.style.overflow = '';
                    document.body.style.position = '';
                    document.body.style.width = '';
                });
            });
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') fecharDrawer();
        });

        let touchStartX = 0;
        let touchStartY = 0;
        let touchAtivo = false;

        document.addEventListener('touchstart', (e) => {
            const touch = e.touches[0];
            touchStartX = touch.clientX;
            touchStartY = touch.clientY;
            touchAtivo = (touchStartX < 30);
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (!touchAtivo) return;
            const touch = e.touches[0];
            const dx = touch.clientX - touchStartX;
            const dy = Math.abs(touch.clientY - touchStartY);
            if (dx > 60 && dy < 50) {
                abrirDrawer();
                touchAtivo = false;
            }
        }, { passive: true });

        if (drawer) {
            let startX = 0;
            let abriu = false;
            drawer.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
                abriu = false;
            }, { passive: true });
            drawer.addEventListener('touchmove', (e) => {
                const dx = e.touches[0].clientX - startX;
                if (dx < -50 && !abriu) {
                    fecharDrawer();
                    abriu = true;
                }
            }, { passive: true });
        }
    }

    window.abrirDrawerApp = abrirDrawer;
    window.fecharDrawerApp = fecharDrawer;

    function init() {
        const path = window.location.pathname;
        if (path === '/' || path === '/login' || path === '/signup' || path === '/ver-landing') return;
        if (!document.querySelector('.usuario-info')) return;
        if (!isMobile()) return;

        criarHeader();
        criarOverlay();
        criarDrawer();
        ligarEventos();

        window.addEventListener('resize', () => {
            if (!isMobile()) {
                fecharDrawer();
                const header = document.querySelector('.app-header');
                if (header) header.style.display = 'none';
            } else {
                const header = document.querySelector('.app-header');
                if (header) header.style.display = '';
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();