// ============================================
// M.A TECH — Bottom Nav
// ============================================

(function() {
    'use strict';

    if (window.__matech_bottom_nav_ativo) return;
    window.__matech_bottom_nav_ativo = true;

    function isMobile() {
        return window.matchMedia('(max-width: 768px)').matches;
    }

    function icone(nome, tam) {
        return window.ICONE ? window.ICONE(nome, { tamanho: tam || 22 }) : '';
    }

    function rotaAtiva() {
        const path = window.location.pathname;
        if (path === '/clientes' || path === '/bem_vindo' || path.startsWith('/cliente/')) return 'clientes';
        if (path === '/followups') return 'followups';
        if (path === '/relatorios') return 'relatorios';
        if (path === '/meus_nichos' || path === '/novo_nicho') return 'nichos';
        if (path === '/configuracoes' || path === '/planos' || path === '/indicar') return 'menu';
        if (path === '/consultoria') return 'consultoria';
        return null;
    }

    function getFollowups() {
        return window.__followups_total_cache || 0;
    }

    // Busca o total de follow-ups e atualiza o badge
    function carregarTotal() {
        fetch('/api/total-followups')
            .then(r => r.json())
            .then(d => {
                const total = d.total || 0;
                window.__followups_total_cache = total;

                const nav = document.querySelector('.app-bottom-nav');
                if (!nav) return;

                const link = nav.querySelector('a[href="/followups"]');
                if (!link) return;

                let badge = link.querySelector('.badge-nav');
                const iconeEl = link.querySelector('.icone-nav');

                if (total > 0) {
                    if (!badge && iconeEl) {
                        badge = document.createElement('span');
                        badge.className = 'badge-nav';
                        iconeEl.appendChild(badge);
                    }
                    if (badge) {
                        badge.textContent = total > 99 ? '99+' : total;
                    }
                } else if (badge) {
                    badge.remove();
                }
            })
            .catch(() => {});
    }

    // Busca o total de Consultorias pendentes e atualiza o badge
    function carregarConsultoria() {
        fetch('/api/consultoria-pendente')
            .then(r => r.json())
            .then(d => {
                const total = d.pendente || 0;
                window.__consultoria_pendente_cache = total;

                const nav = document.querySelector('.app-bottom-nav');
                if (!nav) return;

                const link = nav.querySelector('a[href="/consultoria"]');
                if (!link) return;

                let badge = link.querySelector('.badge-nav');
                const iconeEl = link.querySelector('.icone-nav');

                if (total > 0) {
                    if (!badge && iconeEl) {
                        badge = document.createElement('span');
                        badge.className = 'badge-nav';
                        iconeEl.appendChild(badge);
                    }
                    if (badge) {
                        badge.textContent = total > 9 ? '9+' : total;
                    }
                } else if (badge) {
                    badge.remove();
                }
            })
            .catch(() => {});
    }

    function criarBottomNav() {
        document.querySelectorAll('.app-bottom-nav').forEach(n => n.remove());
        if (!isMobile()) return;
        if (!document.querySelector('.usuario-info')) return;

        const ativa = rotaAtiva();
        const total = getFollowups();
        const badge = total > 0 ? `<span class="badge-nav">${total > 99 ? '99+' : total}</span>` : '';

        const nav = document.createElement('nav');
        nav.className = 'app-bottom-nav';
        nav.innerHTML = `
            <a href="/consultoria" class="nav-item ${ativa === 'consultoria' ? 'ativo' : ''}">
                <span class="icone-nav">${icone('briefcase')}</span>
                <span class="txt-nav">Consultoria</span>
            </a>
            <a href="/relatorios" class="nav-item ${ativa === 'relatorios' ? 'ativo' : ''}">
                <span class="icone-nav">${icone('relatorios')}</span>
                <span class="txt-nav">Relatorios</span>
            </a>
            <a href="/clientes" class="nav-item destaque" title="Atendimento">
                <span class="icone-nav">${icone('raio', 26)}</span>
            </a>
            <a href="/followups" class="nav-item ${ativa === 'followups' ? 'ativo' : ''}" id="nav-followups-btn">
                <span class="icone-nav">${icone('followups')}${badge}</span>
                <span class="txt-nav">Follow-ups</span>
            </a>
            <a href="/meus_nichos" class="nav-item ${ativa === 'nichos' ? 'ativo' : ''}">
                <span class="icone-nav">${icone('nichos')}</span>
                <span class="txt-nav">Nichos</span>
            </a>
        `;

        document.body.appendChild(nav);

        const menuBtn = document.getElementById('nav-menu-btn');
        if (menuBtn) {
            menuBtn.addEventListener('click', () => {
                if (window.abrirDrawerApp) {
                    window.abrirDrawerApp();
                } else {
                    const drawer = document.getElementById('app-drawer');
                    const overlay = document.getElementById('app-overlay');
                    if (drawer) drawer.classList.add('aberto');
                    if (overlay) overlay.classList.add('aberto');
                    document.body.classList.add('drawer-aberto');
                }
            });
        }

        // Busca os totais e atualiza os badges
        setTimeout(carregarTotal, 150);
        setTimeout(carregarConsultoria, 300);
    }

    function init() {
        const path = window.location.pathname;
        if (path === '/' || path === '/login' || path === '/signup' || path === '/ver-landing') return;
        criarBottomNav();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();