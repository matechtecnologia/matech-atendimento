/* ============================================================
   M.A Tech — Badge da Consultoria (VERMELHO)
   Mostra "1" ou "2" no card do hub quando o cliente tem
   consultoria com novidade (atualizado_em > vista_em).
   Cor: vermelho (#ff3b3b) — igual ao Follow-ups.
   ============================================================ */

(function () {
    'use strict';

    const API = '/api/consultoria-pendente';

    function aplicar(badge) {
        const numero = (badge && badge.pendente) ? badge.pendente : 0;

        const cards = document.querySelectorAll('.card-area');
        cards.forEach(function (card) {
            const h4 = card.querySelector('h4');
            if (h4 && h4.textContent.toLowerCase().indexOf('consultoria') >= 0) {
                if (getComputedStyle(card).position === 'static') {
                    card.style.position = 'relative';
                }
                injetarBadgeNoCard(card, numero);
            }
        });

        const navLinks = document.querySelectorAll('.app-bottom-nav a, .nav-item, .app-drawer-lista a');
        navLinks.forEach(function (link) {
            const href = link.getAttribute('href') || '';
            if (href === '/consultoria' || href.indexOf('/consultoria') === 0) {
                const iconeWrap = link.querySelector('.icone-nav') || link.querySelector('.icone') || link;
                injetarBadgeNoMenu(iconeWrap, numero);
            }
        });
    }

    function injetarBadgeNoCard(card, numero) {
        const antigo = card.querySelector('.consult-badge-card');
        if (antigo) antigo.remove();
        if (!numero || numero <= 0) return;

        const badge = document.createElement('span');
        badge.className = 'consult-badge-card';
        badge.textContent = numero > 9 ? '9+' : String(numero);
        badge.setAttribute('title', 'Consultoria esperando retorno');
        card.appendChild(badge);
    }

    function injetarBadgeNoMenu(elemento, numero) {
        if (!elemento) return;
        const antigo = elemento.querySelector('.consult-badge-num');
        if (antigo) antigo.remove();
        if (!numero || numero <= 0) return;

        const badge = document.createElement('span');
        badge.className = 'consult-badge-num';
        badge.textContent = numero > 9 ? '9+' : String(numero);
        elemento.appendChild(badge);
    }

    async function carregar() {
        try {
            const r = await fetch(API);
            const j = await r.json();
            aplicar(j);
        } catch (e) {
            // silencioso
        }
    }

    function injetarCSS() {
        if (document.getElementById('consult-badge-css')) return;
        const st = document.createElement('style');
        st.id = 'consult-badge-css';
        st.textContent = `
            /* Badge no card do hub — VERMELHO */
            .consult-badge-card {
                position: absolute;
                top: 14px;
                right: 14px;
                min-width: 24px;
                height: 24px;
                padding: 0 7px;
                background: linear-gradient(135deg, #ff3b3b, #dc2626);
                color: #ffffff;
                border-radius: 100px;
                font-size: 12px;
                font-weight: 800;
                font-family: 'SF Mono', Consolas, monospace;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 14px rgba(255, 59, 59, 0.6), 0 0 0 2px rgba(10, 10, 10, 0.6);
                animation: consult-badge-pulse 2s ease-in-out infinite;
                z-index: 5;
                line-height: 1;
            }

            /* Badge no menu mobile — VERMELHO */
            .consult-badge-num {
                position: absolute;
                top: -6px;
                right: -8px;
                min-width: 16px;
                height: 16px;
                padding: 0 4px;
                background: linear-gradient(135deg, #ff3b3b, #dc2626);
                color: #ffffff;
                border-radius: 100px;
                font-size: 10px;
                font-weight: 800;
                font-family: 'SF Mono', Consolas, monospace;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 0 0 2px rgba(15, 15, 15, 0.9);
                z-index: 10;
                line-height: 1;
            }

            @keyframes consult-badge-pulse {
                0%, 100% {
                    transform: scale(1);
                    box-shadow: 0 4px 14px rgba(255, 59, 59, 0.6), 0 0 0 2px rgba(10, 10, 10, 0.6);
                }
                50% {
                    transform: scale(1.08);
                    box-shadow: 0 6px 22px rgba(255, 59, 59, 0.85), 0 0 0 2px rgba(10, 10, 10, 0.6);
                }
            }
        `;
        document.head.appendChild(st);
    }

    function init() {
        const path = window.location.pathname;
        if (path === '/' || path === '/login' || path === '/signup' || path === '/ver-landing') return;

        injetarCSS();
        carregar();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();