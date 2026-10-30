"""Persistencia testada sem Oracle real, credenciais ou dados cadastrados."""

import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJETO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJETO / "SoulUP"))

import armazenamento


def usuario_ficticio():
    return {
        "id": "USR_TESTE_001",
        "nome": "Ana Exemplo",
        "email": "ana@example.invalid",
        "senha": "senha-ficticia",
        "cpf": "00000000000",
        "qrcode": "QR_USR_TESTE_001",
        "saldo": 25.0,
        "pontos": 30000,
    }


class TestArmazenamentoOracle(unittest.TestCase):
    def setUp(self):
        self.cursor = MagicMock(
            spec=["execute", "fetchall", "fetchone", "rowcount", "close"]
        )
        self.cursor.rowcount = 1
        self.conexao = MagicMock(spec=["cursor", "commit", "rollback", "close"])
        self.conexao.cursor.return_value = self.cursor
        self.patch_conectar = patch.object(
            armazenamento, "conectar", return_value=self.conexao
        )
        self.conectar = self.patch_conectar.start()
        self.addCleanup(self.patch_conectar.stop)

    def conferir_fechamento(self):
        self.cursor.close.assert_called_once_with()
        self.conexao.close.assert_called_once_with()

    def test_consulta_email_normalizado_usa_bind_e_fecha_recursos(self):
        usuario = usuario_ficticio()
        self.cursor.fetchall.return_value = [tuple(usuario.values())]
        email = "  ANA' OR '1'='1@EXAMPLE.INVALID  "

        resultado = armazenamento.consultar_usuarios(email)

        sql, parametros = self.cursor.execute.call_args.args
        self.assertIn("WHERE EMAIL = :email", sql)
        self.assertNotIn(email.strip(), sql)
        self.assertEqual(parametros, {"email": email.strip().lower()})
        self.assertEqual(resultado, [usuario])
        self.assertIsInstance(resultado[0]["saldo"], float)
        self.assertIsInstance(resultado[0]["pontos"], int)
        self.conexao.commit.assert_not_called()
        self.conexao.rollback.assert_not_called()
        self.conferir_fechamento()

    def test_consulta_sem_email_retorna_lista_vazia(self):
        self.cursor.fetchall.return_value = []
        self.assertEqual(armazenamento.consultar_usuarios(), [])
        sql, parametros = self.cursor.execute.call_args.args
        self.assertNotIn("WHERE EMAIL", sql)
        self.assertEqual(parametros, {})
        self.conferir_fechamento()

    def test_busca_email_inexistente_retorna_none(self):
        self.cursor.fetchall.return_value = []
        self.assertIsNone(armazenamento.buscar_usuario_por_email("ausente@example.invalid"))
        self.conferir_fechamento()

    def test_busca_id_parametrizada(self):
        usuario = usuario_ficticio()
        self.cursor.fetchone.return_value = tuple(usuario.values())
        id_usuario = "id' OR '1'='1"
        self.assertEqual(armazenamento.buscar_usuario_por_id(id_usuario), usuario)
        sql, parametros = self.cursor.execute.call_args.args
        self.assertIn("WHERE ID_USUARIO = :id", sql)
        self.assertNotIn(id_usuario, sql)
        self.assertEqual(parametros, {"id": id_usuario})
        self.conferir_fechamento()

    def test_busca_id_inexistente_retorna_none(self):
        self.cursor.fetchone.return_value = None
        self.assertIsNone(armazenamento.buscar_usuario_por_id("USR_AUSENTE"))
        self.conferir_fechamento()

    def test_falha_em_consulta_fecha_recursos(self):
        self.cursor.execute.side_effect = armazenamento.oracledb.DatabaseError("simulado")
        with self.assertRaises(armazenamento.oracledb.DatabaseError):
            armazenamento.consultar_usuarios()
        self.conexao.commit.assert_not_called()
        self.conferir_fechamento()

    def test_cadastro_insere_campos_com_binds_e_commit(self):
        usuario = usuario_ficticio()
        self.assertTrue(armazenamento.cadastrar_usuario(usuario))
        sql, parametros = self.cursor.execute.call_args.args
        self.assertIn("INSERT INTO SOULPASS_USUARIOS_PY", sql)
        for campo, valor in usuario.items():
            self.assertIn(":" + campo, sql)
            self.assertEqual(parametros[campo], valor)
        self.conexao.commit.assert_called_once_with()
        self.conexao.rollback.assert_not_called()
        self.conferir_fechamento()

    def test_alteracao_nome_usa_id_nome_limpo_e_commit(self):
        self.assertTrue(armazenamento.alterar_nome_usuario("USR_TESTE_001", "  Nome Novo  "))
        sql, parametros = self.cursor.execute.call_args.args
        self.assertIn("SET NOME = :nome WHERE ID_USUARIO = :id", sql)
        self.assertEqual(parametros, {"nome": "Nome Novo", "id": "USR_TESTE_001"})
        self.conexao.commit.assert_called_once_with()
        self.conferir_fechamento()

    def test_nome_invalido_nao_abre_conexao(self):
        for nome in ("   ", "a" * 101):
            with self.subTest(tamanho=len(nome)):
                with self.assertRaises(ValueError):
                    armazenamento.alterar_nome_usuario("USR_TESTE_001", nome)
        self.conectar.assert_not_called()

    def test_exclusao_usa_bind_e_retorna_se_encontrou(self):
        self.cursor.rowcount = 0
        self.assertFalse(armazenamento.excluir_usuario("USR_AUSENTE"))
        sql, parametros = self.cursor.execute.call_args.args
        self.assertIn("DELETE FROM SOULPASS_USUARIOS_PY WHERE ID_USUARIO = :id", sql)
        self.assertEqual(parametros, {"id": "USR_AUSENTE"})
        self.conexao.commit.assert_called_once_with()
        self.conferir_fechamento()

    def test_escrita_com_falha_faz_rollback_sem_commit(self):
        self.cursor.execute.side_effect = armazenamento.oracledb.DatabaseError("simulado")
        with self.assertRaises(armazenamento.oracledb.DatabaseError):
            armazenamento.cadastrar_usuario(usuario_ficticio())
        self.conexao.rollback.assert_called_once_with()
        self.conexao.commit.assert_not_called()
        self.conferir_fechamento()

    def test_falha_no_commit_tambem_faz_rollback(self):
        self.conexao.commit.side_effect = armazenamento.oracledb.DatabaseError("simulado")
        with self.assertRaises(armazenamento.oracledb.DatabaseError):
            armazenamento.excluir_usuario("USR_TESTE_001")
        self.conexao.rollback.assert_called_once_with()
        self.conferir_fechamento()

    def test_falha_ao_criar_cursor_fecha_conexao(self):
        self.conexao.cursor.side_effect = armazenamento.oracledb.DatabaseError("simulado")
        with self.assertRaises(armazenamento.oracledb.DatabaseError):
            armazenamento.cadastrar_usuario(usuario_ficticio())
        self.cursor.close.assert_not_called()
        self.conexao.rollback.assert_called_once_with()
        self.conexao.close.assert_called_once_with()

    def test_falha_na_conexao_nao_tenta_fechar_recurso_inexistente(self):
        self.conectar.side_effect = armazenamento.oracledb.DatabaseError("simulado")
        with self.assertRaises(armazenamento.oracledb.DatabaseError):
            armazenamento.excluir_usuario("USR_TESTE_001")
        self.conexao.rollback.assert_not_called()
        self.conexao.close.assert_not_called()
        self.cursor.close.assert_not_called()

    def test_falha_no_fechamento_cursor_ainda_fecha_conexao(self):
        self.cursor.close.side_effect = armazenamento.oracledb.DatabaseError("simulado")
        with self.assertRaises(armazenamento.oracledb.DatabaseError):
            armazenamento.fechar_recursos(self.cursor, self.conexao)
        self.conexao.close.assert_called_once_with()

    def test_passagem_debita_pontos_e_credita_tarifa_no_mesmo_update(self):
        self.assertTrue(armazenamento.resgatar_premio("USR_TESTE_001", 15000, 5.0))
        sql, parametros = self.cursor.execute.call_args.args
        self.assertIn("PONTOS = PONTOS - :custo, SALDO = SALDO + :credito", sql)
        self.assertIn("WHERE ID_USUARIO = :id AND PONTOS >= :custo", sql)
        self.assertEqual(parametros, {"custo": 15000, "credito": 5.0, "id": "USR_TESTE_001"})
        self.conexao.commit.assert_called_once_with()
        self.conexao.rollback.assert_not_called()
        self.conferir_fechamento()

    def test_premio_sem_pontos_suficientes_retorna_false(self):
        self.cursor.rowcount = 0
        self.assertFalse(armazenamento.resgatar_premio("USR_TESTE_001", 15000))
        self.assertEqual(self.cursor.execute.call_args.args[1]["credito"], 0)
        self.conferir_fechamento()

    def test_premio_invalido_nao_abre_conexao(self):
        for custo, credito in ((0, 0), (-1, 0), (True, 0), (1.5, 0),
                               (1, -1), (1, 5.01), (1, True), (1, float("nan"))):
            with self.subTest(custo=custo, credito=credito):
                with self.assertRaises(ValueError):
                    armazenamento.resgatar_premio("USR_TESTE_001", custo, credito)
        self.conectar.assert_not_called()

    def test_embarque_saldo_abaixo_de_cinco_nao_debita_nem_insere(self):
        self.cursor.fetchone.return_value = (4.99,)
        sucesso, mensagem = armazenamento.registrar_embarque("USR_TESTE_001")
        self.assertFalse(sucesso)
        self.assertIn("Saldo insuficiente", mensagem)
        self.cursor.execute.assert_called_once_with(
            "SELECT SALDO FROM SOULPASS_USUARIOS_PY WHERE ID_USUARIO = :id FOR UPDATE",
            {"id": "USR_TESTE_001"},
        )
        self.conexao.rollback.assert_called_once_with()
        self.conexao.commit.assert_not_called()
        self.conferir_fechamento()

    def test_embarque_usuario_inexistente_nao_debita(self):
        self.cursor.fetchone.return_value = None
        self.assertFalse(armazenamento.registrar_embarque("USR_AUSENTE")[0])
        self.assertEqual(self.cursor.execute.call_count, 1)
        self.conexao.rollback.assert_called_once_with()
        self.conexao.commit.assert_not_called()
        self.conferir_fechamento()

    @patch.object(armazenamento.time, "time", return_value=1000.0)
    def test_embarque_repetido_antes_de_120_segundos_bloqueia(self, relogio):
        self.cursor.fetchone.side_effect = [(5.0,), (880.000001,)]
        sucesso, mensagem = armazenamento.registrar_embarque("USR_TESTE_001")
        self.assertFalse(sucesso)
        self.assertIn("120 segundos", mensagem)
        self.assertEqual(self.cursor.execute.call_count, 2)
        self.conexao.rollback.assert_called_once_with()
        self.conexao.commit.assert_not_called()
        self.conferir_fechamento()

    @patch.object(armazenamento.time, "time", return_value=1000.0)
    def test_embarque_com_cinco_reais_e_intervalo_exato_de_120_segundos(self, relogio):
        self.cursor.fetchone.side_effect = [(5.0,), (880.0,)]
        self.assertTrue(armazenamento.registrar_embarque("USR_TESTE_001")[0])
        chamadas = self.cursor.execute.call_args_list
        self.assertEqual(len(chamadas), 4)
        self.assertIn("FOR UPDATE", chamadas[0].args[0])
        self.assertIn("MAX(HORARIO)", chamadas[1].args[0])
        self.assertIn("SET SALDO = SALDO - :tarifa", chamadas[2].args[0])
        self.assertEqual(chamadas[2].args[1], {"tarifa": 5.0, "id": "USR_TESTE_001"})
        self.assertIn("INSERT INTO SOULPASS_EMBARQUES_PY", chamadas[3].args[0])
        self.assertEqual(chamadas[3].args[1], {"id": "USR_TESTE_001", "horario": 1000.0, "tarifa": 5.0})
        self.conexao.commit.assert_called_once_with()
        self.conexao.rollback.assert_not_called()
        self.conferir_fechamento()

    @patch.object(armazenamento.time, "time", return_value=1000.0)
    def test_primeiro_embarque_nao_exige_horario_anterior(self, relogio):
        self.cursor.fetchone.side_effect = [(5.0,), (None,)]
        self.assertTrue(armazenamento.registrar_embarque("USR_TESTE_001")[0])
        self.conexao.commit.assert_called_once_with()
        self.conferir_fechamento()

    @patch.object(armazenamento.time, "time", return_value=1000.0)
    def test_falha_no_registro_do_embarque_desfaz_tambem_debito(self, relogio):
        self.cursor.fetchone.side_effect = [(25.0,), (None,)]
        self.cursor.execute.side_effect = [None, None, None,
            armazenamento.oracledb.DatabaseError("falha simulada no INSERT")]
        with self.assertRaises(armazenamento.oracledb.DatabaseError):
            armazenamento.registrar_embarque("USR_TESTE_001")
        self.assertEqual(self.cursor.execute.call_count, 4)
        self.conexao.rollback.assert_called_once_with()
        self.conexao.commit.assert_not_called()
        self.conferir_fechamento()

    def test_consulta_embarques_filtra_por_usuario_e_converte_tipos(self):
        self.cursor.fetchall.return_value = [(1000, 5)]
        resultado = armazenamento.consultar_embarques("USR_TESTE_001")
        sql, parametros = self.cursor.execute.call_args.args
        self.assertIn("WHERE ID_USUARIO = :id ORDER BY HORARIO", sql)
        self.assertEqual(parametros, {"id": "USR_TESTE_001"})
        self.assertEqual(resultado, [{"horario": datetime.fromtimestamp(1000).isoformat(timespec="seconds"), "tarifa": 5.0}])
        self.conferir_fechamento()


