import json
import os

usuarios = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== PASTA DOS DADOS =====
PASTA_DADOS = os.path.join(BASE_DIR, "Dados_User")


ARQUIVO = os.path.join(
    PASTA_DADOS,
    "usuarios.json"
)

# ===== CARREGAR USUÁRIOS =====
def carregar_usuarios():
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except:
        return []

# ===== SALVAR USUÁRIOS =====
def salvar_usuarios(usuarios):
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, indent=4)