# SoulPass - Challenge Python

Protótipo de cartão digital para a SoulUp. O programa permite cadastrar usuários, consultar dados, converter pontos em uma passagem de demonstração e acompanhar os próprios embarques.

A Sprint 4 mantém os menus e as imagens da primeira versão, troca a persistência principal por Oracle, exporta consultas em JSON e consulta a API pública Open-Meteo para ajudar no planejamento da viagem.

## Executar no Windows

Testado com Python 3.12.14. Abra o PowerShell nesta pasta:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .\SoulUP\config_banco_local.py)) {
    Copy-Item .\SoulUP\config_banco_exemplo.py .\SoulUP\config_banco_local.py
}
```

O comando copy é só para a primeira configuração. Se o arquivo local já existe, preserve-o. Preencha nele seu usuário, senha e DSN Oracle. O nome salvo da conexão no SQL Developer é diferente do campo Username. Exemplo de DSN: oracle.fiap.com.br:1521/ORCL. Cada integrante usa seu próprio acesso ou o acesso combinado pela equipe.

Depois:

```bat
.venv\Scripts\python.exe SoulUP\preparar_banco.py
.venv\Scripts\python.exe SoulUP\main.py
```

A preparação cria somente as duas tabelas ausentes do projeto. Não apaga ou recria tabelas existentes. Também é possível executar sql/criar_tabelas.sql manualmente no Oracle, uma única vez. É necessário acesso à internet e permissão para criar tabelas. Os caminhos dos arquivos funcionam a partir da raiz ou da pasta SoulUP.

## Usar e demonstrar

1. Menu 1: cadastre um perfil fictício com CPF de teste válido, saldo e pontos iniciais de demonstração. E-mail é normalizado; nome, CPF, valores e duplicidades são validados.
2. Menu 2: faça login. Na área do usuário, 1 consulta saldo/pontos; 2 resgata; 4 registra embarque; 5 consulta histórico; 6 altera nome; 7 exclui após confirmação; 8 exporta JSON; 9 gera as imagens novamente; 3 sai da conta.
3. Menu 3: consulte por e-mail e escolha exportar o resultado. O JSON fica em SoulUP/Exportacoes, com dados do perfil, seus embarques e o resumo. Senha e CPF não são exportados.
4. Menu 5: consulte uma cidade. A API retorna clima atual e previsão dos próximos cinco dias. Confira cidade/estado/país, pois é utilizada a primeira localidade encontrada.
5. Menu 4: encerre o programa. Os dados ficam no Oracle e podem ser consultados ao reabrir.

Uma passagem custa 15000 pontos e acrescenta R$ 5,00 ao saldo. Cada embarque debita R$ 5,00; saldo insuficiente e repetição em menos de 120 segundos são bloqueados. Débito e histórico são confirmados juntos. Os demais prêmios continuam sendo simulações, sem entrega ou pagamento real.

O QR Code e o cartão PNG ficam em SoulUP/QRCod e SoulUP/Cartao_usr. Uma falha ao gerar imagens não desfaz uma gravação já confirmada: o menu informa isso e permite tentar novamente.

## Verificação

```bat
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes automáticos usam perfis fictícios e simulam Oracle/rede; as imagens são geradas em pastas temporárias. A integração real também foi conferida separadamente com Oracle e Open-Meteo em 30/10/2026. Consulte docs/VERIFICACAO.md e o exemplo de consulta sem dados pessoais reais em docs/exemplo_consulta.json.

## Integrantes

| Nome                                    | RM     |
| --------------------------------------- | ------ |
| João Vitor de Cruz Lima                 | 571277 |
| Matheus Ferreira Antônio                | 570933 |
| Sophia Silveira dos Santos              | 571932 |
| Renato da Silva Tenorio                 | 572928 |
| Renato Ruiz Ferreira Fonseca Scolamieri | 568667 |
