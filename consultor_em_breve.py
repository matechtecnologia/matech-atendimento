# consultor_em_breve.py
# Tela "EM DESENVOLVIMENTO" da Consultoria Empresarial.
# Cliente ve essa tela. Admin vai direto pro chat.

from fastapi.responses import HTMLResponse, RedirectResponse


HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#7c3aed">
<title>Consultoria Empresarial - M.A Tech</title>
<link rel="stylesheet" href="/static/app.min.css?v=9999">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    background: #0a0a0f;
    color: #e8e8f0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
    min-height: 100vh;
    overflow-x: hidden;
}

.fundo {
    position: fixed;
    inset: 0;
    z-index: 0;
    background: 
        radial-gradient(circle at 20% 20%, rgba(124, 58, 237, 0.15) 0%, transparent 40%),
        radial-gradient(circle at 80% 80%, rgba(0, 217, 126, 0.10) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(124, 58, 237, 0.08) 0%, transparent 60%);
    pointer-events: none;
}

.fundo::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image: 
        linear-gradient(rgba(124, 58, 237, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124, 58, 237, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
    -webkit-mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
}

.container {
    position: relative;
    z-index: 1;
    max-width: 620px;
    margin: 0 auto;
    padding: 32px 20px 60px;
}

.voltar {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #8a8a9a;
    text-decoration: none;
    font-size: 13px;
    margin-bottom: 24px;
    transition: color 0.2s;
}
.voltar:hover { color: #a78bfa; }

.hero {
    text-align: center;
    margin-bottom: 40px;
    animation: fadeUp 0.6s ease-out;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(124, 58, 237, 0.12);
    border: 1px solid rgba(124, 58, 237, 0.3);
    color: #a78bfa;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 24px;
}
.badge::before {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #a78bfa;
    box-shadow: 0 0 12px #a78bfa;
    animation: pulse 1.8s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.85); }
}

