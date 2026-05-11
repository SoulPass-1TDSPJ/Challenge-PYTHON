
from armazenamento import carregar_usuarios, salvar_usuarios


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
                    "pontos": pontos
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

                           
                            case _:

                                print("Opcao invalida!")

                    break

         
            if not login:

                print("Email ou senha incorretos!")

       
        case "3":

            print("Saindo...")
            break

       
        case _:

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

