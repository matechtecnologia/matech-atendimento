from fastapi.responses import HTMLResponse

HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Preparando Consultoria - M.A Tech</title>
<link rel="stylesheet" href="/static/app.min.css?v=310935">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background: #0a0a0a; color: #e8e8e8;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
    padding: 24px;
}
.loading-box {
    max-width: 420px; width: 100%; text-align: center;
}
.loading-avatar {
    width: 96px; height: 96px; border-radius: 50%;
    background: linear-gradient(135deg, #7c3aed 0%, #00d97e 100%);
    margin: 0 auto 24px;
    display: flex; align-items: center; justify-content: center;
    font-size: 44px;
    box-shadow: 0 0 0 4px rgba(124,58,237,0.15), 0 0 40px rgba(124,58,237,0.4);
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); box-shadow: 0 0 0 4px rgba(124,58,237,0.15), 0 0 40px rgba(124,58,237,0.4); }
    50% { transform: scale(1.05); box-shadow: 0 0 0 8px rgba(124,58,237,0.1), 0 0 60px rgba(124,58,237,0.6); }
}
h1 {
    font-size: 20px; font-weight: 700; color: #fff;
    margin-bottom: 8px; letter-spacing: -0.02em;
}
.sub {
    font-size: 14px; color: #8a8a8a; margin-bottom: 32px;
}
.frases {
    display: flex; flex-direction: column; gap: 10px;
    margin-bottom: 32px;
}
.frase {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px;
    background: #141414; border: 1px solid #1a1a1a;
    border-radius: 10px;
    font-size: 13px; color: #8a8a8a;
    opacity: 0; transform: translateY(8px);
    transition: all 0.4s ease;
    text-align: left;
}
.frase.ativa {
    opacity: 1; transform: translateY(0);
    border-color: #7c3aed55;
    color: #e8e8e8;
    background: #1a1620;
}
.frase.ok {
    opacity: 1; transform: translateY(0);
    border-color: #00d97e55;
    color: #00d97e;
    background: #0f1a15;
}
.frase .icon {
    width: 20px; height: 20px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
}
.frase.ok .icon { color: #00d97e; }
.frase.ativa .icon {
    border: 2px solid #7c3aed55;
    border-top-color: #7c3aed;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.aviso {
    font-size: 12px; color: #5a5a5a;
    padding: 12px;
    border-top: 1px solid #1a1a1a;
}
</style>
</head>
<body>
<div class="loading-box">
    <div class="loading-avatar">🤖</div>
    <h1>Preparando sua consultoria</h1>
    <p class="sub">Aguarde enquanto analiso seu negocio...</p>

    <div class="frases">
        <div class="frase" id="f1"><div class="icon">○</div> Lendo seus nichos configurados</div>
        <div class="frase" id="f2"><div class="icon">○</div> Analisando seus clientes</div>
        <div class="frase" id="f3"><div class="icon">○</div> Verificando historico de conversas</div>
        <div class="frase" id="f4"><div class="icon">○</div> Checando follow-ups pendentes</div>
        <div class="frase" id="f5"><div class="icon">○</div> Calculando uso da IA</div>
    </div>

    <div class="aviso">Isso leva apenas alguns segundos</div>
</div>

<script>
const etapas = ["f1","f2","f3","f4","f5"];
let i = 0;

function proxima() {
    if (i < etapas.length) {
        const el = document.getElementById(etapas[i]);
        el.className = "frase ativa";
        setTimeout(() => {
            el.className = "frase ok";
            el.querySelector(".icon").textContent = "✓";
            i++;
            proxima();
        }, 600);
    } else {
        // Tudo pronto - redireciona pro chat
        setTimeout(() => {
            window.location.href = "/consultoria";
        }, 400);
    }
}

setTimeout(proxima, 300);
</script>
</body>
</html>"""


def registrar_loading(app, Cookie):
    @app.get("/consultoria/loading", response_class=HTMLResponse)
    def consultoria_loading():
        return HTMLResponse(HTML)
