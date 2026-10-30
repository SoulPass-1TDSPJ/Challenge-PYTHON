"""Cria somente as duas tabelas do SoulPass que ainda não existem."""

import os

import oracledb

from armazenamento import conectar, fechar_recursos


def preparar_banco():
    """Lê o SQL do projeto e cria as tabelas ausentes, sem apagar dados."""
    caminho = os.path.join(os.path.dirname(__file__), "..", "sql", "criar_tabelas.sql")
    with open(caminho, encoding="utf-8") as arquivo:
        comandos = [comando.strip() for comando in arquivo.read().split(";") if comando.strip()]
    tabelas = ("SOULPASS_USUARIOS_PY", "SOULPASS_EMBARQUES_PY")
    if len(comandos) != len(tabelas):
        raise ValueError("Confira o script SQL: são esperados dois CREATE TABLE.")

    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        for tabela, comando in zip(tabelas, comandos):
            cursor.execute(
                "SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME = :tabela",
                {"tabela": tabela},
            )
            if cursor.fetchone()[0]:
                print(f"{tabela}: já existe, preservada.")
            else:
                cursor.execute(comando)
                print(f"{tabela}: criada.")
    finally:
        fechar_recursos(cursor, conexao)
    print("Preparação concluída. Execute SoulUP/main.py.")


if __name__ == "__main__":
    try:
        preparar_banco()
    except oracledb.Error as erro:
        print(f"Não foi possível preparar o Oracle ({erro.args[0].full_code}).")
        print("Confira o login, o script SQL e a permissão para criar tabelas.")
        raise SystemExit(1)
    except (ValueError, OSError) as erro:
        print(erro)
        raise SystemExit(1)
