"""Testes dos cartões usando somente usuários fictícios e pastas temporárias."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PROJETO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJETO / "SoulUP"))

import cartao
from PIL import Image


class TestCartao(unittest.TestCase):
    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory(
            prefix=".teste_cartao_", dir=PROJETO
        )
        self.addCleanup(self.temporario.cleanup)
        self.pasta = Path(self.temporario.name)
        self.qr = self.pasta / "QRCod"
        self.cartoes = self.pasta / "Cartao_usr"
        self.patch_qr = patch.object(cartao, "PASTA_QR", str(self.qr))
        self.patch_cartoes = patch.object(cartao, "PASTA_CARTOES", str(self.cartoes))
        self.patch_qr.start()
        self.patch_cartoes.start()
        self.addCleanup(self.patch_qr.stop)
        self.addCleanup(self.patch_cartoes.stop)
        self.usuario = {
            "id": "USR_TESTE_001",
            "qrcode": "QR_USR_TESTE_001",
            "nome": "Ana Teste Silva",
            "email": "ana.teste@example.invalid",
            "saldo": 12.5,
        }

    def test_gera_pngs_e_conteudo_do_qr(self):
        with patch.object(cartao.qrcode, "make", wraps=cartao.qrcode.make) as criar_qr:
            caminhos = cartao.gerar_arquivos_usuario(self.usuario)

        self.assertEqual(
            caminhos,
            {
                "qrcode": str(self.qr / "QR_USR_TESTE_001.png"),
                "cartao": str(self.cartoes / "CARTAO_USR_TESTE_001.png"),
            },
        )
        criar_qr.assert_called_once_with(
            "NOME: Ana Teste Silva\n"
            "EMAIL: ana.teste@example.invalid\n"
            "ID: USR_TESTE_001"
        )
        with Image.open(caminhos["qrcode"]) as qr:
            self.assertEqual(qr.format, "PNG")
        with Image.open(caminhos["cartao"]) as imagem:
            self.assertEqual(imagem.format, "PNG")
            self.assertEqual(imagem.size, (750, 350))
            self.assertEqual(imagem.getpixel((0, 0)), (27, 5, 38))

    def test_atualiza_nome_e_saldo(self):
        caminhos = cartao.gerar_arquivos_usuario(self.usuario)
        qr = Path(caminhos["qrcode"])
        imagem = Path(caminhos["cartao"])
        qr_anterior = qr.read_bytes()
        cartao_anterior = imagem.read_bytes()

        self.usuario["nome"] = "Beatriz Exemplo Souza"
        cartao.gerar_arquivos_usuario(self.usuario)
        self.assertNotEqual(qr.read_bytes(), qr_anterior)
        self.assertNotEqual(imagem.read_bytes(), cartao_anterior)

        qr_apos_nome = qr.read_bytes()
        cartao_apos_nome = imagem.read_bytes()
        self.usuario["saldo"] = 38.75
        cartao.gerar_arquivos_usuario(self.usuario)
        self.assertEqual(qr.read_bytes(), qr_apos_nome)
        self.assertNotEqual(imagem.read_bytes(), cartao_apos_nome)

    def test_rejeita_caminhos_invalidos_sem_exclusao_parcial(self):
        caminhos = cartao.gerar_arquivos_usuario(self.usuario)
        originais = {
            caminho: Path(caminho).read_bytes() for caminho in caminhos.values()
        }
        for campo in ("id", "qrcode"):
            for valor in ("../fora", "..\\fora", str(self.pasta / "fora"), ""):
                with self.subTest(campo=campo, valor=valor):
                    usuario_invalido = dict(self.usuario)
                    usuario_invalido[campo] = valor
                    with self.assertRaises(ValueError):
                        cartao.gerar_arquivos_usuario(usuario_invalido)
                    with self.assertRaises(ValueError):
                        cartao.excluir_arquivos_usuario(usuario_invalido)
                    for caminho, conteudo in originais.items():
                        self.assertEqual(Path(caminho).read_bytes(), conteudo)

    def test_exclui_somente_arquivos_do_usuario_ficticio(self):
        caminhos = cartao.gerar_arquivos_usuario(self.usuario)
        outro_usuario = dict(self.usuario)
        outro_usuario.update(id="USR_TESTE_002", qrcode="QR_USR_TESTE_002")
        caminhos_outro = cartao.gerar_arquivos_usuario(outro_usuario)
        legado = self.cartoes / "CARTAO_LEGADO.png"
        Image.new("RGB", (2, 2), "green").save(legado)
        preservados = [Path(caminho) for caminho in caminhos_outro.values()]
        preservados.append(legado)
        conteudos = {caminho: caminho.read_bytes() for caminho in preservados}

        removidos = cartao.excluir_arquivos_usuario(self.usuario)

        self.assertEqual(set(removidos), set(caminhos.values()))
        for caminho in caminhos.values():
            self.assertFalse(Path(caminho).exists())
        for caminho, conteudo in conteudos.items():
            self.assertEqual(caminho.read_bytes(), conteudo)
        self.assertEqual(cartao.excluir_arquivos_usuario(self.usuario), [])


if __name__ == "__main__":
    unittest.main()
