"""Regressoes dos menus com usuarios ficticios e todas as integracoes simuladas."""

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import call, patch

PROJETO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJETO / "SoulUP"))

import main


def usuario_ficticio():
    return {
        "id": "USR_12345",
        "nome": "Ana Exemplo",
        "email": "ana@example.invalid",
        "senha": "senha-ficticia",
        "cpf": "12345678909",
        "qrcode": "QR_USR_12345",
        "saldo": 25.0,
        "pontos": 30000,
    }


def entradas_cadastro():
    return ["  Ana Exemplo  ", "  ANA@EXAMPLE.INVALID  ", "senha-ficticia",
            "123.456.789-09", "25,50", "30000"]


class TestValidacoes(unittest.TestCase):
    def test_cpf_rejeita_letras_unicode_repetidos_e_digitos_incorretos(self):
        invalidos = ["abcdefghijk", "1234567890a", "１２３４５６７８９０９",
                     "12345678900", "1234567890", "123456789090", ""]
        invalidos.extend(str(numero) * 11 for numero in range(10))
        for cpf in invalidos:
            with self.subTest(cpf=cpf):
                self.assertFalse(main.validar_cpf(cpf))

    def test_cpf_valido_pontuado_ou_sem_pontuacao(self):
        for cpf in ("12345678909", " 123.456.789-09 "):
            with self.subTest(cpf=cpf):
                self.assertTrue(main.validar_cpf(cpf))
                self.assertEqual(main.limpar_cpf(cpf), "12345678909")

    def test_saldo_rejeita_naN_infinito_negativos_e_valores_fora_do_limite(self):
        for saldo in ("nan", "NaN", "inf", "-inf", "1e309", "-0.01", "10000000000"):
            with self.subTest(saldo=saldo):
                with self.assertRaises(ValueError):
                    main.validar_valores(saldo, "1")

    def test_pontos_rejeitam_decimais_negativos_e_valores_fora_do_limite(self):
        for pontos in ("1.5", "1,5", "-1", "1000000000000", "nan", "inf"):
            with self.subTest(pontos=pontos):
                with self.assertRaises(ValueError):
                    main.validar_valores("5", pontos)

    def test_valores_validos_aceitam_virgula_e_zero(self):
        self.assertEqual(main.validar_valores("25,50", "30000"), (25.5, 30000))
        self.assertEqual(main.validar_valores("0", "0"), (0.0, 0))


