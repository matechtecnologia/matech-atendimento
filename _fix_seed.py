with open("plano_estrategico.py", "r", encoding="utf-8") as f:
    c = f.read()

# Se ja tem QUALQUER fase, pula o seed de fases
c = c.replace(
    'cur.execute("SELECT COUNT(*) FROM roadmap_phases")\n        if cur.fetchone()[0] == 0:',
    'cur.execute("SELECT COUNT(*) FROM roadmap_phases")\n        if False:  # desativado: ja tem fases populadas'
)

with open("plano_estrategico.py", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - seed de fases desativado")
