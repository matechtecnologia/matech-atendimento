// ============================================
// M.A Tech — Ajuda contextual
// ============================================

const AJUDA = {
    '/clientes': {
        titulo: 'Meus Clientes',
        descricao: 'Aqui você gerencia todos os seus clientes e leads. É o coração do sistema.',
        dicas: [
            'Use a <b>barra de busca</b> pra encontrar qualquer cliente por nome, WhatsApp ou origem',
            'Clique em <b>Filtros</b> pra filtrar por status ou ordenar a lista',
            'Cada card tem 3 botões: <b>relógio roxo</b> (histórico), <b>raio verde</b> (atender) e <b>lápis âmbar</b> (editar)',
            'A <b>borda colorida à esquerda</b> mostra o status: cinza=novo, verde=atendendo, âmbar=negociando, verde-escuro=cliente, vermelho=perdido',
            'Use <b>+ Novo Cliente</b> pra cadastrar alguém novo'
        ]
    },
    '/cliente_detalhe': {
        titulo: 'Detalhes do Cliente',
        descricao: 'Tudo sobre este cliente em um só lugar: dados, histórico e status.',
        dicas: [
            '<b>Atender este cliente</b> inicia um novo atendimento com IA',
            '<b>Editar</b> muda qualquer dado do cliente',
            'O histórico mostra todas as mensagens trocadas, em ordem',
            'Quando você marca o status como <b>Cliente</b>, ele para de aparecer nos follow-ups'
        ]
    },
    '/atendimento_cliente': {
        titulo: 'Atendendo Cliente',
        descricao: 'Cole a mensagem que o cliente enviou e receba a resposta da IA em segundos.',
        dicas: [
            'Cole a mensagem <b>exatamente</b> como o cliente escreveu, com erros e tudo',
            'Escolha o <b>nicho</b> correto (produto/serviço que você está vendendo)',
            'Use o <b>Modo instrução</b> quando quiser dar uma ordem direta pra IA',
            'A IA leva de 2 a 4 segundos pra responder'
        ]
    },
    '/resultado': {
        titulo: 'Resposta da IA',
        descricao: 'A IA analisou a conversa e preparou 3 coisas pra você.',
        dicas: [
            '<b>O QUE FALAR</b> — o áudio que você vai gravar pro cliente',
            '<b>TEXTO PARA ENVIAR</b> — mensagem pronta pro WhatsApp',
            '<b>ESTÁGIO</b> — o funil atualizou automaticamente',
            'Clique em <b>COPIAR</b> em cada bloco pra levar a resposta'
        ]
    },
    '/followups': {
        titulo: 'Quem falar hoje',
        descricao: 'A IA analisa todos os seus clientes e mostra quem precisa de atenção agora.',
        dicas: [
            '<b>Urgente</b> (vermelho) — fale hoje ou já passou do prazo',
            '<b>Atenção</b> (âmbar) — fale nos próximos 2 dias',
            '<b>Agenda</b> (verde) — programado pra depois',
            'Clique em <b>ATENDER</b> pra já abrir o atendimento com esse cliente',
            'Use o bloco <b>Silenciar follow-ups</b> pra pausar as notificações'
        ]
    },
    '/relatorios': {
        titulo: 'Relatórios',
        descricao: 'Visão geral do seu desempenho comercial nos últimos 7 dias.',
        dicas: [
            '<b>Taxa de conversão</b> — quantos leads viraram clientes',
            '<b>Funil</b> — onde estão seus clientes em cada etapa',
            '<b>De onde vêm seus clientes</b> — Instagram, indicação, etc',
            '<b>Top clientes</b> e <b>Top nichos</b>'
        ]
    },
    '/meus_nichos': {
        titulo: 'Meus Nichos',
        descricao: 'Cada nicho é um produto ou serviço diferente que você vende.',
        dicas: [
            'A IA usa o nicho pra falar do seu produto, do seu jeito',
            'Você pode <b>atualizar o preço</b> e outros campos (menos o nome)',
            'Pra adicionar mais nichos, faça upgrade de plano',
            'Cada atendimento usa 1 nicho — escolha o certo na hora de atender'
        ]
    },
    '/novo_nicho': {
        titulo: 'Novo Nicho',
        descricao: 'Crie mais um produto ou serviço pra IA atender.',
        dicas: [
            'Responda as 7 perguntas com o máximo de detalhe',
            'Quanto melhor a resposta, melhor a IA fala do seu produto',
            'O sistema bloqueia nichos vagos ("coisas", "produtos") ou com 2 produtos misturados ("carro e moto")',
            'Se vende 2 coisas diferentes, cadastre 2 nichos separados'
        ]
    },
    '/planos': {
        titulo: 'Planos',
        descricao: 'Escolha o plano ideal pro seu volume de negócios.',
        dicas: [
            'O plano <b>Grátis</b> permite 1 nicho — bom pra testar',
            'Quanto mais nichos, mais produtos/serviços você pode vender',
            'Pagamento via <b>PIX</b> — ativa em segundos',
            'Renovação mensal, sem fidelidade'
        ]
    },
    '/indicar': {
        titulo: 'Indique e ganhe',
        descricao: 'Compartilhe seu link e ganhe 1 mês grátis por indicação.',
        dicas: [
            'Compartilhe seu link no WhatsApp com amigos vendedores',
            'Quando o indicado pagar o primeiro PIX, você ganha <b>+30 dias</b>',
            'Sem limite de indicações — quanto mais, melhor',
            'Acompanhe aqui quem você indicou e quantos já pagaram'
        ]
    },
    '/configuracoes': {
        titulo: 'Configurações',
        descricao: 'Ajuste o comportamento do app.',
        dicas: [
            '<b>Vibração ao tocar</b> — feedback tátil quando clica em botões (só celular)',
            '<b>Animações</b> — transições suaves entre telas',
            '<b>Silenciar follow-ups</b> — pausa o badge vermelho por 1, 2, 3 ou 7 dias',
            'Acesse <b>Indique e ganhe</b> pra compartilhar seu link',
            'Sair da conta faz logout de todos os dispositivos'
        ]
    },
    '/admin': {
        titulo: 'Painel Admin',
        descricao: 'Visão geral de todos os vendedores da plataforma.',
        dicas: [
            'Clique em qualquer vendedor pra ver detalhes, editar, bloquear ou excluir',
            'Você pode <b>editar nichos, clientes e histórico</b> de qualquer vendedor',
            'Use <b>+ CRIAR VENDEDOR</b> pra cadastrar contas manualmente',
            'Em <b>Leads da Landing</b> você vê quem deixou WhatsApp no site'
        ]
    },
    '/admin/dashboard': {
        titulo: 'Dashboard',
        descricao: 'Evolução da plataforma nos últimos 6 meses.',
        dicas: [
            '<b>Vendedores</b> — quantos cadastrados e variação vs mês anterior',
            '<b>Leads</b> — quantos capturados e % que viraram vendedores',
            '<b>Clientes</b> — total e média por vendedor',
            'Veja o gráfico de crescimento e distribuição por plano'
        ]
    },
    '/admin/leads': {
        titulo: 'Leads da Landing',
        descricao: 'Visitantes que deixaram WhatsApp no formulário do site.',
        dicas: [
            'Cada lead mostra nome, WhatsApp e quando preencheu',
            'Clique em <b>ABRIR WHATSAPP</b> pra iniciar conversa direto',
            'Entre em contato rápido — leads esfriam em horas'
        ]
    },
    '/bem_vindo': {
        titulo: 'Bem-vindo à M.A Tech',
        descricao: 'Sua IA está configurada e pronta pra atender.',
        dicas: [
            'Cadastre seu primeiro cliente pra começar',
            'Cole a mensagem do WhatsApp — a IA responde em segundos',
            'Use <b>Follow-ups</b> pra ver quem precisa de atenção'
        ]
    }
};

