import json
import os

usuarios = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== PASTA DOS DADOS =====
PASTA_DADOS = os.path.join(BASE_DIR, "Dados_User")


ARQUIVO = os.path.join(PASTA_DADOS, "usuarios.json")


# ===== CARREGAR USUÁRIOS =====
def carregar_usuarios():
    # carrega e retorna os usuários cadastrados no arquivo JSON, caso o arquivo não exista, retorna uma lista vazia
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except:
        return []


# ===== SALVAR USUÁRIOS =====
def salvar_usuarios(usuarios):
    # salva a lista de usuários no arquivo JSON, sobrescrevendo o conteúdo anterior
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, indent=4)


# ===== BUSCAR USUÁRIO PELO EMAIL =====
def buscar_usuario_por_email(usuarios, email):
    """Busca um usuário pelo e-mail informado."""

    for usuario in usuarios:
        if usuario["email"] == email:
            return usuario

    return None


# ===== ALTERAR NOME DO USUÁRIO =====
def alterar_nome_usuario(usuarios, email, novo_nome):
    """Altera o nome de um usuário cadastrado."""

    usuario_encontrado = buscar_usuario_por_email(usuarios, email)

    if usuario_encontrado is None:
        return False

    usuario_encontrado["nome"] = novo_nome

    salvar_usuarios(usuarios)

    return True


# excluir usuário
def excluir_usuario(usuarios, email):
    """Exclui um usuário cadastrado."""

    usuario_encontrado = buscar_usuario_por_email(usuarios, email)

    if usuario_encontrado is None:
        return False

    usuarios.remove(usuario_encontrado)

    salvar_usuarios(usuarios)

    return True
