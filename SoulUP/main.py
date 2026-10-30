"""Menus do SoulPass: cadastro, cartão, embarques, consulta e clima."""

import random

import oracledb
from requests.exceptions import RequestException

import armazenamento
from api_clima import consultar_clima
from cartao import excluir_arquivos_usuario, gerar_arquivos_usuario


# Mantidos os prêmios e custos da primeira versão.
# Uma passagem resgatada acrescenta uma tarifa ao saldo do cartão.
PREMIOS = [
    ("Conta de Água", 10000, 0),
    ("Vale Cinema", 2000000, 0),
    ("Mochila Esportiva", 3000000, 0),
    ("Smartwatch", 50000000, 0),
    ("Passagem de ônibus", 15000, armazenamento.TARIFA),
]


def limpar_cpf(cpf):
    """Retira os separadores do CPF e retorna somente o texto normalizado."""
    return cpf.strip().replace(".", "").replace("-", "")


def validar_cpf(cpf):
    """Recebe CPF com ou sem pontuação; retorna a validade dos dois dígitos."""
    cpf = limpar_cpf(cpf)
    if len(cpf) != 11 or any(numero not in "0123456789" for numero in cpf):
        return False
    if cpf == cpf[0] * 11:
        return False

    # Calcula primeiro o dígito da posição 9, depois o da posição 10.
    for tamanho in (9, 10):
        soma = 0
        peso = tamanho + 1
        for indice in range(tamanho):
            soma += int(cpf[indice]) * peso
            peso -= 1
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if digito != int(cpf[tamanho]):
            return False
    return True


def validar_email(email):
    """Faz a validação básica de formato e tamanho do e-mail."""
    if not 3 <= len(email) <= 150 or email.count("@") != 1:
        return False
    if any(caracter.isspace() for caracter in email) or ".." in email:
        return False
    nome, dominio = email.split("@")
    return (
        bool(nome)
        and "." in dominio
        and not nome.startswith(".")
        and not nome.endswith(".")
        and not dominio.startswith(".")
        and not dominio.endswith(".")
        and all(parte for parte in dominio.split("."))
    )


def validar_valores(saldo_texto, pontos_texto):
    """Converte saldo e pontos, valida limites e retorna uma tupla com ambos."""
    try:
        saldo = float(saldo_texto.replace(",", "."))
        pontos = int(pontos_texto)
    except ValueError as erro:
        raise ValueError("Informe saldo numérico e pontos inteiros.") from erro

    # A comparação também rejeita NaN e infinito; os limites seguem o SQL.
    if not 0 <= saldo <= 9999999999.99:
        raise ValueError("Saldo inválido: use de 0 a 9999999999,99.")
    if not 0 <= pontos <= 999999999999:
        raise ValueError("Pontos inválidos: use de 0 a 999999999999.")
    return round(saldo, 2), pontos


def gerar_identificador():
    """Gera um ID livre; o banco também protege a chave contra duplicidade."""
    for tentativa in range(10):
        identificador = "USR_" + str(random.randint(10000, 99999))
        if armazenamento.buscar_usuario_por_id(identificador) is None:
            return identificador
    raise ValueError("Não foi possível gerar um ID livre. Tente cadastrar novamente.")


def atualizar_cartao(usuario):
    """Gera as imagens sem confundir falha do arquivo com falha do cadastro."""
    try:
        caminhos = gerar_arquivos_usuario(usuario)
    except (OSError, ValueError):
        print("Os dados estão salvos no banco, mas não foi possível gerar as imagens.")
        print("Use 'Gerar cartão novamente' na área do usuário para tentar depois.")
    else:
        print(f"QR Code: {caminhos['qrcode']}")
        print(f"Cartão: {caminhos['cartao']}")


def consultar_apos_gravacao(id_usuario):
    """Atualiza a tela sem apresentar uma gravação confirmada como se falhasse."""
    try:
        return armazenamento.buscar_usuario_por_id(id_usuario)
    except oracledb.Error:
        print("A alteração foi salva, mas a consulta/cartão não pôde ser atualizada agora.")
        print("Não repita a operação. Consulte seu cadastro novamente depois.")
        return None


def cadastrar():
    """Lê e valida os dados, insere no Oracle e depois gera os arquivos."""
    print("\n===== CADASTRO =====")
    nome = input("Digite o nome: ").strip()
    email = input("Digite o email: ").strip().lower()
    senha = input("Digite a senha (somente senha de teste): ")
    cpf = limpar_cpf(input("Digite o CPF: "))

    if not 1 <= len(nome) <= 100:
        raise ValueError("O nome deve conter de 1 a 100 caracteres.")
    if not validar_email(email):
        raise ValueError("Email inválido!")
    if not 4 <= len(senha) <= 128 or not senha.strip():
        raise ValueError("Senha deve ter entre 4 e 128 caracteres.")
    if not validar_cpf(cpf):
        raise ValueError("CPF inválido! Confira os 11 dígitos.")

    saldo, pontos = validar_valores(
        input("Digite o saldo inicial de demonstração: "),
        input("Digite os pontos iniciais de demonstração: "),
    )
    identificador = gerar_identificador()
    usuario = {
        "id": identificador,
        "nome": nome,
        "email": email,
        "senha": senha,
        "cpf": cpf,
        "qrcode": f"QR_{identificador}",
        "saldo": saldo,
        "pontos": pontos,
    }
    if armazenamento.cadastrar_usuario(usuario):
        print(f"Usuário cadastrado com sucesso! ID: {identificador}")
        atualizar_cartao(usuario)


