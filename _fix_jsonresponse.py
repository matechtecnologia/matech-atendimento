with open("app.py", "r", encoding="utf-8") as f:
    c = f.read()

# Verifica se ja tem o import
if "from fastapi.responses import" not in c:
    print("Nao tem import de fastapi.responses")
    # Procura onde adicionar
    if "from fastapi import" in c:
        c = c.replace(
            "from fastapi import",
            "from fastapi.responses import JSONResponse\nfrom fastapi import",
            1
        )
        print("Adicionado antes de 'from fastapi import'")
else:
    # Ja tem, adiciona JSONResponse
    import re
    m = re.search(r"from fastapi\.responses import ([^\n]+)", c)
    if m:
        imports_atuais = m.group(1)
        if "JSONResponse" not in imports_atuais:
            novo_import = imports_atuais.strip() + ", JSONResponse"
            c = c.replace(
                f"from fastapi.responses import {imports_atuais}",
                f"from fastapi.responses import {novo_import}",
                1
            )
            print(f"Adicionado JSONResponse em: from fastapi.responses import {novo_import}")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
