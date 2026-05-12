from armazenamento import carregar_usuarios, salvar_usuarios
import json
import qrcode
import random
import time
ARQUIVO_QRCODES = "qrcodes.json"
# Controle de embarques
embarques = []

# Controle ambiental #
co2_por_pessoa = 2.3

# Carrega usuarios #
usuarios = carregar_usuarios()

# Gerar QR Code para cada usuario
def gerar_qrcode(Texto):
    imagem = qrcode.make(Texto)
    imagem.save(f"{Texto}.png")
    print(f"QR Code para {Texto} gerado com sucesso!")
   
# =========================
# VALIDAR CPF
# =========================
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


# =========================
# GERAR CPF
# =========================
def gerar_cpf():

    numeros = []

    for i in range(9):
        numeros.append(random.randint(0, 9))

    soma = 0
    peso = 10

    for num in numeros:
        soma += num * peso
        peso -= 1

    digito1 = (soma * 10) % 11

    if digito1 == 10:
        digito1 = 0

    numeros.append(digito1)

    soma = 0
    peso = 11

    for num in numeros:
        soma += num * peso
        peso -= 1

    digito2 = (soma * 10) % 11

    if digito2 == 10:
        digito2 = 0

    numeros.append(digito2)

    cpf = ""

    for n in numeros:
        cpf += str(n)

    return cpf
    
# =========================
# GERAR CARTAO DIGITAL
# =========================

# 1. Configurações dos dados do cartão
nome = "João Silva"
contato = "E-mail: joao@email.com"
cpf = "123.456.789-00"
id_usuario = "USER_001"

#  Criar o QR Code que irá no cartão
qr = qrcode.QRCode(version=1, box_size=3, border=1) # Tamanho reduzido para caber no cartão
qr.add_data(id_usuario)
qr.make(fit=True)

# Gera o QR Code com fundo transparente e linhas brancas
img_qr = qr.make_image(fill_color="white", back_color="black").convert("RGBA")

# Criando base do cartão digital
from PIL import Image, ImageDraw, ImageFont

# Teste rápido para ver se está funcionando:
img = Image.new('RGB', (100, 30), color = (73, 109, 137))
print("Importação bem-sucedida!")

try: 
    font_nome = ImageFont.truetype("arial.ttf", 40)
    font_sub = ImageFont.truetype("arial.ttf", 22)
except IOError:
    font_nome = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    
#Elementos textuais lado esquerdo
    draw.text((60, 140), nome, fill="#FFFFFF", font=font_nome)
    draw.text((60, 200), cargo, fill="#4CAF50", font=font_sub) # Detalhe em verde
    draw.text((60, 280), contato, fill="#BBBBBB", font=font_sub)

#Linha decorativa vertical
    draw.line([(500, 100), (500, 350)], fill="#333333", width=2)

#colocar qr canto direito
    img_qr = img_qr.resize((200, 200))
    card.paste(img_qr, (540, 125), img_qr)

#Salvar o cartão digital
    card.save("cartao_digital_joao.png")
print("Cartão digital gerado com sucesso em 'cartao_digital_joao.png'!")


def salvar_qrcode(nomer_usuario,cpf ,qrcode):
    try:
        with open(
            ARQUIVO_QRCODES, "r", encoding="utf-8") as arquivo:
            
            dados = json.load(arquivo)
            
    except:
        dados = []
        novo_qrcode = {
            "nome": nomer_usuario,
            "cpf": cpf,
            "qrcode": qrcode
        }
        dados.append(novo_qrcode)
        
        
        with open(
            ARQUIVO_QRCODES, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, indent=4, ensure_ascii=False)

        with open("passageiros.json", "r", encoding="utf-8") as f:
         passageiros = json.load(f)

    encontrado = False

    for p in passageiros:

        if p["id"] == id_passageiro:
            encontrado = True

            if p.get("embarque") == True:
                print(" Já embarcou")
                return
            
            p["embarque"] = True
            p["hora_embarque"] = datetime.now().strftime("%H:%M:%S")

            print(f" Embarque liberado: {p['nome']}")
            if not encontrado:
             print(" Passageiro não encontrado")

    with open("passageiros.json", "w", encoding="utf-8") as f:
        json.dump(passageiros, f, indent=4, ensure_ascii=False)
    id_lido = input("Digite o ID do passageiro: ")
    embarque_digital(id_lido)