.icone-hero {
    width: 96px;
    height: 96px;
    margin: 0 auto 24px;
    border-radius: 24px;
    background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 50%, #00d97e 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
    box-shadow: 
        0 0 0 1px rgba(124, 58, 237, 0.3),
        0 20px 60px rgba(124, 58, 237, 0.4),
        0 0 80px rgba(124, 58, 237, 0.2);
    animation: float 3s ease-in-out infinite;
    position: relative;
}
.icone-hero::after {
    content: "";
    position: absolute;
    inset: -4px;
    border-radius: 28px;
    background: linear-gradient(135deg, #7c3aed, #00d97e);
    opacity: 0.4;
    filter: blur(20px);
    z-index: -1;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

h1 {
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.8px;
    line-height: 1.15;
    margin-bottom: 14px;
    background: linear-gradient(135deg, #fff 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.sub {
    font-size: 15px;
    color: #8a8a9a;
    line-height: 1.6;
    max-width: 480px;
    margin: 0 auto;
}

.destaque {
    color: #a78bfa;
    font-weight: 600;
}

/* Cards do que vem */
.cards {
    display: flex;
    flex-direction: column;
    gap: 14px;
    margin-bottom: 32px;
}

.card {
    background: linear-gradient(180deg, #14141f 0%, #111119 100%);
    border: 1px solid #1e1e2e;
    border-radius: 14px;
    padding: 20px;
    display: flex;
    gap: 16px;
    align-items: flex-start;
    transition: all 0.25s ease;
    animation: fadeUp 0.6s ease-out backwards;
    position: relative;
    overflow: hidden;
}
.card:nth-child(1) { animation-delay: 0.1s; }
.card:nth-child(2) { animation-delay: 0.2s; }
.card:nth-child(3) { animation-delay: 0.3s; }
.card:nth-child(4) { animation-delay: 0.4s; }

.card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #7c3aed, #a78bfa);
    opacity: 0;
    transition: opacity 0.25s;
}

.card:hover {
    border-color: #2e2e42;
    transform: translateX(2px);
}
.card:hover::before {
    opacity: 1;
}

.card-icone {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: rgba(124, 58, 237, 0.12);
    border: 1px solid rgba(124, 58, 237, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
}

.card-texto { flex: 1; }

.card-titulo {
    font-size: 15px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 4px;
    letter-spacing: -0.2px;
}

.card-desc {
    font-size: 13px;
    color: #8a8a9a;
    line-height: 1.5;
}

/* Rodapé CTA */
.rodape {
    text-align: center;
    padding: 24px;
    background: linear-gradient(180deg, transparent 0%, rgba(124, 58, 237, 0.05) 100%);
    border-radius: 14px;
    border: 1px solid #1e1e2e;
    margin-top: 24px;
    animation: fadeUp 0.6s ease-out 0.5s backwards;
}

.rodape-titulo {
    font-size: 16px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 8px;
}

.rodape-desc {
    font-size: 13px;
    color: #8a8a9a;
    line-height: 1.6;
    margin-bottom: 20px;
}

.rodape-desc strong {
    color: #a78bfa;
    font-weight: 600;
}

.btn-whats {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 14px 28px;
    background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
    color: #fff;
    text-decoration: none;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.3px;
    transition: all 0.2s;
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.4);
    border: none;
    cursor: pointer;
    font-family: inherit;
}
.btn-whats:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(124, 58, 237, 0.55);
}

.btn-voltar-hub {
    display: inline-block;
    margin-top: 16px;
    padding: 10px 20px;
    color: #8a8a9a;
    text-decoration: none;
    font-size: 13px;
    border-radius: 8px;
    transition: all 0.2s;
}
.btn-voltar-hub:hover { color: #fff; background: #1a1a24; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Responsivo */
@media (max-width: 480px) {
    .container { padding: 24px 16px 40px; }
    h1 { font-size: 26px; }
    .sub { font-size: 14px; }
    .icone-hero { width: 80px; height: 80px; font-size: 40px; }
    .card { padding: 16px; gap: 12px; }
    .card-icone { width: 40px; height: 40px; font-size: 20px; }
}
</style>
</head>
<body>
<div class="fundo"></div>

<div class="container">
    <a href="/hub" class="voltar">← Voltar para o Hub</a>

    <div class="hero">
        <div class="badge">Em Desenvolvimento</div>
        <div class="icone-hero">🧠</div>
        <h1>Consultoria Empresarial com IA</h1>
        <p class="sub">
            Não é um chatbot. É um <span class="destaque">consultor que acessa seu negócio inteiro</span> 
            e te ajuda a descobrir onde está o gargalo real.
        </p>
    </div>

    <div class="cards">
        <div class="card">
            <div class="card-icone">🎯</div>
            <div class="card-texto">
                <div class="card-titulo">Diagnóstico com base em dados reais</div>
                <div class="card-desc">
                    A IA lê seus leads, clientes, conversas, follow-ups e financeiro — 
                    e diagnostica o gargalo com base no que está acontecendo de verdade, 
                    não em suposição.
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-icone">📊</div>
            <div class="card-texto">
                <div class="card-titulo">Cálculos de negócio de verdade</div>
                <div class="card-desc">
                    Faturamento, margem, ticket médio, taxa de conversão, CAC, LTV, 
                    projeções. A IA calcula o impacto financeiro de cada decisão antes 
                    de você tomar.
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-icone">🧭</div>
            <div class="card-texto">
                <div class="card-titulo">Plano de ação priorizado</div>
                <div class="card-desc">
                    Não te dá 20 tarefas. Te dá as 3 que realmente importam — ordenadas 
                    por impacto, urgência e viabilidade pra sua realidade.
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-icone">📈</div>
            <div class="card-texto">
                <div class="card-titulo">Acompanhamento contínuo</div>
                <div class="card-desc">
                    Semana a semana a IA compara resultados, identifica variações, 
                    investiga causas e ajusta a rota. Consultoria que continua depois 
                    da primeira conversa.
                </div>
            </div>
        </div>
    </div>

    <div class="rodape">
        <div class="rodape-titulo">Estamos construindo algo grande</div>
        <div class="rodape-desc">
            A Consultoria Empresarial com IA está em <strong>fase final de desenvolvimento</strong>. 
            Enquanto isso, você já pode usar o <strong>Atendimento com IA</strong> para vender mais 
            e organizar seus leads.
        </div>
        <a href="/clientes" class="btn-whats">Usar Atendimento com IA agora →</a>
        <br>
        <a href="/hub" class="btn-voltar-hub">Voltar para o Hub</a>
    </div>
</div>

<script>
// Admin: se for admin, redireciona pro chat real
fetch('/api/eh-admin')
    .then(r => r.json())
    .then(j => {
        if (j.admin) {
            window.location.href = '/consultoria';
        }
    })
    .catch(() => {});
</script>
</body>
</html>"""


def registrar_em_breve(app, Cookie):
    """Registra a rota /consultoria-premium (a que o cliente ve)."""
    
    @app.get("/consultoria-premium", response_class=HTMLResponse)
    def consultoria_premium():
        return HTMLResponse(HTML)