def exibir_usuario(usuario):
    """Mostra a consulta sem exibir a senha ou o CPF."""
    print(f"ID: {usuario['id']}")
    print(f"Nome: {usuario['nome']}")
    print(f"Email: {usuario['email']}")
    print(f"Saldo: R$ {usuario['saldo']:.2f}")
    print(f"Pontos: {usuario['pontos']}")


def exportar(usuario):
    """Exporta o resultado da consulta e informa onde o JSON foi salvo."""
    caminho = armazenamento.exportar_consulta(usuario)
    print(f"Consulta exportada para: {caminho}")
    print("O arquivo não contém senha nem CPF.")


def consultar():
    """Consulta um e-mail no Oracle e oferece exportar o resultado em JSON."""
    email = input("Digite o email do usuário: ").strip().lower()
    if not validar_email(email):
        raise ValueError("Email inválido!")
    usuario = armazenamento.buscar_usuario_por_email(email)
    if usuario is None:
        print("Usuário não encontrado!")
        return
    print("\n===== USUÁRIO ENCONTRADO =====")
    exibir_usuario(usuario)
    if input("Exportar esta consulta em JSON? (s/n): ").strip().lower() == "s":
        exportar(usuario)


def converter_pontos(usuario):
    """Escolhe um prêmio e solicita a atualização atômica de pontos e saldo."""
    print("\n===== RESGATE DE PRÊMIOS (DEMONSTRAÇÃO) =====")
    for numero, (nome, custo, credito) in enumerate(PREMIOS, start=1):
        print(f"{numero}. {nome} - {custo} pontos")
    print("0. Voltar")
    escolha = input("Escolha o prêmio: ").strip()
    if escolha == "0":
        return
    if escolha not in ("1", "2", "3", "4", "5"):
        raise ValueError("Opção de prêmio inválida!")

    nome, custo, credito = PREMIOS[int(escolha) - 1]
    if not armazenamento.resgatar_premio(usuario["id"], custo, credito):
        print("Pontos insuficientes ou usuário não encontrado!")
        return
    print(f"Resgate de demonstração registrado: {nome}.")
    if credito:
        print(f"Crédito acrescentado ao cartão: R$ {credito:.2f}.")
    else:
        print("Demonstração acadêmica: não há entrega de produto ou pagamento real.")
    atualizado = consultar_apos_gravacao(usuario["id"])
    if atualizado is not None:
        exibir_usuario(atualizado)
        atualizar_cartao(atualizado)


def embarcar(usuario):
    """Registra o embarque no banco e atualiza o saldo exibido no cartão."""
    sucesso, mensagem = armazenamento.registrar_embarque(usuario["id"])
    print(mensagem)
    if sucesso:
        atualizado = consultar_apos_gravacao(usuario["id"])
        if atualizado is not None:
            print(f"Saldo restante: R$ {atualizado['saldo']:.2f}")
            atualizar_cartao(atualizado)


def relatorio_ambiental(usuario):
    """Consulta o histórico pessoal e calcula a estimativa usada no protótipo."""
    embarques = armazenamento.consultar_embarques(usuario["id"])
    quantidade = len(embarques)
    co2 = quantidade * armazenamento.CO2_POR_EMBARQUE
    print("\n===== MEUS EMBARQUES =====")
    for embarque in embarques:
        print(f"{embarque['horario']} - R$ {embarque['tarifa']:.2f}")
    print(f"Total de embarques: {quantidade}")
    print(f"Estimativa demonstrativa de CO2 evitado: {co2:.2f} kg.")
    print("Coeficiente fixo do protótipo: 2,3 kg por embarque; não é medição real.")


def alterar_nome(usuario):
    """Altera o nome no banco e atualiza os arquivos do usuário."""
    novo_nome = input("Digite o novo nome: ").strip()
    if armazenamento.alterar_nome_usuario(usuario["id"], novo_nome):
        print("Nome alterado com sucesso!")
        atualizado = consultar_apos_gravacao(usuario["id"])
        if atualizado is not None:
            atualizar_cartao(atualizado)
    else:
        print("Usuário não encontrado!")


def excluir_conta(usuario):
    """Pede confirmação e exclui o cadastro; retorna se deve encerrar o login."""
    confirmacao = input("Tem certeza que deseja excluir sua conta e seus embarques? (s/n): ")
    if confirmacao.strip().lower() != "s":
        print("Exclusão cancelada!")
        return False

    if not armazenamento.excluir_usuario(usuario["id"]):
        print("Usuário não encontrado!")
        return True
    print("Conta e histórico excluídos do banco.")
    try:
        excluir_arquivos_usuario(usuario)
    except (OSError, ValueError):
        print("Não foi possível remover as imagens locais. Confira QRCod e Cartao_usr.")
    return True


