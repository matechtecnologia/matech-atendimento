import app

# Registra a rota de loading
try:
    import consultor_loading
    consultor_loading.registrar_loading(app.app, app.Cookie)
    print("OK - rota /consultoria/loading registrada")
except Exception as e:
    print(f"ERRO: {e}")

# Confirma
print([r.path for r in app.app.routes if "loading" in r.path])
