import os
import sys
import json
import requests
from datetime import datetime

# ===== CONFIG =====
URL_PRODUCAO = "https://matech-novo.onrender.com/admin/backup"
URL_LOCAL = "http://127.0.0.1:8000/admin/backup"
TOKEN = "matech-backup-2026"
PASTA_BACKUPS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")


def baixar(url):
    try:
        r = requests.get(f"{url}?token={TOKEN}", timeout=60)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code}: {r.text[:200]}")
            return None
        return r.json()
    except Exception as e:
        print(f"  Erro: {e}")
        return None


def salvar(dados, sufixo=""):
    if not os.path.exists(PASTA_BACKUPS):
        os.makedirs(PASTA_BACKUPS)

    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome = f"backup_{agora}{sufixo}.json"
    caminho = os.path.join(PASTA_BACKUPS, nome)

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    tamanho = os.path.getsize(caminho) / 1024
    print(f"  Salvo: {nome} ({tamanho:.1f} KB)")
    return caminho


def limpar_antigos(dias=30):
    """Remove backups mais antigos que X dias."""
    if not os.path.exists(PASTA_BACKUPS):
        return
    agora = datetime.now()
    removidos = 0
    for nome in os.listdir(PASTA_BACKUPS):
        if not nome.startswith("backup_") or not nome.endswith(".json"):
            continue
        caminho = os.path.join(PASTA_BACKUPS, nome)
        mtime = datetime.fromtimestamp(os.path.getmtime(caminho))
        if (agora - mtime).days > dias:
            os.remove(caminho)
            removidos += 1
    if removidos > 0:
        print(f"  Removidos: {removidos} backup(s) antigo(s)")


def main():
    print(f"=== Backup M.A Tech — {datetime.now().strftime('%d/%m/%Y %H:%M')} ===")

    # Tenta produção primeiro
    print("Tentando produção...")
    dados = baixar(URL_PRODUCAO)

    # Se falhar, tenta local
    if not dados:
        print("Produção falhou. Tentando local...")
        dados = baixar(URL_LOCAL)

    if not dados:
        print("ERRO: não conseguiu baixar de nenhum lugar")
        sys.exit(1)

    # Verifica se tem tabelas
    if not dados.get("tabelas"):
        print("ERRO: backup vazio ou inválido")
        sys.exit(1)

    # Salva
    print("Salvando...")
    salvar(dados)

    # Contadores
    print("\nResumo:")
    for tabela, linhas in dados.get("tabelas", {}).items():
        if isinstance(linhas, list):
            print(f"  {tabela}: {len(linhas)} registro(s)")
        else:
            print(f"  {tabela}: ERRO — {linhas}")

    # Limpa antigos
    print("\nLimpando backups > 30 dias...")
    limpar_antigos(30)

    print("\nOK: backup concluído com sucesso")


if __name__ == "__main__":
    main()