# =========================
# MENU PRINCIPAL
# =========================

while True:

    print("\n===== SOUL UP =====")
    print("1. Cadastrar usuario")
    print("2. Login")
    print("3. Sair")

    opcao = input("Escolha uma opcao: ")

    match opcao:

        # =========================
        # CADASTRO
        # =========================
        case "1":

            nome = input("Digite o nome: ")
            email = input("Digite o email: ")
            senha = input("Digite a senha: ")

            cpf = input("Digite o CPF: ")
            if len(cpf) > 11:
                print("Erro: O número ultrapassou o limite de 11 dígitos!")
                continue

            # 2. Verifica se faltam dígitos (opcional, mas recomendado)
            elif len(cpf) < 11:
                print("Erro: O CPF deve ter exatamente 11 dígitos!")
                continue

            

            print(f"CPF aceito e validado: {cpf}")


            if not validar_cpf(cpf):

                print("CPF invalido!")
                continue

            
            
            qrcode_usuario = (
                "QR_"
                + str(random.randint(1000, 9999))
            
            )
            gerar_qrcode(qrcode_usuario)

            saldo = float(input("Digite o saldo: "))

            pontos = int(input("Digite os pontos: "))

            email_existe = False

            for usuario in usuarios:

                if (
                    usuario["email"] == email or usuario["cpf"] == cpf):
                    email_existe = True
                    break

            if email_existe:

                print("Email ou CPF ja cadastrados!")

            else:

                usuario = {
                    "nome": nome,
                    "email": email,
                    "senha": senha,
                    "cpf": cpf,
                    "qrcode": qrcode,
                    "saldo": saldo,
                    "pontos": pontos
                }

                usuarios.append(usuario)

                salvar_usuarios(usuarios)

                print("Usuario cadastrado!")

        # =========================
        # LOGIN
        # =========================
        case "2":

            email = input("Digite o email: ")
            senha = input("Digite a senha: ")

            login = False

            for usuario in usuarios:

                if (
                    usuario["email"] == email
                    and usuario["senha"] == senha
                ):

                    login = True

                    usuario_logado = usuario

                    print(
                        f"\nBem-vindo "
                        f"{usuario_logado['nome']}"
                    )

                    while True:

                        print(
                            "\n===== AREA DO USUARIO ====="
                        )

                        print("1. Ver pontos")
                        print("2. Converter pontos")
                        print("3. Logout")
                        print("4. Realizar embarque")
                        print("5. Relatorio ambiental")

                        opcao_usuario = input(
                            "Escolha: "
                        )

                        match opcao_usuario:

                            # =========================
                            # VER PONTOS
                            # =========================
                            case "1":

                                print(
                                    f"Voce possui "
                                    f"{usuario_logado['pontos']} pontos"
                                )

                            # =========================
                            # CONVERTER PONTOS
                            # =========================
                            case "2":

                                pontos = int(
                                    input(
                                        "Digite os pontos: "
                                    )
                                )

                                if (
                                    pontos
                                    <= usuario_logado["pontos"]
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

                            # =========================
                            # LOGOUT
                            # =========================
                            case "3":

                                print("Logout realizado.")
                                break

                            # =========================
                            # EMBARQUE
                            # =========================
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
                                            usuario_logado["cartao"]
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
                                        usuario_logado["cartao"],

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

                            # =========================
                            # RELATORIO AMBIENTAL
                            # =========================
                            case "5":

                                total = len(embarques)

                                co2 = (
                                    total
                                    * co2_por_pessoa
                                )

                                print(
                                    "\n===== RELATORIO ====="
                                )

                                print(
                                    f"Passageiros: {total}"
                                )

                                print(
                                    f"CO2 evitado: "
                                    f"{co2:.2f} kg"
                                )

                            case _:

                                print("Opcao invalida!")

                    break

            if not login:

                print("Email ou senha incorretos!")

        # =========================
        # SAIR
        # =========================
        case "3":

            print("Saindo...")
            break

        case _:

            print("Opcao invalida!")