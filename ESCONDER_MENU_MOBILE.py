import io

path = 'static/app-mobile.css'
with io.open(path, 'r', encoding='utf-8') as f:
    c = f.read()

if 'esconder-menu-mobile' in c:
    print("JA TEM")
    exit()

extra = '''

/* ===== ESCONDE MENU DO TOPO NO MOBILE (ja tem drawer + bottom nav) ===== */
@media (max-width: 768px) {
    .usuario-info {
        display: none !important;
    }
    .topo {
        justify-content: center !important;
    }
    .topo h1 {
        margin: 0 auto;
    }
}
'''

c = c + extra

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print("OK: menu topo escondido no mobile")

# Regerar app.min.css
import os
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

print(f"OK: app.min.css regenerado ({os.path.getsize('static/app.min.css')/1024:.1f} KB)")