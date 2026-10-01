// ============================================
// M.A Tech — Ajuda contextual
// ============================================

const AJUDA = {
    '/clientes': {
        titulo: 'Meus Clientes',
        descricao: 'Gerencie todos os seus clientes e leads em um só lugar.',
        dicas: [
            'Use <b>+ Novo Cliente</b> pra cadastrar nome e WhatsApp',
            'Busque por nome, WhatsApp ou origem na <b>barra de busca</b>',
            'Clique em <b>Filtros</b> pra filtrar por status ou ordenar a lista',
            'Cada card tem 2 botões: <b>⚡ Atender</b> (abre a IA) e <b>✏️ Editar</b> (muda dados do cliente)',
            'A <b>cor da barra à esquerda</b> mostra o status: cinza=novo lead, verde=atendendo, âmbar=negociando, verde escuro=cliente, vermelho=perdido'
        ]
    },
    '/cliente_detalhe': {
        titulo: 'Detalhes do Cliente',
        descricao: 'Dados completos, histórico de conversa e status deste cliente.',
        dicas: [
            'Clique em <b>⚡ Atender este cliente</b> pra gerar uma nova resposta com IA',
            'Use <b>✏️ Editar</b> pra alterar nome, WhatsApp, email, origem, status ou observações',
            'Todo o <b>histórico de conversa</b> fica aqui, em ordem cronológica',
            'Quando o status é <b>Cliente</b>, ele para de aparecer nos follow-ups pendentes'
        ]
    },
    '/atendimento_cliente': {
        titulo: 'Atendendo Cliente',
        descricao: 'Cole a mensagem do cliente e receba a resposta da IA em segundos.',
        dicas: [
            'Cole a mensagem <b>exatamente</b> como o cliente enviou no WhatsApp, com erros e tudo',
            'Escolha o <b>nicho</b> (produto/serviço que você está vendendo)',
            'Use o <b>Modo instrução</b> quando quiser dar uma ordem direta pra IA (ex: "refaça a última pergunta", "manda o preço") — nesse modo, a IA executa em vez de responder ao cliente',
            'A IA leva de 2 a 4 segundos pra gerar'
        ]
    },
    '/resultado': {
        titulo: 'Resposta Gerada',
        descricao: 'A IA analisou a conversa e preparou os 3 blocos.',
        dicas: [
            '<b>O QUE FALAR</b> — roteiro do áudio pra você gravar (linguagem natural)',
            '<b>TEXTO PARA ENVIAR</b> — só aparece quando tem preço, link ou info técnica. Na maioria das vezes é NENHUM',
            '<b>ESTÁGIO</b> — o funil atualizou automaticamente baseado na conversa',
            'Clique em <b>📋 COPIAR</b> pra levar o texto'
        ]
    },
    '/followups': {
        titulo: 'Quem falar hoje',
        descricao: 'A IA analisa todos os seus clientes e mostra quem precisa de atenção agora.',
        dicas: [
            '<b>Urgente</b> (vermelho) — fale hoje ou já passou do prazo',
            '<b>Atenção</b> (âmbar) — fale nos próximos 2 dias',
            '<b>Agenda</b> (verde) — programado pra depois',
            'Clique em <b>⚡ ATENDER</b> pra já abrir o atendimento',
            'Quer pausar esses avisos? Vá em <b>Configurações → Silenciar follow-ups</b>'
        ]
    },
    '/relatorios': {
        titulo: 'Relatórios',
        descricao: 'Veja o desempenho do seu negócio em qualquer período.',
        dicas: [
            '<b>Total de clientes</b>, <b>em andamento</b>, <b>ganhos</b> e <b>perdidos</b> no topo',
            '<b>Taxa de conversão</b> mostra de cada 100 clientes quantos viraram cliente',
            '<b>Funil de vendas</b> mostra onde estão seus clientes em cada etapa',
            '<b>De onde vêm seus clientes</b> — Instagram, indicação, prospecção, etc',
            'No <b>final da página</b> tem o filtro de período — escolhe De/Até ou clica em 7/30/90 dias'
        ]
    },
    '/meus_nichos': {
        titulo: 'Meus Nichos',
        descricao: 'Cada nicho é um produto ou serviço diferente que você vende.',
        dicas: [
            'A IA usa o nicho pra falar do seu produto, do seu jeito',
            'Você pode <b>editar preço, público, dor, objeção, diferencial e tom</b> — o nome e o produto não mudam',
            'Quando você salva, a IA <b>regenera o prompt automaticamente</b>',
            'Pra adicionar mais nichos, faça upgrade de plano'
        ]
    },
    '/novo_nicho': {
        titulo: 'Novo Nicho',
        descricao: 'Crie mais um produto ou serviço pra IA atender.',
        dicas: [
            'Responda as 7 perguntas com o máximo de detalhe — é isso que ensina a IA a vender',
            'O sistema bloqueia nichos vagos ("coisas", "produtos") ou com 2 coisas misturadas ("carro e moto")',
            'Se vende 2 coisas diferentes, cadastre 2 nichos separados',
            'Capriche nas respostas — quanto melhor o nicho, melhor a IA vende'
        ]
    },
    '/planos': {
        titulo: 'Planos',
        descricao: 'Escolha o plano de acordo com o que você vende.',
        dicas: [
            '<b>Grátis</b> — 1 nicho, ideal pra testar',
            '<b>Básico R$ 97</b> — 3 nichos',
            '<b>Pro R$ 297</b> — 10 nichos',
            '<b>Empresarial R$ 597</b> — 25 nichos',
            'Pagamento via <b>PIX</b>, ativa em segundos, sem fidelidade'
        ]
    },
    '/configuracoes': {
        titulo: 'Configurações',
        descricao: 'Ajuste o app e gerencie sua conta.',
        dicas: [
            '<b>Vibração ao tocar</b> — feedback tátil quando clica nos botões (só no celular)',
            '<b>Animações</b> — transições suaves entre as telas',
            '<b>Silenciar follow-ups</b> — pausa o badge vermelho por 1, 2, 3 ou 7 dias',
            '<b>Indique e ganhe</b> — compartilhe seu link e ganhe 30 dias grátis por cada amigo que assinar'
        ]
    },
    '/indicar': {
        titulo: 'Indique e ganhe',
        descricao: 'Compartilhe seu link e ganhe 1 mês grátis por indicação.',
        dicas: [
            'Copie seu <b>link único</b> e envie pra amigos vendedores',
            'Quando o indicado <b>pagar o primeiro PIX</b>, você ganha +30 dias grátis',
            'Sem limite de indicações — quanto mais, melhor',
            'Acompanhe aqui quem você indicou e quantos já pagaram'
        ]
    },
    '/admin': {
        titulo: 'Painel Admin',
        descricao: 'Visão geral de todos os vendedores da plataforma.',
        dicas: [
            'Clique em qualquer vendedor pra ver detalhes, editar, bloquear ou excluir',
            'Você pode <b>editar nichos, clientes e histórico</b> de qualquer vendedor',
            'Use <b>+ CRIAR VENDEDOR</b> pra cadastrar contas manualmente',
            'Em <b>📥 Leads da Landing</b> você vê quem deixou WhatsApp no site'
        ]
    },
    '/admin/dashboard': {
        titulo: 'Dashboard',
        descricao: 'Evolução da plataforma nos últimos 6 meses.',
        dicas: [
            '<b>Vendedores</b> — quantos cadastrados e variação vs mês anterior',
            '<b>Leads</b> — quantos capturados e % que viraram vendedores',
            '<b>Clientes</b> — total e média por vendedor',
            'Veja o gráfico de crescimento e a distribuição por plano'
        ]
    },
    '/admin/leads': {
        titulo: 'Leads da Landing',
        descricao: 'Visitantes que deixaram WhatsApp no formulário do site.',
        dicas: [
            'Cada lead mostra nome, WhatsApp, email e quando preencheu',
            'Clique em <b>ABRIR WHATSAPP</b> pra iniciar conversa direto',
            'Leads esfriam rápido — entre em contato no mesmo dia'
        ]
    },
    '/bem_vindo': {
        titulo: 'Bem-vindo à M.A Tech',
        descricao: 'Sua IA está pronta pra atender.',
        dicas: [
            'Cadastre seu primeiro cliente pra começar',
            'Cole a mensagem do WhatsApp — a IA responde em segundos',
            'Use <b>Follow-ups</b> pra ver quem precisa de atenção hoje'
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

    // Botão Ajuda
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
                    <button onclick="abrirPainelAjuda()" title="Fechar" style="background:#1a1a1a; color:#8a8a8a; border:1px solid #2a2a2a; width:28px; height:28px; border-radius:6px; cursor:pointer; font-size:12px; padding:0; line-height:1; display:flex; align-items:center; justify-content:center; font-family:inherit;">x</button>
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