class TestFluxosMenu(unittest.TestCase):
    def setUp(self):
        self.patch_banco = patch.object(main, "armazenamento", autospec=True)
        self.banco = self.patch_banco.start()
        self.addCleanup(self.patch_banco.stop)
        self.banco.buscar_usuario_por_id.return_value = None
        self.banco.buscar_usuario_por_email.return_value = None
        self.banco.cadastrar_usuario.return_value = True
        self.banco.alterar_nome_usuario.return_value = True
        self.banco.excluir_usuario.return_value = True
        self.banco.resgatar_premio.return_value = True
        self.banco.registrar_embarque.return_value = (True, "Embarque realizado!")
        self.banco.exportar_consulta.return_value = "consulta_ficticia.json"

        self.patch_gerar = patch.object(main, "gerar_arquivos_usuario", return_value={
            "qrcode": "qr_ficticio.png", "cartao": "cartao_ficticio.png"
        })
        self.gerar_imagens = self.patch_gerar.start()
        self.addCleanup(self.patch_gerar.stop)
        self.patch_excluir = patch.object(main, "excluir_arquivos_usuario")
        self.excluir_imagens = self.patch_excluir.start()
        self.addCleanup(self.patch_excluir.stop)
        self.patch_api = patch.object(main, "consultar_clima", side_effect=AssertionError("API real proibida no teste"))
        self.api = self.patch_api.start()
        self.addCleanup(self.patch_api.stop)
        self.patch_aleatorio = patch.object(main.random, "randint", return_value=12345)
        self.patch_aleatorio.start()
        self.addCleanup(self.patch_aleatorio.stop)
        self.saida = io.StringIO()
        self.captura = redirect_stdout(self.saida)
        self.captura.__enter__()
        self.addCleanup(self.captura.__exit__, None, None, None)

    def test_menu_quatro_sai_sem_consultar_oracle_ou_api(self):
        with patch("builtins.input", side_effect=["4"]):
            main.main()
        self.assertIn("Saindo...", self.saida.getvalue())
        self.assertEqual(self.banco.mock_calls, [])
        self.api.assert_not_called()
        self.gerar_imagens.assert_not_called()

    def test_cadastro_valida_campos_e_valores_antes_de_acessar_banco(self):
        casos = []
        for indice, invalido in ((0, " "), (1, "email-invalido"), (2, "abc"),
                                 (3, "abcdefghijk"), (4, "nan"), (5, "1.5")):
            entradas = entradas_cadastro()
            entradas[indice] = invalido
            casos.append(entradas)
        for entradas in casos:
            with self.subTest(entradas=entradas):
                with patch("builtins.input", side_effect=entradas):
                    with self.assertRaises(ValueError):
                        main.cadastrar()
        self.assertEqual(self.banco.mock_calls, [])
        self.gerar_imagens.assert_not_called()

    def test_cadastro_normaliza_dados_e_so_gera_imagens_apos_insercao(self):
        eventos = []
        self.banco.cadastrar_usuario.side_effect = lambda usuario: eventos.append("banco") or True
        self.gerar_imagens.side_effect = lambda usuario: eventos.append("imagens") or {
            "qrcode": "qr_ficticio.png", "cartao": "cartao_ficticio.png"
        }
        with patch("builtins.input", side_effect=entradas_cadastro()):
            main.cadastrar()
        usuario = self.banco.cadastrar_usuario.call_args.args[0]
        self.assertEqual(eventos, ["banco", "imagens"])
        self.assertEqual(usuario["nome"], "Ana Exemplo")
        self.assertEqual(usuario["email"], "ana@example.invalid")
        self.assertEqual(usuario["cpf"], "12345678909")
        self.assertEqual(usuario["saldo"], 25.5)
        self.assertEqual(usuario["pontos"], 30000)
        self.assertEqual(usuario["qrcode"], "QR_USR_12345")
        self.gerar_imagens.assert_called_once_with(usuario)

    def test_duplicado_informa_erro_e_volta_ao_menu_sem_gerar_imagens(self):
        detalhe = SimpleNamespace(code=1, full_code="ORA-00001")
        self.banco.cadastrar_usuario.side_effect = main.oracledb.IntegrityError(detalhe)
        with patch("builtins.input", side_effect=["1"] + entradas_cadastro() + ["4"]):
            main.main()
        self.banco.cadastrar_usuario.assert_called_once()
        self.assertIn("já cadastrado", self.saida.getvalue())
        self.assertNotIn("cadastrado com sucesso", self.saida.getvalue())
        self.assertIn("Saindo...", self.saida.getvalue())
        self.gerar_imagens.assert_not_called()
        self.banco.excluir_usuario.assert_not_called()

    def test_cadastro_confirmado_com_imagem_falha_nao_reinsere_usuario(self):
        self.gerar_imagens.side_effect = OSError("falha ficticia na imagem")
        with patch("builtins.input", side_effect=["1"] + entradas_cadastro() + ["4"]):
            main.main()
        self.banco.cadastrar_usuario.assert_called_once()
        texto = self.saida.getvalue()
        self.assertIn("Usuário cadastrado com sucesso", texto)
        self.assertIn("dados estão salvos no banco", texto)
        self.assertIn("Gerar cartão novamente", texto)
        self.assertNotIn("Operação não concluída", texto)
        self.assertIn("Saindo...", texto)

    def test_id_sorteado_ja_existente_e_trocado_sem_sobrescrever_usuario(self):
        self.banco.buscar_usuario_por_id.side_effect = [usuario_ficticio(), None]
        with patch.object(main.random, "randint", side_effect=[12345, 54321]):
            self.assertEqual(main.gerar_identificador(), "USR_54321")
        self.assertEqual(self.banco.buscar_usuario_por_id.call_args_list,
                         [call("USR_12345"), call("USR_54321")])
        self.banco.cadastrar_usuario.assert_not_called()

    def test_login_incorreto_nao_abre_menu_do_usuario(self):
        self.banco.buscar_usuario_por_email.return_value = usuario_ficticio()
        with patch("builtins.input", side_effect=["ana@example.invalid", "senha-errada"]):
            main.login()
        self.banco.buscar_usuario_por_id.assert_not_called()
        self.assertIn("Email ou senha incorretos", self.saida.getvalue())

    def test_login_alterar_embarcar_exportar_usam_perfil_atualizado(self):
        original = usuario_ficticio()
        renomeado = dict(original, nome="Nome Novo")
        embarcado = dict(renomeado, saldo=20.0)
        self.banco.buscar_usuario_por_email.return_value = original
        self.banco.buscar_usuario_por_id.side_effect = [
            original, renomeado, renomeado, embarcado, embarcado, embarcado
        ]
        with patch("builtins.input", side_effect=[
            " ANA@EXAMPLE.INVALID ", "senha-ficticia", "6", " Nome Novo ", "4", "8", "3"
        ]):
            main.login()
        self.banco.buscar_usuario_por_email.assert_called_once_with("ana@example.invalid")
        self.banco.alterar_nome_usuario.assert_called_once_with(original["id"], "Nome Novo")
        self.banco.registrar_embarque.assert_called_once_with(original["id"])
        self.banco.exportar_consulta.assert_called_once_with(embarcado)
        self.assertEqual(self.gerar_imagens.call_args_list,
                         [call(renomeado), call(embarcado)])
        texto = self.saida.getvalue()
        self.assertIn("Saldo restante: R$ 20.00", texto)
        self.assertIn("Consulta exportada para: consulta_ficticia.json", texto)
        self.assertIn("Logout realizado", texto)

    def test_passagem_selecionada_debita_15000_e_credita_cinco(self):
        usuario = usuario_ficticio()
        atualizado = dict(usuario, pontos=15000, saldo=30.0)
        self.banco.buscar_usuario_por_id.return_value = atualizado
        with patch("builtins.input", side_effect=["5"]):
            main.converter_pontos(usuario)
        self.banco.resgatar_premio.assert_called_once_with(usuario["id"], 15000, 5.0)
        self.gerar_imagens.assert_called_once_with(atualizado)
        self.assertIn("Crédito acrescentado ao cartão: R$ 5.00", self.saida.getvalue())

    def test_embarque_recusado_nao_consulta_saldo_nem_regenera_cartao(self):
        self.banco.registrar_embarque.return_value = (False, "Saldo insuficiente.")
        main.embarcar(usuario_ficticio())
        self.banco.buscar_usuario_por_id.assert_not_called()
        self.gerar_imagens.assert_not_called()
        self.assertIn("Saldo insuficiente", self.saida.getvalue())

    def test_embarque_confirmado_com_falha_da_consulta_avisa_para_nao_repetir(self):
        self.banco.buscar_usuario_por_id.side_effect = main.oracledb.DatabaseError("falha ficticia apos gravacao")
        main.embarcar(usuario_ficticio())
        self.banco.registrar_embarque.assert_called_once_with("USR_12345")
        self.gerar_imagens.assert_not_called()
        texto = self.saida.getvalue()
        self.assertIn("Embarque realizado!", texto)
        self.assertIn("A alteração foi salva", texto)
        self.assertIn("Não repita a operação", texto)
        self.assertNotIn("Não houve confirmação de sucesso", texto)

    def test_exclusao_cancelada_mantem_login_ate_logout_explicito(self):
        usuario = usuario_ficticio()
        self.banco.buscar_usuario_por_id.return_value = usuario
        with patch("builtins.input", side_effect=["7", "n", "1", "3"]):
            main.area_usuario(usuario["id"])
        self.banco.excluir_usuario.assert_not_called()
        self.excluir_imagens.assert_not_called()
        self.assertEqual(self.banco.buscar_usuario_por_id.call_count, 3)
        texto = self.saida.getvalue()
        self.assertIn("Exclusão cancelada", texto)
        self.assertIn("Pontos: 30000", texto)
        self.assertIn("Logout realizado", texto)

    def test_exclusao_confirmada_com_falha_na_imagem_encerra_login(self):
        usuario = usuario_ficticio()
        self.banco.buscar_usuario_por_id.return_value = usuario
        self.excluir_imagens.side_effect = OSError("falha ficticia ao remover imagem")
        with patch("builtins.input", side_effect=["7", "s"]):
            main.area_usuario(usuario["id"])
        self.banco.excluir_usuario.assert_called_once_with(usuario["id"])
        self.excluir_imagens.assert_called_once_with(usuario)
        self.banco.buscar_usuario_por_id.assert_called_once_with(usuario["id"])
        texto = self.saida.getvalue()
        self.assertIn("Conta e histórico excluídos do banco", texto)
        self.assertIn("Não foi possível remover as imagens locais", texto)

    def test_exclusao_com_falha_no_banco_preserva_imagens(self):
        usuario = usuario_ficticio()
        self.banco.buscar_usuario_por_id.return_value = usuario
        self.banco.excluir_usuario.side_effect = main.oracledb.DatabaseError("falha ficticia")
        with patch("builtins.input", side_effect=["7", "s"]):
            main.area_usuario(usuario["id"])
        self.excluir_imagens.assert_not_called()
        self.assertNotIn("Conta e histórico excluídos", self.saida.getvalue())


if __name__ == "__main__":
    unittest.main()
