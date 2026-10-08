import app
from consultor_rotas import _get_plano, _uso_hoje

plano = _get_plano(3, app.get_conn, app.close_conn)
usado = _uso_hoje(3, app.get_conn, app.close_conn)
print(f"Plano: {plano}")
print(f"Usado hoje: {usado}")
