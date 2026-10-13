// ============================================
// M.A Tech — Ajuda contextual
// ============================================

const AJUDA = {

    '/hub': {
        titulo: 'Areas M.A Tech',
        descricao: 'Esse e o ponto de partida. Aqui voce acessa tudo: atendimento com IA, consultoria empresarial e as ferramentas do seu negocio. Cada card leva pra uma area diferente do sistema.',
        dicas: [
            'Comece cadastrando seus clientes na area de atendimento.',
            'A IA so funciona bem depois que voce configura seu nicho (produto, publico, preco).',
            'Se for sua primeira vez, faca o onboarding completo antes de usar.'
        ]
    },

    '/clientes': {
        titulo: 'Meus Clientes',
        descricao: 'Aqui ficam todos os seus leads e clientes. Cada um tem status, origem e historico de conversa. Voce pode cadastrar manualmente ou deixar a IA registrar automaticamente quando voce colar uma mensagem.',
        dicas: [
            'Use filtros pra encontrar clientes por status (novo lead, negociacao, cliente).',
            'Clique no cliente pra ver o historico completo de conversas.',
            'Clique em "Atender" pra gerar uma resposta da IA pra esse cliente especifico.',
            'Quanto mais rapido voce responde um lead novo, maior a chance de fechar.'
        ]
    },

    '/cliente_detalhe': {
        titulo: 'Detalhes do Cliente',
        descricao: 'Tela com o historico completo desse cliente. Mostra todas as conversas, o status atual e as ultimas mensagens que a IA gerou pra ele.',
        dicas: [
            'O historico fica salvo pra sempre, entao voce nunca perde contexto.',
            'Use o botao "Atender" pra continuar a conversa de onde parou.',
            'Atualize o status do cliente quando ele avancar no funil.'
        ]
    },

    '/atendimento_cliente': {
        titulo: 'Atender Cliente',
        descricao: 'Aqui voce cola a mensagem que o cliente te mandou no WhatsApp. A IA vai analisar o historico e devolver 3 blocos prontos: O QUE FALAR (audio), TEXTO PARA ENVIAR e o ESTAGIO do lead.',
        dicas: [
            'Cole a mensagem EXATA do cliente. Nao resuma.',
            'A IA leva de 2 a 7 segundos pra gerar a resposta.',
            'Depois que a IA responder, voce copia o texto e envia no WhatsApp normalmente.',
            'Se for uma INSTRUCAO sua pra IA (nao uma mensagem do cliente), marque a opcao "Isso e instrucao".'
        ]
    },

    '/resultado': {
        titulo: 'Resposta da IA',
        descricao: 'A IA devolve 3 blocos: O QUE FALAR (pra voce gravar audio), TEXTO PARA ENVIAR (pra copiar direto) e o ESTAGIO do cliente (pra atualizar o funil). E so copiar, colar no WhatsApp e seguir a venda.',
        dicas: [
            'Grave audio com o texto de "O QUE FALAR" - passa mais confianca que texto.',
            'Se o bloco "TEXTO PARA ENVIAR" estiver com "NENHUM", significa que e melhor gravar audio.',
            'O ESTAGIO atualiza o funil automaticamente - nao precisa mexer manualmente.',
            'Se a resposta nao ficou boa, tente colar mais contexto ou reescreva a mensagem do cliente.'
        ]
    },

    '/followups': {
        titulo: 'Follow-ups',
        descricao: 'Lista de clientes que voce precisa dar atencao. Cada lead tem um prazo sugerido baseado no estagio dele. O sistema te avisa quem esta atrasado pra voce nao esquecer ninguem.',
        dicas: [
            'Abra essa tela toda manha. E a coisa mais importante do dia.',
            'Cliente novo lead: responder em ate 1 dia.',
            'Cliente em atendimento ou negociacao: contato a cada 2 dias.',
            'Nao deixe ninguem passar de 3 dias sem resposta.'
        ]
    },

    '/meus_nichos': {
        titulo: 'Meus Nichos',
        descricao: 'Cada nicho e um produto ou servico diferente que voce vende. A IA usa essas informacoes pra gerar respostas especificas pro seu negocio. Sem nicho bem configurado, a IA responde generico.',
        dicas: [
            'Configure quantos nichos seu plano permitir.',
            'Nicho bem preenchido = IA que fala do SEU produto, com SEU tom.',
            'Se voce vende pra publicos diferentes, crie nichos separados.',
            'Voce pode pausar um nicho sem apagar (util pra testar).'
        ]
    },

    '/novo_nicho': {
        titulo: 'Novo Nicho',
        descricao: 'Formulario de 7 perguntas que ensina a IA sobre o que voce vende. Quanto mais detalhado, melhor a resposta.',
        dicas: [
            'Produto: o que exatamente voce vende.',
            'Publico: seja especifico ("donos de pet shop", nao "empresarios").',
            'Preco: coloque o valor real. A IA usa isso pra tratar objecao.',
            'Dor: qual problema real seu cliente tem.',
            'Objecao: o que as pessoas falam pra nao comprar.',
            'Diferencial: por que comprar de voce e nao do concorrente.',
            'Tom: como voce fala no WhatsApp (direto, amigavel, formal).'
        ]
    },

    '/planos': {
        titulo: 'Planos',
        descricao: 'Veja seu consumo, faca upgrade ou veja todos os planos disponiveis. Cada plano tem limite de interacoes por mes, e o primeiro mes tem desconto de 50%.',
        dicas: [
            'O contador mostra quanto voce ja usou do limite mensal.',
            'Quando passa de 100%, aparece um aviso. So bloqueia em 120%.',
            'O excedente e cobrado a R$ 0,10 por interacao extra.',
            'Se esta usando muito, considere upgrade de plano.'
        ]
    },

    '/indicar': {
        titulo: 'Indique e Ganhe',
        descricao: 'Programa de indicacao: voce ganha desconto quando um amigo assina a M.A Tech. Compartilhe seu link unico e receba creditos a cada pessoa que entrar.',
        dicas: [
            'Cada indicacao que virar cliente pago te da 1 mes gratis.',
            'O link e unico e rastreia todas as suas indicacoes.',
            'Compartilhe com outros vendedores que tambem atendem no WhatsApp.',
            'Quanto mais indicacoes, mais tempo voce fica sem pagar.'
        ]
    },

    '/configuracoes': {
        titulo: 'Configuracoes',
        descricao: 'Ajustes da sua conta: nome, WhatsApp, senha, e-mail e preferencias de notificacao.',
        dicas: [
            'Mantenha o WhatsApp atualizado pra receber avisos.',
            'Troque a senha se desconfiar de acesso indevido.',
            'Se quiser cancelar, faca em Planos > Cancelar assinatura.'
        ]
    },

    '/obrigado': {
        titulo: 'Obrigado!',
        descricao: 'Sua conta foi criada com sucesso. Agora e hora de configurar seu negocio pra IA comecar a trabalhar pra voce.',
        dicas: [
            'Proximo passo: responder as 7 perguntas do onboarding.',
            'Depois, cadastre seus primeiros clientes.',
            'Cole a mensagem do WhatsApp e veja a IA trabalhar.'
        ]
    },

    '/bem_vindo': {
        titulo: 'Bem-vindo a M.A Tech',
        descricao: 'Sua IA foi configurada com sucesso. Agora ela ja sabe o que voce vende, pra quem vende e como falar. Esta pronta pra te ajudar a atender e fechar mais vendas.',
        dicas: [
            'Proximo passo: cadastre seu primeiro cliente.',
            'Cole a mensagem que ele te mandou no WhatsApp.',
            'A IA devolve a resposta pronta em segundos.',
            'Use o botao "?" a qualquer momento pra ver dicas dessa tela.'
        ]
    },

    '/termos': {
        titulo: 'Termos de Uso',
        descricao: 'Regras pra usar a M.A Tech. Descreve o que voce pode e nao pode fazer no sistema, seus direitos e nossas responsabilidades.',
        dicas: [
            'Leia com atencao antes de usar.',
            'Se discordar, nao use a plataforma.',
            'Duvidas: matechtecnologia01@gmail.com'
        ]
    },

    '/privacidade': {
        titulo: 'Politica de Privacidade',
        descricao: 'Como a M.A Tech cuida dos seus dados. Explica o que coletamos, como usamos e seus direitos (LGPD).',
        dicas: [
            'Seus dados nao sao vendidos pra ninguem.',
            'Voce pode pedir exclusao quando quiser.',
            'Conversas dos clientes ficam criptografadas e so voce acessa.'
        ]
    },

    '/consultoria': {
        titulo: 'Consultoria Empresarial',
        descricao: 'Area com IA consultora que diagnostica seu negocio. Ela analisa seus dados reais, identifica o gargalo e sugere um plano de acao. Esta em desenvolvimento - em breve liberada pra todos.',
        dicas: [
            'Enquanto esta em dev, o cliente ve uma tela "Em breve".',
            'Quando for liberada, ela vai acessar todos os seus dados pra diagnosticar.',
            'A consultoria e o primeiro passo pra vender Gestao e CRM no futuro.'
        ]
    },

    '/admin': {
        titulo: 'Painel Admin',
        descricao: 'Area exclusiva do administrador. Aqui voce ve todos os vendedores cadastrados, seus planos, status e dados de contato. Use pra dar suporte e acompanhar crescimento.',
        dicas: [
            'Clique num vendedor pra ver os detalhes e o historico dele.',
            'Voce pode editar plano manualmente (util pra testes ou cortesias).',
            'Crie vendedor manualmente se precisar cadastrar alguem sem passar pelo signup.',
            'Acompanhe os leads da landing page na aba "Leads".'
        ]
    },

    '/admin/dashboard': {
        titulo: 'Dashboard Admin',
        descricao: 'Visao geral da plataforma: evolucao dos ultimos 6 meses, vendedores ativos, leads recebidos, clientes pagantes e receita. Tudo que voce precisa pra tomar decisao.',
        dicas: [
            'O grafico mostra a evolucao mes a mes de vendedores e leads.',
            'Use pra ver se a landing e os anuncios estao convertendo.',
            'Compare o crescimento de leads com o de clientes pagantes.',
            'Se os leads sobem mas pagantes nao, o problema esta na conversao.'
        ]
    },

    '/admin/leads': {
        titulo: 'Leads da Landing',
        descricao: 'Lista de visitantes que deixaram o WhatsApp na landing page querendo conhecer o sistema. Sao oportunidades quentes - entre em contato rapido.',
        dicas: [
            'Clique no lead pra abrir o WhatsApp dele direto.',
            'Contate em ate 1 hora. Lead frio esfria rapido.',
            'Se nao responder no primeiro dia, tente no segundo.',
            'Quem deixa WhatsApp na landing tem interesse real - nao perca.'
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