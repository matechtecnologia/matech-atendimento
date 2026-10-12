with open("templates/planos.html", "r", encoding="utf-8") as f:
    c = f.read()

# Volta o campo valor no formulario do Basico
c = c.replace(
    '''<input type="hidden" name="plano" value="basico">
                    <button type="submit" class="btn-gerar" style="margin-top:0;">ASSINAR</button>''',
    '''<input type="hidden" name="plano" value="basico">
                    <input type="hidden" name="valor" value="97.00">
                    <button type="submit" class="btn-gerar" style="margin-top:0;">ASSINAR</button>'''
)

with open("templates/planos.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - campo valor restaurado no Basico")
