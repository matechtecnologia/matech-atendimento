with open("gemini.py", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace('MODELO = "gemini-2.5-flash-lite"', 'MODELO = "gemini-3.5-flash-lite"')

with open("gemini.py", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - modelo trocado para gemini-3.5-flash-lite")
