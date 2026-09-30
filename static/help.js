// ============================================
// M.A TECH — Ajuda contextual + Aba ativa
// ============================================

const AJUDA = {
    '/clientes': {
        titulo: '👥 Meus Clientes',
        descricao: 'Aqui você gerencia todos os seus clientes e leads. É o coração do sistema.',
        dicas: [
            'Clique em <b>⚡ Atender</b> pra colar a mensagem do cliente e receber a resposta da IA',
            'Use <b>💬 Ver histórico</b> pra ver todas as conversas anteriores',
            'Clique em <b>✏️ Editar</b> pra mudar status, telefone ou observações',
            'Filtre por status ou busque pelo nome no topo',
            'Quando o cliente vira <b>Cliente</b>, ele sai automaticamente da lista de follow-ups'
        ]
    },
    '/cliente_detalhe': {
        titulo: '📋 Detalhes do Cliente',
        descricao: 'Tudo sobre este cliente em um só lugar: dados, histórico e status.',
        dicas: [
            '<b>⚡ Atender este cliente</b> inicia um novo atendimento com IA',
            '<b>✏️ Editar</b> muda qualquer dado do cliente',
            'O histórico mostra todas as mensagens trocadas, em ordem'
        ]
    },
    '/atendimento_cliente': {
        titulo: '⚡ Atendendo Cliente',
        descricao: 'Cole a mensagem que o cliente enviou e receba a resposta da IA em segundos.',
        dicas: [
            'Cole a mensagem <b>exatamente</b> como o cliente escreveu',
            'Escolha o <b>nicho</b> correto',
            'Use o <b>Modo instrução</b> pra dar uma ordem direta pra IA',
            'A IA leva de 2 a 4 segundos pra responder'
        ]
    },
    '/resultado': {
        titulo: '🎯 Resposta da IA',
        descricao: 'A IA analisou a conversa e preparou 3 coisas pra você.',
        dicas: [
            '<b>🎤 O QUE FALAR</b> — o áudio que você vai gravar',
            '<b>📝 TEXTO PARA ENVIAR</b> — mensagem pronta pro WhatsApp',
            '<b>📊 ESTÁGIO</b> — o funil atualizou automaticamente'
        ]
    },
    '/followups': {
        titulo: '🎯 Quem falar hoje',
        descricao: 'A IA analisa TODOS os seus clientes e mostra quem precisa de atenção agora.',
        dicas: [
            '<b>🔴 Urgente</b> — fale hoje ou já passou do prazo',
            '<b>🟠 Atenção</b> — fale nos próximos 2 dias',
            '<b>🟢 Agenda</b> — programado pra depois',
            'Use o bloco <b>🔕 Silenciar follow-ups</b> no topo pra pausar as notificações'
        ]
    },
    '/relatorios': {
        titulo: '📊 Relatórios',
        descricao: 'Visão geral do seu desempenho comercial nos últimos 7 dias.',
        dicas: [
            '<b>Taxa de conversão</b> — quantos leads viraram clientes',
            '<b>Funil</b> — onde estão seus clientes em cada etapa',
            '<b>De onde vêm seus clientes</b>',
            '<b>Top clientes</b> e <b>top nichos</b>'
        ]
    },
    '/meus_nichos': {
        titulo: '🎯 Meus Nichos',
        descricao: 'Cada nicho é um produto ou serviço diferente que você vende.',
        dicas: [
            'A IA usa o nicho pra falar do seu produto, do seu jeito',
            'Você pode <b>atualizar o preço</b> de cada nicho quando quiser',
            'Pra adicionar mais nichos, faça upgrade de plano'
        ]
    },
    '/novo_nicho': {
        titulo: '➕ Novo Nicho',
        descricao: 'Crie mais um produto ou serviço pra IA atender.',
        dicas: [
            'Responda as 7 perguntas com o máximo de detalhe',
            'Quanto melhor a resposta, melhor a IA fala do seu produto',
            'O nicho <b>não pode ser editado nem apagado</b> depois de criado (exceto preço)'
        ]
    },
    '/planos': {
        titulo: '💳 Planos',
        descricao: 'Escolha o plano ideal pro seu volume de negócios.',
        dicas: [
            'O plano <b>Grátis</b> permite 1 nicho',
            'Quanto mais nichos, mais produtos/serviços você pode vender',
            'Pagamento via <b>PIX</b> — ativa em segundos'
        ]
    },
    '/admin': {
        titulo: '👑 Painel Admin',
        descricao: 'Visão geral de todos os vendedores da plataforma.',
        dicas: [
            'Clique em qualquer vendedor pra ver detalhes e editar tudo',
            'Acompanhe os <b>📥 leads da landing</b> que deixaram WhatsApp',
            'Bloqueie, mude plano ou exclua qualquer conta'
        ]
    },
    '/bem_vindo': {
        titulo: '🎉 Bem-vindo à M.A Tech',
        descricao: 'Sua IA está configurada e pronta pra atender.',
        dicas: [
            'Cadastre seu primeiro cliente pra começar',
            'Cole a mensagem do WhatsApp — a IA responde em segundos',
            'Use <b>🎯 Follow-ups</b> pra ver quem precisa de atenção'
        ]
    }
};

function detectarRota() {
    const path = window.location.pathname;
    if (path.match(/^\/cliente\/\d+$/)) return '/cliente_detalhe';
    if (path.match(/^\/cliente\/\d+\/atender$/)) return '/atendimento_cliente';
    if (path.match(/^\/resultado\/\d+$/)) return '/resultado';
    if (path.match(/^\/admin\/vendedor\/\d+/)) return '/admin';
    if (path === '/') return null;
    return path;
}

