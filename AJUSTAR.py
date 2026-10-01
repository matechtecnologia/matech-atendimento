import io
import os
import re

# ============================================
# 1. DESFAZ o "esconder menu mobile"
# ============================================
path_css = 'static/app-mobile.css'
with io.open(path_css, 'r', encoding='utf-8') as f:
    css = f.read()

# Remove o bloco "esconder-menu-mobile"
padrao = re.compile(r'/\*\s*=+\s*ESCONDE MENU DO TOPO NO MOBILE.*?(?=/\*|\Z)', re.DOTALL)
css = padrao.sub('', css)

with io.open(path_css, 'w', encoding='utf-8') as f:
    f.write(css)
print("OK: bloco 'esconder menu mobile' removido")

# ============================================
# 2. REMOVE os 4 links do drawer
# ============================================
path_js = 'static/app-mobile.js'
with io.open(path_js, 'r', encoding='utf-8') as f:
    js = f.read()

# Procura o array "links = [" e remove as linhas dos 4 links
antigo = """        const links = [
            { href: '/clientes', rota: '/clientes', icone: 'clientes', texto: 'Clientes' },
            { href: '/followups', rota: '/followups', icone: 'followups', texto: 'Follow-ups', badge: total },
            { href: '/relatorios', rota: '/relatorios', icone: 'relatorios', texto: 'Relatórios' },
            { href: '/meus_nichos', rota: '/meus_nichos', icone: 'nichos', texto: 'Meus Nichos' },
            { href: '/planos', rota: '/planos', icone: 'planos', texto: 'Planos' },
            { href: '/indicar', rota: '/indicar', icone: 'indicar', texto: 'Indique e ganhe' },
            { href: '/configuracoes', rota: '/configuracoes', icone: 'configuracoes', texto: 'Configurações' },
        ];"""

novo = """        const links = [
            { href: '/planos', rota: '/planos', icone: 'planos', texto: 'Planos' },
            { href: '/indicar', rota: '/indicar', icone: 'indicar', texto: 'Indique e ganhe' },
            { href: '/configuracoes', rota: '/configuracoes', icone: 'configuracoes', texto: 'Configurações' },
        ];"""

if antigo in js:
    js = js.replace(antigo, novo, 1)
    with io.open(path_js, 'w', encoding='utf-8') as f:
        f.write(js)
    print("OK: 4 links removidos do drawer")
else:
    print("AVISO: padrao do drawer nao bateu")
    # Tenta variacao (com ou sem emoji)
    antigo2 = """        const links = [
            { href: '/clientes', rota: '/clientes', icone: 'clientes', texto: 'Clientes' },"""
    if antigo2 in js:
        # Remove linha por linha
        for rota in ['/clientes', '/followups', '/relatorios', '/meus_nichos']:
            js = re.sub(r'\s*\{ href: \'' + re.escape(rota) + r'\'[^\n]*\},\n?', '\n', js)
        with io.open(path_js, 'w', encoding='utf-8') as f:
            f.write(js)
        print("OK: links removidos (metodo alternativo)")

# ============================================
# 3. Regerar app.min.css e app.min.js
# ============================================
css_ordem = ['style.css', 'app-mobile.css', 'tema.css', 'splash.css']
css_final = '/* M.A Tech */\n\n'
for nome in css_ordem:
    p = os.path.join('static', nome)
    if not os.path.exists(p): continue
    with io.open(p, 'r', encoding='utf-8') as f:
        css_final += '\n/* ===== ' + nome + ' ===== */\n'
        css_final += f.read()
        css_final += '\n'
with io.open('static/app.min.css', 'w', encoding='utf-8') as f:
    f.write(css_final)
print(f"OK: app.min.css regenerado")

js_ordem = ['app.js', 'icons.js', 'app-mobile.js', 'app-bottom-nav.js', 'help.js', 'app-ux.js', 'app-roleta.js']
js_final = '/* M.A Tech */\n\n'
for nome in js_ordem:
    p = os.path.join('static', nome)
    if not os.path.exists(p): continue
    with io.open(p, 'r', encoding='utf-8') as f:
        js_final += '\n/* ===== ' + nome + ' ===== */\n'
        js_final += f.read()
        js_final += '\n;\n'
with io.open('static/app.min.js', 'w', encoding='utf-8') as f:
    f.write(js_final)
print(f"OK: app.min.js regenerado")

print("\n=== PRONTO ===")