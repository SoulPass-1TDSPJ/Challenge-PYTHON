
from armazenamento import carregar_usuarios, salvar_usuarios

import time
#controle de embarque
embarque = []
#controle ambiental
co2_por_pessoa = 2.3  

# Carrega os usuarios salvos no sistema
usuarios = carregar_usuarios()



while True:

    # Menu 
    print("\n===== SOUL UP =====")
    print("1. Cadastrar usuario")
    print("2. Login")
    print("3. Sair")


    opcao = input("Escolha uma opcao: ")

  
    match opcao:

   
        case "1":

            # Entrada de dados do usuario
            nome = input("Digite o nome do usuario: ")
            email = input("Digite o email do usuario: ")
            senha = input("Digite a senha do usuario: ")
            
            def validar_cpf(cpf):

    # Remove caracteres
        cpf = cpf.replace(".", "").replace("-", "")

    # Verifica tamanho
    if len(cpf) != 11:
        return False

    # Verifica se todos os números são iguais
    if cpf == cpf[0] * 11:
        return False

   
    # Primeiro dígito


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

    
    # Segundo dígito
    

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

cpf = input("Digite o CPF: ")

if validar_cpf(cpf):
    print("CPF válido")
else:
    print("CPF inválido")

import random

def gerar_cpf():

    numeros = []

    for i in range(9):
        numeros.append(random.randint(0, 9))

    # Primeiro dígito
    soma = 0
    peso = 10

    for num in numeros:
        soma += num * peso
        peso -= 1

    digito1 = (soma * 10) % 11

    if digito1 == 10:
        digito1 = 0

    numeros.append(digito1)

    # Segundo dígito
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

    cpf = gerar_cpf()

print("CPF gerado:", cpf)

def formatar_cpf(cpf):

    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

cpf = gerar_cpf()

print("CPF:", formatar_cpf(cpf))

if validar_cpf(cpf):
    print("CPF válido")

    usuarios = []

cpf = input("CPF: ")

if validar_cpf(cpf):

    nome = input("Nome: ")

    usuario = {
        "cpf": cpf,
        "nome": nome
    }

    usuarios.append(usuario)

    print("Usuário cadastrado")

else:
    print("CPF inválido")

    
            # Entrada dos pontos iniciais
                pontos = int(
                input("Digite os pontos do usuario: ")
            )

          
            email_existe = False

         
            for usuario in usuarios:

          
                if usuario["email"] == email:

                    email_existe = True
                    break

          
            if email_existe:

                print("Email ja cadastrado!")

         
            else:

              
                usuario = {
                    "nome": nome,
                    "email": email,
                    "senha": senha,
                    "pontos": pontos,
                    "cpf": cpf,
                    "cartao": cartao,
                    "qrcode": qrcode,
                    "saldo": saldo
                }

              
                usuarios.append(usuario)

             
                salvar_usuarios(usuarios)

                print("Usuario cadastrado com sucesso!")

     
        case "2":

            # Entrada do login
            email = input("Digite o email: ")
            senha = input("Digite a senha: ")

          
            login = False

           
            for usuario in usuarios:

                if (
                    usuario["email"] == email
                    and usuario["cpf"] == cpf
                    and usuario["senha"] == senha
                ):

                    print(
                        f"\nBem-vindo {usuario['nome']}!"
                    )

                    login = True

                   
                    usuario_logado = usuario

                 
                    while True:

                        print(
                            "\n===== AREA DO USUARIO ====="
                        )

                        print("1. Ver pontos")
                        print("2. Converter pontos")
                        print("3. Logout")
                        print("4. Realizar embarque")
                        print("5. Relatorio de impacto ambiental")

                     
                        opcao_usuario = input(
                            "Escolha uma opcao: "
                        )

                      
                        match opcao_usuario:

                          
                            case "1":

                                print(
                                    f"Voce possui "
                                    f"{usuario_logado['pontos']} pontos."
                                )

                           
                            case "2":

                               
                                pontos = int(
                                    input(
                                        "Digite os pontos "
                                        "a serem convertidos: "
                                    )
                                )

                              
                                if (
                                    pontos
                                    <= usuario_logado["pontos"]
                                ):

                                   
                                    usuario_logado["pontos"] -= pontos

                                  
                                    salvar_usuarios(usuarios)

                                    print(
                                        "Pontos convertidos "
                                        "com sucesso!"
                                    )

                                    print(
                                        f"Saldo atual: "
                                        f"{usuario_logado['pontos']} pontos"
                                    )

                                else:

                                    print(
                                        "Pontos insuficientes!"
                                    )

                            
                            case "3":

                                print("Logout realizado.")

                                break

                           
                            case "4":

                                print("Opcao invalida!")
                                
                                horario= time.time()
                                # Verficia saldo 
                                if usuario_logado["saldo"] > 0:
                                    print("Embarque negado! Saldo insuficiente.")
                                else:
                                    suspeito = False
                                    #verifica uso repetido do cartao
                                    for embarque in embarque:
                                        if (
                                            embarque["cartao"]
                                            == usuario_logado["cartao"]
                                        
                                        ):
                                            diferenca = horario - embarque["horario"]
                                            if diferenca < 120:  # 2 minutos
                                                suspeito = True
                                                print("comportamento supeito detectado! Embarque negado.")
                                                embarque.append({
                                                    "cartao": usuario_logado["cartao"],
                                                    "horario": horario
                                                })
                                                usario_logado["saldo"] -= 5
                                                salvar_usuarios(usuarios)
                                                print("embarque registrado, mas saldo penalizado em 5 pontos.")
                                                print(
                                                    f"Saldo atual: {usuario_logado['saldo']} pontos"
                                                )
                            case "5":
                                total_embarques = len(embarque)
                                co2_evitado = ( total_embarques * co2_por_pessoa )
                                print("\n===== RELATORIO DE IMPACTO AMBIENTAL =====")
                                print(f"total de passageiros:  "
                                      f"{total_embarques}")
                                print(f"CO2 evitado: {co2_evitado:.2f} kg")
                                  

                    break

         
            if not login:

                print("Email ou senha incorretos!")

       
        case "3":

            print("Saindo...")
            break

       
        case "4":

            print("Opcao invalida!")
    

# "tabela" de cupons válidos
cupons = {
    "DESCONTO10": 10,   # código: porcentagem de desconto
    "PROMO20": 20,
    "VIP50": 50
}

def aplicar_cupom(valor_total):
    codigo = input("Digite o cupom (ou ENTER para pular): ").upper()
    
    if codigo == "":
        return valor_total  # sem cupom, retorna valor original
    
    if codigo in cupons:
        desconto = cupons[codigo]
        valor_desconto = valor_total * (desconto / 100)
        valor_final = valor_total - valor_desconto
        print(f"Cupom válido! {desconto}% de desconto.")
        print(f"Desconto: R$ {valor_desconto:.2f}")
        print(f"Valor final: R$ {valor_final:.2f}")
        return valor_final
    else:
        print("Cupom inválido!")
        return valor_total     
        

