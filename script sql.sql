-- =============================================================================
--  APEX MOTORSPORT TELEMETRY DATABASE
--  Banco de Dados de Telemetria - Nível Empresarial
--  Versão: 1.0 | Criado para análise de dados com Power BI
-- =============================================================================
CREATE DATABASE IF NOT EXISTS apex_telemetria
  CHARACTER SET utf8mb4 /*faz desta forma para aceitar caracteres especiais*/
  COLLATE utf8mb4_unicode_ci; /*usa ci que ajuda a encontrar dados tipo Pneu e pneu sem diferenciá-los*/

USE apex_telemetria;

-- =============================================================================
--  SEÇÃO 1: TABELAS DE REFERÊNCIA / DIMENSÕES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1.1 Países
-- -----------------------------------------------------------------------------
CREATE TABLE paises (
    id_pais        SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, /*UNSIGNED garante que nunca tera numero negativo*/
    codigo_iso     CHAR(3)      NOT NULL UNIQUE, /*usa char 3 poque é alpha 3, tipo Brasil = BRA*/
    nome           VARCHAR(100) NOT NULL,
    continente     VARCHAR(50)  NOT NULL
);

-- -----------------------------------------------------------------------------
-- 1.2 Equipes / Times
-- -----------------------------------------------------------------------------
CREATE TABLE equipes (
    id_equipe      SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome           VARCHAR(100) NOT NULL UNIQUE,
    apelido        VARCHAR(30),
    id_pais        SMALLINT UNSIGNED NOT NULL,
    diretor        VARCHAR(100),
    ano_fundacao   YEAR,
    ativo          TINYINT NOT NULL DEFAULT 1, /*tinyint consome menos espaço na memoria*/
    CONSTRAINT fk_equipe_pais FOREIGN KEY (id_pais) REFERENCES paises (id_pais)
);

-- -----------------------------------------------------------------------------
-- 1.3 Pilotos
-- -----------------------------------------------------------------------------
CREATE TABLE pilotos (
    id_piloto      SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    codigo_piloto  CHAR(3)     NOT NULL UNIQUE,   -- ex: HAM, VER, LEC
    nome           VARCHAR(100) NOT NULL,
    sobrenome      VARCHAR(100) NOT NULL,
    id_pais        SMALLINT UNSIGNED NOT NULL,
    data_nascimento DATE,
    numero_carro   TINYINT UNSIGNED,
    id_equipe      SMALLINT UNSIGNED NOT NULL,
    ativo          TINYINT NOT NULL DEFAULT 1,
    CONSTRAINT fk_piloto_pais   FOREIGN KEY (id_pais)    REFERENCES paises (id_pais),
    CONSTRAINT fk_piloto_equipe FOREIGN KEY (id_equipe)  REFERENCES equipes (id_equipe)
);
-- -----------------------------------------------------------------------------
-- 1.4 Categorias de Competição
-- -----------------------------------------------------------------------------
CREATE TABLE categorias (
    id_categoria   TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome           VARCHAR(80) NOT NULL UNIQUE,   -- ex: Formula 1, Formula E, GT3
    descricao      VARCHAR(255)
);

-- -----------------------------------------------------------------------------
-- 1.5 Temporadas
-- -----------------------------------------------------------------------------
CREATE TABLE temporadas (
    id_temporada   SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_categoria   TINYINT UNSIGNED NOT NULL,
    ano            YEAR NOT NULL,
    descricao      VARCHAR(100),
    UNIQUE KEY uq_temp_cat_ano (id_categoria, ano),
    CONSTRAINT fk_temporada_cat FOREIGN KEY (id_categoria) REFERENCES categorias (id_categoria)
);

-- -----------------------------------------------------------------------------
-- 1.6 Circuitos / Pistas
-- -----------------------------------------------------------------------------
CREATE TABLE circuitos (
    id_circuito    SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome           VARCHAR(120) NOT NULL,
    apelido        VARCHAR(60),
    id_pais        SMALLINT UNSIGNED NOT NULL,
    cidade         VARCHAR(80),
    comprimento_m  DECIMAL(8,1),   -- comprimento da pista em metros
    numero_curvas  TINYINT UNSIGNED,
    sentido        ENUM('horário','anti-horário') NOT NULL DEFAULT 'horário',
    altitude_m     SMALLINT,       -- altitude média em metros
    latitude       DECIMAL(10,7),
    longitude      DECIMAL(10,7),
    ativo          TINYINT NOT NULL DEFAULT 1,
    CONSTRAINT fk_circuito_pais FOREIGN KEY (id_pais) REFERENCES paises (id_pais)
);

