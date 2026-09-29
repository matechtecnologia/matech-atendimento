// ============================================
// M.A TECH — Ajuda contextual (painel abaixo do cabeçalho)
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
            'O histórico mostra todas as mensagens trocadas, em ordem',
            'Quando você marca o status como <b>Cliente</b>, o sistema para de cobrar follow-up'
        ]
    },
    '/atendimento_cliente': {
        titulo: '⚡ Atendendo Cliente',
        descricao: 'Cole a mensagem que o cliente enviou e receba a resposta da IA em segundos.',
        dicas: [
            'Cole a mensagem <b>exatamente</b> como o cliente escreveu, com erros e tudo',
            'Escolha o <b>nicho</b> correto (produto/serviço que você está vendendo)',
            'Use o <b>Modo instrução</b> quando quiser dar uma ordem pra IA',
            'A IA leva de 2 a 4 segundos pra responder'
        ]
    },
    '/resultado': {
        titulo: '🎯 Resposta da IA',
        descricao: 'A IA analisou a conversa e preparou 3 coisas pra você.',
        dicas: [
            '<b>🎤 O QUE FALAR</b> — é o áudio que você vai gravar pro cliente',
            '<b>📝 TEXTO PARA ENVIAR</b> — mensagem pronta pra colar no WhatsApp',
            '<b>📊 ESTÁGIO</b> — o funil atualizou automaticamente',
            'Clique em <b>📋 COPIAR</b> pra copiar cada bloco'
        ]
    },
    '/followups': {
        titulo: '🎯 Quem falar hoje',
        descricao: 'A IA analisa TODOS os seus clientes e mostra quem precisa de atenção agora.',
        dicas: [
            '<b>🔴 Urgente</b> — fale hoje ou já passou do prazo',
            '<b>🟠 Atenção</b> — fale nos próximos 2 dias',
            '<b>🟢 Agenda</b> — programado pra depois',
            'Clique em <b>⚡ ATENDER</b> pra já abrir o atendimento',
            'Depois que você fala com o cliente, ele sai da lista automaticamente'
        ]
    },
    '/relatorios': {
        titulo: '📊 Relatórios',
        descricao: 'Visão geral do seu desempenho comercial nos últimos 7 dias.',
        dicas: [
            '<b>Taxa de conversão</b> — de cada 100 leads, quantos viraram clientes',
            '<b>Funil</b> — onde estão seus clientes em cada etapa',
            '<b>De onde vêm seus clientes</b> — Instagram, indicação, etc',
            '<b>Top clientes</b> — quem você mais atendeu',
            '<b>Top nichos</b> — qual produto/serviço dá mais resultado'
        ]
    },
    '/meus_nichos': {
        titulo: '🎯 Meus Nichos',
        descricao: 'Cada nicho é um produto ou serviço diferente que você vende.',
        dicas: [
            'A IA usa o nicho pra falar do seu produto, do seu jeito',
            'Nichos <b>não podem ser editados nem apagados</b> depois de criados',
            'Pra adicionar mais nichos, faça upgrade de plano',
            'Cada atendimento usa 1 nicho — escolha o certo na hora de atender'
        ]
    },
    '/novo_nicho': {
        titulo: '➕ Novo Nicho',
        descricao: 'Crie mais um produto ou serviço pra IA atender.',
        dicas: [
            'Responda as 7 perguntas com o máximo de detalhe',
            'Quanto melhor a resposta, melhor a IA fala do seu produto',
            'O nicho <b>não pode ser editado nem apagado</b> depois de criado'
        ]
    },
    '/planos': {
        titulo: '💳 Planos',
        descricao: 'Escolha o plano ideal pro seu volume de negócios.',
        dicas: [
            'O plano <b>Grátis</b> permite 1 nicho — bom pra testar',
            'Quanto mais nichos, mais produtos/serviços você pode vender',
            'Pagamento via <b>PIX</b> — ativa em segundos',
            'Renovação mensal, sem fidelidade'
        ]
    },
    '/admin': {
        titulo: '👑 Painel Admin',
        descricao: 'Visão geral de todos os vendedores da plataforma.',
        dicas: [
            'Clique em qualquer vendedor pra ver detalhes e editar tudo',
            'Você pode <b>editar nichos, clientes, histórico</b> de qualquer um',
            'Use <b>➕ CRIAR VENDEDOR</b> pra cadastrar contas manualmente',
            'Bloqueie, mude plano ou exclua qualquer conta'
        ]
    },
    '/bem_vindo': {
        titulo: '🎉 Bem-vindo à M.A Tech',
        descricao: 'Sua IA está configurada e pronta pra atender.',
        dicas: [
            'Cadastre seu primeiro cliente pra começar',
            'Cole a mensagem do WhatsApp — a IA responde em 2 a 4 segundos',
            'Use o botão <b>🎯 Follow-ups</b> pra ver quem precisa de atenção'
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

    // Fecha se estiver aberto
    if (painel.style.display === 'block') {
        painel.style.display = 'none';
        if (btn) btn.classList.remove('ativo');
        return;
    }

    // Abre
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

    // ===== Botão "? Ajuda" no cabeçalho =====
    if (!usuarioInfo.querySelector('.ajuda-header-btn')) {
        const btn = document.createElement('a');
        btn.className = 'ajuda-header-btn';
        btn.href = 'javascript:void(0)';
        btn.innerHTML = '<span class="ajuda-icone">?</span> Ajuda';
        btn.title = 'Como usar esta tela';
        btn.onclick = abrirPainelAjuda;

        const sair = Array.from(usuarioInfo.querySelectorAll('a')).find(a => (a.getAttribute('href') || '') === '/logout');
        if (sair) {
            usuarioInfo.insertBefore(btn, sair);
        } else {
            usuarioInfo.appendChild(btn);
        }
    }

    // ===== Painel de ajuda abaixo do cabeçalho =====
    if (!document.getElementById('ajuda-painel')) {
        const topo = document.querySelector('.topo');
        if (!topo) return;

        const painel = document.createElement('div');
        painel.id = 'ajuda-painel';
        // INLINE STYLE GARANTE QUE FICA OCULTO POR PADRÃO
        painel.style.display = 'none';
        painel.style.marginTop = '0';
        painel.style.marginBottom = '24px';
        painel.style.background = 'linear-gradient(135deg, #0f1a15 0%, #141414 100%)';
        painel.style.border = '1px solid #222222';
        painel.style.borderLeft = '4px solid #00d97e';
        painel.style.borderRadius = '12px';
        painel.style.boxShadow = '0 12px 40px rgba(0,217,126,0.08)';
        painel.style.animation = 'fade-in-up 0.3s ease both';

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

        // Insere logo depois do cabeçalho
        topo.parentNode.insertBefore(painel, topo.nextSibling);
    }
});