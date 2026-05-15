from armazenamento import carregar_usuarios, salvar_usuarios

import os
import qrcode
import random
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Pasta dos QR Codes
PASTA_QR = os.path.join(
    BASE_DIR,
    "QRCod"
)

# Pasta dos cartões
PASTA_CARTOES = os.path.join(
    BASE_DIR,
    "Cartao_usr"
)


from PIL import Image, ImageDraw, ImageFont


# CONTROLE DE EMBARQUES
embarques = []

# CONTROLE AMBIENTAL

co2_por_pessoa = 2.3

# CARREGAR USUÁRIOS
usuarios = carregar_usuarios()

# GERAR QR CODE
def gerar_qrcode(nome_arquivo, texto):

    qr = qrcode.make(texto)
    
    caminho = os.path.join(PASTA_QR,f"{nome_arquivo}.png")

    qr.save(caminho)

    print(f"QR Code salvo como {caminho}")


# GERAR CARTÃO DIGITAL


from PIL import Image, ImageDraw, ImageFont

def gerar_cartao(usuario):
    largura = 750
    altura = 350

    # 1. Cria a imagem base vazia
    card = Image.new("RGB", (largura, altura))
    draw = ImageDraw.Draw(card)

    # 2. Definição das cores ciano (RGB)
    cor_topo = (0, 50, 70)      # Ciano Escuro
    cor_base = (0, 180, 200)    # Ciano Claro

    # 3. Desenha o fundo em degradê vertical
    for y in range(altura):
        proporcao = y / altura
        r = int(cor_topo[0] + (cor_base[0] - cor_topo[0]) * proporcao)
        g = int(cor_topo[1] + (cor_base[1] - cor_topo[1]) * proporcao)
        b = int(cor_topo[2] + (cor_base[2] - cor_topo[2]) * proporcao)
        
        draw.line([(0, y), (largura, y)], fill=(r, g, b))

    # Fontes
    try:
        font_nome = ImageFont.truetype("ariblk.ttf", 37)
        font_info = ImageFont.truetype("arial.ttf", 22)
    except:
        font_nome = ImageFont.load_default()
        font_info = ImageFont.load_default()


    # Nome
    draw.text(
        (50, 80),
        usuario["nome"],
        fill="white",
        font=font_nome
    )

    # Email
    draw.text(
        (50, 160),
        f"Email: {usuario['email']}",
        fill="#AAAAAA",
        font=font_info
    )

    # ID
    draw.text(
        (50, 210),
        f"ID: {usuario['id']}",
        fill="#AAAAAA",
        font=font_info
    )

    # Saldo
    draw.text(
        (50, 260),
        f"Saldo: R${usuario['saldo']}",
        fill="white",
        font=font_info
    )
    # IMAGEM 
   
    
    foto = Image.open("SoulUP/Photo/icon.png")
    foto = foto.convert("RGBA")              
    
    # 2. Altera o tamanho para o formato retangular mais largo (Largura=x, Altura=y)
    foto = foto.resize((160, 80))
    
    # 3. Cola no canto superior direito (X=660, Y=25) utilizando o canal Alpha como máscara
    # Como o cartão tem 800px de largura, o ícone terminará no pixel 750 (deixando 50px de margem)
    card.paste(foto, (515, 10), foto)

    
    
   # Abrir QR Code
    qr = Image.open(
     os.path.join(
        PASTA_QR,
        f"{usuario['qrcode']}.png"
    )
    )

    # Colocar QR no cartão
    qr = qr.resize((180, 180))
    card.paste(qr, (500, 95))


    nome_cartao = os.path.join(
    PASTA_CARTOES,
    f"CARTAO_{usuario['id']}.png"
)

    # Salvar cartão
    card.save(nome_cartao)

    print(
    f"Cartão salvo como {nome_cartao}"
    )




# VALIDAR CPF

def validar_cpf(cpf):

    cpf = cpf.replace(".", "").replace("-", "")

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = 0
    peso = 10

    for i in range(9):

        soma += int(cpf[i]) * peso
        peso -= 1

    resto = (soma * 10) % 11

    if resto == 10:
        resto = 0

    if resto != int(cpf[9]):
        return False

    soma = 0
    peso = 11

    for i in range(10):

        soma += int(cpf[i]) * peso
        peso -= 1

    resto = (soma * 10) % 11

    if resto == 10:
        resto = 0

    if resto != int(cpf[10]):
        return False

    return True