ALTER TABLE circuitos 
MODIFY COLUMN sentido ENUM('horário', 'anti-horário', 'misto', 'reto') NOT NULL DEFAULT 'horário';
-- -----------------------------------------------------------------------------
-- 1.7 Eventos / Grandes Prêmios
-- -----------------------------------------------------------------------------
CREATE TABLE eventos (
    id_evento      SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_temporada   SMALLINT UNSIGNED NOT NULL,
    id_circuito    SMALLINT UNSIGNED NOT NULL,
    nome           VARCHAR(120) NOT NULL,
    rodada         TINYINT UNSIGNED,
    data_inicio    DATE NOT NULL,
    data_fim       DATE NOT NULL,
    status         ENUM('agendado','em_andamento','concluido','cancelado') NOT NULL DEFAULT 'agendado',
    CONSTRAINT fk_evento_temp   FOREIGN KEY (id_temporada) REFERENCES temporadas (id_temporada),
    CONSTRAINT fk_evento_circ   FOREIGN KEY (id_circuito)  REFERENCES circuitos (id_circuito)
);

-- -----------------------------------------------------------------------------
-- 1.8 Sessões (treino livre, quali, sprint, corrida)
-- -----------------------------------------------------------------------------
CREATE TABLE sessoes (
    id_sessao      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_evento      SMALLINT UNSIGNED NOT NULL,
    tipo           ENUM('treino_livre_1','treino_livre_2','treino_livre_3',
                        'classificacao','sprint_classificacao','sprint',
                        'corrida','teste') NOT NULL, /*ENUM é usado para definir uma lista predefinida de seleções, ou seja so da pra preencher com os nomes que foram declarados*/
    numero         TINYINT UNSIGNED DEFAULT 1,
    data_hora_inicio DATETIME NOT NULL,
    data_hora_fim    DATETIME,
    condicao_pista   ENUM('seco','umido','molhado','muito_molhado') DEFAULT 'seco',
    temperatura_ar   DECIMAL(5,2),   -- °C
    temperatura_pista DECIMAL(5,2),  -- °C
    umidade_pct      DECIMAL(5,2), -- é abreviação de percentage (porcentagem)
    pressao_hpa      DECIMAL(7,2), -- hpa é abreviação de hectopascal, medida padrao, identica ao milibar
    velocidade_vento_kmh DECIMAL(5,2),
    CONSTRAINT fk_sessao_evento FOREIGN KEY (id_evento) REFERENCES eventos (id_evento)
);

-- =============================================================================
--  SEÇÃO 2: HARDWARE / VEÍCULOS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 2.1 Fabricantes
-- -----------------------------------------------------------------------------
CREATE TABLE fabricantes (
    id_fabricante  SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome           VARCHAR(80) NOT NULL UNIQUE,
    id_pais        SMALLINT UNSIGNED NOT NULL,
    CONSTRAINT fk_fab_pais FOREIGN KEY (id_pais) REFERENCES paises (id_pais)
);

-- -----------------------------------------------------------------------------
-- 2.2 Modelos de Veículo (chassi)
-- -----------------------------------------------------------------------------
CREATE TABLE modelos_veiculo (
    id_modelo      SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_fabricante  SMALLINT UNSIGNED NOT NULL,
    nome           VARCHAR(80) NOT NULL,
    ano_modelo     YEAR,
    categoria      VARCHAR(60),
    CONSTRAINT fk_modelo_fab FOREIGN KEY (id_fabricante) REFERENCES fabricantes (id_fabricante)
);

-- -----------------------------------------------------------------------------
-- 2.3 Veículos (chassi individual)
-- -----------------------------------------------------------------------------
CREATE TABLE veiculos (
    id_veiculo     SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_modelo      SMALLINT UNSIGNED NOT NULL,
    id_equipe      SMALLINT UNSIGNED NOT NULL,
    numero_chassi  VARCHAR(50) NOT NULL UNIQUE,
    numero_carro   TINYINT UNSIGNED,
    data_fabricacao DATE,
    km_total       DECIMAL(10,2) DEFAULT 0,
    status         ENUM('ativo','manutencao','aposentado','destruido') DEFAULT 'ativo',
    CONSTRAINT fk_veiculo_modelo FOREIGN KEY (id_modelo)  REFERENCES modelos_veiculo (id_modelo),
    CONSTRAINT fk_veiculo_equipe FOREIGN KEY (id_equipe)  REFERENCES equipes (id_equipe)
);

