// ============================================
// M.A TECH — Splash Screen
// ============================================

(function() {
    'use strict';

    // Não mostra se já foi visto nessa sessão
    if (sessionStorage.getItem('matech_splash_visto') === '1') return;

    // Só mostra em telas logadas
    const path = window.location.pathname;
    if (path === '/' || path === '/login' || path === '/signup' || path === '/ver-landing') return;

    function criarSplash() {
        if (document.getElementById('app-splash')) return;

        const splash = document.createElement('div');
        splash.id = 'app-splash';

        const texto = 'M.A Tech';
        let letrasHTML = '';
        for (let i = 0; i < texto.length; i++) {
            const ch = texto[i];
            const delay = 0.1 + i * 0.06;
            if (ch === ' ') {
                letrasHTML += `<span class="letra" style="animation-delay: ${delay}s">&nbsp;</span>`;
            } else if (ch === 'T' || ch === 'e' || ch === 'c' || ch === 'h') {
                // Parte "Tech" fica verde
                letrasHTML += `<em><span class="letra" style="animation-delay: ${delay}s">${ch}</span></em>`;
            } else {
                letrasHTML += `<span class="letra" style="animation-delay: ${delay}s">${ch}</span>`;
            }
        }

        splash.innerHTML = `
            <div class="logo-splash">${letrasHTML}</div>
            <div class="subtitulo">Atendimento com IA</div>
            <div class="barra-carregando"></div>
        `;

        document.body.appendChild(splash);

        // Sai depois de 1.8s
        setTimeout(() => {
            splash.classList.add('saindo');
            sessionStorage.setItem('matech_splash_visto', '1');
            setTimeout(() => splash.remove(), 600);
        }, 1800);
    }

    // Roda ANTES da página renderizar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', criarSplash);
    } else {
        criarSplash();
    }
})();