def mostrar_erro_banco(erro):
    """Mostra uma orientação curta, sem imprimir a configuração de conexão."""
    detalhe = erro.args[0]
    codigo = getattr(detalhe, "code", None)
    if codigo == 1017:
        print("Oracle: usuário ou senha inválidos. Confira config_banco_local.py.")
    elif codigo == 942:
        print("Tabelas não encontradas. Execute sql/criar_tabelas.sql no seu Oracle.")
    elif codigo == 1:
        print("Email, CPF ou ID já cadastrado. Nenhum cadastro existente foi substituído.")
    else:
        codigo_completo = getattr(detalhe, "full_code", "erro de conexão/operação")
        print(f"Não foi possível concluir a operação no Oracle ({codigo_completo}).")
        print("Confira a conexão e consulte o cadastro antes de repetir a operação.")


def area_usuario(id_usuario):
    """Mantém o menu do usuário e consulta dados atualizados a cada operação."""
    while True:
        try:
            usuario = armazenamento.buscar_usuario_por_id(id_usuario)
            if usuario is None:
                print("Esse cadastro não existe mais. Faça login novamente.")
                return
            print(f"\n===== ÁREA DO USUÁRIO: {usuario['nome']} =====")
            print("1. Ver pontos e saldo")
            print("2. Converter pontos")
            print("3. Logout")
            print("4. Realizar embarque")
            print("5. Relatório ambiental e histórico")
            print("6. Alterar meu nome")
            print("7. Excluir minha conta")
            print("8. Exportar minha consulta em JSON")
            print("9. Gerar cartão novamente")
            escolha = input("Escolha: ").strip()
            match escolha:
                case "1":
                    exibir_usuario(usuario)
                case "2":
                    converter_pontos(usuario)
                case "3":
                    print("Logout realizado.")
                    return
                case "4":
                    embarcar(usuario)
                case "5":
                    relatorio_ambiental(usuario)
                case "6":
                    alterar_nome(usuario)
                case "7":
                    if excluir_conta(usuario):
                        return
                case "8":
                    exportar(usuario)
                case "9":
                    atualizar_cartao(usuario)
                case _:
                    print("Opção inválida!")
        except oracledb.Error as erro:
            mostrar_erro_banco(erro)
            # Sem a consulta do perfil não podemos continuar com dados antigos.
            return
        except (ValueError, OSError) as erro:
            print(f"Operação não concluída: {erro}")


def login():
    """Confere o login no banco e abre o menu do cadastro encontrado."""
    email = input("Digite o email: ").strip().lower()
    senha = input("Digite a senha: ")
    if not validar_email(email):
        raise ValueError("Email inválido!")
    usuario = armazenamento.buscar_usuario_por_email(email)
    if usuario is None or usuario["senha"] != senha:
        print("Email ou senha incorretos!")
        return
    print(f"Bem-vindo, {usuario['nome']}!")
    area_usuario(usuario["id"])


def mostrar_clima():
    """Consulta API pública para ajudar a planejar a viagem de transporte."""
    cidade = input("Cidade para planejar sua viagem: ")
    clima = consultar_clima(cidade)
    print(f"\n===== CLIMA: {clima['cidade']} / {clima['estado']} / {clima['pais']} =====")
    print(f"Agora: {clima['temperatura']:.1f} °C - {clima['condicao']}")
    print(f"Sensação: {clima['sensacao']:.1f} °C | Umidade: {clima['umidade']}%")
    print("Previsão para os próximos cinco dias (mínima e máxima):")
    for data, minima, maxima, condicao in clima["previsoes"]:
        print(f"{data}: {minima:.1f} a {maxima:.1f} °C - {condicao}")
    print("Fonte: Open-Meteo. A busca usa a primeira cidade encontrada; confira a localização.")


def main():
    """Executa os menus; falhas de uma opção não encerram o programa inteiro."""
    print("SoulPass - protótipo acadêmico de cartão e transporte.")
    print("Use somente dados fictícios na demonstração.")
    while True:
        print("\n===== MENU PRINCIPAL =====")
        print("1. Cadastrar usuário")
        print("2. Login")
        print("3. Consultar usuário e exportar JSON")
        print("4. Sair")
        print("5. Clima para planejar a viagem")
        try:
            escolha = input("Escolha uma opção: ").strip()
            match escolha:
                case "1":
                    cadastrar()
                case "2":
                    login()
                case "3":
                    consultar()
                case "4":
                    print("Saindo...")
                    return
                case "5":
                    mostrar_clima()
                case _:
                    print("Opção inválida!")
        except oracledb.Error as erro:
            mostrar_erro_banco(erro)
        except RequestException:
            print("Não foi possível consultar o clima. Confira a internet ou tente depois.")
        except (ValueError, OSError) as erro:
            print(f"Operação não concluída: {erro}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma encerrado.")
