import io, os

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
print(f"OK: {os.path.getsize('static/app.min.js')/1024:.1f} KB")