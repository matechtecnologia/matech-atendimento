# ============================================
# M.A Tech - IA de Agenda (regras)
# ============================================
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime, timedelta, time


def _conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


# ---------------- SUGESTAO 1: HORARIO LIVRE ----------------

def sugerir_horarios_livres(uid, dias_frente=7, min_horas=2):
    """Procura janelas de >= min_horas livres nos proximos dias (horario comercial 8-20h)."""
    hoje = date.today()
    sugestoes = []
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for i in range(1, dias_frente + 1):
                d = hoje + timedelta(days=i)
                cur.execute("""
                    SELECT hora_inicio, hora_fim FROM gestao_tempo_compromissos
                     WHERE usuario_id=%s AND data=%s AND hora_inicio IS NOT NULL AND hora_fim IS NOT NULL
                     ORDER BY hora_inicio
                """, (uid, d))
                ocupados = cur.fetchall()
                # monta lista de gaps no horario 8h-20h
                blocos = [(time(8,0), time(20,0))]
                for o in ocupados:
                    ini_o, fim_o = o["hora_inicio"], o["hora_fim"]
                    novos = []
                    for ini_b, fim_b in blocos:
                        if fim_o <= ini_b or ini_o >= fim_b:
                            novos.append((ini_b, fim_b))
                        else:
                            if ini_o > ini_b:
                                novos.append((ini_b, ini_o))
                            if fim_o < fim_b:
                                novos.append((fim_o, fim_b))
                    blocos = novos
                # pega gaps >= min_horas
                for ini_b, fim_b in blocos:
                    delta_h = (datetime.combine(d, fim_b) - datetime.combine(d, ini_b)).total_seconds() / 3600
                    if delta_h >= min_horas:
                        sugestoes.append({
                            "tipo": "horario_livre",
                            "data": d.isoformat(),
                            "hora_inicio": ini_b.strftime("%H:%M"),
                            "hora_fim": fim_b.strftime("%H:%M"),
                            "horas": round(delta_h, 1),
                            "mensagem": f"Voce tem {delta_h:.1f}h livres em {d.strftime('%d/%m')} das {ini_b.strftime('%H:%M')} as {fim_b.strftime('%H:%M')}. Quer agendar algo?"
                        })
                        break  # so 1 por dia, evita poluir
                if len(sugestoes) >= 3:
                    break
    return sugestoes


# ---------------- SUGESTAO 2: DETECCAO DE PADROES ----------------

def detectar_padroes(uid, min_ocorrencias=3, dias_analise=60):
    """Detecta compromissos com mesmo titulo+hora que aparecem em >= min_ocorrencias semanas diferentes."""
    hoje = date.today()
    ini = hoje - timedelta(days=dias_analise)
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT LOWER(titulo) AS tit, EXTRACT(DOW FROM data) AS dow, hora_inicio,
                       COUNT(DISTINCT data) AS ocorrencias
                  FROM gestao_tempo_compromissos
                 WHERE usuario_id=%s AND data BETWEEN %s AND %s
                   AND hora_inicio IS NOT NULL
                 GROUP BY LOWER(titulo), EXTRACT(DOW FROM data), hora_inicio
                HAVING COUNT(DISTINCT data) >= %s
                 ORDER BY ocorrencias DESC
                 LIMIT 5
            """, (uid, ini, hoje, min_ocorrencias))
            padroes = cur.fetchall()
            # filtra os que ja tem rotina cadastrada
            cur.execute("SELECT LOWER(titulo) AS tit, dia_semana, hora_inicio FROM gestao_tempo_rotinas WHERE usuario_id=%s", (uid,))
            rotinas = {(r["tit"], int(r["dia_semana"]), r["hora_inicio"].strftime("%H:%M") if r["hora_inicio"] else None) for r in cur.fetchall()}
    dias_nome = ["Domingo", "Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado"]
    sugestoes = []
    for p in padroes:
        chave = (p["tit"], int(p["dow"]), p["hora_inicio"].strftime("%H:%M"))
        if chave in rotinas:
            continue  # ja existe rotina
        sugestoes.append({
            "tipo": "padrao",
            "titulo": p["tit"].title(),
            "dia_semana": int(p["dow"]),
            "hora_inicio": p["hora_inicio"].strftime("%H:%M"),
            "ocorrencias": p["ocorrencias"],
            "mensagem": f"Voce fez '{p['tit'].title()}' {p['ocorrencias']}x em {dias_nome[int(p['dow'])]}s as {p['hora_inicio'].strftime('%H:%M')}. Criar rotina?"
        })
    return sugestoes


# ---------------- SUGESTAO 3: ALERTA DE SOBRECARGA ----------------

def detectar_sobrecarga(uid, dias_frente=3, min_compromissos=5, min_alta=3):
    """Avisa se algum dia proximo tem muitos compromissos ou muitos de prioridade alta."""
    hoje = date.today()
    sugestoes = []
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for i in range(0, dias_frente):
                d = hoje + timedelta(days=i)
                cur.execute("""
                    SELECT COUNT(*) AS total,
                           COUNT(*) FILTER (WHERE prioridade='alta') AS altas
                      FROM gestao_tempo_compromissos
                     WHERE usuario_id=%s AND data=%s AND concluido=FALSE
                """, (uid, d))
                r = cur.fetchone()
                if r["total"] >= min_compromissos or r["altas"] >= min_alta:
                    sugestoes.append({
                        "tipo": "sobrecarga",
                        "data": d.isoformat(),
                        "total": int(r["total"]),
                        "altas": int(r["altas"]),
                        "mensagem": f"{d.strftime('%d/%m')}: {r['total']} compromissos ({r['altas']} de prioridade alta). Quer remarcar algum?"
                    })
    return sugestoes


# ---------------- SUGESTAO 4: SUGESTAO DE FOCO ----------------

def sugerir_foco(uid, dias_frente=7, min_horas=3):
    """Sugere bloquear um periodo livre >= min_horas como foco."""
    livres = sugerir_horarios_livres(uid, dias_frente=dias_frente, min_horas=min_horas)
    sugestoes = []
    for s in livres[:2]:  # so 2
        sugestoes.append({
            "tipo": "foco",
            "data": s["data"],
            "hora_inicio": s["hora_inicio"],
            "hora_fim": s["hora_fim"],
            "horas": s["horas"],
            "mensagem": f"Que tal bloquear {s['hora_inicio']}-{s['hora_fim']} em {s['data'][8:10]}/{s['data'][5:7]} pra foco?"
        })
    return sugestoes


# ---------------- CONSOLIDADO ----------------

def gerar_sugestoes(uid):
    """Retorna lista consolidada (max 5) de todas as funcoes."""
    sugestoes = []
    try:
        sugestoes.extend(detectar_sobrecarga(uid))
    except Exception: pass
    try:
        sugestoes.extend(detectar_padroes(uid))
    except Exception: pass
    try:
        sugestoes.extend(sugerir_foco(uid))
    except Exception: pass
    try:
        sugestoes.extend(sugerir_horarios_livres(uid))
    except Exception: pass
    # ordena por tipo de urgencia
    ordem = {"sobrecarga": 0, "padrao": 1, "foco": 2, "horario_livre": 3}
    sugestoes.sort(key=lambda s: ordem.get(s["tipo"], 99))
    return sugestoes[:5]
