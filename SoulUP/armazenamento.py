"""CRUD Oracle e exportacao JSON, usando funcoes como nos exemplos da aula 7."""

import json
import os
import time
from datetime import datetime

import oracledb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_EXPORTACOES = os.path.join(BASE_DIR, "Exportacoes")
CAMPOS_USUARIO = ("id", "nome", "email", "senha", "cpf", "qrcode", "saldo", "pontos")
COLUNAS_USUARIO = "ID_USUARIO, NOME, EMAIL, SENHA, CPF, QRCODE, SALDO, PONTOS"
TARIFA = 5.0
CO2_POR_EMBARQUE = 2.3


def conectar():
    """Abre uma conexao Oracle com os dados locais; retorna a conexao."""
    try:
        from config_banco_local import USUARIO, SENHA, DSN
    except ModuleNotFoundError as erro:
        raise ValueError("Copie config_banco_exemplo.py para config_banco_local.py.") from erro
    if not USUARIO.strip() or not SENHA or not DSN.strip():
        raise ValueError("Preencha USUARIO, SENHA e DSN em SoulUP/config_banco_local.py.")
    return oracledb.connect(user=USUARIO, password=SENHA, dsn=DSN)


def fechar_recursos(cursor, conexao):
    """Fecha o cursor e a conexao utilizados pela operacao."""
    try:
        if cursor is not None:
            cursor.close()
    finally:
        if conexao is not None:
            conexao.close()


def converter_usuario(registro):
    """Converte uma tupla retornada pelo Oracle em um dicionario de usuario."""
    usuario = dict(zip(CAMPOS_USUARIO, registro))
    usuario["saldo"] = float(usuario["saldo"])
    usuario["pontos"] = int(usuario["pontos"])
    return usuario


def consultar_usuarios(email=None):
    """Consulta todos os usuarios ou um e-mail; retorna lista de dicionarios."""
    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        sql = "SELECT " + COLUNAS_USUARIO + " FROM SOULPASS_USUARIOS_PY"
        parametros = {}
        if email is not None:
            sql += " WHERE EMAIL = :email"
            parametros["email"] = email.strip().lower()
        sql += " ORDER BY NOME, ID_USUARIO"
        cursor.execute(sql, parametros)
        return [converter_usuario(registro) for registro in cursor.fetchall()]
    finally:
        fechar_recursos(cursor, conexao)


def buscar_usuario_por_email(email):
    """Recebe um e-mail e retorna o usuario ou None se nao existir."""
    usuarios = consultar_usuarios(email)
    return usuarios[0] if usuarios else None


def buscar_usuario_por_id(id_usuario):
    """Recebe o ID de um usuario e retorna seu dicionario ou None."""
    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT " + COLUNAS_USUARIO + " FROM SOULPASS_USUARIOS_PY WHERE ID_USUARIO = :id",
            {"id": id_usuario},
        )
        registro = cursor.fetchone()
        return converter_usuario(registro) if registro else None
    finally:
        fechar_recursos(cursor, conexao)


def executar_alteracao(sql, parametros):
    """Executa escrita parametrizada; confirma ou desfaz e retorna linhas afetadas."""
    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(sql, parametros)
        quantidade = cursor.rowcount
        conexao.commit()
    except oracledb.Error:
        if conexao is not None:
            conexao.rollback()
        raise
    else:
        return quantidade
    finally:
        fechar_recursos(cursor, conexao)


def cadastrar_usuario(usuario):
    """Insere um usuario no Oracle, sem substituir os demais cadastros."""
    return executar_alteracao(
        """INSERT INTO SOULPASS_USUARIOS_PY
           (ID_USUARIO, NOME, EMAIL, SENHA, CPF, QRCODE, SALDO, PONTOS)
           VALUES (:id, :nome, :email, :senha, :cpf, :qrcode, :saldo, :pontos)""",
        {campo: usuario[campo] for campo in CAMPOS_USUARIO},
    ) == 1


def alterar_nome_usuario(id_usuario, novo_nome):
    """Altera o nome do ID informado; retorna True quando encontrar o cadastro."""
    if not novo_nome.strip() or len(novo_nome.strip()) > 100:
        raise ValueError("O nome deve conter de 1 a 100 caracteres.")
    return executar_alteracao(
        "UPDATE SOULPASS_USUARIOS_PY SET NOME = :nome WHERE ID_USUARIO = :id",
        {"nome": novo_nome.strip(), "id": id_usuario},
    ) == 1