# MENU PRINCIPAL
while True:

    print("\n===== SOUL PASS =====")
    print("1. Cadastrar usuário")
    print("2. Login")
    print("3. Sair")

    opcao = input("Escolha uma opção: ")

    match opcao:
        
        # CADASTRO
        case "1":

            nome = input("Digite o nome: ")
            email = input("Digite o email: ")
            senha = input("Digite a senha: ")

            cpf = input("Digite o CPF: ")

            cpf = cpf.replace(".", "").replace("-", "")

            if len(cpf) != 11:

                print("CPF deve conter 11 dígitos!")
                continue

            if not validar_cpf(cpf):

                print("CPF inválido!")
                continue

            saldo = float(input("Digite o saldo: "))
            pontos = int(input("Digite os pontos: "))

            usuario_existe = False

            for usuario in usuarios:

                if (
                    usuario["email"] == email
                    or
                    usuario["cpf"] == cpf
                    ):

                    usuario_existe = True
                    break

            if usuario_existe:

                print("Email ou CPF já cadastrados!")

            else:

                # GERAR ID ÚNICA

                id_usuario = (
                    "USR_"
                    + str(random.randint(10000, 99999))
                )
                
                # QR CODE
                nome_qrcode = f"QR_{id_usuario}"

                dados_qr = (
                    f"NOME: {nome}\n"
                    f"EMAIL: {email}\n"
                    f"ID: {id_usuario}"
                )

                gerar_qrcode(
                    nome_qrcode,
                    dados_qr
                )

                # CRIAR USUÁRIO

                usuario = {

                    "id": id_usuario,
                    "nome": nome,
                    "email": email,
                    "senha": senha,
                    "cpf": cpf,
                    "qrcode": nome_qrcode,
                    "saldo": saldo,
                    "pontos": pontos
                }

                usuarios.append(usuario)

                salvar_usuarios(usuarios)
                
                # GERAR CARTÃO
                
                gerar_cartao(usuario)

                print("\nUsuário cadastrado com sucesso!")
                print(f"ID do usuário: {id_usuario}")

        # LOGIN
        case "2":

            email = input("Digite o email: ")
            senha = input("Digite a senha: ")

            login = False

            for usuario in usuarios:

                if (
                    usuario["email"] == email
                    and
                    usuario["senha"] == senha
                ):

                    login = True

                    usuario_logado = usuario

                    print(
                        f"\nBem-vindo "
                        f"{usuario_logado['nome']}"
                    )

                    while True:

                        print("\n===== ÁREA DO USUÁRIO =====")
                        print("1. Ver pontos")
                        print("2. Converter pontos")
                        print("3. Logout")
                        print("4. Realizar embarque")
                        print("5. Relatório ambiental")

                        opcao_usuario = input(
                            "Escolha: "
                        )

                        match opcao_usuario:
                            # VER PONTOS

                            case "1":

                                print(
                                    f"Você possui "
                                    f"{usuario_logado['pontos']} pontos"
                                )

                            # CONVERTER PONTOS
                            case "2":

                                pontos = int(
                                    input(
                                        "Digite os pontos: "
                                    )
                                )

                                if (
                                    pontos
                                    <=
                                    usuario_logado["pontos"]
                                ):

                                    usuario_logado["pontos"] -= pontos

                                    salvar_usuarios(usuarios)

                                    print(
                                        "Pontos convertidos!"
                                    )

                                else:

                                    print(
                                        "Pontos insuficientes!"
                                    )
                            # LOGOUT
                            case "3":

                                print("Logout realizado.")
                                break

                            # EMBARQUE
                            case "4":

                                horario = time.time()

                                if (
                                    usuario_logado["saldo"]
                                    <= 0
                                ):

                                    print(
                                        "Saldo insuficiente!"
                                    )

                                else:

                                    suspeito = False

                                    for embarque in embarques:

                                        if (
                                            embarque["cartao"]
                                            ==
                                            usuario_logado["id"]
                                        ):

                                            diferenca = (
                                                horario
                                                -
                                                embarque["horario"]
                                            )

                                            if diferenca < 120:

                                                suspeito = True

                                                print(
                                                    "Comportamento suspeito!"
                                                )

                                    embarques.append({

                                        "cartao":
                                        usuario_logado["id"],

                                        "horario":
                                        horario
                                    })

                                    usuario_logado["saldo"] -= 5

                                    salvar_usuarios(usuarios)

                                    print(
                                        "Embarque realizado!"
                                    )

                                    print(
                                        f"Saldo restante: "
                                        f"{usuario_logado['saldo']}"
                                    )

                            # RELATÓRIO AMBIENTAL
                            case "5":

                                total = len(embarques)

                                co2 = (
                                    total
                                    *
                                    co2_por_pessoa
                                )

                                print(
                                    "\n===== RELATÓRIO ====="
                                )

                                print(
                                    f"Passageiros: {total}"
                                )

                                print(
                                    f"CO2 evitado: "
                                    f"{co2:.2f} kg"
                                )

                            case _:

                                print("Opção inválida!")

                    break

            if not login:

                print("Email ou senha incorretos!")

        # SAIR
        case "3":

            print("Saindo...")
            break

        case _:

            print("Opção inválida!")