-- -----------------------------------------------------------------------------
-- 2.4 Motores
-- -----------------------------------------------------------------------------
CREATE TABLE motores (
    id_motor       SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_fabricante  SMALLINT UNSIGNED NOT NULL,
    codigo         VARCHAR(30) NOT NULL UNIQUE,
    nome           VARCHAR(80) NOT NULL,
    tipo           ENUM('combustao_interna','hibrido','eletrico') NOT NULL,
    cilindros      TINYINT UNSIGNED,
    cilindrada_cc  SMALLINT UNSIGNED,
    potencia_cv    SMALLINT UNSIGNED,
    torque_nm      SMALLINT UNSIGNED,
    CONSTRAINT fk_motor_fab FOREIGN KEY (id_fabricante) REFERENCES fabricantes (id_fabricante)
);

-- -----------------------------------------------------------------------------
-- 2.5 Especificações de Setup por Sessão
-- -----------------------------------------------------------------------------
CREATE TABLE setups_veiculo (
    id_setup       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_veiculo     SMALLINT UNSIGNED NOT NULL,
    id_sessao      INT UNSIGNED NOT NULL,
    id_piloto      SMALLINT UNSIGNED NOT NULL,
    -- Aerodinâmica
    asa_dianteira_graus   DECIMAL(5,2),
    asa_traseira_graus    DECIMAL(5,2),
    -- Suspensão
    altura_dianteira_mm   DECIMAL(6,2),
    altura_traseira_mm    DECIMAL(6,2),
    mola_dianteira_nm     DECIMAL(7,2),
    mola_traseira_nm      DECIMAL(7,2),
    -- Pneus
    composto_dianteiro    ENUM('slick_soft','slick_medium','slick_hard','intermediario','chuva') DEFAULT 'slick_medium',
    composto_traseiro     ENUM('slick_soft','slick_medium','slick_hard','intermediario','chuva') DEFAULT 'slick_medium',
    pressao_pneu_dd_psi   DECIMAL(5,2),
    pressao_pneu_de_psi   DECIMAL(5,2),
    pressao_pneu_td_psi   DECIMAL(5,2),
    pressao_pneu_te_psi   DECIMAL(5,2),
    -- Freios
    balanco_freio_pct     DECIMAL(5,2),
    -- Combustível
    carga_combustivel_kg  DECIMAL(6,2),
    observacoes           TEXT,
    criado_em             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_setup_veiculo FOREIGN KEY (id_veiculo) REFERENCES veiculos (id_veiculo),
    CONSTRAINT fk_setup_sessao  FOREIGN KEY (id_sessao)  REFERENCES sessoes (id_sessao),
    CONSTRAINT fk_setup_piloto  FOREIGN KEY (id_piloto)  REFERENCES pilotos (id_piloto)
);

-- =============================================================================
--  SEÇÃO 3: SENSORES E TELEMETRIA (CORE)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 3.1 Tipos de Sensor
-- -----------------------------------------------------------------------------
CREATE TABLE tipos_sensor (
    id_tipo_sensor SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    codigo         VARCHAR(30) NOT NULL UNIQUE,
    nome           VARCHAR(80) NOT NULL,
    categoria      ENUM('motor','transmissao','freio','suspensao','pneu',
                        'aerodinamica','eletrico','ambiente','gps','piloto') NOT NULL,
    unidade        VARCHAR(20),     -- ex: rpm, °C, bar, m/s², km/h, V
    valor_min      DECIMAL(12,4),
    valor_max      DECIMAL(12,4),
    frequencia_hz  SMALLINT UNSIGNED,  -- frequência de amostragem
    descricao      VARCHAR(255)
);

-- -----------------------------------------------------------------------------
-- 3.2 Sensores Instalados (instância física por veículo)
-- -----------------------------------------------------------------------------
CREATE TABLE sensores (
    id_sensor      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_veiculo     SMALLINT UNSIGNED NOT NULL,
    id_tipo_sensor SMALLINT UNSIGNED NOT NULL,
    numero_serie   VARCHAR(50),
    posicao        VARCHAR(60),    -- ex: "roda dianteira direita", "turbo saída"
    data_instalacao DATE,
    data_remocao    DATE,
    ativo           TINYINT NOT NULL DEFAULT 1,
    CONSTRAINT fk_sensor_veiculo FOREIGN KEY (id_veiculo)     REFERENCES veiculos (id_veiculo),
    CONSTRAINT fk_sensor_tipo   FOREIGN KEY (id_tipo_sensor)  REFERENCES tipos_sensor (id_tipo_sensor)
);

