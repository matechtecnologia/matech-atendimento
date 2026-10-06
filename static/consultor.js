// consultor.js
// M.A Tech — JS da area de Consultoria
// Modal de ajuda especifico quando o cliente clica no "?" na tela /consultoria

(function() {
    'use strict';

    window.abrirModalAjudaConsultoria = function() {
        // Se ja existe o modal aberto, nao duplica
        var existente = document.getElementById('consultor-modal-ajuda');
        if (existente) { existente.remove(); return; }

        // Cria o modal
        var overlay = document.createElement('div');
        overlay.id = 'consultor-modal-ajuda';
        overlay.style.cssText = [
            'position:fixed','inset:0','background:rgba(0,0,0,0.75)',
            'backdrop-filter:blur(6px)','z-index:9999999',
            'display:flex','align-items:center','justify-content:center',
            'padding:20px','animation:fadeIn 0.2s ease-out'
        ].join(';');

        var modal = document.createElement('div');
        modal.style.cssText = [
            'background:#141414','border:1px solid #222',
            'border-left:4px solid #00d97e','border-radius:16px',
            'padding:28px 26px','max-width:520px','width:100%',
            'max-height:85vh','overflow-y:auto',
            'box-shadow:0 20px 60px rgba(0,0,0,0.6)'
        ].join(';');

        modal.innerHTML = `
            <style>
                @keyframes fadeIn { from{opacity:0} to{opacity:1} }
                @keyframes slideUp { from{transform:translateY(20px);opacity:0} to{transform:translateY(0);opacity:1} }
                .consultor-modal-anim { animation: slideUp 0.25s ease-out; }
            </style>
            <div class="consultor-modal-anim">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:20px;">
                    <div>
                        <div style="font-size:10px;color:#00d97e;font-weight:800;letter-spacing:0.18em;text-transform:uppercase;font-family:monospace;margin-bottom:8px;">Ajuda · Consultoria</div>
                        <h2 style="font-size:22px;color:#fff;margin:0 0 6px;font-weight:800;letter-spacing:-0.02em;">Como funciona</h2>
                        <p style="color:#8a8a8a;font-size:13px;margin:0;line-height:1.5;">Um consultor de IA que analisa seu negócio e aponta o próximo passo concreto.</p>
                    </div>
                    <button id="consultor-modal-fechar" style="background:transparent;border:none;color:#8a8a8a;font-size:22px;cursor:pointer;padding:0 4px;line-height:1;font-family:inherit;">&times;</button>
                </div>

                <div style="display:flex;flex-direction:column;gap:16px;">
                    <div style="display:flex;gap:14px;align-items:flex-start;">
                        <div style="flex-shrink:0;width:26px;height:26px;background:rgba(0,217,126,0.15);border-radius:8px;display:flex;align-items:center;justify-content:center;color:#00d97e;font-size:12px;font-weight:800;font-family:monospace;">1</div>
                        <div>
                            <div style="color:#fff;font-weight:700;font-size:14px;margin-bottom:3px;">Análise do seu negócio</div>
                            <div style="color:#8a8a8a;font-size:13px;line-height:1.55;">O consultor lê seus dados reais (clientes, atendimentos, uso) e começa dali — não pergunta o que já sabe.</div>
                        </div>
                    </div>

                    <div style="display:flex;gap:14px;align-items:flex-start;">
                        <div style="flex-shrink:0;width:26px;height:26px;background:rgba(0,217,126,0.15);border-radius:8px;display:flex;align-items:center;justify-content:center;color:#00d97e;font-size:12px;font-weight:800;font-family:monospace;">2</div>
                        <div>
                            <div style="color:#fff;font-weight:700;font-size:14px;margin-bottom:3px;">Detecção do gargalo</div>
                            <div style="color:#8a8a8a;font-size:13px;line-height:1.55;">Conversa curta e direta pra achar o que está travando o crescimento de verdade.</div>
                        </div>
                    </div>

                    <div style="display:flex;gap:14px;align-items:flex-start;">
                        <div style="flex-shrink:0;width:26px;height:26px;background:rgba(0,217,126,0.15);border-radius:8px;display:flex;align-items:center;justify-content:center;color:#00d97e;font-size:12px;font-weight:800;font-family:monospace;">3</div>
                        <div>
                            <div style="color:#fff;font-weight:700;font-size:14px;margin-bottom:3px;">Indicação do próximo passo</div>
                            <div style="color:#8a8a8a;font-size:13px;line-height:1.55;">Sem empurrar serviço. Aponta o que faz sentido pro seu caso, com o que já está disponível hoje.</div>
                        </div>
                    </div>

                    <div style="display:flex;gap:14px;align-items:flex-start;">
                        <div style="flex-shrink:0;width:26px;height:26px;background:rgba(0,217,126,0.15);border-radius:8px;display:flex;align-items:center;justify-content:center;color:#00d97e;font-size:12px;font-weight:800;font-family:monospace;">4</div>
                        <div>
                            <div style="color:#fff;font-weight:700;font-size:14px;margin-bottom:3px;">Histórico salvo</div>
                            <div style="color:#8a8a8a;font-size:13px;line-height:1.55;">Sai quando quiser. Volta e continua de onde parou — o consultor lembra de tudo.</div>
                        </div>
                    </div>
                </div>

                <div style="margin-top:24px;padding-top:20px;border-top:1px solid #222;">
                    <div style="color:#8a8a8a;font-size:12px;line-height:1.6;">
                        <strong style="color:#00d97e;">Limite diário:</strong> você tem um número de interações por dia conforme seu plano. Ao atingir, é só voltar no dia seguinte.
                    </div>
                </div>

                <button id="consultor-modal-ok" style="width:100%;margin-top:20px;padding:14px;background:#00d97e;color:#0a0a0a;border:none;border-radius:10px;font-size:14px;font-weight:800;cursor:pointer;font-family:inherit;">
                    Entendi
                </button>
            </div>
        `;

        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        // Fechar: clique no fundo
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) overlay.remove();
        });

        // Fechar: ESC
        var escHandler = function(e) {
            if (e.key === 'Escape') { overlay.remove(); document.removeEventListener('keydown', escHandler); }
        };
        document.addEventListener('keydown', escHandler);

        // Botoes
        setTimeout(function() {
            var btnX = document.getElementById('consultor-modal-fechar');
            var btnOk = document.getElementById('consultor-modal-ok');
            if (btnX) btnX.addEventListener('click', function() { overlay.remove(); });
            if (btnOk) btnOk.addEventListener('click', function() { overlay.remove(); });
        }, 0);
    };

    console.log('[Consultor] modulo carregado');
})();