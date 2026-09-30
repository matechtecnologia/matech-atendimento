// ============================================
// M.A TECH — Aviso de plano expirando
// Mostra 1x por dia, dispensável
// ============================================

(function() {
    'use strict';

    function hoje() {
        const d = new Date();
        return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate();
    }

    function jaMostrouHoje() {
        return localStorage.getItem('matech_aviso_plano_data') === hoje();
    }

    function marcarComoMostrado() {
        localStorage.setItem('matech_aviso_plano_data', hoje());
    }

    function isPublica() {
        const path = window.location.pathname;
        return path === '/' || path === '/login' || path === '/signup' || path === '/ver-landing';
    }

    function criarBanner(dados) {
        if (document.getElementById('aviso-plano-banner')) return;

        const banner = document.createElement('div');
        banner.id = 'aviso-plano-banner';
        banner.className = 'aviso-plano-banner';
        banner.innerHTML = `
            <div class="aviso-plano-inner">
                <div class="aviso-plano-icone">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="8" x2="12" y2="12"/>
                        <line x1="12" y1="16" x2="12.01" y2="16"/>
                    </svg>
                </div>
                <div class="aviso-plano-texto">
                    <div class="aviso-plano-titulo">
                        ⏳ Seu plano <strong>${dados.plano}</strong> expira em <strong>${dados.dias} dia(s)</strong>
                    </div>
                    <div class="aviso-plano-desc">
                        Renove até <strong>${dados.data}</strong> pra não perder o acesso. Renovação é rápida via PIX.
                    </div>
                </div>
                <a href="/planos" class="aviso-plano-cta">RENOVAR</a>
                <button type="button" class="aviso-plano-fechar" id="aviso-plano-fechar" aria-label="Fechar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
        `;

        document.body.appendChild(banner);

        const btnFechar = document.getElementById('aviso-plano-fechar');
        if (btnFechar) {
            btnFechar.addEventListener('click', () => {
                banner.classList.add('saindo');
                setTimeout(() => banner.remove(), 300);
                marcarComoMostrado();
            });
        }

        requestAnimationFrame(() => {
            banner.classList.add('visivel');
        });
    }

    function init() {
        if (isPublica()) return;
        if (jaMostrouHoje()) return;
        if (!document.querySelector('.usuario-info')) return;

        fetch('/api/aviso-plano')
            .then(r => r.json())
            .then(d => {
                if (d && d.mostrar) {
                    // Espera 1s pra não atrapalhar o load da página
                    setTimeout(() => criarBanner(d), 1000);
                }
            })
            .catch(() => {});
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();