-- -----------------------------------------------------------------------------
-- 3.3 Voltas (Laps)
-- -----------------------------------------------------------------------------
CREATE TABLE voltas (
    id_volta       BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_sessao      INT UNSIGNED NOT NULL,
    id_piloto      SMALLINT UNSIGNED NOT NULL,
    id_veiculo     SMALLINT UNSIGNED NOT NULL,
    numero_volta   SMALLINT UNSIGNED NOT NULL,
    tempo_ms       INT UNSIGNED,           -- tempo da volta em milissegundos
    valida         TINYINT NOT NULL DEFAULT 1,
    pit_in         TINYINT NOT NULL DEFAULT 0,
    pit_out        TINYINT NOT NULL DEFAULT 0,
    composto_pneu  ENUM('slick_soft','slick_medium','slick_hard','intermediario','chuva'),
    idade_pneu_voltas SMALLINT UNSIGNED,
    combustivel_kg DECIMAL(6,2),
    posicao_inicio TINYINT UNSIGNED,
    posicao_fim    TINYINT UNSIGNED,
    CONSTRAINT fk_volta_sessao  FOREIGN KEY (id_sessao)  REFERENCES sessoes (id_sessao),
    CONSTRAINT fk_volta_piloto  FOREIGN KEY (id_piloto)  REFERENCES pilotos (id_piloto),
    CONSTRAINT fk_volta_veiculo FOREIGN KEY (id_veiculo) REFERENCES veiculos (id_veiculo)
);

-- -----------------------------------------------------------------------------
-- 3.4 Setores de Volta
-- -----------------------------------------------------------------------------
CREATE TABLE setores_volta (
    id_setor       BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_volta       BIGINT UNSIGNED NOT NULL,
    numero_setor   TINYINT UNSIGNED NOT NULL,   -- 1, 2 ou 3
    tempo_ms       INT UNSIGNED,
    velocidade_max_kmh DECIMAL(7,2),
    CONSTRAINT fk_setor_volta FOREIGN KEY (id_volta) REFERENCES voltas (id_volta)
);

-- -----------------------------------------------------------------------------
-- 3.5 Telemetria Bruta (série temporal de alta frequência)
--     Esta é a tabela mais volumosa — representa os dados dos sensores
--     a cada amostragem durante uma volta/sessão.
-- -----------------------------------------------------------------------------
CREATE TABLE telemetria (
    id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_sessao      INT UNSIGNED     NOT NULL,
    id_volta       BIGINT UNSIGNED,             -- NULL durante outlap ou pitstop
    id_veiculo     SMALLINT UNSIGNED NOT NULL,
    id_piloto      SMALLINT UNSIGNED NOT NULL,
    id_sensor      INT UNSIGNED     NOT NULL,
    timestamp_ms   BIGINT UNSIGNED  NOT NULL,   -- ms desde início da sessão
    valor          DECIMAL(14,6)    NOT NULL,
    qualidade      TINYINT UNSIGNED NOT NULL DEFAULT 100, -- 0-100% confiança
    CONSTRAINT fk_tel_sessao  FOREIGN KEY (id_sessao)  REFERENCES sessoes (id_sessao),
    CONSTRAINT fk_tel_veiculo FOREIGN KEY (id_veiculo) REFERENCES veiculos (id_veiculo),
    CONSTRAINT fk_tel_piloto  FOREIGN KEY (id_piloto)  REFERENCES pilotos (id_piloto),
    CONSTRAINT fk_tel_sensor  FOREIGN KEY (id_sensor)  REFERENCES sensores (id_sensor),
    INDEX idx_tel_sessao_ts  (id_sessao, timestamp_ms),
    INDEX idx_tel_volta      (id_volta),
    INDEX idx_tel_sensor     (id_sensor, timestamp_ms),
    INDEX idx_tel_veiculo_ts (id_veiculo, timestamp_ms)
);

-- -----------------------------------------------------------------------------
-- 3.6 Telemetria Agregada por Volta (snapshot resumido para Power BI)
--     Evita varrer bilhões de linhas — replica KPIs já calculados.
-- -----------------------------------------------------------------------------
CREATE TABLE telemetria_volta_resumo (
    id_resumo           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_volta            BIGINT UNSIGNED NOT NULL UNIQUE,
    -- Motor
    rpm_medio           DECIMAL(8,2),
    rpm_max             DECIMAL(8,2),
    temperatura_motor_media DECIMAL(6,2),
    temperatura_motor_max   DECIMAL(6,2),
    -- Velocidade
    velocidade_media_kmh    DECIMAL(7,2),
    velocidade_max_kmh      DECIMAL(7,2),
    -- Freios
    temperatura_freio_dd_media DECIMAL(7,2),
    temperatura_freio_de_media DECIMAL(7,2),
    temperatura_freio_td_media DECIMAL(7,2),
    temperatura_freio_te_media DECIMAL(7,2),
    pressao_freio_max_bar      DECIMAL(7,3),
    -- Pneus
    temperatura_pneu_dd_media  DECIMAL(7,2),
    temperatura_pneu_de_media  DECIMAL(7,2),
    temperatura_pneu_td_media  DECIMAL(7,2),
    temperatura_pneu_te_media  DECIMAL(7,2),
    -- G-forces
    g_longitudinal_max         DECIMAL(6,3),
    g_lateral_max              DECIMAL(6,3),
    -- Combustível
    consumo_combustivel_kg     DECIMAL(6,3),
    -- ERS / Energia (para híbridos/elétricos)
    energia_recuperada_kj      DECIMAL(10,3),
    energia_implantada_kj      DECIMAL(10,3),
    -- Direção
    angulo_volante_medio       DECIMAL(7,3),
    CONSTRAINT fk_resumo_volta FOREIGN KEY (id_volta) REFERENCES voltas (id_volta)
);

