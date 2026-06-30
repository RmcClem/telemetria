Projeto de análise de dados com tema de automobilismo, criado para treinar SQL, modelagem de banco de dados e visualização em um cenário mais próximo de uma empresa, em vez de partir de um dataset pronto da internet.

Objetivo
O foco não foi fazer uma análise complexa, e sim explorar o processo: modelar um banco relacional, popular esse banco com dados realistas e então extrair insights. Para isso criei uma dúvida para fazer a análise:

Equipes que investem mais em manutenção preventiva gastam menos com manutenção corretiva?

Como o projeto foi construído

Modelagem do banco — Pedi ajuda ao Claude para estruturar um banco de dados MySQL (apex_telemetria) nos moldes de um ambiente corporativo.
Geração de dados sintéticos — Usei a biblioteca Faker em Python para popular o banco com dados realistas, fugindo dos datasets genéricos mais comuns.
Análise e consultas — A partir daqui, fiz o máximo possível sem gerar código com IA, resolvendo problemas e escrevendo consultas com base em documentação oficial e fóruns. O objetivo era consolidar o aprendizado na prática.

Tecnologias utilizadas

MySQL — modelagem e armazenamento dos dados
Python (Faker) — geração de dados sintéticos
Jupyter / VS Code — desenvolvimento e exploração

Estrutura do banco

O banco apex_telemetria tem 32 tabelas, organizadas em 9 seções:
Referência / Dimensões (8 tabelas) — paises, equipes, pilotos, categorias, temporadas, circuitos, eventos, sessoes
Hardware / Veículos (5 tabelas) — fabricantes, modelos_veiculo, veiculos, motores, setups_veiculo
Sensores e Telemetria (6 tabelas) — tipos_sensor, sensores, voltas, setores_volta, telemetria, telemetria_volta_resumo
Operações e Estratégia (4 tabelas) — pit_stops, alertas_pista, incidentes, resultados
Manutenção e Confiabilidade (4 tabelas) — componentes, uso_componentes, manutencoes, falhas
Meteorologia (1 tabela) — meteorologia
Posicionamento GPS (1 tabela) — gps_posicoes
Classificação e Campeonato (1 tabela) — classificacao_campeonato
Engenharia / Desenvolvimento (2 tabelas) — canais_telemetria, relatorios_engenharia

Status

Projeto de portfólio em desenvolvimento, com foco em consolidar fundamentos de SQL, modelagem de dados e BI.
