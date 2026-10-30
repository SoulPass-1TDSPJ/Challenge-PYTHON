"""Consulta de clima para planejar viagens, conforme a atividade da Aula 6."""

from datetime import date

import requests


# Códigos de condição do tempo retornados pela Open-Meteo.
CONDICOES = {
    0: "Céu limpo",
    1: "Predominantemente limpo",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Nevoeiro",
    48: "Nevoeiro com formação de gelo",
    51: "Garoa leve",
    53: "Garoa moderada",
    55: "Garoa intensa",
    56: "Garoa congelante leve",
    57: "Garoa congelante intensa",
    61: "Chuva leve",
    63: "Chuva moderada",
    65: "Chuva forte",
    66: "Chuva congelante leve",
    67: "Chuva congelante forte",
    71: "Neve leve",
    73: "Neve moderada",
    75: "Neve forte",
    77: "Grãos de neve",
    80: "Pancadas de chuva leves",
    81: "Pancadas de chuva moderadas",
    82: "Pancadas de chuva fortes",
    85: "Pancadas de neve leves",
    86: "Pancadas de neve fortes",
    95: "Trovoadas",
    96: "Trovoadas com granizo leve",
    99: "Trovoadas com granizo forte",
}


def _consultar_json(url, parametros):
    """Recebe URL e parâmetros; retorna o dicionário JSON da resposta.

    Erros de conexão, timeout e HTTP seguem para o tratamento do menu.
    Uma resposta sem JSON válido gera ValueError.
    """
    resposta = requests.get(url, params=parametros, timeout=15)
    resposta.raise_for_status()
    try:
        dados = resposta.json()
    except ValueError:
        raise ValueError("A API de clima retornou uma resposta JSON inválida.")

    if not isinstance(dados, dict):
        raise ValueError("A API de clima retornou dados em formato inesperado.")
    return dados


def _validar_numero(valor, campo):
    """Recebe valor e nome do campo; retorna um número válido ou gera ValueError."""
    # Zero é válido. None, texto, booleanos, infinito e NaN não são números úteis.
    if type(valor) not in (int, float):
        raise ValueError(f"A API não informou um número válido para {campo}.")
    if not -float("inf") < valor < float("inf"):
        raise ValueError(f"A API informou um número inválido para {campo}.")
    return valor


def _descrever_condicao(codigo):
    """Recebe um código numérico; retorna a descrição da condição em português."""
    _validar_numero(codigo, "a condição do tempo")
    if codigo != int(codigo) or codigo < 0:
        raise ValueError("A API informou um código de condição do tempo inválido.")
    return CONDICOES.get(codigo, "Condição não informada")


def _validar_data(data):
    """Recebe uma data da API; retorna o texto no formato AAAA-MM-DD."""
    if not isinstance(data, str) or len(data) != 10:
        raise ValueError("A API informou uma data de previsão inválida.")
    try:
        if date.fromisoformat(data).isoformat() != data:
            raise ValueError("Formato diferente de AAAA-MM-DD.")
    except ValueError:
        raise ValueError("A API informou uma data de previsão inválida.")
    return data


