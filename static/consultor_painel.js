/* ============================================================
   M.A Tech — Painel da Consultoria
   Drawer roxo com status + historico + passos
   ============================================================ */

(function () {
    'use strict';

    const API_STATUS = '/consultoria/status';
    const API_HIST = '/consultoria/historico';

    let statusAtual = null;
    let historicoAberto = false;
    let painelAberto = false;

    function el(id) { return document.getElementById(id); }

    function fmtData(iso) {
        if (!iso) return '—';
        try {
            const d = new Date(iso);
            const dd = String(d.getDate()).padStart(2, '0');
            const mm = String(d.getMonth() + 1).padStart(2, '0');
            const aa = d.getFullYear();
            const hh = String(d.getHours()).padStart(2, '0');
            const mi = String(d.getMinutes()).padStart(2, '0');
            return `${dd}/${mm}/${aa} ${hh}:${mi}`;
        } catch (e) {
            return '—';
        }
    }

    function escapar(s) {
        if (!s) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function classePrazo(prazo) {
        const p = (prazo || '').toLowerCase().trim();
        if (p.indexOf('hoje') >= 0) return 'hoje';
        if (p.indexOf('semana') >= 0) return 'essa-semana';
        if (p.indexOf('mes') >= 0 || p.indexOf('mês') >= 0) return 'esse-mes';
        return '';
    }

    // ---------- ABRIR / FECHAR ----------
    function abrirPainel() {
        painelAberto = true;
        el('consult-painel-drawer').classList.add('aberto');
        el('consult-painel-overlay').classList.add('aberto');
        document.body.style.overflow = 'hidden';
        carregarStatus();
    }

    function fecharPainel() {
        painelAberto = false;
        el('consult-painel-drawer').classList.remove('aberto');
        el('consult-painel-overlay').classList.remove('aberto');
        document.body.style.overflow = '';
    }

    // ---------- CARREGAR STATUS ----------
    async function carregarStatus() {
        try {
            const r = await fetch(API_STATUS);
            const j = await r.json();
            if (j.ok && j.status) {
                statusAtual = j.status;
                renderStatus(j.status);
            }
        } catch (e) {
            console.warn('Painel: falha ao carregar status', e);
        }
    }

    function renderStatus(s) {
        // Gargalo
        const g = el('painel-gargalo');
        if (s.gargalo_detectado) {
            g.classList.remove('vazio');
            g.classList.add('destaque');
            g.textContent = s.gargalo_detectado;
        } else {
            g.classList.remove('destaque');
            g.classList.add('vazio');
            g.innerHTML = '<span class="consult-spinner"></span> ainda analisando...';
        }

        // Servico
        const sv = el('painel-servico');
        if (s.servico_nome) {
            sv.classList.remove('vazio');
            sv.classList.add('destaque');
            sv.textContent = s.servico_nome;
        } else {
            sv.classList.remove('destaque');
            sv.classList.add('vazio');
            sv.innerHTML = '<span class="consult-spinner"></span> ainda analisando...';
        }

        // Uso
        const pct = Math.min(100, Math.round((s.usado / Math.max(1, s.limite)) * 100));
        const barra = el('painel-uso-barra');
        barra.style.width = pct + '%';
        barra.classList.remove('aviso', 'limite');
        const restantes = s.limite - s.usado;
        if (restantes <= 0) barra.classList.add('limite');
        else if (restantes <= 2) barra.classList.add('aviso');

        el('painel-uso-texto').textContent = `${s.usado} / ${s.limite}`;
        el('painel-uso-plano').textContent = s.plano || 'gratis';

        // Meta
        el('painel-meta-criada').textContent = fmtData(s.criado_em);
        el('painel-meta-atualizada').textContent = fmtData(s.atualizado_em);
        el('painel-meta-msgs').textContent = s.total_mensagens || 0;
        const stEl = el('painel-meta-status');
        stEl.textContent = s.status || 'ativa';
        stEl.classList.remove('status-ativa', 'status-encerrada');
        stEl.classList.add('status-' + (s.status || 'ativa'));

        // Passos
        renderPassos(s.passos || [], s.passos_total || 0, s.passos_concluidos || 0);
    }

    function renderPassos(passos, total, concluidos) {
        const box = el('painel-passos-lista');
        const prog = el('painel-passos-progresso');
        if (!box || !prog) return;

        if (!passos || passos.length === 0) {
            prog.style.display = 'none';
            box.innerHTML = '<div class="consult-passos-vazio"><span class="consult-spinner"></span> ainda gerando plano...</div>';
            return;
        }

        prog.style.display = 'flex';
        const pct = Math.round((concluidos / Math.max(1, total)) * 100);
        prog.querySelector('.consult-passos-numero').textContent = `${concluidos} / ${total}`;
        prog.querySelector('.barra-mini-preenchida').style.width = pct + '%';

        box.innerHTML = passos.map(function (p) {
            const cls = p.concluido ? 'concluido' : '';
            const prazoCls = classePrazo(p.prazo);
            const checkSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
            return `
                <div class="consult-passo ${cls}" data-id="${p.id}">
                    <button class="consult-passo-check" data-id="${p.id}" title="${p.concluido ? 'Desmarcar' : 'Marcar como concluído'}">
                        ${checkSvg}
                    </button>
                    <div class="consult-passo-corpo">
                        <div class="consult-passo-titulo">${escapar(p.titulo)}</div>
                        <div class="consult-passo-acao">${escapar(p.acao)}</div>
                        <span class="consult-passo-prazo ${prazoCls}">${escapar(p.prazo || 'essa semana')}</span>
                    </div>
                </div>
            `;
        }).join('');

        box.querySelectorAll('.consult-passo-check').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                const pid = btn.getAttribute('data-id');
                togglePasso(pid);
            });
        });
    }

    async function togglePasso(pid) {
        try {
            const r = await fetch('/consultoria/passo/' + pid + '/toggle', { method: 'POST' });
            const j = await r.json();
            if (j.ok) {
                // Atualiza o estado local sem refetch
                carregarStatus();
            }
        } catch (e) {
            console.warn('Painel: falha ao toggle passo', e);
        }
    }

    // ---------- HISTORICO ----------
    async function carregarHistorico() {
        try {
            const r = await fetch(API_HIST);
            const j = await r.json();
            if (j.ok) {
                renderHistorico(j.historico || []);
            }
        } catch (e) {
            console.warn('Painel: falha ao carregar historico', e);
        }
    }

    function renderHistorico(lista) {
        const box = el('painel-hist-lista');
        if (!lista.length) {
            box.innerHTML = '<div class="consult-hist-vazio">Nenhuma consultoria anterior ainda.</div>';
            return;
        }
        box.innerHTML = lista.map(function (h) {
            const data = fmtData(h.criado_em).split(' ')[0];
            const garg = h.gargalo ? escapar(h.gargalo) : 'sem diagnóstico salvo';
            const serv = h.servico_nome ? escapar(h.servico_nome) : '—';
            return `
                <div class="consult-hist-item" data-id="${h.id}">
                    <div class="consult-hist-item-topo">
                        <span class="id">#${h.id}</span>
                        <span>${data}</span>
                    </div>
                    <div class="consult-hist-item-gargalo">${garg}</div>
                    <div class="consult-hist-item-servico">${serv}</div>
                </div>
            `;
        }).join('');

        box.querySelectorAll('.consult-hist-item').forEach(function (item) {
            item.addEventListener('click', function () {
                const id = item.getAttribute('data-id');
                abrirModalHistorico(id);
            });
        });
    }

    // ---------- MODAL HISTORICO ----------
    async function abrirModalHistorico(id) {
        try {
            const r = await fetch(API_HIST + '/' + id);
            const j = await r.json();
            if (!j.ok) {
                alert('Nao consegui carregar essa consultoria.');
                return;
            }
            renderModal(j.consultoria, j.mensagens);
            el('consult-hist-modal').classList.add('aberto');
            document.body.style.overflow = 'hidden';
        } catch (e) {
            alert('Erro de rede: ' + e.message);
        }
    }

    function fecharModalHistorico() {
        el('consult-hist-modal').classList.remove('aberto');
        if (!painelAberto) document.body.style.overflow = '';
    }

    function renderModal(c, msgs) {
        el('hist-modal-titulo').textContent = 'Consultoria #' + c.id;
        el('hist-modal-data').textContent = fmtData(c.criado_em);

        const g = c.gargalo ? escapar(c.gargalo) : '(nenhum diagnóstico salvo)';
        const s = c.servico_nome ? escapar(c.servico_nome) : '(nenhum serviço indicado)';
        el('hist-modal-gargalo').innerHTML = g;
        el('hist-modal-servico').innerHTML = s;

        el('hist-modal-info').textContent =
            `${c.total_mensagens} mensagem(ns) · status: ${c.status}`;

        // Passos (read-only) — se tiver
        const passosBox = el('hist-modal-passos');
        if (passosBox) {
            if (c.passos && c.passos.length) {
                passosBox.style.display = 'block';
                passosBox.innerHTML = '<div class="consult-modal-passos-titulo">Plano de ação que foi gerado</div>' +
                    c.passos.map(function (p) {
                        const prazoCls = classePrazo(p.prazo);
                        const check = p.concluido ? '✓ ' : '• ';
                        return `<div class="consult-passo ${p.concluido ? 'concluido' : ''}" style="cursor:default;">
                            <div class="consult-passo-corpo">
                                <div class="consult-passo-titulo">${escapar(p.titulo)}</div>
                                <div class="consult-passo-acao">${escapar(p.acao)}</div>
                                <span class="consult-passo-prazo ${prazoCls}">${escapar(p.prazo || 'essa semana')}</span>
                            </div>
                        </div>`;
                    }).join('');
            } else {
                passosBox.style.display = 'none';
                passosBox.innerHTML = '';
            }
        }

        const usuarioInicial = (window.USUARIO_INICIAL || 'V');
        const box = el('hist-modal-msgs');
        if (!msgs.length) {
            box.innerHTML = '<div class="consult-hist-vazio">Sem mensagens registradas.</div>';
            return;
        }

        box.innerHTML = msgs.map(function (m) {
            const ehCliente = m.direcao === 'cliente';
            const classe = ehCliente ? 'cliente' : '';
            const avatarCls = ehCliente ? 'user' : 'ia';
            const avatarConteudo = ehCliente
                ? escapar(usuarioInicial)
                : '<img src="/static/logo.png" alt="M.A Tech">';
            const bolhaCls = ehCliente ? 'cliente' : 'consultor';
            return `
                <div class="consult-modal-msg ${classe}">
                    <div class="consult-modal-avatar ${avatarCls}">${avatarConteudo}</div>
                    <div class="consult-modal-bolha ${bolhaCls}">${escapar(m.mensagem)}</div>
                </div>
            `;
        }).join('');
    }

    // ---------- TOGGLE HISTORICO ----------
    function toggleHistorico() {
        historicoAberto = !historicoAberto;
        el('painel-hist-toggle').classList.toggle('aberto', historicoAberto);
        el('painel-hist-lista').classList.toggle('aberta', historicoAberto);
        if (historicoAberto) carregarHistorico();
    }

    // ---------- INICIALIZACAO ----------
    document.addEventListener('DOMContentLoaded', function () {
        const btn = el('btn-status-painel');
        if (btn) btn.addEventListener('click', abrirPainel);

        const fechar = el('painel-fechar-btn');
        if (fechar) fechar.addEventListener('click', fecharPainel);

        const overlay = el('consult-painel-overlay');
        if (overlay) overlay.addEventListener('click', fecharPainel);

        const histToggle = el('painel-hist-toggle');
        if (histToggle) histToggle.addEventListener('click', toggleHistorico);

        const fecharModal = el('hist-modal-fechar');
        if (fecharModal) fecharModal.addEventListener('click', fecharModalHistorico);

        const modal = el('consult-hist-modal');
        if (modal) {
            modal.addEventListener('click', function (e) {
                if (e.target === modal) fecharModalHistorico();
            });
        }

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                if (el('consult-hist-modal').classList.contains('aberto')) {
                    fecharModalHistorico();
                } else if (painelAberto) {
                    fecharPainel();
                }
            }
        });
    });

    window.ConsultorPainel = {
        atualizarStatus: function (novoStatus) {
            if (!novoStatus) return;
            statusAtual = novoStatus;
            if (painelAberto) renderStatus(novoStatus);
        }
    };
})();