-- =============================================================================
--  SEÇÃO 4: OPERAÇÕES E ESTRATÉGIA
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 4.1 Pit Stops
-- -----------------------------------------------------------------------------
CREATE TABLE pit_stops (
    id_pitstop     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_volta       BIGINT UNSIGNED NOT NULL,
    duracao_ms     INT UNSIGNED,        -- tempo total no pit em ms
    troca_pneu     TINYINT NOT NULL DEFAULT 1,
    composto_entrada ENUM('slick_soft','slick_medium','slick_hard','intermediario','chuva'),
    composto_saida   ENUM('slick_soft','slick_medium','slick_hard','intermediario','chuva'),
    abastecimento_kg DECIMAL(6,2) DEFAULT 0,
    penalidade       TINYINT NOT NULL DEFAULT 0,
    CONSTRAINT fk_pit_volta FOREIGN KEY (id_volta) REFERENCES voltas (id_volta)
);

-- -----------------------------------------------------------------------------
-- 4.2 Alertas / Flags de Pista
-- -----------------------------------------------------------------------------
CREATE TABLE alertas_pista (
    id_alerta      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_sessao      INT UNSIGNED NOT NULL,
    tipo           ENUM('verde','amarelo','preta','preta_branca','safety_car','virtual_safety_car',
                        'bandeira_vermelha','carro_medico','drs_habilitado',
                        'drs_desabilitado') NOT NULL,
    timestamp_inicio_ms BIGINT UNSIGNED NOT NULL,
    timestamp_fim_ms    BIGINT UNSIGNED,
    motivo              VARCHAR(255),
    CONSTRAINT fk_alerta_sessao FOREIGN KEY (id_sessao) REFERENCES sessoes (id_sessao)
);

-- -----------------------------------------------------------------------------
-- 4.3 Incidentes / Penalidades
-- -----------------------------------------------------------------------------
CREATE TABLE incidentes (
    id_incidente   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_sessao      INT UNSIGNED NOT NULL,
    id_piloto      SMALLINT UNSIGNED NOT NULL,
    tipo           ENUM('colisao','toque','ultrapassagem_ilegal','ignorar_bandeira',
                        'excesso_velocidade_pit','parametro_tecnico','outro') NOT NULL,
    descricao      TEXT,
    penalidade     ENUM('nenhuma','advertencia','5_segundos','10_segundos',
                        'drive_through','stop_and_go','desclassificacao') DEFAULT 'nenhuma',
    volta_ocorrencia SMALLINT UNSIGNED,
    CONSTRAINT fk_incidente_sessao  FOREIGN KEY (id_sessao)  REFERENCES sessoes (id_sessao),
    CONSTRAINT fk_incidente_piloto  FOREIGN KEY (id_piloto)  REFERENCES pilotos (id_piloto)
);

-- -----------------------------------------------------------------------------
-- 4.4 Resultados de Corrida
-- -----------------------------------------------------------------------------
CREATE TABLE resultados (
    id_resultado   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_sessao      INT UNSIGNED NOT NULL,
    id_piloto      SMALLINT UNSIGNED NOT NULL,
    id_veiculo     SMALLINT UNSIGNED NOT NULL,
    posicao_largada   TINYINT UNSIGNED,
    posicao_final     TINYINT UNSIGNED,
    voltas_completadas SMALLINT UNSIGNED,
    tempo_total_ms    BIGINT UNSIGNED,
    diferenca_lider_ms BIGINT,
    pontos            DECIMAL(5,2) DEFAULT 0,
    volta_rapida      TINYINT(1) NOT NULL DEFAULT 0,
    status_corrida    ENUM('finalizado','nao_classificado','abandonou','desclassificado') DEFAULT 'finalizado',
    motivo_abandono   VARCHAR(120),
    CONSTRAINT fk_result_sessao  FOREIGN KEY (id_sessao)  REFERENCES sessoes (id_sessao),
    CONSTRAINT fk_result_piloto  FOREIGN KEY (id_piloto)  REFERENCES pilotos (id_piloto),
    CONSTRAINT fk_result_veiculo FOREIGN KEY (id_veiculo) REFERENCES veiculos (id_veiculo)
);

