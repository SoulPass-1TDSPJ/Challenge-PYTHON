# SoulPass - Challenge Python, Sprint 4

## Integrantes

| Nome                                    | RM     |
| --------------------------------------- | ------ |
| João Vitor de Cruz Lima                 | 571277 |
| Matheus Ferreira Antônio                | 570933 |
| Sophia Silveira dos Santos              | 571932 |
| Renato da Silva Tenorio                 | 572928 |
| Renato Ruiz Ferreira Fonseca Scolamieri | 568667 |

## Vídeo

## Solução e critérios Python

O SoulPass demonstra um cartão de transporte com conversão de pontos SoulUp. A evolução mantém o terminal, QR e cartão e acrescenta persistência Oracle e clima para planejar a viagem.

- Menus: cadastro e consulta no principal; alteração e exclusão na área do usuário.
- Banco: INSERT de usuário; SELECT por e-mail/ID; UPDATE de nome; DELETE após confirmação. Saldo, pontos e embarques também ficam persistidos.
- JSON: a opção de consulta oferece exportar; o arquivo contém dados consultados no Oracle e histórico pessoal, sem senha/CPF.
- API externa: geocodificação e previsão Open-Meteo com requests, parâmetros, timeout e tratamento de erro.
- Relevância: cartão, pontos, saldo e embarques são dados do transporte; clima auxilia a planejar o deslocamento. Não há integração implementada com o front-end da equipe.
- Organização: funções com parâmetros/retornos; listas, tuplas e dicionários; validações; try/except/else/finally.

## Roteiro

| Tempo     | Mostrar e explicar                                                                                |
| --------- | ------------------------------------------------------------------------------------------------- |
| 0:00-0:30 | Nomes/RMs, sumário, tema e relação com SoulUp/transporte.                                         |
| 0:30-1:20 | Cadastrar perfil fictício, consultar e mostrar os PNGs gerados. Não mostrar a senha Oracle.       |
| 1:20-2:10 | Login, alteração do nome e nova consulta; fechar/reabrir confirma a persistência.                 |
| 2:10-3:00 | Converter 15000 pontos em R$5; realizar embarque; mostrar bloqueio de repetição e histórico.      |
| 3:00-3:40 | Exportar consulta, abrir JSON e explicar os dados relevantes.                                     |
| 3:40-4:15 | Consultar clima de São Paulo e explicar o uso da API no planejamento.                             |
| 4:15-4:50 | Explicar um SQL com bind, commit/rollback/finally; excluir o perfil fictício e conferir ausência. |
| 4:50-5:00 | Mostrar os testes e explicar a assistência registrada e as limitações do protótipo.               |

Use saldo inicial de R$10 e pelo menos 15000 pontos para demonstrar o fluxo. Prepare um CPF fictício válido. Cada integrante deve saber explicar sua participação e os trechos mostrados; não basta ler o roteiro.

## Arquivos de apoio

README.md contém instalação e menus; ALTERACOES.md aponta funções e linhas; VERIFICACAO.md registra resultados; exemplo_consulta.json é a exportação de um perfil fictício do teste real.