def excluir_usuario(id_usuario):
    """Exclui um usuario; seus embarques sao excluidos pela chave estrangeira."""
    return executar_alteracao(
        "DELETE FROM SOULPASS_USUARIOS_PY WHERE ID_USUARIO = :id", {"id": id_usuario}
    ) == 1


def resgatar_premio(id_usuario, custo, credito=0):
    """Debita pontos e acrescenta o credito do premio numa unica operacao."""
    if isinstance(custo, bool) or not isinstance(custo, int) or custo <= 0:
        raise ValueError("O custo do premio precisa ser um inteiro positivo.")
    if not isinstance(credito, (int, float)) or isinstance(credito, bool) or not 0 <= credito <= TARIFA:
        raise ValueError("Credito do premio invalido.")
    return executar_alteracao(
        """UPDATE SOULPASS_USUARIOS_PY
           SET PONTOS = PONTOS - :custo, SALDO = SALDO + :credito
           WHERE ID_USUARIO = :id AND PONTOS >= :custo""",
        {"custo": custo, "credito": credito, "id": id_usuario},
    ) == 1


def registrar_embarque(id_usuario):
    """Debita uma tarifa e grava o embarque na mesma transacao; retorna sucesso e mensagem."""
    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        # O bloqueio evita duas cobrancas concorrentes sobre o mesmo saldo.
        cursor.execute(
            "SELECT SALDO FROM SOULPASS_USUARIOS_PY WHERE ID_USUARIO = :id FOR UPDATE",
            {"id": id_usuario},
        )
        registro = cursor.fetchone()
        if registro is None or float(registro[0]) < TARIFA:
            conexao.rollback()
            return False, "Saldo insuficiente para a tarifa de R$ 5,00."
        cursor.execute(
            "SELECT MAX(HORARIO) FROM SOULPASS_EMBARQUES_PY WHERE ID_USUARIO = :id",
            {"id": id_usuario},
        )
        ultimo = cursor.fetchone()[0]
        horario = round(time.time(), 6)
        if ultimo is not None and horario - float(ultimo) < 120:
            conexao.rollback()
            return False, "Embarque repetido: aguarde 120 segundos entre os embarques."
        cursor.execute(
            "UPDATE SOULPASS_USUARIOS_PY SET SALDO = SALDO - :tarifa WHERE ID_USUARIO = :id",
            {"tarifa": TARIFA, "id": id_usuario},
        )
        cursor.execute(
            "INSERT INTO SOULPASS_EMBARQUES_PY (ID_USUARIO, HORARIO, TARIFA) VALUES (:id, :horario, :tarifa)",
            {"id": id_usuario, "horario": horario, "tarifa": TARIFA},
        )
        conexao.commit()
        return True, "Embarque realizado!"
    except oracledb.Error:
        if conexao is not None:
            conexao.rollback()
        raise
    finally:
        fechar_recursos(cursor, conexao)


def consultar_embarques(id_usuario):
    """Retorna lista de dicionarios com os embarques de um unico usuario."""
    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT HORARIO, TARIFA FROM SOULPASS_EMBARQUES_PY WHERE ID_USUARIO = :id ORDER BY HORARIO",
            {"id": id_usuario},
        )
        return [
            {"horario": datetime.fromtimestamp(float(horario)).isoformat(timespec="seconds"),
             "tarifa": float(tarifa)}
            for horario, tarifa in cursor.fetchall()
        ]
    finally:
        fechar_recursos(cursor, conexao)


def dados_publicos(usuario):
    """Monta a consulta exportavel sem senha e CPF."""
    return {campo: usuario[campo] for campo in ("id", "nome", "email", "qrcode", "saldo", "pontos")}


def exportar_consulta(usuario):
    """Exporta usuario e embarques para um novo JSON UTF-8; retorna caminho."""
    embarques = consultar_embarques(usuario["id"])
    dados = {
        "exportado_em": datetime.now().isoformat(timespec="seconds"),
        "usuario": dados_publicos(usuario),
        "embarques": embarques,
        "resumo": {"quantidade_embarques": len(embarques),
                   "co2_estimado_kg": round(len(embarques) * CO2_POR_EMBARQUE, 2)},
    }
    os.makedirs(PASTA_EXPORTACOES, exist_ok=True)
    # O modo x preserva qualquer exportacao anterior mesmo em chamadas seguidas.
    nome = "consulta_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".json"
    caminho = os.path.join(PASTA_EXPORTACOES, nome)
    with open(caminho, "x", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)
    return caminho
