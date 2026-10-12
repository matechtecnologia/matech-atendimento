# limites_mensais.py
# Logica de planos, limites mensais, excedente e desconto do 1o mes.

# Estrutura dos planos
PLANOS = {
    "gratis": {
        "nome": "Grátis",
        "preco": 0,
        "preco_primeiro_mes": 0,
        "interacoes_mes": 150,
        "sugestao": "1 conversa/dia",
    },
    "basico": {
        "nome": "Básico",
        "preco": 97,
        "preco_primeiro_mes": 47,
        "interacoes_mes": 1500,
        "sugestao": "10 conversas/dia",
    },
    "pro": {
        "nome": "Pro",
        "preco": 297,
        "preco_primeiro_mes": 147,
        "interacoes_mes": 4500,
        "sugestao": "30 conversas/dia",
    },
    "empresarial": {
        "nome": "Empresarial",
        "preco": 597,
        "preco_primeiro_mes": 297,
        "interacoes_mes": 9000,
        "sugestao": "60 conversas/dia",
    },
    "admin": {
        "nome": "Admin",
        "preco": 0,
        "preco_primeiro_mes": 0,
        "interacoes_mes": 999999,
        "sugestao": "ilimitado",
    },
}

# Preco do excedente (por interacao extra)
PRECO_EXCEDENTE = 0.10  # R$ 0,10 por interacao

# Percentuais de aviso e bloqueio
AVISO_PERCENTUAL = 1.0    # 100% = avisa
BLOQUEIO_PERCENTUAL = 1.2 # 120% = bloqueia


def get_plano(nome):
    """Retorna dados do plano. Default: gratis."""
    return PLANOS.get((nome or "gratis").lower(), PLANOS["gratis"])


def get_limite_mensal(nome):
    """Retorna o limite de interacoes do mes."""
    return get_plano(nome)["interacoes_mes"]


def get_preco(nome, primeiro_mes=False):
    """Retorna o preco do plano. Se primeiro_mes, aplica desconto."""
    p = get_plano(nome)
    return p["preco_primeiro_mes"] if primeiro_mes else p["preco"]


def get_mes_atual():
    """Retorna o mes atual no formato YYYY-MM."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m")


def get_uso_mensal(vendedor_id, get_conn, close_conn):
    """Retorna (interacoes_usadas, interacoes_extras) do mes."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(interacoes, 0), COALESCE(interacoes_extras, 0)
            FROM uso_mensal
            WHERE vendedor_id = %s AND mes_ano = %s
        """, (vendedor_id, get_mes_atual()))
        r = cur.fetchone()
        cur.close()
        close_conn(conn)
        return (int(r[0]), int(r[1])) if r else (0, 0)
    except Exception as e:
        print(f"limites_mensais: erro get_uso_mensal - {e}")
        try: close_conn(conn)
        except: pass
        return (0, 0)


def incrementar_uso(vendedor_id, get_conn, close_conn):
    """Aumenta 1 interacao no mes."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO uso_mensal (vendedor_id, mes_ano, interacoes)
            VALUES (%s, %s, 1)
            ON CONFLICT (vendedor_id, mes_ano)
            DO UPDATE SET 
                interacoes = uso_mensal.interacoes + 1,
                atualizado_em = NOW()
        """, (vendedor_id, get_mes_atual()))
        conn.commit()
        cur.close()
        close_conn(conn)
        return True
    except Exception as e:
        print(f"limites_mensais: erro incrementar_uso - {e}")
        try: close_conn(conn)
        except: pass
        return False


def verificar_limite(vendedor_id, plano, get_conn, close_conn):
    """Retorna dict com status do limite.
    
    {
      "permitido": bool,
      "usado": int,
      "limite": int,
      "excedente": int,
      "aviso": bool,
      "bloqueado": bool,
      "percentual": int,
      "mensagem": str
    }
    """
    usado, extras = get_uso_mensal(vendedor_id, get_conn, close_conn)
    limite = get_limite_mensal(plano)
    
    percentual = int((usado / limite * 100)) if limite else 0
    
    aviso = usado >= (limite * AVISO_PERCENTUAL)
    bloqueado = usado >= (limite * BLOQUEIO_PERCENTUAL)
    excedente = max(0, usado - limite)
    
    permitido = not bloqueado
    
    msg = ""
    if bloqueado:
        msg = f"Você atingiu 120% do limite ({usado}/{limite}). Faça upgrade ou compre interações extras."
    elif aviso:
        msg = f"Você está em {percentual}% do limite ({usado}/{limite}). Considere upgrade."
    
    return {
        "permitido": permitido,
        "usado": usado,
        "extras": extras,
        "limite": limite,
        "excedente": excedente,
        "aviso": aviso,
        "bloqueado": bloqueado,
        "percentual": percentual,
        "mensagem": msg,
    }


def calcular_custo_excedente(excedente):
    """Calcula custo do excedente."""
    return round(excedente * PRECO_EXCEDENTE, 2)


def e_primeiro_mes(vendedor_id, get_conn, close_conn):
    """Retorna True se este cliente nunca foi cobrado."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT 1 FROM primeira_cobranca WHERE vendedor_id = %s
        """, (vendedor_id,))
        r = cur.fetchone()
        cur.close()
        close_conn(conn)
        return r is None
    except Exception as e:
        print(f"limites_mensais: erro e_primeiro_mes - {e}")
        try: close_conn(conn)
        except: pass
        return False


def registrar_primeira_cobranca(vendedor_id, plano, valor, get_conn, close_conn):
    """Marca que o cliente foi cobrado pela 1a vez."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO primeira_cobranca (vendedor_id, plano, valor_cobrado)
            VALUES (%s, %s, %s)
            ON CONFLICT (vendedor_id) DO NOTHING
        """, (vendedor_id, plano, valor))
        conn.commit()
        cur.close()
        close_conn(conn)
        return True
    except Exception as e:
        print(f"limites_mensais: erro registrar_primeira - {e}")
        try: close_conn(conn)
        except: pass
        return False
