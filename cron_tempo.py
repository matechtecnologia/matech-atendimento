# ============================================
# M.A Tech - Cron do Tempo (loop local)
# ============================================
import os
import time
from dotenv import load_dotenv

load_dotenv()
from gestao_tempo_notif import verificar_e_enviar

INTERVALO = 60  # segundos

print("Cron do Tempo iniciado. Rodando a cada", INTERVALO, "segundos.")
print("Ctrl+C para parar.\n")

while True:
    try:
        r = verificar_e_enviar()
        print(f"[{r.get('momento','?')}] criadas={r.get('criadas',0)}")
    except Exception as e:
        print("Erro:", e)
    time.sleep(INTERVALO)