-- =============================================================================
--  SEÇÃO 5: MANUTENÇÃO E CONFIABILIDADE
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 5.1 Componentes Regulamentados (peças com limite de uso)
-- -----------------------------------------------------------------------------
CREATE TABLE componentes (
    id_componente  SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome           VARCHAR(80) NOT NULL,
    tipo           ENUM('motor','caixa_cambio','motor_energia','unidade_eletrica',
                        'baterias','turbo','radiador','outro') NOT NULL,
    vida_util_km   DECIMAL(10,2),
    vida_util_horas DECIMAL(8,2)
);

-- -----------------------------------------------------------------------------
-- 5.2 Uso de Componentes por Piloto/Temporada
-- -----------------------------------------------------------------------------
CREATE TABLE uso_componentes (
    id_uso         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_piloto      SMALLINT UNSIGNED NOT NULL,
    id_temporada   SMALLINT UNSIGNED NOT NULL,
    id_componente  SMALLINT UNSIGNED NOT NULL,
    numero_serie   VARCHAR(50),
    data_introducao DATE NOT NULL,
    km_acumulado   DECIMAL(10,2) DEFAULT 0,
    horas_acumuladas DECIMAL(8,2) DEFAULT 0,
    penalidade_grid  TINYINT NOT NULL DEFAULT 0,
    status           ENUM('em_uso','reserva','danificado','descartado') DEFAULT 'em_uso',
    CONSTRAINT fk_uso_piloto    FOREIGN KEY (id_piloto)    REFERENCES pilotos (id_piloto),
    CONSTRAINT fk_uso_temporada FOREIGN KEY (id_temporada) REFERENCES temporadas (id_temporada),
    CONSTRAINT fk_uso_comp      FOREIGN KEY (id_componente) REFERENCES componentes (id_componente)
);

-- -----------------------------------------------------------------------------
-- 5.3 Ordens de Manutenção
-- -----------------------------------------------------------------------------
CREATE TABLE manutencoes (
    id_manutencao  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_veiculo     SMALLINT UNSIGNED NOT NULL,
    tipo           ENUM('preventiva','corretiva','revisao_pos_evento',
                        'troca_componente','upgrade','inspecao') NOT NULL,
    descricao      TEXT,
    mecanico_responsavel VARCHAR(100),
    data_inicio    DATETIME NOT NULL,
    data_fim       DATETIME,
    custo_estimado DECIMAL(12,2),
    custo_real     DECIMAL(12,2),
    status         ENUM('aberta','em_progresso','concluida','cancelada') DEFAULT 'aberta',
    CONSTRAINT fk_manut_veiculo FOREIGN KEY (id_veiculo) REFERENCES veiculos (id_veiculo)
);

-- -----------------------------------------------------------------------------
-- 5.4 Falhas / Anomalias Detectadas
-- -----------------------------------------------------------------------------
CREATE TABLE falhas (
    id_falha       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_sessao      INT UNSIGNED NOT NULL,
    id_veiculo     SMALLINT UNSIGNED NOT NULL,
    id_sensor      INT UNSIGNED,
    timestamp_ms   BIGINT UNSIGNED,
    tipo           ENUM('critica','alta','media','baixa') NOT NULL DEFAULT 'media',
    sistema        VARCHAR(80),
    descricao      TEXT NOT NULL,
    valor_lido     DECIMAL(14,6),
    valor_esperado DECIMAL(14,6),
    resolvida      TINYINT NOT NULL DEFAULT 0,
    id_manutencao  INT UNSIGNED,
    CONSTRAINT fk_falha_sessao  FOREIGN KEY (id_sessao)   REFERENCES sessoes (id_sessao),
    CONSTRAINT fk_falha_veiculo FOREIGN KEY (id_veiculo)  REFERENCES veiculos (id_veiculo),
    CONSTRAINT fk_falha_sensor  FOREIGN KEY (id_sensor)   REFERENCES sensores (id_sensor),
    CONSTRAINT fk_falha_manut   FOREIGN KEY (id_manutencao) REFERENCES manutencoes (id_manutencao)
);

-- =============================================================================
--  SEÇÃO 6: METEOROLOGIA POR EVENTO
-- =============================================================================

