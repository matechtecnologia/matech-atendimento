// ============================================
// M.A TECH — App Mobile
// Drawer lateral + header + gestures
// ============================================

(function() {
    'use strict';

    // Só roda no mobile
    function isMobile() {
        return window.matchMedia('(max-width: 768px)').matches;
    }

    // Pega os dados do usuário
    function getUsuario() {
        const span = document.querySelector('.usuario-info span');
        return span ? span.textContent.trim() : 'Usuário';
    }

    function isAdmin() {
        // Verifica se tem link admin no menu
        return !!document.querySelector('.usuario-info a[href="/admin"]');
    }

    // Pega o total de followups pendentes
    function getFollowups() {
        const el = document.querySelector('.usuario-info a[href="/followups"] .badge-menu, .usuario-info a[href="/followups"] span');
        if (el) {
            const n = parseInt(el.textContent.trim());
            return isNaN(n) ? 0 : n;
        }
        return 0;
    }

    // Detecta rota ativa
    function rotaAtiva() {
        const path = window.location.pathname;
        if (path === '/clientes' || path === '/bem_vindo' || path.startsWith('/cliente/')) return '/clientes';
        if (path === '/relatorios') return '/relatorios';
        if (path === '/followups') return '/followups';
        if (path === '/meus_nichos' || path === '/novo_nicho') return '/meus_nichos';
        if (path === '/planos' || path === '/assinar' || path.startsWith('/pagamento/')) return '/planos';
        if (path === '/admin' || path.startsWith('/admin/')) return '/admin';
        return null;
    }

    // Cria o header fixo
    function criarHeader() {
        if (document.querySelector('.app-header')) return;

        const header = document.createElement('header');
        header.className = 'app-header';
        header.innerHTML = `
            <a href="/clientes" class="logo-app">
                <span class="dot"></span>
                M.A <em>Tech</em>
            </a>
            <button class="app-hamburger" id="app-hamburger" aria-label="Abrir menu">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="badge-notif" id="hamburger-notif" style="display:none;"></span>
            </button>
        `;
        document.body.appendChild(header);

        // Badge de notificação no hamburger
        const total = getFollowups();
        const badge = header.querySelector('#hamburger-notif');
        if (total > 0) {
            badge.textContent = total > 99 ? '99+' : total;
            badge.style.display = 'flex';
        }
    }

    // Cria overlay
    function criarOverlay() {
        if (document.querySelector('.app-overlay')) return;
        const overlay = document.createElement('div');
        overlay.className = 'app-overlay';
        overlay.id = 'app-overlay';
        document.body.appendChild(overlay);
    }

    // Cria drawer
    function criarDrawer() {
        if (document.querySelector('.app-drawer')) return;

        const nome = getUsuario();
        const admin = isAdmin();
        const ativa = rotaAtiva();
        const total = getFollowups();
        const primeiraLetra = nome.charAt(0).toUpperCase();

        const links = [
            { href: '/clientes', rota: '/clientes', icone: '👥', texto: 'Clientes' },
            { href: '/followups', rota: '/followups', icone: '🎯', texto: 'Follow-ups', badge: total },
            { href: '/relatorios', rota: '/relatorios', icone: '📊', texto: 'Relatórios' },
            { href: '/meus_nichos', rota: '/meus_nichos', icone: '🎨', texto: 'Meus Nichos' },
            { href: '/planos', rota: '/planos', icone: '💳', texto: 'Planos' },
        ];

        if (admin) {
            links.push({ href: '/admin/dashboard', rota: '/admin/dashboard', icone: '📈', texto: 'Dashboard' });
            links.push({ href: '/admin/leads', rota: '/admin/leads', icone: '📥', texto: 'Leads' });
            links.push({ href: '/admin', rota: '/admin', icone: '👑', texto: 'Admin' });
        }

        let linksHTML = '';
        for (const l of links) {
            const ativo = (l.rota === ativa) ? ' menu-ativo' : '';
            const badge = l.badge > 0 ? `<span class="badge-menu">${l.badge > 99 ? '99+' : l.badge}</span>` : '';
            linksHTML += `<a href="${l.href}" class="${ativo.trim()}">
                <span class="icone">${l.icone}</span>
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
                    <span class="icone">🚪</span>
                    Sair da conta
                </a>
            </div>
        `;
        document.body.appendChild(drawer);
    }

    // Abrir/fechar drawer
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

    // Eventos
    function ligarEventos() {
        const hamburger = document.getElementById('app-hamburger');
        const overlay = document.getElementById('app-overlay');

        if (hamburger) {
            hamburger.addEventListener('click', abrirDrawer);
        }

        if (overlay) {
            overlay.addEventListener('click', fecharDrawer);
        }

        // Fecha com ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') fecharDrawer();
        });

        // Swipe da esquerda pra abrir
        let touchStartX = 0;
        let touchStartY = 0;
        let touchAtivo = false;

        document.addEventListener('touchstart', (e) => {
            const touch = e.touches[0];
            touchStartX = touch.clientX;
            touchStartY = touch.clientY;
            // Só ativa se começar nos primeiros 30px da esquerda
            touchAtivo = (touchStartX < 30);
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (!touchAtivo) return;
            const touch = e.touches[0];
            const dx = touch.clientX - touchStartX;
            const dy = Math.abs(touch.clientY - touchStartY);

            // Só abre se for movimento horizontal claro
            if (dx > 60 && dy < 50) {
                abrirDrawer();
                touchAtivo = false;
            }
        }, { passive: true });

        // Swipe pra fechar (dentro do drawer)
        const drawer = document.getElementById('app-drawer');
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

    // Inicializa
    function init() {
        const path = window.location.pathname;
        // Não mostra em telas públicas
        if (path === '/' || path === '/login' || path === '/signup' || path === '/ver-landing') return;

        // Não mostra se não tiver usuário logado
        if (!document.querySelector('.usuario-info')) return;

        if (!isMobile()) return;

        criarHeader();
        criarOverlay();
        criarDrawer();
        ligarEventos();

        // Re-detecta ao girar o celular
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