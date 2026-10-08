// loading_global.js v3
// Mostra loading SO nas telas do cliente final (nao no admin/plano)

(function() {
    // Paginas que NAO tem loading (admin)
    const EXCLUIR = ["/plano", "/admin", "/planos", "/configuracoes"];

    const path = window.location.pathname;
    for (const ex of EXCLUIR) {
        if (path === ex || path.startsWith(ex + "/")) return;
    }

    const CSS = `
    #global-loading {
        position: fixed; inset: 0;
        background: #0a0a0a;
        display: none;
        align-items: center; justify-content: center;
        z-index: 999999;
        opacity: 0;
        transition: opacity 0.15s;
    }
    #global-loading.ativo { opacity: 1; }
    #global-loading .box { max-width: 380px; width: 100%; text-align: center; padding: 24px; }
    #global-loading .avatar {
        width: 72px; height: 72px; border-radius: 50%;
        background: linear-gradient(135deg, #7c3aed 0%, #00d97e 100%);
        margin: 0 auto 20px;
        display: flex; align-items: center; justify-content: center;
        font-size: 32px;
        box-shadow: 0 0 0 4px rgba(124,58,237,0.15), 0 0 32px rgba(124,58,237,0.4);
        animation: gl-pulse 1.5s ease-in-out infinite;
    }
    @keyframes gl-pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.08); } }
    #global-loading h2 { color: #fff; font-size: 16px; margin: 0 0 6px; font-weight: 700; letter-spacing: -0.02em; }
    #global-loading p { color: #8a8a8a; font-size: 13px; margin: 0; }
    #global-loading .barra { width: 100%; height: 3px; background: #1a1a1a; border-radius: 2px; overflow: hidden; margin-top: 20px; }
    #global-loading .barra-i {
        height: 100%; width: 30%;
        background: linear-gradient(90deg, #7c3aed, #00d97e);
        animation: gl-barra 1.2s ease-in-out infinite; border-radius: 2px;
    }
    @keyframes gl-barra { 0% { transform: translateX(-100%); } 100% { transform: translateX(400%); } }
    `;

    const style = document.createElement("style");
    style.textContent = CSS;
    document.head.appendChild(style);

    const div = document.createElement("div");
    div.id = "global-loading";
    div.innerHTML = `
        <div class="box">
            <div class="avatar">🤖</div>
            <h2>M.A Tech</h2>
            <p>Carregando...</p>
            <div class="barra"><div class="barra-i"></div></div>
        </div>
    `;
    document.body.appendChild(div);

    function mostrar() {
        const el = document.getElementById("global-loading");
        if (!el) return;
        el.style.display = "flex";
        requestAnimationFrame(() => el.classList.add("ativo"));
    }

    function esconder() {
        const el = document.getElementById("global-loading");
        if (!el) return;
        el.classList.remove("ativo");
        setTimeout(() => { el.style.display = "none"; }, 150);
    }

    document.addEventListener("click", function(e) {
        const link = e.target.closest("a");
        if (!link) return;
        const href = link.getAttribute("href");
        if (!href) return;
        if (href.startsWith("http") && !href.includes(location.hostname)) return;
        if (link.target === "_blank") return;
        if (href.startsWith("#")) return;
        if (href.startsWith("javascript:")) return;
        if (href.startsWith("mailto:") || href.startsWith("tel:")) return;
        if (link.hasAttribute("download")) return;

        // Ignora links pro admin
        const nextPath = href.split("?")[0];
        for (const ex of EXCLUIR) {
            if (nextPath === ex || nextPath.startsWith(ex + "/")) return;
        }

        setTimeout(mostrar, 200);
    });

    window.addEventListener("pageshow", esconder);
    window.addEventListener("load", esconder);
    window.addEventListener("popstate", esconder);
})();