CREATE TABLE meteorologia (
    id_meteo       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_evento      SMALLINT UNSIGNED NOT NULL,
    timestamp      DATETIME NOT NULL,
    temperatura_ar DECIMAL(5,2),
    temperatura_pista DECIMAL(5,2),
    umidade_pct    DECIMAL(5,2),
    pressao_hpa    DECIMAL(7,2),
    velocidade_vento_kmh DECIMAL(5,2),
    direcao_vento_graus  SMALLINT UNSIGNED,
    precipitacao_mm      DECIMAL(6,2) DEFAULT 0,
    condicao       ENUM('ceu_limpo','sol','nublado','parcialmente_nublado','chuva_leve',
                        'chuva_forte','tempestade') DEFAULT 'sol',
    CONSTRAINT fk_meteo_evento FOREIGN KEY (id_evento) REFERENCES eventos (id_evento),
    INDEX idx_meteo_evento_ts (id_evento, timestamp)
);

-- =============================================================================
--  SEÇÃO 7: POSICIONAMENTO GPS
-- =============================================================================

CREATE TABLE gps_posicoes (
    id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_sessao      INT UNSIGNED NOT NULL,
    id_veiculo     SMALLINT UNSIGNED NOT NULL,
    timestamp_ms   BIGINT UNSIGNED NOT NULL,
    latitude       DECIMAL(10,7) NOT NULL,
    longitude      DECIMAL(10,7) NOT NULL,
    altitude_m     DECIMAL(8,2),
    velocidade_kmh DECIMAL(7,2),
    direcao_graus  DECIMAL(6,2),
    precisao_m     DECIMAL(6,2),
    CONSTRAINT fk_gps_sessao  FOREIGN KEY (id_sessao)  REFERENCES sessoes (id_sessao),
    CONSTRAINT fk_gps_veiculo FOREIGN KEY (id_veiculo) REFERENCES veiculos (id_veiculo),
    INDEX idx_gps_sessao_ts  (id_sessao, timestamp_ms),
    INDEX idx_gps_veiculo_ts (id_veiculo, timestamp_ms)
);

-- =============================================================================
--  SEÇÃO 8: CLASSIFICAÇÃO E CAMPEONATO
-- =============================================================================

CREATE TABLE classificacao_campeonato (
    id_class       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_temporada   SMALLINT UNSIGNED NOT NULL,
    id_piloto      SMALLINT UNSIGNED NOT NULL,
    id_equipe      SMALLINT UNSIGNED NOT NULL,
    posicao        TINYINT UNSIGNED NOT NULL,
    pontos_total   DECIMAL(7,2) NOT NULL DEFAULT 0,
    vitorias       TINYINT UNSIGNED NOT NULL DEFAULT 0,
    poles          TINYINT UNSIGNED NOT NULL DEFAULT 0,
    podios         TINYINT UNSIGNED NOT NULL DEFAULT 0,
    voltas_rapidas TINYINT UNSIGNED NOT NULL DEFAULT 0,
    atualizado_em  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_class_temp_piloto (id_temporada, id_piloto),
    CONSTRAINT fk_class_temporada FOREIGN KEY (id_temporada) REFERENCES temporadas (id_temporada),
    CONSTRAINT fk_class_piloto    FOREIGN KEY (id_piloto)    REFERENCES pilotos (id_piloto),
    CONSTRAINT fk_class_equipe    FOREIGN KEY (id_equipe)    REFERENCES equipes (id_equipe)
);

-- =============================================================================
--  SEÇÃO 9: DADOS DE ENGENHARIA / DESENVOLVIMENTO
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 9.1 Canais de Telemetria Definidos (mapeamento sensor → dado analisado)
-- -----------------------------------------------------------------------------
CREATE TABLE canais_telemetria (
    id_canal       SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome           VARCHAR(80) NOT NULL UNIQUE,
    grupo          VARCHAR(60),
    id_tipo_sensor SMALLINT UNSIGNED,
    formula_calculo TEXT,     -- ex: "(sensor_a + sensor_b) / 2"
    unidade        VARCHAR(20),
    descricao      TEXT,
    CONSTRAINT fk_canal_tipo FOREIGN KEY (id_tipo_sensor) REFERENCES tipos_sensor (id_tipo_sensor)
);

-- -----------------------------------------------------------------------------
-- 9.2 Relatórios de Engenharia
-- -----------------------------------------------------------------------------
CREATE TABLE relatorios_engenharia (
    id_relatorio   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_sessao      INT UNSIGNED NOT NULL,
    id_piloto      SMALLINT UNSIGNED,
    engenheiro     VARCHAR(100) NOT NULL,
    tipo           ENUM('corrida','qualificacao','treino','pos_evento','desenvolvimento') NOT NULL,
    titulo         VARCHAR(200) NOT NULL,
    conteudo       LONGTEXT,
    versao         TINYINT UNSIGNED NOT NULL DEFAULT 1,
    criado_em      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_relat_sessao  FOREIGN KEY (id_sessao)  REFERENCES sessoes (id_sessao),
    CONSTRAINT fk_relat_piloto  FOREIGN KEY (id_piloto)  REFERENCES pilotos (id_piloto)
);
-- =============================================================================
-- SCRIPT DE POVOAMENTO COMPLETO - APEX MOTORSPORT
-- =============================================================================