class TestExportacaoConsulta(unittest.TestCase):
    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory(
            prefix=".teste_exportacao_", dir=PROJETO
        )
        self.addCleanup(self.temporario.cleanup)
        self.pasta = Path(self.temporario.name) / "exportacoes"
        self.patch_pasta = patch.object(armazenamento, "PASTA_EXPORTACOES", str(self.pasta))
        self.patch_pasta.start()
        self.addCleanup(self.patch_pasta.stop)
        self.patch_historico = patch.object(armazenamento, "consultar_embarques", return_value=[
            {"horario": "2026-01-02T03:00:00", "tarifa": 5.0},
            {"horario": "2026-01-02T03:03:00", "tarifa": 5.0},
        ])
        self.historico = self.patch_historico.start()
        self.addCleanup(self.patch_historico.stop)
        self.patch_conectar = patch.object(armazenamento, "conectar", side_effect=AssertionError("Oracle real proibido no teste"))
        self.conectar = self.patch_conectar.start()
        self.addCleanup(self.patch_conectar.stop)

    def test_exportacao_utf8_sem_cpf_senha_e_com_resumo_pessoal(self):
        usuario = usuario_ficticio()
        usuario["nome"] = "Usuária Fictícia"
        original = dict(usuario)
        caminho = Path(armazenamento.exportar_consulta(usuario))
        texto = caminho.read_text(encoding="utf-8")
        dados = json.loads(texto)

        self.assertEqual(caminho.parent, self.pasta)
        self.assertIn("Usuária Fictícia", texto)
        self.assertEqual(set(dados["usuario"]), {"id", "nome", "email", "qrcode", "saldo", "pontos"})
        self.assertNotIn("cpf", dados["usuario"])
        self.assertNotIn("senha", dados["usuario"])
        self.assertNotIn(usuario["cpf"], texto)
        self.assertNotIn(usuario["senha"], texto)
        self.assertEqual(dados["resumo"], {"quantidade_embarques": 2, "co2_estimado_kg": 4.6})
        self.assertEqual(len(dados["embarques"]), 2)
        self.historico.assert_called_once_with(usuario["id"])
        self.conectar.assert_not_called()
        self.assertEqual(usuario, original)

    def test_colisao_de_nome_preserva_conteudo_existente(self):
        instante = datetime(2026, 1, 2, 3, 4, 5, 6789)
        self.pasta.mkdir()
        caminho = self.pasta / ("consulta_" + instante.strftime("%Y%m%d_%H%M%S_%f") + ".json")
        conteudo = b'{"arquivo_anterior": true}\n'
        caminho.write_bytes(conteudo)

        with patch.object(armazenamento, "datetime") as relogio:
            relogio.now.return_value = instante
            with self.assertRaises(FileExistsError):
                armazenamento.exportar_consulta(usuario_ficticio())

        self.assertEqual(caminho.read_bytes(), conteudo)
        self.assertEqual(list(self.pasta.iterdir()), [caminho])
        self.conectar.assert_not_called()

    def test_falha_na_consulta_nao_cria_exportacao_parcial(self):
        self.historico.side_effect = armazenamento.oracledb.DatabaseError("simulado")
        with self.assertRaises(armazenamento.oracledb.DatabaseError):
            armazenamento.exportar_consulta(usuario_ficticio())
        self.assertFalse(self.pasta.exists())
        self.conectar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