function detectarRota() {
    const path = window.location.pathname;
    if (path.match(/^\/cliente\/\d+$/)) return '/cliente_detalhe';
    if (path.match(/^\/cliente\/\d+\/atender$/)) return '/atendimento_cliente';
    if (path.match(/^\/resultado\/\d+$/)) return '/resultado';
    if (path === '/admin/dashboard') return '/admin/dashboard';
    if (path === '/admin/leads') return '/admin/leads';
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
    painel.style.display = 'block';
    if (btn) btn.classList.add('ativo');
}

window.abrirPainelAjuda = abrirPainelAjuda;

document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    if (path === '/' || path === '/login' || path === '/signup' || path === '/ver-landing') return;

    const rota = detectarRota();
    const info = AJUDA[rota];
    if (!info) return;

    const usuarioInfo = document.querySelector('.usuario-info');
    if (!usuarioInfo) return;

    // Botão Ajuda (sem borda)
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

    // Destaca a aba atual
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

    // Painel de ajuda
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
                    <button onclick="abrirPainelAjuda()" title="Fechar" style="background:#1a1a1a; color:#8a8a8a; border:1px solid #2a2a2a; width:28px; height:28px; border-radius:6px; cursor:pointer; font-size:12px; padding:0; line-height:1; display:flex; align-items:center; justify-content:center; font-family:inherit;">×</button>
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