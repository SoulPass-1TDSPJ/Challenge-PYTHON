"""Verifica a consulta de clima sem depender da disponibilidade da internet."""

import copy
import unittest
from unittest.mock import Mock, patch

import requests

from SoulUP import api_clima


class ConsultaClimaTestes(unittest.TestCase):
    def setUp(self):
        self.local = {
            "results": [
                {
                    "name": "São Paulo",
                    "admin1": "São Paulo",
                    "country": "Brasil",
                    "latitude": -23.5,
                    "longitude": -46.6,
                }
            ]
        }
        self.tempo = {
            "current": {
                "temperature_2m": 0,
                "apparent_temperature": 0,
                "relative_humidity_2m": 0,
                "weather_code": 0,
            },
            "daily": {
                "time": [f"2026-10-{dia:02d}" for dia in range(20, 26)],
                "temperature_2m_min": [0] * 6,
                "temperature_2m_max": [10] * 6,
                "weather_code": [2] * 6,
            },
        }

    def resposta(self, dados):
        resposta = Mock()
        resposta.json.return_value = dados
        return resposta

    def test_sucesso_retorna_clima_e_cinco_tuplas_sem_descartar_zero(self):
        respostas = [self.resposta(self.local), self.resposta(self.tempo)]
        with patch.object(api_clima.requests, "get", side_effect=respostas) as consulta:
            resultado = api_clima.consultar_clima(" São Paulo ")

        self.assertEqual(resultado["cidade"], "São Paulo")
        self.assertEqual(resultado["estado"], "São Paulo")
        self.assertEqual(resultado["pais"], "Brasil")
        self.assertEqual(resultado["temperatura"], 0)
        self.assertEqual(resultado["sensacao"], 0)
        self.assertEqual(resultado["umidade"], 0)
        self.assertEqual(resultado["condicao"], "Céu limpo")
        self.assertEqual(len(resultado["previsoes"]), 5)
        self.assertEqual(
            resultado["previsoes"][0],
            ("2026-10-21", 0, 10, "Parcialmente nublado"),
        )
        self.assertTrue(all(isinstance(dia, tuple) for dia in resultado["previsoes"]))
        self.assertEqual(consulta.call_count, 2)
        geocodificacao, previsao = consulta.call_args_list
        self.assertEqual(geocodificacao.kwargs["params"]["name"], "São Paulo")
        self.assertEqual(geocodificacao.kwargs["params"]["language"], "pt")
        self.assertEqual(geocodificacao.kwargs["params"]["count"], 1)
        self.assertEqual(previsao.kwargs["params"]["temperature_unit"], "celsius")
        self.assertEqual(previsao.kwargs["params"]["timezone"], "auto")
        self.assertEqual(previsao.kwargs["params"]["forecast_days"], 6)
        for chamada in consulta.call_args_list:
            self.assertEqual(chamada.kwargs["timeout"], 15)
        for resposta in respostas:
            resposta.raise_for_status.assert_called_once()

    def test_cidade_invalida_nao_inicia_requisicao(self):
        for cidade in (None, "", " ", "A", "A" * 101, "São Paulo2", "???", "--"):
            with self.subTest(cidade=cidade):
                with patch.object(api_clima.requests, "get") as consulta:
                    with self.assertRaises(ValueError):
                        api_clima.consultar_clima(cidade)
                    consulta.assert_not_called()

    def test_cidade_ausente_nao_inventa_resultado(self):
        for dados in ({}, {"results": []}):
            with self.subTest(dados=dados):
                with patch.object(api_clima.requests, "get", return_value=self.resposta(dados)):
                    with self.assertRaisesRegex(ValueError, "Cidade não encontrada"):
                        api_clima.consultar_clima("Cidade inexistente")

    def test_timeout_e_conexao_propagam_para_menu(self):
        for erro in (requests.exceptions.Timeout("demorou"), requests.exceptions.ConnectionError("sem conexão")):
            with self.subTest(erro=type(erro).__name__):
                with patch.object(api_clima.requests, "get", side_effect=erro):
                    with self.assertRaises(type(erro)):
                        api_clima.consultar_clima("São Paulo")

    def test_http_verificado_antes_de_ler_json(self):
        resposta = self.resposta(self.local)
        resposta.raise_for_status.side_effect = requests.exceptions.HTTPError("503")
        with patch.object(api_clima.requests, "get", return_value=resposta):
            with self.assertRaises(requests.exceptions.HTTPError):
                api_clima.consultar_clima("São Paulo")
        resposta.json.assert_not_called()

    def test_json_invalido_gera_mensagem_util(self):
        for etapa in (0, 1):
            with self.subTest(etapa=etapa):
                respostas = [self.resposta(self.local), self.resposta(self.tempo)]
                respostas[etapa].json.side_effect = ValueError("JSON quebrado")
                with patch.object(api_clima.requests, "get", side_effect=respostas):
                    with self.assertRaisesRegex(ValueError, "JSON inválida"):
                        api_clima.consultar_clima("São Paulo")

    def test_geocodificacao_malformada_e_rejeitada(self):
        casos = [[], {"results": None}, {"results": [None]}]
        for campo, valor in (("name", None), ("latitude", None), ("latitude", True), ("longitude", 181)):
            dados = copy.deepcopy(self.local)
            dados["results"][0][campo] = valor
            casos.append(dados)
        for dados in casos:
            with self.subTest(dados=dados):
                with patch.object(api_clima.requests, "get", return_value=self.resposta(dados)):
                    with self.assertRaises(ValueError):
                        api_clima.consultar_clima("São Paulo")

    def test_clima_atual_incompleto_e_rejeitado(self):
        casos = ({}, {"current": None, "daily": self.tempo["daily"]})
        for dados in casos:
            with self.subTest(dados=dados):
                respostas = [self.resposta(self.local), self.resposta(dados)]
                with patch.object(api_clima.requests, "get", side_effect=respostas):
                    with self.assertRaises(ValueError):
                        api_clima.consultar_clima("São Paulo")

    def test_numeros_invalidos_do_clima_sao_rejeitados(self):
        casos = (
            ("temperature_2m", None),
            ("temperature_2m", True),
            ("temperature_2m", float("nan")),
            ("temperature_2m", float("inf")),
            ("apparent_temperature", "20"),
            ("relative_humidity_2m", 101),
            ("weather_code", None),
            ("weather_code", 1.5),
        )
        for campo, valor in casos:
            with self.subTest(campo=campo, valor=valor):
                dados = copy.deepcopy(self.tempo)
                dados["current"][campo] = valor
                respostas = [self.resposta(self.local), self.resposta(dados)]
                with patch.object(api_clima.requests, "get", side_effect=respostas):
                    with self.assertRaises(ValueError):
                        api_clima.consultar_clima("São Paulo")

    def test_previsao_malformada_e_rejeitada(self):
        casos = (
            ("time", None),
            ("time", ["2026-10-20"] * 5),
            ("time", ["2026-10-20", "2026-02-30"] + ["2026-10-22"] * 4),
            ("time", ["2026-10-20", "2026-W44-5"] + ["2026-10-22"] * 4),
            ("time", ["2026-10-20", None] + ["2026-10-22"] * 4),
            ("temperature_2m_min", [0, None, 0, 0, 0, 0]),
            ("temperature_2m_max", [10, -1, 10, 10, 10, 10]),
            ("weather_code", [0, None, 0, 0, 0, 0]),
            ("weather_code", [0] * 7),
        )
        for campo, valor in casos:
            with self.subTest(campo=campo, valor=valor):
                dados = copy.deepcopy(self.tempo)
                dados["daily"][campo] = valor
                respostas = [self.resposta(self.local), self.resposta(dados)]
                with patch.object(api_clima.requests, "get", side_effect=respostas):
                    with self.assertRaises(ValueError):
                        api_clima.consultar_clima("São Paulo")


if __name__ == "__main__":
    unittest.main()
