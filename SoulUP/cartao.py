"""Geração e exclusão dos arquivos de QR Code e cartão digital do SoulUP."""

import os

import qrcode
from PIL import Image, ImageDraw, ImageFont


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_QR = os.path.join(BASE_DIR, "QRCod")
PASTA_CARTOES = os.path.join(BASE_DIR, "Cartao_usr")


def abreviar_nome(nome):
    """Recebe o nome completo e retorna o primeiro nome e as demais iniciais."""
    partes = nome.strip().split()

    if len(partes) == 0:
        return ""

    resultado = [partes[0]]

    for parte in partes[1:]:
        resultado.append(parte[0].upper())

    return " ".join(resultado)


def _caminho_png(pasta, nome_arquivo):
    """Recebe pasta e nome sem extensão e retorna um caminho seguro de PNG."""
    if not isinstance(nome_arquivo, str) or not nome_arquivo:
        raise ValueError("Nome de arquivo inválido.")

    if not all(letra.isalnum() or letra in "_-" for letra in nome_arquivo):
        raise ValueError("O nome do arquivo deve conter apenas letras, números, _ e -.")

    pasta = os.path.abspath(pasta)
    caminho = os.path.join(pasta, f"{nome_arquivo}.png")
    caminho_real = os.path.realpath(caminho)

    if os.path.normcase(os.path.commonpath([pasta, caminho_real])) != os.path.normcase(pasta):
        raise ValueError("O arquivo deve permanecer dentro da pasta de destino.")

    return caminho


def _caminhos_usuario(usuario):
    """Recebe os dados do usuário e retorna os caminhos validados de seus PNGs."""
    identificador = usuario["id"]
    if not isinstance(identificador, str) or not identificador:
        raise ValueError("ID de usuário inválido.")

    return {
        "qrcode": _caminho_png(PASTA_QR, usuario["qrcode"]),
        "cartao": _caminho_png(PASTA_CARTOES, f"CARTAO_{identificador}"),
    }


def gerar_qrcode(nome_arquivo, texto):
    """Recebe nome sem extensão e texto, salva o QR Code e retorna seu caminho."""
    caminho = _caminho_png(PASTA_QR, nome_arquivo)
    os.makedirs(PASTA_QR, exist_ok=True)
    qr = qrcode.make(texto)
    qr.save(caminho)
    return caminho


def gerar_cartao(usuario):
    """Recebe os dados do usuário, salva seu cartão e retorna o caminho do PNG."""
    caminhos = _caminhos_usuario(usuario)
    os.makedirs(PASTA_CARTOES, exist_ok=True)
    largura = 750
    altura = 350
    card = Image.new("RGB", (largura, altura))
    draw = ImageDraw.Draw(card)

    cor_topo = (27, 5, 38)
    cor_base = (195, 4, 144)

    for y in range(altura):
        proporcao = y / altura
        r = int(cor_topo[0] + (cor_base[0] - cor_topo[0]) * proporcao)
        g = int(cor_topo[1] + (cor_base[1] - cor_topo[1]) * proporcao)
        b = int(cor_topo[2] + (cor_base[2] - cor_topo[2]) * proporcao)
        draw.line([(0, y), (largura, y)], fill=(r, g, b))

    try:
        font_nome = ImageFont.truetype("ariblk.ttf", 37)
        font_info = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font_nome = ImageFont.load_default()
        font_info = ImageFont.load_default()

    draw.text((50, 80), abreviar_nome(usuario["nome"]), fill="white", font=font_nome)
    draw.text((50, 160), f"Email: {usuario['email']}", fill="#B8509C", font=font_info)
    draw.text((50, 210), f"ID: {usuario['id']}", fill="#B8509C", font=font_info)
    draw.text((50, 260), f"Saldo: R${usuario['saldo']:.2f}", fill="white", font=font_info)

    with Image.open(os.path.join(BASE_DIR, "Photo", "Icon.png")) as arquivo_foto:
        foto = arquivo_foto.convert("RGBA")
        foto = foto.resize((160, 80))
        card.paste(foto, (515, 10), foto)

    with Image.open(caminhos["qrcode"]) as arquivo_qr:
        qr = arquivo_qr.resize((180, 180))
        card.paste(qr, (500, 95))

    card.save(caminhos["cartao"])
    return caminhos["cartao"]


def gerar_arquivos_usuario(usuario):
    """Recebe um usuário e retorna os caminhos do QR Code e do cartão gerados."""
    caminhos = _caminhos_usuario(usuario)
    dados_qr = (
        f"NOME: {usuario['nome']}\n"
        f"EMAIL: {usuario['email']}\n"
        f"ID: {usuario['id']}"
    )
    gerar_qrcode(usuario["qrcode"], dados_qr)
    gerar_cartao(usuario)
    return caminhos


def excluir_arquivos_usuario(usuario):
    """Recebe um usuário, exclui seus dois PNGs e retorna os caminhos removidos."""
    caminhos = _caminhos_usuario(usuario)
    removidos = []
    for caminho in caminhos.values():
        try:
            os.remove(caminho)
        except FileNotFoundError:
            continue
        removidos.append(caminho)
    return removidos
