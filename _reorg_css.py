with open("plano_ui.py", "r", encoding="utf-8") as f:
    c = f.read()

css_novo = '''
.grupo { display:flex; gap:6px; align-items:center; padding:2px 8px; border-right:1px solid #2a2a2a; }
.grupo:last-child { border-right:none; }
.grupo-label { color:#5a5a5a; font-size:9px; font-weight:700; letter-spacing:1px; margin-right:4px; text-transform:uppercase; }
'''

if ".grupo-label" not in c:
    c = c.replace(".menu a:hover, .menu a.ativo", css_novo + "\n.menu a:hover, .menu a.ativo")
    with open("plano_ui.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - CSS adicionado")
else:
    print("ja tem")
