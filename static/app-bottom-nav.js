// ============================================
// M.A TECH - Bottom Nav
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

    function ehGestaoPessoalFinanceira() {
        return window.location.pathname.indexOf('/gestao/pessoal/financeira') === 0;
    }

    function ehGestaoTempo() {
        return window.location.pathname.indexOf('/gestao/pessoal/tempo') === 0;
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

    function rotaAtivaGestao() {
        const path = window.location.pathname;
        if (path === '/gestao/pessoal/financeira/planejado') return 'planejado';
        if (path === '/gestao/pessoal/financeira/caixinha') return 'caixinha';
        if (path === '/gestao/pessoal/financeira/socio') return 'socio';
        if (path === '/gestao/pessoal/financeira/dashboarding') return 'dashboarding';
        if (path === '/gestao/pessoal/financeira' || path === '/gestao/pessoal/financeira/lancar' || path === '/gestao/pessoal/financeira/extrato') return 'financeiro';
        return null;
    }

    function rotaAtivaTempo() {
        const path = window.location.pathname;
        if (path === '/gestao/pessoal/tempo/planejado') return 'planejado';
        if (path === '/gestao/pessoal/tempo/rotinas') return 'rotinas';
        if (path === '/gestao/pessoal/tempo/config') return 'config';
        return null;
    }

    function getFollowups() {
        return window.__followups_total_cache || 0;
    }

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
                    if (badge) badge.textContent = total > 99 ? '99+' : total;
                } else if (badge) {
                    badge.remove();
                }
            })
            .catch(() => {});
    }

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
                    if (badge) badge.textContent = total > 9 ? '9+' : total;
                } else if (badge) {
                    badge.remove();
                }
            })
            .catch(() => {});
    }

    function criarNavGestao() {
        const ativa = rotaAtivaGestao();
        const nav = document.createElement('nav');
        nav.className = 'app-bottom-nav';
        nav.innerHTML = `
            <a href="/gestao/pessoal/financeira/planejado" class="nav-item ${ativa === 'planejado' ? 'ativo' : ''}">
                <span class="icone-nav">${icone('relatorios')}</span>
                <span class="txt-nav">Planejado</span>
            </a>
            <a href="/gestao/pessoal/financeira/caixinha" class="nav-item ${ativa === 'caixinha' ? 'ativo' : ''}">
                <span class="icone-nav">${icone('briefcase')}</span>
                <span class="txt-nav">Caixinha</span>
            </a>
            <a href="/gestao/pessoal/financeira" class="nav-item destaque ${ativa === 'financeiro' ? 'ativo' : ''}" title="Financeiro">
                <span class="icone-nav">${icone('raio', 26)}</span>
            </a>
            <a href="/gestao/pessoal/financeira/socio" class="nav-item ${ativa === 'socio' ? 'ativo' : ''}">
                <span class="icone-nav">${icone('briefcase')}</span>
                <span class="txt-nav">Socio</span>
            </a>
            <a href="/gestao/pessoal/financeira/dashboarding" class="nav-item ${ativa === 'dashboarding' ? 'ativo' : ''}">
                <span class="icone-nav">${icone('dashboard')}</span>
                <span class="txt-nav">Dash</span>
            </a>
        `;
        document.body.appendChild(nav);
    }

    function criarNavTempo() {
        const ativa = rotaAtivaTempo();
        const nav = document.createElement('nav');
        nav.className = 'app-bottom-nav';
        nav.innerHTML = `
            <a href="/gestao/pessoal/tempo/planejado" class="nav-item ${ativa === 'planejado' ? 'ativo' : ''}">
                <span class="icone-nav">${icone('planos')}</span>
                <span class="txt-nav">Planejado</span>
            </a>
            <a href="/gestao/pessoal/tempo/rotinas" class="nav-item ${ativa === 'rotinas' ? 'ativo' : ''}">
                <span class="icone-nav">${icone('relatorios')}</span>
                <span class="txt-nav">Rotinas</span>
            </a>
            <a href="/gestao/pessoal/tempo" class="nav-item destaque" title="Hoje">
                <span class="icone-nav">${icone('raio', 26)}</span>
            </a>
            <a href="/socio" class="nav-item">
                <span class="icone-nav">${icone('dashboard')}</span>
                <span class="txt-nav">Socio</span>
            </a>
            <a href="/gestao/pessoal/tempo/config" class="nav-item ${ativa === 'config' ? 'ativo' : ''}">
                <span class="icone-nav">${icone('configuracoes')}</span>
                <span class="txt-nav">Config</span>
            </a>
        `;
        document.body.appendChild(nav);
    }

    function criarBottomNav() {
        document.querySelectorAll('.app-bottom-nav').forEach(n => n.remove());
        if (!isMobile()) return;
        if (!document.querySelector('.usuario-info')) return;

        if (ehGestaoPessoalFinanceira()) {
            criarNavGestao();
            return;
        }

        if (ehGestaoTempo()) {
            criarNavTempo();
            return;
        }

        const ativa = rotaAtiva();
        const total = getFollowups();
        const badge = total > 0 ? `<span class="badge-nav">${total > 99 ? '99+' : total}</span>` : '';

        const nav = document.createElement('nav');
        nav.className = 'app-bottom-nav';
        nav.innerHTML = `
            <a href="/gestao" class="nav-item">
                <span class="icone-nav">${icone('dashboard')}</span>
                <span class="txt-nav">Gestor</span>
            </a>
            <a href="/consultoria/loading" class="nav-item ${ativa === 'consultoria' ? 'ativo' : ''}">
                <span class="icone-nav">${icone('briefcase')}</span>
                <span class="txt-nav">Consultor</span>
            </a>
            <a href="/clientes" class="nav-item destaque ${ativa === 'clientes' ? 'ativo' : ''}" title="Raio">
                <span class="icone-nav">${icone('raio', 26)}</span>
            </a>
            <a href="/socio" class="nav-item">
                <span class="icone-nav">${icone('briefcase')}</span>
                <span class="txt-nav">Socio</span>
            </a>
            <a href="/notas" class="nav-item">
                <span class="icone-nav">${icone('relatorios')}</span>
                <span class="txt-nav">Notas</span>
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
