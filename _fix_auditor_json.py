with open("auditor_ia.py", "r", encoding="utf-8") as f:
    c = f.read()

# Escapa as chaves do JSON de exemplo (duplica { e })
c = c.replace(
    '''Formato exato:
{"inventou": true ou false, "campo": "endereco", "o_que_a_ia_disse": "...", "pergunta_pro_vendedor": "..."}

Se NAO inventou nada:
{"inventou": false, "campo": "", "o_que_a_ia_disse": "", "pergunta_pro_vendedor": ""}''',
    '''Formato exato:
{{"inventou": true ou false, "campo": "endereco", "o_que_a_ia_disse": "...", "pergunta_pro_vendedor": "..."}}

Se NAO inventou nada:
{{"inventou": false, "campo": "", "o_que_a_ia_disse": "", "pergunta_pro_vendedor": ""}}'''
)

with open("auditor_ia.py", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - chaves escapadas")