function abrirPainelAjuda() {
    const painel = document.getElementById('ajuda-painel');
    const btn = document.querySelector('.ajuda-header-btn');
    if (!painel) return;
    if (painel.style.display === 'block') {
        painel.style.display = 'none';
        if (btn) btn.classList.remove('ativo');
        return;
    }
	window.abrirPainelAjuda = abrirPainelAjuda;
    painel.style.display = 'block';
    if (btn) btn.classList.add('ativo');
}

document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    if (path === '/' || path === '/login' || path === '/signup') return;

    const rota = detectarRota();
    const info = AJUDA[rota];
    if (!info) return;

    const usuarioInfo = document.querySelector('.usuario-info');
    if (!usuarioInfo) return;

        // ===== Destaca a aba atual =====
    let rotaAtiva = null;
    if (path === '/clientes' || path === '/bem_vindo' || path.startsWith('/cliente/')) rotaAtiva = '/clientes';
    else if (path === '/relatorios') rotaAtiva = '/relatorios';
    else if (path === '/followups') rotaAtiva = '/followups';
    else if (path === '/meus_nichos' || path === '/novo_nicho') rotaAtiva = '/meus_nichos';
    else if (path === '/planos' || path === '/assinar' || path.startsWith('/pagamento/')) rotaAtiva = '/planos';
    else if (path === '/admin' || path.startsWith('/admin/')) rotaAtiva = '/admin';

    if (rotaAtiva) {
        usuarioInfo.querySelectorAll('a[data-rota]').forEach(a => {
            if (a.getAttribute('data-rota') === rotaAtiva) {
                a.style.color = '#0a0a0a';
                a.style.background = '#00d97e';
                a.style.fontWeight = '800';
                a.style.padding = '6px 14px';
                a.style.borderRadius = '6px';
                a.style.boxShadow = '0 4px 16px rgba(0,217,126,0.4)';
                a.style.textDecoration = 'none';
            }
        });
    }

    // ===== Botão Ajuda =====
    if (!usuarioInfo.querySelector('.ajuda-header-btn')) {
        const btn = document.createElement('a');
        btn.className = 'ajuda-header-btn';
        btn.href = 'javascript:void(0)';
        btn.innerHTML = '<span class="ajuda-icone">?</span> Ajuda';
        btn.title = 'Como usar esta tela';
        btn.onclick = abrirPainelAjuda;
        btn.style.color = '#8a8a8a';
        btn.style.textDecoration = 'none';
        btn.style.fontWeight = '500';
        btn.style.fontSize = '14px';
        btn.style.display = 'inline-flex';
        btn.style.alignItems = 'center';
        btn.style.gap = '6px';
        btn.style.cursor = 'pointer';
        btn.style.lineHeight = '1';

        const icone = btn.querySelector('.ajuda-icone');
        icone.style.display = 'inline-flex';
        icone.style.alignItems = 'center';
        icone.style.justifyContent = 'center';
        icone.style.width = '18px';
        icone.style.height = '18px';
        icone.style.borderRadius = '50%';
        icone.style.background = '#1f1f1f';
        icone.style.color = '#8a8a8a';
        icone.style.fontWeight = '800';
        icone.style.fontSize = '12px';
        icone.style.fontFamily = 'monospace';

        const sair = Array.from(usuarioInfo.querySelectorAll('a')).find(a => (a.getAttribute('href') || '') === '/logout');
        if (sair) usuarioInfo.insertBefore(btn, sair);
        else usuarioInfo.appendChild(btn);
    }

    // ===== Painel de ajuda =====
    if (!document.getElementById('ajuda-painel')) {
        const topo = document.querySelector('.topo');
        if (!topo) return;
        const painel = document.createElement('div');
        painel.id = 'ajuda-painel';
        painel.style.display = 'none';
        painel.style.marginTop = '0';
        painel.style.marginBottom = '24px';
        painel.style.background = 'linear-gradient(135deg, #0f1a15 0%, #141414 100%)';
        painel.style.border = '1px solid #222222';
        painel.style.borderLeft = '4px solid #00d97e';
        painel.style.borderRadius = '12px';
        painel.style.boxShadow = '0 12px 40px rgba(0,217,126,0.08)';
        painel.innerHTML = `
            <div style="padding: 22px 24px;">
                <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:10px;">
                    <h3 style="margin:0; font-size:17px; color:#fff; font-weight:700;">${info.titulo}</h3>
                    <button onclick="abrirPainelAjuda()" title="Fechar" style="background:#1a1a1a; color:#8a8a8a; border:1px solid #2a2a2a; width:28px; height:28px; border-radius:6px; cursor:pointer; font-size:12px; padding:0; line-height:1; display:flex; align-items:center; justify-content:center; font-family:inherit;">✕</button>
                </div>
                <p style="color:#8a8a8a; font-size:14px; line-height:1.6; margin:0 0 16px 0; padding-bottom:14px; border-bottom:1px solid #222222;">${info.descricao}</p>
                <div style="display:flex; flex-direction:column; gap:8px;">
                    ${info.dicas.map(d => `<div style="padding:8px 8px 8px 26px; color:#e8e8e8; font-size:13.5px; line-height:1.6; position:relative; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="position:absolute; left:8px; top:8px; color:#00d97e; font-weight:800;">✓</span>${d}</div>`).join('')}
                </div>
            </div>
        `;
        topo.parentNode.insertBefore(painel, topo.nextSibling);
    }
});