# Mapa das alterações

Referências conferidas em 30/10/2026. Os números abaixo são as linhas iniciais das funções na cópia entregue.

| Arquivo e linha | Parte e motivo |
|---|---|
| SoulUP/main.py:29 | validar_cpf rejeita letras, caracteres fora dos dígitos ASCII, sequências repetidas e verificadores incorretos sem cair no int indevido da versão anterior. |
| SoulUP/main.py:52 | validar_email confere formato básico e tamanho; os menus normalizam espaços externos e maiúsculas. |
| SoulUP/main.py:70 | validar_valores aceita vírgula no saldo, exige pontos inteiros e bloqueia negativos, NaN, infinito e valores acima das colunas SQL. |
| SoulUP/main.py:86 | gerar_identificador consulta os IDs sorteados antes do INSERT. A chave primária também impede sobrescrever usuários. |
| SoulUP/main.py:95 | atualizar_cartao informa quando o banco já salvou e só a imagem falhou. consultar_apos_gravacao, linha 107, também diferencia falha de consulta após commit. |
| SoulUP/main.py:117 | cadastrar reúne as entradas validadas num dicionário e salva no Oracle antes de gerar o cartão. |
| SoulUP/main.py:154 | exibir_usuario omite CPF e senha; consultar, linha 170, busca por e-mail e oferece a exportação. |
| SoulUP/main.py:185 | converter_pontos mantém os prêmios, mas a passagem agora acrescenta R$5 ao saldo na mesma operação que debita os pontos. Outros resgates são identificados como demonstração. |
| SoulUP/main.py:212 | embarcar usa a transação do banco e atualiza o cartão com o novo saldo. |
| SoulUP/main.py:223 | relatorio_ambiental consulta somente os embarques do usuário e identifica o CO2 como estimativa do protótipo. |
| SoulUP/main.py:236 | alterar_nome atualiza o cadastro e as imagens; excluir_conta, linha 248, pede confirmação, apaga no banco e remove somente os arquivos do perfil. |
| SoulUP/main.py:266 | mostrar_erro_banco orienta sobre login, tabelas ausentes, duplicidade e outras falhas sem imprimir credenciais. |
| SoulUP/main.py:282 | area_usuario mantém os submenus existentes, acrescenta exportação/segunda via e busca o perfil atualizado. login começa na linha 332. |
| SoulUP/main.py:346 | mostrar_clima apresenta o resultado da API e cinco dias de previsão. |
| SoulUP/main.py:359 | main concentra a execução e o tratamento de falhas; importar as funções para verificar o código não abre mais o menu automaticamente. |
| SoulUP/armazenamento.py:18 | conectar lê apenas a configuração local ignorada pelo Git; fechar_recursos, linha 29, fecha cursor/conexão em finally. |
| SoulUP/armazenamento.py:47 | consultar_usuarios retorna lista de dicionários; buscas por e-mail e ID começam nas linhas 65 e 71. Os valores entram por bind. |
| SoulUP/armazenamento.py:87 | executar_alteracao usa commit no sucesso, rollback no erro e finally para fechar recursos. |
| SoulUP/armazenamento.py:106 | INSERT do cadastro; UPDATE do nome na linha 116; DELETE por ID na linha 126. A lista inteira do JSON não é mais sobrescrita. |
| SoulUP/armazenamento.py:133 | resgatar_premio usa um único UPDATE com condição de pontos suficientes. |
| SoulUP/armazenamento.py:147 | registrar_embarque bloqueia o saldo durante a operação, exige tarifa completa, controla 120 segundos e confirma débito/histórico juntos. |
| SoulUP/armazenamento.py:189 | consultar_embarques retorna apenas o histórico do ID solicitado, inclusive após reabrir o programa. |
| SoulUP/armazenamento.py:208 | dados_publicos seleciona os campos exportáveis; exportar_consulta, linha 213, gera um JSON novo com o histórico e preserva exportações anteriores. |
| SoulUP/api_clima.py:41 | _consultar_json faz GET com parâmetros, timeout e verificação HTTP/JSON. |
| SoulUP/api_clima.py:89 | consultar_clima busca a cidade, consulta Open-Meteo e valida clima/previsão. Dicionário no resultado e lista de tuplas para os cinco dias. |
| SoulUP/cartao.py:29 | _caminho_png valida nomes e mantém os arquivos dentro da pasta correta. |
| SoulUP/cartao.py:68 | gerar_cartao preserva o visual anterior, corrige o caminho do ícone e mostra o saldo com duas casas. |
| SoulUP/cartao.py:112 | gerar_arquivos_usuario reúne QR/cartão; exclusão dos arquivos começa na linha 125. |
| SoulUP/preparar_banco.py:10 | Prepara somente as duas tabelas ausentes, sem DROP ou substituição de tabelas existentes. |
| sql/criar_tabelas.sql:3 | Tabela de usuários com chave primária, e-mail/CPF/QR únicos e saldo/pontos não negativos. |
| sql/criar_tabelas.sql:16 | Tabela de embarques relacionada ao usuário, com exclusão em cascata apenas do respectivo histórico. |
| SoulUP/config_banco_exemplo.py:1 | Modelo vazio de configuração. O arquivo local preenchido não acompanha a entrega. |
| requirements.txt:1 e .gitignore:1 | Dependências verificadas; configuração, ambiente virtual, arquivos novos de pessoas e exportações ficam fora do versionamento. |
| tests:1 | Quatro arquivos verificam regressões com unittest; são apoio de teste, separados da implementação usada nos menus. |
| README.md:1, REGISTRO_IA.md:1 e docs/ENTREGA.md:1 | Instalação, relação com as aulas, registro verdadeiro da assistência e roteiro para o vídeo ainda pendente. |

O JSON e as imagens pessoais que já estavam no repositório não foram modificados ou importados. O exemplo exportado nesta entrega usa somente um perfil fictício criado e removido no teste real.
