from armazenamento import carregar_usuarios, salvar_usuarios
usuarios = carregar_usuarios()
while True:
    print("\n===== SOUL UP =====")
    print("1. Cadastrar usuário")
    print("2. Listar usuários")
    print("3. Converter pontos")
    print("4. Sair")
    
    opcao= input("Escolha uma opção: ")
    
    match opcao:
        case "1":
            #Validacao de nome, email e pontos
            nome = input("Digite o nome do usuário: ")
            email = input("Digite o email do usuário: ")
            pontos = int(input("Digite os pontos do usuário: "))
            # Verificar se o email já está cadastrado
            for usuario in usuarios:
                if usuario["email"] == email:
                    print("Email já cadastrado.")
                    break
            else:
                usuario = {"nome": nome, "email": email, "pontos": pontos}
                usuarios.append(usuario)
                salvar_usuarios(usuarios)
            print("Usuário cadastrado com sucesso!") 
        case "2":
            if len(usuarios) == 0:
                print("Nenhum usuário cadastrado.")
            else:
                print("Usuários cadastrados:")
                for usuario in usuarios:
                    print(f"Nome: {usuario['nome']}, Email: {usuario['email']}, Pontos: {usuario['pontos']}")
        case "3":
            if len(usuarios) == 0:
                print("Nenhum usuário cadastrado.")
            else:
                email = input("Digite o email do usuário: ")
                for usuario in usuarios:
                    if usuario["email"] == email:
                        pontos = int(input("Digite os pontos a serem convertidos: "))
                        if pontos <= usuario["pontos"]:
                            usuario["pontos"] -= pontos
                            print("Pontos convertidos com sucesso!")
                        else:
                            print("Pontos insuficientes.")
                        break
                else:
                    print("Usuário não encontrado.")
        case "4":
            print("Saindo...")
            break
        case _:
            print("Opção inválida.")


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

        