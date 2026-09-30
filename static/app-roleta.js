// ============================================
// M.A Tech — Roleta das abas do rodapé
// Ordem: Menu → Relatórios → Clientes → Nichos → Follow-ups
// ============================================

(function() {
    'use strict';

    var ABAS = [
        { nome: 'Menu',       tipo: 'drawer', url: null },            // 0
        { nome: 'Relatórios', tipo: 'link', url: '/relatorios' },     // 1
        { nome: 'Clientes',   tipo: 'link', url: '/clientes' },       // 2
        { nome: 'Nichos',     tipo: 'link', url: '/meus_nichos' },    // 3
        { nome: 'Follow-ups', tipo: 'link', url: '/followups' }       // 4
    ];

    function isMobile() { return matchMedia('(max-width: 768px)').matches; }
    function ehPublica() {
        var p = location.pathname;
        return p === '/' || p === '/login' || p === '/signup' || p === '/ver-landing';
    }
    function acharAbaAtual() {
        var p = location.pathname;
        if (p === '/relatorios') return 1;
        if (p === '/clientes' || p === '/bem_vindo' || p.startsWith('/cliente/')) return 2;
        if (p === '/meus_nichos' || p === '/novo_nicho') return 3;
        if (p === '/followups') return 4;
        return -1;
    }

    var atual = -1;
    var x0 = 0, y0 = 0;
    var tracking = false;
    var disparou = false;
    var indo = false;

    function mostrarCard(nome, dir) {
        var antigo = document.getElementById('roleta-card');
        if (antigo) antigo.remove();

        var card = document.createElement('div');
        card.id = 'roleta-card';
        var css = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%) scale(0.85);';
        css += 'background:rgba(20,20,20,0.96);border:1px solid rgba(0,217,126,0.4);';
        css += 'border-radius:18px;padding:16px 22px;z-index:999999;opacity:0;';
        css += 'transition:opacity 0.25s ease, transform 0.35s cubic-bezier(0.16,1,0.3,1);';
        css += 'pointer-events:none;display:flex;align-items:center;gap:14px;';
        css += 'box-shadow:0 24px 60px rgba(0,0,0,0.8);';
        css += 'font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;';
        css += 'min-width:220px;';
        card.style.cssText = css;

        var seta = dir === 'next' ? '→' : '←';
        var label = dir === 'next' ? 'Próxima' : 'Anterior';
        card.innerHTML =
            '<div style="width:40px;height:40px;border-radius:11px;' +
            'background:linear-gradient(135deg,#00d97e,#008a4f);' +
            'display:flex;align-items:center;justify-content:center;' +
            'color:#0a0a0a;font-weight:800;font-size:20px;flex-shrink:0;">' + seta + '</div>' +
            '<div><div style="font-size:10px;color:#5a5a5a;text-transform:uppercase;' +
            'letter-spacing:0.12em;font-weight:800;margin-bottom:3px;">' + label + '</div>' +
            '<div style="font-size:17px;color:#fff;font-weight:800;white-space:nowrap;">' + nome + '</div></div>';

        document.body.appendChild(card);
        requestAnimationFrame(function() {
            card.style.opacity = '1';
            card.style.transform = 'translate(-50%,-50%) scale(1)';
        });
        setTimeout(function() {
            card.style.opacity = '0';
            setTimeout(function() { card.remove(); }, 250);
        }, 450);
    }

    function mostrarLimite() {
        var c = document.createElement('div');
        c.style.position = 'fixed';
        c.style.top = '50%';
        c.style.left = '50%';
        c.style.transform = 'translate(-50%,-50%) scale(0.85)';
        c.style.background = 'rgba(20,20,20,0.96)';
        c.style.border = '1px solid rgba(255,59,59,0.45)';
        c.style.borderRadius = '14px';
        c.style.padding = '14px 22px';
        c.style.zIndex = '999999';
        c.style.opacity = '0';
        c.style.transition = 'all 0.25s cubic-bezier(0.16,1,0.3,1)';
        c.style.pointerEvents = 'none';
        c.style.boxShadow = '0 20px 50px rgba(0,0,0,0.7)';
        c.style.fontFamily = '-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif';
        c.innerHTML = '<div style="font-size:14px;color:#ff3b3b;font-weight:800;">Limite da roleta</div>';
        document.body.appendChild(c);
        requestAnimationFrame(function() {
            c.style.opacity = '1';
            c.style.transform = 'translate(-50%,-50%) scale(1)';
        });
        setTimeout(function() {
            c.style.opacity = '0';
            setTimeout(function() { c.remove(); }, 250);
        }, 700);
    }

    function navegar(prox) {
        if (indo) return;
        indo = true;

        if (prox === 0) {
            // Menu — abre o drawer
            mostrarCard('Menu', 'prev');
            if (navigator.vibrate) navigator.vibrate(15);
            setTimeout(function() {
                if (window.abrirDrawerApp) window.abrirDrawerApp();
                indo = false;
            }, 200);
            return;
        }

        var destino = ABAS[prox];
        var dir = prox > atual ? 'next' : 'prev';
        mostrarCard(destino.nome, dir);
        if (navigator.vibrate) navigator.vibrate(15);

        var wrap = document.querySelector('.container-atendimento');
        if (wrap) {
            wrap.style.transition = 'opacity 0.22s ease, transform 0.28s cubic-bezier(0.16,1,0.3,1)';
            wrap.style.transform = dir === 'next' ? 'translateX(-6%)' : 'translateX(6%)';
            wrap.style.opacity = '0';
        }

        setTimeout(function() {
            location.href = destino.url;
        }, 200);
    }

    function init() {
        if (!isMobile()) return;
        if (ehPublica()) return;
        if (!document.querySelector('.usuario-info')) return;

        atual = acharAbaAtual();
        if (atual === -1) return;

        document.addEventListener('touchstart', function(e) {
            var t = e.target;
            if (t.closest('input, textarea, select, button, a, label')) return;
            if (document.body.classList.contains('drawer-aberto')) return;
            if (document.querySelector('.hist-modal.aberto')) return;
            if (document.querySelector('#acoes-overlay.aberto')) return;
            if (indo) return;

            x0 = e.touches[0].clientX;
            y0 = e.touches[0].clientY;
            tracking = true;
            disparou = false;
        }, { passive: true });

        document.addEventListener('touchmove', function(e) {
            if (!tracking || disparou) return;
            var dx = e.touches[0].clientX - x0;
            var dy = Math.abs(e.touches[0].clientY - y0);

            if (dy > 45) { tracking = false; return; }

            var LIM = 70;

            if (dx < -LIM) {
                // ← ESQUERDA → próxima
                disparou = true;
                tracking = false;
                if (atual < ABAS.length - 1) {
                    navegar(atual + 1);
                } else {
                    if (navigator.vibrate) navigator.vibrate([10, 30, 10]);
                    mostrarLimite();
                }
            } else if (dx > LIM) {
                // → DIREITA → anterior
                disparou = true;
                tracking = false;
                if (atual > 0) {
                    navegar(atual - 1);
                } else {
                    if (navigator.vibrate) navigator.vibrate([10, 30, 10]);
                    mostrarLimite();
                }
            }
        }, { passive: true });

        document.addEventListener('touchend', function() {
            tracking = false;
        }, { passive: true });
    }

    window.addEventListener('pageshow', function() {
        indo = false;
        var wrap = document.querySelector('.container-atendimento');
        if (wrap) {
            wrap.style.transition = '';
            wrap.style.transform = '';
            wrap.style.opacity = '';
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();