USE apex_telemetria;
-- DROP DATABASE apex_telemetria;
SHOW TABLES;
SELECT * FROM resultados;
SELECT * FROM relatorios_engenharia;

CREATE OR REPLACE VIEW vw_voltas_completa AS
SELECT
    v.id_volta,
    s.id_sessao,
    e.nome                     AS evento,
    e.data_inicio              AS data_evento,
    c.nome                     AS circuito,
    c.id_pais                  AS id_pais_circuito,
    p.codigo_iso               AS pais_circuito,
    s.tipo                     AS tipo_sessao,
    s.condicao_pista,
    s.temperatura_ar           AS temp_ar_sessao,
    s.temperatura_pista        AS temp_pista_sessao,
    pi.codigo_piloto,
    CONCAT(pi.nome,' ',pi.sobrenome) AS piloto,
    eq.nome                    AS equipe,
    v.numero_volta,
    v.tempo_ms,
    ROUND(v.tempo_ms / 1000.0, 3) AS tempo_seg,
    CONCAT(
        LPAD(FLOOR(v.tempo_ms/60000),1,'0'),':',
        LPAD(FLOOR((v.tempo_ms MOD 60000)/1000),2,'0'),'.',
        LPAD(v.tempo_ms MOD 1000,3,'0')
    )                          AS tempo_fmt,
    v.valida,
    v.pit_in,
    v.pit_out,
    v.composto_pneu,
    v.idade_pneu_voltas,
    v.combustivel_kg,
    v.posicao_inicio,
    v.posicao_fim,
    t.ano                      AS temporada
FROM voltas v
JOIN sessoes    s  ON s.id_sessao   = v.id_sessao
JOIN eventos    e  ON e.id_evento   = s.id_evento
JOIN temporadas t  ON t.id_temporada = e.id_temporada
JOIN circuitos  c  ON c.id_circuito  = e.id_circuito
JOIN paises     p  ON p.id_pais      = c.id_pais
JOIN pilotos    pi ON pi.id_piloto   = v.id_piloto
JOIN equipes    eq ON eq.id_equipe   = pi.id_equipe;


#CONSULTAS
#CONSULTA 1 - Saber se quem faz manutençoes preventivas tem menos gastos com corretivas do quem nao faz ou faz menos
USE apex_telemetria;
SELECT * FROM manutencoes LIMIT 100;
SELECT DISTINCT tipo FROM manutencoes;
SELECT id_veiculo, tipo,
		SUM(custo_estimado) AS total_estimado, 
		SUM(custo_real) AS total_real, 
        SUM(custo_real) - (SUM(custo_estimado)) AS diferenca_real_estimado 
FROM manutencoes GROUP BY id_veiculo, tipo HAVING tipo='corretiva' OR tipo='preventiva';

SELECT tipo, count(*) AS quantidade FROM manutencoes GROUP BY 1;
SELECT id_veiculo, tipo, count(*) AS quantidade_preventiva FROM manutencoes WHERE tipo='preventiva' GROUP BY id_veiculo;

ALTER VIEW consulta_manutencao AS
SELECT id_veiculo, COUNT(CASE WHEN tipo='preventiva' THEN 1 END) AS quantidade_preventiva,
					COUNT(CASE WHEN tipo='corretiva' THEN 1 END) AS quantidade_corretiva,
                    SUM(CASE WHEN tipo='preventiva' THEN custo_estimado END) AS custo_estimado_preventiva,
                    SUM(CASE WHEN tipo='preventiva' THEN custo_real END) AS custo_real_preventiva,
                    SUM(CASE WHEN tipo='corretiva' THEN custo_estimado END) AS custo_estimado_corretiva,
                    SUM(CASE WHEN tipo='corretiva' THEN custo_real END) AS custo_real_corretiva,
					SUM(CASE WHEN tipo='preventiva' OR tipo='corretiva' THEN custo_estimado END) AS custo_estimado_total,
                    SUM(CASE WHEN tipo='preventiva' OR tipo='corretiva' THEN custo_real END) AS custo_real_total
FROM manutencoes GROUP BY id_veiculo;
SELECT * FROM consulta_manutencao;
SELECT AVG(custo_real_preventiva) AS media_custo_real_preventiva, 
		AVG(custo_real_corretiva) AS media_custo_real_corretiva FROM consulta_manutencao;

SELECT e.nome,v.*
FROM consulta_manutencao AS v INNER JOIN equipes AS e ON v.id_veiculo = e.id_equipe ORDER BY id_veiculo ASC;
