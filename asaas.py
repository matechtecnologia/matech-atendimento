import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIGURAÇÃO ==========
# Sandbox: https://api-sandbox.asaas.com/v3
# Produção: https://api.asaas.com/v3
ASAAS_URL = os.getenv("ASAAS_URL", "https://api-sandbox.asaas.com/v3")
ASAAS_API_KEY = os.getenv("ASAAS_API_KEY", "")

def _headers():
    return {
        "Content-Type": "application/json",
        "User-Agent": "M.A Tech",
        "access_token": ASAAS_API_KEY
    }

def criar_cliente(nome, email, cpf_cnpj):
    """Cria um cliente no Asaas. Retorna o ID ou None."""
    url = f"{ASAAS_URL}/customers"
    payload = {
        "name": nome,
        "email": email,
        "cpfCnpj": cpf_cnpj
    }
    try:
        r = requests.post(url, json=payload, headers=_headers(), timeout=15)
        if r.status_code == 200:
            return r.json().get("id")
        print(f"ERRO criar_cliente: {r.status_code} - {r.text}")
        return None
    except Exception as e:
        print(f"ERRO criar_cliente: {e}")
        return None

def criar_cobranca_pix(customer_id, valor, descricao, vencimento):
    """Cria uma cobrança PIX. Retorna o ID da cobrança ou None."""
    url = f"{ASAAS_URL}/payments"
    payload = {
        "customer": customer_id,
        "billingType": "PIX",
        "value": valor,
        "dueDate": vencimento,
        "description": descricao
    }
    try:
        r = requests.post(url, json=payload, headers=_headers(), timeout=15)
        if r.status_code == 200:
            return r.json().get("id")
        print(f"ERRO criar_cobranca: {r.status_code} - {r.text}")
        return None
    except Exception as e:
        print(f"ERRO criar_cobranca: {e}")
        return None

def obter_qr_code(payment_id):
    """Retorna os dados do QR Code PIX."""
    url = f"{ASAAS_URL}/payments/{payment_id}/pixQrCode"
    try:
        r = requests.get(url, headers=_headers(), timeout=15)
        if r.status_code == 200:
            return r.json()
        print(f"ERRO obter_qr_code: {r.status_code} - {r.text}")
        return None
    except Exception as e:
        print(f"ERRO obter_qr_code: {e}")
        return None

def consultar_pagamento(payment_id):
    """Consulta o status de um pagamento."""
    url = f"{ASAAS_URL}/payments/{payment_id}"
    try:
        r = requests.get(url, headers=_headers(), timeout=15)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None