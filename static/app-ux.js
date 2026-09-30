// ============================================
// M.A TECH — UX: Haptic + Transições
// ============================================

(function() {
    'use strict';

    const PREF_HAPTIC = () => localStorage.getItem('matech_haptic') !== 'off';
    const PREF_ANIMACOES = () => localStorage.getItem('matech_animacoes') !== 'off';

    // ===== RESET de segurança (caso algo trave) =====
    window.addEventListener('pageshow', () => {
        document.body.style.opacity = '1';
        document.body.style.transform = 'translateX(0)';
        document.body.classList.remove('drawer-aberto');
    });

    // ===== HAPTIC FEEDBACK =====
    function vibrar(ms) {
        if (!PREF_HAPTIC()) return;
        if (!('vibrate' in navigator)) return;
        try { navigator.vibrate(ms || 10); } catch (e) {}
    }

    function ligarHaptic() {
        document.addEventListener('click', (e) => {
            const alvo = e.target.closest('button, .btn-gerar, .btn-mini, .btn-copiar, .btn-acao, .app-hamburger, .toggle, .segmented button');
            if (alvo) vibrar(12);
        }, { passive: true });
    }

    // ===== TRANSIÇÕES ENTRE TELAS =====
    function ligarTransicoes() {
        if (!window.matchMedia('(max-width: 768px)').matches) return;
        if (!PREF_ANIMACOES()) return;

        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (!link) return;

            const href = link.getAttribute('href');
            if (!href) return;
            if (href.startsWith('#') || href.startsWith('javascript:')) return;
            if (href.startsWith('/logout')) return;
            if (link.target === '_blank') return;
            if (href.startsWith('http') && !href.startsWith(location.origin)) return;
            if (href === location.pathname) return;

            e.preventDefault();

            // Fecha drawer se estiver aberto
            const drawer = document.getElementById('app-drawer');
            const overlay = document.getElementById('app-overlay');
            if (drawer) drawer.classList.remove('aberto');
            if (overlay) overlay.classList.remove('aberto');
            document.body.classList.remove('drawer-aberto');

            // Animação leve (não trava a tela)
            document.body.style.transition = 'opacity 0.15s ease';
            document.body.style.opacity = '0.7';

            setTimeout(() => {
                window.location.href = href;
            }, 150);
        });

        // Entrada suave
        document.body.style.opacity = '0';
        document.body.style.transition = 'opacity 0.2s ease';
        requestAnimationFrame(() => {
            document.body.style.opacity = '1';
        });
    }

    // ===== PULL TO REFRESH =====
    function ligarPullToRefresh() {
        if (!window.matchMedia('(max-width: 768px)').matches) return;

        let startY = 0;
        let puxando = false;
        let indicador = null;
        let pronto = false;

        function criarIndicador() {
            if (indicador) return indicador;
            indicador = document.createElement('div');
            indicador.id = 'ptr-indicador';
            indicador.style.cssText = `
                position: fixed;
                top: 70px;
                left: 50%;
                transform: translateX(-50%) translateY(-40px);
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: #141414;
                border: 1px solid #222;
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9997;
                opacity: 0;
                transition: all 0.25s ease;
                pointer-events: none;
                box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            `;
            const spinner = document.createElement('div');
            spinner.style.cssText = `
                width: 16px;
                height: 16px;
                border: 2px solid #1a1a1a;
                border-top-color: #00d97e;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            `;
            indicador.appendChild(spinner);
            document.body.appendChild(indicador);
            return indicador;
        }

        document.addEventListener('touchstart', (e) => {
            if (window.scrollY > 10) return;
            startY = e.touches[0].clientY;
            puxando = true;
            pronto = false;
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (!puxando) return;
            const dy = e.touches[0].clientY - startY;
            if (dy > 60) {
                const ind = criarIndicador();
                ind.style.opacity = '1';
                ind.style.transform = 'translateX(-50%) translateY(0)';
                if (dy > 120) pronto = true;
            }
        }, { passive: true });

        document.addEventListener('touchend', () => {
            if (!puxando) return;
            puxando = false;
            if (indicador) {
                indicador.style.opacity = '0';
                indicador.style.transform = 'translateX(-50%) translateY(-40px)';
            }
            if (pronto) {
                setTimeout(() => window.location.reload(), 150);
            }
        }, { passive: true });
    }

    // ===== INIT =====
    function init() {
        const path = window.location.pathname;
        if (path === '/' || path === '/login' || path === '/signup') return;

        ligarHaptic();
        ligarTransicoes();
        ligarPullToRefresh();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();