def consultar_clima(cidade):
    """Recebe o nome da cidade e retorna um dicionário com clima e previsão.

    A primeira localidade encontrada é usada, como na Aula 6. O resultado tem
    cidade, estado, pais, temperatura, sensacao, umidade, condicao e previsoes.
    Previsoes é uma lista de cinco tuplas (data, minima, maxima, condicao),
    começando amanhã. Temperaturas são em Celsius e datas no horário local.
    Entrada ou resposta inválida gera ValueError; erros de rede propagam como
    requests.exceptions.RequestException para serem tratados pelo menu.
    """
    if not isinstance(cidade, str):
        raise ValueError("Informe o nome de uma cidade como texto.")
    cidade = cidade.strip()
    if not 2 <= len(cidade) <= 100:
        raise ValueError("Digite uma cidade com 2 a 100 caracteres.")

    tem_letra = False
    for caracter in cidade:
        if caracter.isdigit():
            raise ValueError("O nome da cidade não pode conter números.")
        if caracter.isalpha():
            tem_letra = True
        elif caracter not in " '-.,":
            raise ValueError("Use letras, espaços, apóstrofos, hífens, pontos ou vírgulas na cidade.")
    if not tem_letra:
        raise ValueError("Informe o nome de uma cidade com letras.")

    parametros_cidade = {
        "name": cidade,
        "count": 1,
        "language": "pt",
        "format": "json",
    }
    dados_cidade = _consultar_json(
        "https://geocoding-api.open-meteo.com/v1/search", parametros_cidade
    )
    cidades = dados_cidade.get("results", [])
    if not isinstance(cidades, list):
        raise ValueError("A API retornou uma lista de cidades inválida.")
    if not cidades:
        raise ValueError("Cidade não encontrada. Confira o nome e tente novamente.")

    localidade = cidades[0]
    if not isinstance(localidade, dict):
        raise ValueError("A API retornou uma localização inválida.")
    nome = localidade.get("name")
    estado = localidade.get("admin1", "")
    pais = localidade.get("country", "")
    if not isinstance(nome, str) or not nome.strip():
        raise ValueError("A API não informou o nome da cidade encontrada.")
    if not isinstance(estado, str) or not isinstance(pais, str):
        raise ValueError("A API retornou estado ou país em formato inválido.")
    latitude = _validar_numero(localidade.get("latitude"), "a latitude")
    longitude = _validar_numero(localidade.get("longitude"), "a longitude")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("A API retornou coordenadas inválidas para a cidade.")

    parametros_tempo = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code",
        "daily": "temperature_2m_min,temperature_2m_max,weather_code",
        "temperature_unit": "celsius",
        "timezone": "auto",
        "forecast_days": 6,  # Hoje e os próximos cinco dias.
    }
    dados_tempo = _consultar_json(
        "https://api.open-meteo.com/v1/forecast", parametros_tempo
    )
    atual = dados_tempo.get("current")
    diario = dados_tempo.get("daily")
    if not isinstance(atual, dict) or not isinstance(diario, dict):
        raise ValueError("A API não disponibilizou o clima atual e a previsão diária.")

    temperatura = _validar_numero(atual.get("temperature_2m"), "a temperatura atual")
    sensacao = _validar_numero(atual.get("apparent_temperature"), "a sensação térmica")
    umidade = _validar_numero(atual.get("relative_humidity_2m"), "a umidade")
    if not 0 <= umidade <= 100:
        raise ValueError("A API informou umidade fora do intervalo de 0 a 100%.")
    condicao = _descrever_condicao(atual.get("weather_code"))

    datas = diario.get("time")
    minimas = diario.get("temperature_2m_min")
    maximas = diario.get("temperature_2m_max")
    codigos = diario.get("weather_code")
    for valores in (datas, minimas, maximas, codigos):
        if not isinstance(valores, list) or len(valores) < 6:
            raise ValueError("A API não retornou todos os próximos cinco dias da previsão.")
        if len(valores) != len(datas):
            raise ValueError("A API retornou listas de previsão com tamanhos diferentes.")

    previsoes = []
    # O índice 0 é hoje; os índices de 1 a 5 representam os próximos dias.
    for indice in range(1, 6):
        data = _validar_data(datas[indice])
        minima = _validar_numero(minimas[indice], "a temperatura mínima prevista")
        maxima = _validar_numero(maximas[indice], "a temperatura máxima prevista")
        if minima > maxima:
            raise ValueError("A API informou uma mínima maior que a máxima na previsão.")
        condicao_dia = _descrever_condicao(codigos[indice])
        previsoes.append((data, minima, maxima, condicao_dia))

    return {
        "cidade": nome.strip(),
        "estado": estado,
        "pais": pais,
        "temperatura": temperatura,
        "sensacao": sensacao,
        "umidade": umidade,
        "condicao": condicao,
        "previsoes": previsoes,
    }
