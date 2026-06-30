"""
=============================================================================
 APEX MOTORSPORT — POPULADOR DO BANCO DE DADOS
 Usa Faker para gerar dados realistas e coerentes
 
 INSTALAÇÃO (rode uma vez no terminal):
   pip install mysql-connector-python faker

 CONFIGURAÇÃO:
   Ajuste as variáveis em CONFIGURAÇÕES abaixo (host, user, password)

 EXECUÇÃO:
   python popular_banco.py
=============================================================================
"""

import random
import math
from datetime import datetime, timedelta, date
from faker import Faker

import mysql.connector

fake = Faker("pt_BR")
random.seed(42)  # garante que os dados são reproduzíveis

# =============================================================================
#  CONFIGURAÇÕES — ajuste aqui
# =============================================================================
DB_CONFIG = {
    "host":     "127.0.0.1",
    "port":     3306,
    "user":     "root",       # <-- seu usuário MySQL
    "password": "",           # <-- sua senha MySQL
    "database": "apex_telemetria",
    "charset":  "utf8mb4",
}

VOLUME = "medio"  # "pequeno" | "medio" | "grande"

VOLUMES = {
    "pequeno": {"temporadas": 1, "eventos_por_temp": 5,  "voltas_corrida": 40, "telemetria": False},
    "medio":   {"temporadas": 2, "eventos_por_temp": 10, "voltas_corrida": 60, "telemetria": True},
    "grande":  {"temporadas": 3, "eventos_por_temp": 20, "voltas_corrida": 71, "telemetria": True},
}

CFG = VOLUMES[VOLUME]

# =============================================================================
#  HELPERS
# =============================================================================
def connect():
    return mysql.connector.connect(**DB_CONFIG)

def run(cursor, sql, vals=None):
    cursor.execute(sql, vals or ())
    return cursor.lastrowid

def run_many(cursor, sql, rows):
    cursor.executemany(sql, rows)

def rnd(a, b, decimals=2):
    return round(random.uniform(a, b), decimals)

def fmt_tempo(ms):
    m = ms // 60000
    s = (ms % 60000) // 1000
    ms_r = ms % 1000
    return f"{m}:{s:02d}.{ms_r:03d}"

# =============================================================================
#  DADOS MESTRES — Referências fixas realistas
# =============================================================================
PAISES = [
    ("BRA", "Brasil",           "América do Sul"),
    ("GBR", "Reino Unido",      "Europa"),
    ("ITA", "Itália",           "Europa"),
    ("AUT", "Áustria",          "Europa"),
    ("DEU", "Alemanha",         "Europa"),
    ("NLD", "Países Baixos",    "Europa"),
    ("MCO", "Mônaco",           "Europa"),
    ("ESP", "Espanha",          "Europa"),
    ("FRA", "França",           "Europa"),
    ("USA", "Estados Unidos",   "América do Norte"),
    ("AUS", "Austrália",        "Oceania"),
    ("JPN", "Japão",            "Ásia"),
    ("MEX", "México",           "América do Norte"),
    ("SGP", "Singapura",        "Ásia"),
    ("ARE", "Emirados Árabes",  "Ásia"),
    ("BEL", "Bélgica",          "Europa"),
    ("HUN", "Hungria",          "Europa"),
    ("BAH", "Bahrein",          "Ásia"),
    ("CAN", "Canadá",           "América do Norte"),
    ("CHN", "China",            "Ásia"),
]

EQUIPES_DATA = [
    # (nome, apelido, iso_pais, diretor, fundacao)
    ("Mercedes-AMG PETRONAS",       "Mercedes",    "GBR", "Toto Wolff",       2010),
    ("Scuderia Ferrari",            "Ferrari",     "ITA", "Fred Vasseur",     1929),
    ("Oracle Red Bull Racing",      "Red Bull",    "AUT", "Christian Horner", 2005),
    ("McLaren F1 Team",             "McLaren",     "GBR", "Andrea Stella",    1963),
    ("Aston Martin Aramco F1 Team", "Aston Martin","GBR", "Mike Krack",       2021),
    ("BWT Alpine F1 Team",          "Alpine",      "FRA", "Oliver Oakes",     1977),
    ("Williams Racing",             "Williams",    "GBR", "James Vowles",     1977),
    ("MoneyGram Haas F1 Team",      "Haas",        "USA", "Ayao Komatsu",     2016),
    ("Visa Cash App RB F1 Team",    "Racing Bulls","ITA", "Laurent Mekies",   2006),
    ("Stake F1 Team Kick Sauber",   "Sauber",      "DEU", "Mattia Binotto",   1993),
]

PILOTOS_DATA = [
    # (codigo, nome, sobrenome, iso_pais, numero, equipe_idx)
    ("HAM", "Lewis",     "Hamilton",   "GBR", 44, 1),  # Ferrari
    ("RUS", "George",    "Russell",    "GBR", 63, 0),  # Mercedes
    ("VER", "Max",       "Verstappen", "NLD",  1, 2),  # Red Bull
    ("NOR", "Lando",     "Norris",     "GBR",  4, 3),  # McLaren
    ("LEC", "Charles",   "Leclerc",    "MCO", 16, 1),  # Ferrari
    ("PIA", "Oscar",     "Piastri",    "AUS", 81, 3),  # McLaren
    ("ALO", "Fernando",  "Alonso",     "ESP", 14, 4),  # Aston
    ("STR", "Lance",     "Stroll",     "CAN", 18, 4),  # Aston
    ("GAS", "Pierre",    "Gasly",      "FRA", 10, 5),  # Alpine
    ("OCO", "Esteban",   "Ocon",       "FRA", 31, 5),  # Alpine
    ("ALB", "Alexander", "Albon",      "GBR", 23, 6),  # Williams
    ("SAR", "Logan",     "Sargeant",   "USA",  2, 6),  # Williams
    ("MAG", "Kevin",     "Magnussen",  "DNK", 20, 7),  # Haas
    ("HUL", "Nico",      "Hülkenberg", "DEU", 27, 7),  # Haas
    ("TSU", "Yuki",      "Tsunoda",    "JPN", 22, 8),  # RB
    ("LAW", "Liam",      "Lawson",     "NZL", 30, 8),  # RB
    ("BOT", "Valtteri",  "Bottas",     "FIN", 77, 9),  # Sauber
    ("ZHO", "Guanyu",    "Zhou",       "CHN", 24, 9),  # Sauber
    ("ANT", "Andrea",    "Kimi",       "ITA", 12, 0),  # Mercedes (rookie fictício)
    ("BEA", "Oliver",    "Bearman",    "GBR", 87, 1),  # Ferrari
]

CIRCUITOS_DATA = [
    # (nome, apelido, iso, cidade, comp_m, curvas, sentido, alt, lat, lon)
    ("Autódromo José Carlos Pace",   "Interlagos",   "BRA", "São Paulo",    4309, 15, "anti-horário",  785, -23.7036, -46.6975),
    ("Circuit de Monaco",            "Monaco",        "MCO", "Monte Carlo",  3337, 19, "horário",         7,  43.7347,   7.4205),
    ("Silverstone Circuit",          "Silverstone",   "GBR", "Silverstone",  5891, 18, "horário",       153,  52.0786,  -1.0169),
    ("Autodromo Nazionale Monza",    "Monza",         "ITA", "Monza",        5793, 11, "horário",       162,  45.6156,   9.2811),
    ("Circuit de Barcelona-Catalunya","Barcelona",    "ESP", "Barcelona",    4657, 16, "horário",       115,  41.5700,   2.2611),
    ("Hungaroring",                  "Budapest",      "HUN", "Budapest",     4381, 14, "horário",       264,  47.5789,  19.2486),
    ("Circuit Gilles Villeneuve",    "Montreal",      "CAN", "Montreal",     4361, 14, "anti-horário",   13,  45.5000, -73.5226),
    ("Suzuka Circuit",               "Suzuka",        "JPN", "Suzuka",       5807, 18, "misto",          40,  34.8431, 136.5411),
    ("Marina Bay Street Circuit",    "Singapura",     "SGP", "Singapura",    4940, 23, "horário",        15,   1.2914, 103.8638),
    ("Yas Marina Circuit",           "Abu Dhabi",     "ARE", "Abu Dhabi",    5281, 16, "anti-horário",    3,  24.4672,  54.6031),
    ("Spa-Francorchamps",            "Spa",           "BEL", "Spa",          7004, 20, "horário",       401,  50.4372,   5.9715),
    ("Bahrain International Circuit","Bahrein",       "BAH", "Sakhir",       5412, 15, "horário",         7,  26.0325,  50.5106),
    ("Shanghai International Circuit","Xangai",       "CHN", "Xangai",       5451, 16, "horário",         5,  31.3389, 121.2198),
    ("Circuit of The Americas",      "Austin",        "USA", "Austin",       5513, 20, "anti-horário",  161,  30.1328, -97.6411),
    ("Autodromo Hermanos Rodriguez", "Cidade do México","MEX","Cidade do México",4304,17,"horário",2240, 19.4042, -99.0907),
]

TIPOS_SENSOR_DATA = [
    # (codigo, nome, categoria, unidade, v_min, v_max, freq_hz)
    ("RPM",          "Rotação Motor",                "motor",       "rpm",    0,    20000, 200),
    ("TEMP_MOT",     "Temperatura Motor",            "motor",       "°C",     0,    200,    10),
    ("PRESS_OLEO",   "Pressão do Óleo",              "motor",       "bar",    0,     15,    50),
    ("CONSUMO",      "Consumo Combustível",          "motor",       "kg/lap", 0,      5,    10),
    ("COMBUSTIVEL",  "Nível de Combustível",         "motor",       "kg",     0,    110,     5),
    ("VELOC",        "Velocidade Linear",            "aerodinamica","km/h",   0,    400,    50),
    ("ACCEL_LONG",   "Aceleração Longitudinal",      "suspensao",   "g",     -8,      8,   200),
    ("ACCEL_LAT",    "Aceleração Lateral",           "suspensao",   "g",     -7,      7,   200),
    ("TEMP_PNEU_DD", "Temp. Pneu Dianteiro Dir",     "pneu",        "°C",     0,    150,    10),
    ("TEMP_PNEU_DE", "Temp. Pneu Dianteiro Esq",     "pneu",        "°C",     0,    150,    10),
    ("TEMP_PNEU_TD", "Temp. Pneu Traseiro Dir",      "pneu",        "°C",     0,    150,    10),
    ("TEMP_PNEU_TE", "Temp. Pneu Traseiro Esq",      "pneu",        "°C",     0,    150,    10),
    ("PRESS_PNEU_DD","Pressão Pneu Diant. Dir",      "pneu",        "psi",   15,     35,    10),
    ("PRESS_PNEU_DE","Pressão Pneu Diant. Esq",      "pneu",        "psi",   15,     35,    10),
    ("PRESS_PNEU_TD","Pressão Pneu Tras. Dir",       "pneu",        "psi",   15,     35,    10),
    ("PRESS_PNEU_TE","Pressão Pneu Tras. Esq",       "pneu",        "psi",   15,     35,    10),
    ("TEMP_FREIO_DD","Temp. Freio Dianteiro Dir",    "freio",       "°C",     0,   1200,    20),
    ("TEMP_FREIO_DE","Temp. Freio Dianteiro Esq",    "freio",       "°C",     0,   1200,    20),
    ("TEMP_FREIO_TD","Temp. Freio Traseiro Dir",     "freio",       "°C",     0,   1200,    20),
    ("TEMP_FREIO_TE","Temp. Freio Traseiro Esq",     "freio",       "°C",     0,   1200,    20),
    ("PRESS_FREIO",  "Pressão Linha de Freio",       "freio",       "bar",    0,    200,   100),
    ("VOLT_ERS",     "Tensão Bateria ERS",           "eletrico",    "V",      0,   1000,    10),
    ("CARGA_ERS",    "Carga Bateria ERS",            "eletrico",    "%",      0,    100,    10),
    ("ACELERADOR",   "Posição do Acelerador",        "motor",       "%",      0,    100,   100),
    ("FREIO_PEDAL",  "Posição do Freio",             "freio",       "%",      0,    100,   100),
    ("MARCHA",       "Marcha Engatada",              "transmissao", "n",     -1,      8,    50),
    ("DRS",          "Status DRS",                  "aerodinamica","bool",   0,      1,    10),
    ("GPS_LAT",      "Latitude GPS",                "gps",         "graus", -90,    90,    50),
    ("GPS_LON",      "Longitude GPS",               "gps",         "graus",-180,   180,    50),
    ("FREQ_CARD",    "Frequência Cardíaca",          "piloto",      "bpm",   40,    220,     1),
    ("TEMP_COCKPIT", "Temperatura Cockpit",          "piloto",      "°C",     0,     60,     5),
]

# Pontos por posição F1
PONTOS_F1 = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]

COMPOSTOS = ["slick_soft", "slick_medium", "slick_hard", "intermediario", "chuva"]
COMPOSTOS_SECO = ["slick_soft", "slick_medium", "slick_hard"]

# Tempo base por circuito em ms (referência para volta rápida realista)
TEMPO_BASE_CIRCUITO = {
    "Interlagos":      73000,
    "Monaco":          72000,
    "Silverstone":     85000,
    "Monza":           80000,
    "Barcelona":       75000,
    "Budapest":        76000,
    "Montreal":        73000,
    "Suzuka":          89000,
    "Singapura":       95000,
    "Abu Dhabi":       84000,
    "Spa":             103000,
    "Bahrein":         90000,
    "Xangai":          93000,
    "Austin":          94000,
    "Cidade do México":78000,
}

# Habilidade dos pilotos (0 = melhor, +ms = mais lento)
HABILIDADE_PILOTO = {
    "VER": 0,  "NOR": 200, "HAM": 100, "LEC": 150,
    "PIA": 300,"RUS": 350, "ALO": 400, "SAI": 450,
    "GAS": 500,"ALB": 600, "STR": 700, "HUL": 650,
    "TSU": 750,"LAW": 800, "BOT": 900, "MAG": 950,
    "ZHO":1000,"OCO": 850, "ANT":1100, "BEA":1050,
}

# =============================================================================
#  FUNÇÕES DE GERAÇÃO DE DADOS
# =============================================================================

def gerar_tempo_volta(tempo_base_ms, numero_volta, total_voltas,
                      composto, idade_pneu, combustivel_kg,
                      habilidade=0, sc_ativo=False):
    """Simula tempo de volta realista com degradação de pneu e carga de combustível."""
    t = tempo_base_ms + habilidade

    # Composto: soft é mais rápido no início, degrada mais
    offset_composto = {"slick_soft": -400, "slick_medium": 0,
                       "slick_hard": 300, "intermediario": 3000, "chuva": 7000}
    t += offset_composto.get(composto, 0)

    # Degradação: cada volta no pneu adiciona ms (soft degrada mais)
    deg_por_volta = {"slick_soft": 35, "slick_medium": 18,
                     "slick_hard": 8, "intermediario": 25, "chuva": 40}
    t += deg_por_volta.get(composto, 15) * idade_pneu

    # Efeito do combustível: ~30ms por kg (carro pesado = mais lento)
    t += combustivel_kg * 0.03 * 1000  # ms

    # Ruído aleatório ±200ms
    t += random.randint(-200, 200)

    # Safety car: todos andam lento
    if sc_ativo:
        t += random.randint(15000, 25000)

    # Garantia mínima (não pode ser absurdo)
    t = max(t, tempo_base_ms - 2000)
    return int(t)


def escolher_estrategia(total_voltas, condicao):
    """Retorna lista de (volta_pit, composto_in, composto_out)"""
    if condicao in ("molhado", "muito_molhado"):
        # Chuva: pode ter múltiplas trocas
        estrategias = [
            [(10, "chuva", "intermediario"), (35, "intermediario", "slick_medium")],
            [(15, "chuva", "intermediario")],
        ]
    else:
        meio = total_voltas // 2
        estrategias = [
            [(meio - random.randint(-3,3), "slick_medium", "slick_hard")],
            [(meio - 10, "slick_soft",   "slick_hard")],
            [(meio - 5,  "slick_medium", "slick_medium")],
            [(total_voltas//3, "slick_soft", "slick_medium"),
             (total_voltas*2//3, "slick_medium", "slick_hard")],
        ]
    return random.choice(estrategias)


# =============================================================================
#  MÓDULOS DE INSERÇÃO
# =============================================================================

def inserir_referencias(cur):
    """Paises, categorias, fabricantes já podem existir — INSERT IGNORE."""
    print("  → Países...")
    run_many(cur,
        "INSERT IGNORE INTO paises (codigo_iso, nome, continente) VALUES (%s,%s,%s)",
        PAISES)

    print("  → Categorias e temporadas...")
    run(cur, "INSERT IGNORE INTO categorias (nome, descricao) VALUES (%s,%s)",
        ("Fórmula 1", "Campeonato Mundial de Monopostos FIA"))

    print("  → Tipos de sensor...")
    for row in TIPOS_SENSOR_DATA:
        cur.execute("""
            INSERT IGNORE INTO tipos_sensor
              (codigo, nome, categoria, unidade, valor_min, valor_max, frequencia_hz)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""", row)

    print("  → Componentes regulamentados...")
    componentes = [
        ("Motor de Combustão Interna", "motor",          4000, None),
        ("Caixa de Câmbio",            "caixa_cambio",   None, 6.0),
        ("MGU-H",                      "motor_energia",  None, None),
        ("MGU-K",                      "motor_energia",  None, None),
        ("Bateria ERS",                "baterias",       None, None),
        ("Turbocompressor",            "turbo",          None, None),
        ("Unidade Eletrônica (ECU)",   "unidade_eletrica",None,None),
    ]
    run_many(cur,
        "INSERT IGNORE INTO componentes (nome, tipo, vida_util_km, vida_util_horas) VALUES (%s,%s,%s,%s)",
        componentes)


def inserir_equipes_pilotos(cur):
    """Retorna dicts com IDs para uso posterior."""
    print("  → Fabricantes...")
    fabricantes_map = {}
    fabs = [
        ("Mercedes-AMG Petronas F1", "GBR"),
        ("Scuderia Ferrari SpA",     "ITA"),
        ("Red Bull Powertrains",     "AUT"),
        ("McLaren Racing Ltd",       "GBR"),
        ("Renault Sport Racing",     "FRA"),
        ("Honda Racing Corporation", "JPN"),
        ("Aston Martin F1",          "GBR"),
    ]
    for nome, iso in fabs:
        cur.execute("SELECT id_pais FROM paises WHERE codigo_iso=%s", (iso,))
        id_pais = cur.fetchone()[0]
        cur.execute("INSERT IGNORE INTO fabricantes (nome, id_pais) VALUES (%s,%s)", (nome, id_pais))
        cur.execute("SELECT id_fabricante FROM fabricantes WHERE nome=%s", (nome,))
        fabricantes_map[nome] = cur.fetchone()[0]

    id_fab_merc = fabricantes_map["Mercedes-AMG Petronas F1"]
    id_fab_ferr = fabricantes_map["Scuderia Ferrari SpA"]
    id_fab_rb   = fabricantes_map["Red Bull Powertrains"]
    id_fab_mcl  = fabricantes_map["McLaren Racing Ltd"]

    print("  → Motores...")
    motores = [
        (id_fab_merc, "M17-EQ-Power",   "Mercedes M17 E Performance", "hibrido", 6, 1600, 1060, None),
        (id_fab_ferr, "F067-26",         "Ferrari 067/26",             "hibrido", 6, 1600, 1040, None),
        (id_fab_rb,   "RBPTH002",        "Honda RBPTH002",             "hibrido", 6, 1600, 1020, None),
        (id_fab_mcl,  "M17-MCL-Client", "Mercedes M17 (cliente)",     "hibrido", 6, 1600, 1050, None),
    ]
    for m in motores:
        cur.execute("""INSERT IGNORE INTO motores
            (id_fabricante, codigo, nome, tipo, cilindros, cilindrada_cc, potencia_cv, torque_nm)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", m)

    print("  → Equipes...")
    equipes_ids = []
    for nome, apelido, iso, diretor, fund in EQUIPES_DATA:
        cur.execute("SELECT id_pais FROM paises WHERE codigo_iso=%s", (iso,))
        row = cur.fetchone()
        if not row:
            id_pais = 1  # fallback Brasil
        else:
            id_pais = row[0]
        cur.execute("""INSERT IGNORE INTO equipes (nome, apelido, id_pais, diretor, ano_fundacao)
                       VALUES (%s,%s,%s,%s,%s)""", (nome, apelido, id_pais, diretor, fund))
        cur.execute("SELECT id_equipe FROM equipes WHERE nome=%s", (nome,))
        equipes_ids.append(cur.fetchone()[0])

    print("  → Pilotos...")
    pilotos_ids = {}
    for cod, nome, sob, iso, num, eq_idx in PILOTOS_DATA:
        cur.execute("SELECT id_pais FROM paises WHERE codigo_iso=%s", (iso,))
        row = cur.fetchone()
        id_pais = row[0] if row else 1
        id_equipe = equipes_ids[eq_idx]
        cur.execute("""INSERT IGNORE INTO pilotos
            (codigo_piloto, nome, sobrenome, id_pais, numero_carro, id_equipe)
            VALUES (%s,%s,%s,%s,%s,%s)""", (cod, nome, sob, id_pais, num, id_equipe))
        cur.execute("SELECT id_piloto FROM pilotos WHERE codigo_piloto=%s", (cod,))
        pilotos_ids[cod] = cur.fetchone()[0]

    return equipes_ids, pilotos_ids, fabricantes_map


def inserir_circuitos(cur):
    print("  → Circuitos...")
    circ_ids = {}
    for nome, apelido, iso, cidade, comp, curv, sent, alt, lat, lon in CIRCUITOS_DATA:
        cur.execute("SELECT id_pais FROM paises WHERE codigo_iso=%s", (iso,))
        row = cur.fetchone()
        id_pais = row[0] if row else 1
        cur.execute("""INSERT IGNORE INTO circuitos
            (nome, apelido, id_pais, cidade, comprimento_m, numero_curvas, sentido, altitude_m, latitude, longitude)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (nome, apelido, id_pais, cidade, comp, curv, sent, alt, lat, lon))
        cur.execute("SELECT id_circuito FROM circuitos WHERE apelido=%s", (apelido,))
        circ_ids[apelido] = cur.fetchone()[0]
    return circ_ids


def inserir_veiculos(cur, equipes_ids, fab_map):
    """Cria modelos e veículos (chassi individual por piloto por temporada)."""
    print("  → Modelos de veículo e veículos...")
    id_fab_merc = fab_map["Mercedes-AMG Petronas F1"]
    id_fab_ferr = fab_map["Scuderia Ferrari SpA"]
    id_fab_rb   = fab_map["Red Bull Powertrains"]
    id_fab_mcl  = fab_map["McLaren Racing Ltd"]
    id_fab_ren  = fab_map["Renault Sport Racing"]
    id_fab_am   = fab_map["Aston Martin F1"]

    modelos = [
        (id_fab_merc, "W17",   2026, "Fórmula 1"),
        (id_fab_ferr, "SF-26", 2026, "Fórmula 1"),
        (id_fab_rb,   "RB22",  2026, "Fórmula 1"),
        (id_fab_mcl,  "MCL40", 2026, "Fórmula 1"),
        (id_fab_ren,  "A526",  2026, "Fórmula 1"),
        (id_fab_am,   "AMR26", 2026, "Fórmula 1"),
        (id_fab_merc, "FW47",  2026, "Fórmula 1"),
        (id_fab_am,   "VF-26", 2026, "Fórmula 1"),
        (id_fab_rb,   "VCARB3",2026, "Fórmula 1"),
        (id_fab_ferr, "C46",   2026, "Fórmula 1"),
    ]
    modelo_ids = []
    for m in modelos:
        cur.execute("INSERT IGNORE INTO modelos_veiculo (id_fabricante, nome, ano_modelo, categoria) VALUES (%s,%s,%s,%s)", m)
        cur.execute("SELECT id_modelo FROM modelos_veiculo WHERE nome=%s AND ano_modelo=%s", (m[1], m[2]))
        modelo_ids.append(cur.fetchone()[0])

    # 2 veículos por equipe (um por piloto)
    veiculos_por_equipe = {}
    nomes_modelo = ["W17","SF-26","RB22","MCL40","A526","AMR26","FW47","VF-26","VCARB3","C46"]
    siglas =       ["W17", "SF26", "RB22","MCL",  "ALP", "AMR",  "FW",  "VF",   "VCB",  "C46"]
    numeros =      [(63,44),(16,87),(1,30),(4,81),(10,31),(14,18),(23,2),(27,20),(22,30),(77,24)]

    for i, (eq_id, n1, n2) in enumerate(zip(equipes_ids, [n[0] for n in numeros], [n[1] for n in numeros])):
        mid = modelo_ids[i]
        sig = siglas[i]
        veiculos_por_equipe[eq_id] = []
        for j, num in enumerate([n1, n2]):
            chassi = f"{sig}-CH{j+1:02d}-{random.randint(1000,9999)}"
            try:
                cur.execute("""INSERT INTO veiculos
                    (id_modelo, id_equipe, numero_chassi, numero_carro, data_fabricacao, status)
                    VALUES (%s,%s,%s,%s,%s,'ativo')""",
                    (mid, eq_id, chassi, num, f"2026-01-{15+j:02d}"))
                veiculos_por_equipe[eq_id].append(cur.lastrowid)
            except Exception:
                cur.execute("SELECT id_veiculo FROM veiculos WHERE numero_chassi=%s", (chassi,))
                r = cur.fetchone()
                if r:
                    veiculos_por_equipe[eq_id].append(r[0])

    return veiculos_por_equipe


def inserir_sensores(cur, veiculos_por_equipe):
    """Instala sensores em cada veículo."""
    print("  → Sensores nos veículos...")
    cur.execute("SELECT id_tipo_sensor, codigo FROM tipos_sensor")
    tipos = cur.fetchall()

    posicoes_por_sensor = {
        "RPM": "bloco motor", "TEMP_MOT": "cabeça cilindro",
        "VELOC": "chassi central", "ACCEL_LONG": "chassi central",
        "ACCEL_LAT": "chassi central", "PRESS_OLEO": "circuito de óleo",
        "TEMP_PNEU_DD": "roda dianteira dir", "TEMP_PNEU_DE": "roda dianteira esq",
        "TEMP_PNEU_TD": "roda traseira dir",  "TEMP_PNEU_TE": "roda traseira esq",
        "PRESS_PNEU_DD":"roda dianteira dir",  "PRESS_PNEU_DE":"roda dianteira esq",
        "PRESS_PNEU_TD":"roda traseira dir",   "PRESS_PNEU_TE":"roda traseira esq",
        "TEMP_FREIO_DD":"pastilha diant. dir", "TEMP_FREIO_DE":"pastilha diant. esq",
        "TEMP_FREIO_TD":"pastilha tras. dir",  "TEMP_FREIO_TE":"pastilha tras. esq",
        "PRESS_FREIO":  "cilindro mestre",     "VOLT_ERS": "bateria ERS",
        "CARGA_ERS":    "bateria ERS",         "ACELERADOR": "pedal acelerador",
        "FREIO_PEDAL":  "pedal freio",         "MARCHA": "caixa câmbio",
        "DRS": "asa traseira", "GPS_LAT": "antena GPS", "GPS_LON": "antena GPS",
        "FREQ_CARD": "assento piloto", "TEMP_COCKPIT": "painel cockpit",
        "CONSUMO": "sistema combustível", "COMBUSTIVEL": "tanque",
    }

    sensor_ids_por_veiculo = {}
    todos_veiculos = [v for vs in veiculos_por_equipe.values() for v in vs]

    for id_veiculo in todos_veiculos:
        sensor_ids_por_veiculo[id_veiculo] = []
        for id_tipo, codigo in tipos:
            pos = posicoes_por_sensor.get(codigo, "chassi")
            ns = f"SN-{id_veiculo:03d}-{id_tipo:03d}-{random.randint(1000,9999)}"
            cur.execute("""
                INSERT IGNORE INTO sensores
                  (id_veiculo, id_tipo_sensor, numero_serie, posicao, data_instalacao, ativo)
                VALUES (%s,%s,%s,%s,'2026-01-10',1)""", (id_veiculo, id_tipo, ns, pos))
            sensor_ids_por_veiculo[id_veiculo].append(cur.lastrowid or id_tipo)

    return sensor_ids_por_veiculo


def inserir_temporadas_eventos(cur, circ_ids, n_temporadas, n_eventos):
    """Cria temporadas, eventos e sessões."""
    print("  → Temporadas e eventos...")
    cur.execute("SELECT id_categoria FROM categorias WHERE nome='Fórmula 1'")
    id_cat = cur.fetchone()[0]

    temporadas_ids = []
    for offset in range(n_temporadas):
        ano = 2024 + offset
        cur.execute("INSERT IGNORE INTO temporadas (id_categoria, ano, descricao) VALUES (%s,%s,%s)",
                    (id_cat, ano, f"Campeonato Mundial F1 {ano}"))
        cur.execute("SELECT id_temporada FROM temporadas WHERE id_categoria=%s AND ano=%s", (id_cat, ano))
        temporadas_ids.append(cur.fetchone()[0])

    circuitos_lista = list(CIRCUITOS_DATA)
    random.shuffle(circuitos_lista)
    circuitos_lista = circuitos_lista[:n_eventos]

    eventos_sessoes = []  # (id_evento, id_sessao_corrida, apelido_circuito, condicao)

    ano_base = 2024
    for t_idx, id_temporada in enumerate(temporadas_ids):
        data_atual = date(ano_base + t_idx, 3, 1)

        for rodada, (nome_circ, apelido, *_) in enumerate(circuitos_lista, 1):
            id_circuito = circ_ids.get(apelido)
            if not id_circuito:
                continue

            nome_evento = f"Grande Prêmio de {apelido} {ano_base + t_idx}"
            d_ini = data_atual
            d_fim = data_atual + timedelta(days=2)

            cur.execute("""INSERT INTO eventos
                (id_temporada, id_circuito, nome, rodada, data_inicio, data_fim, status)
                VALUES (%s,%s,%s,%s,%s,%s,'concluido')""",
                (id_temporada, id_circuito, nome_evento, rodada,
                 d_ini.strftime("%Y-%m-%d"), d_fim.strftime("%Y-%m-%d")))
            id_evento = cur.lastrowid

            # Condição climática (80% seco, 20% úmido/molhado)
            condicao_roll = random.random()
            if condicao_roll < 0.7:
                condicao = "seco"
            elif condicao_roll < 0.85:
                condicao = "umido"
            else:
                condicao = "molhado"

            temp_ar    = rnd(18, 35)
            temp_pista = rnd(25, 55)
            umidade    = rnd(40, 95)
            pressao    = rnd(1005, 1020)
            vento      = rnd(5, 35)

            # Sessões do fim de semana
            sessoes_tipos = [
                ("treino_livre_1", d_ini,             "14:00:00", "16:00:00"),
                ("treino_livre_2", d_ini,             "18:00:00", "19:00:00"),
                ("treino_livre_3", d_ini+timedelta(1),"13:00:00", "14:00:00"),
                ("classificacao",  d_ini+timedelta(1),"16:00:00", "17:00:00"),
                ("corrida",        d_fim,             "15:00:00", "17:30:00"),
            ]

            id_sessao_corrida = None
            for tipo, dia, h_ini, h_fim in sessoes_tipos:
                dt_ini = datetime.strptime(f"{dia} {h_ini}", "%Y-%m-%d %H:%M:%S")
                dt_fim = datetime.strptime(f"{dia} {h_fim}", "%Y-%m-%d %H:%M:%S")
                cur.execute("""INSERT INTO sessoes
                    (id_evento, tipo, numero, data_hora_inicio, data_hora_fim,
                     condicao_pista, temperatura_ar, temperatura_pista,
                     umidade_pct, pressao_hpa, velocidade_vento_kmh)
                    VALUES (%s,%s,1,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (id_evento, tipo,
                     dt_ini.strftime("%Y-%m-%d %H:%M:%S"),
                     dt_fim.strftime("%Y-%m-%d %H:%M:%S"),
                     condicao, temp_ar, temp_pista, umidade, pressao, vento))
                if tipo == "corrida":
                    id_sessao_corrida = cur.lastrowid

            # Meteorologia ao longo do dia da corrida
            for hora in range(12, 18):
                ts = datetime(d_fim.year, d_fim.month, d_fim.day, hora, 0)
                cur.execute("""INSERT INTO meteorologia
                    (id_evento, timestamp, temperatura_ar, temperatura_pista,
                     umidade_pct, pressao_hpa, velocidade_vento_kmh, direcao_vento_graus,
                     precipitacao_mm, condicao)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (id_evento, ts.strftime("%Y-%m-%d %H:%M:%S"),
                     temp_ar + rnd(-2, 2), temp_pista + rnd(-3, 3),
                     umidade + rnd(-5, 5), pressao + rnd(-1, 1),
                     vento + rnd(-5, 5), random.randint(0, 359),
                     rnd(0, 2) if condicao != "seco" else 0.0,
                     "sol" if condicao == "seco" else "chuva_leve"))

            eventos_sessoes.append((id_evento, id_sessao_corrida, apelido, condicao))
            data_atual += timedelta(days=14)  # próximo GP em 2 semanas

    return temporadas_ids, eventos_sessoes


def inserir_corridas(cur, eventos_sessoes, pilotos_ids, equipes_ids,
                     veiculos_por_equipe, sensor_ids_por_veiculo,
                     total_voltas, inserir_telemetria):
    """Núcleo do gerador: voltas, pit stops, resultados, falhas."""

    print(f"\n  → Corridas ({len(eventos_sessoes)} eventos)...")

    # Mapeia piloto → equipe → veículo
    cur.execute("SELECT id_piloto, id_equipe FROM pilotos")
    piloto_equipe = {r[0]: r[1] for r in cur.fetchall()}

    # Lista de pilotos (código, id)
    pilotos_lista = [(cod, pid) for cod, pid in pilotos_ids.items()]

    pontos_acumulados = {pid: 0 for pid in pilotos_ids.values()}
    estatisticas     = {pid: {"vitorias":0,"poles":0,"podios":0,"vr":0}
                        for pid in pilotos_ids.values()}

    for ev_idx, (id_evento, id_sessao, apelido_circ, condicao) in enumerate(eventos_sessoes):
        print(f"     Evento {ev_idx+1}/{len(eventos_sessoes)}: {apelido_circ} ({condicao})")

        tempo_base = TEMPO_BASE_CIRCUITO.get(apelido_circ, 85000)

        # Embaralha grid (ordem de largada)
        grid = list(pilotos_lista)
        random.shuffle(grid)

        # Pole position: registra estatística
        pole_piloto_id = grid[0][1]
        estatisticas[pole_piloto_id]["poles"] += 1

        # Para cada piloto, determina veículo
        def get_veiculo(pid):
            eq = piloto_equipe.get(pid)
            vs = veiculos_por_equipe.get(eq, [])
            return random.choice(vs) if vs else None

        # Safety Car aleatório
        sc_inicio = random.randint(10, total_voltas - 15) if random.random() < 0.4 else None
        sc_fim    = (sc_inicio + random.randint(3, 6)) if sc_inicio else None

        # Abandono: ~15% dos pilotos abandonam
        abandonam = set()
        for cod, pid in pilotos_lista:
            if random.random() < 0.12:
                abandonam.add(pid)

        resultados_corrida = []
        id_voltas_por_piloto = {}

        # ---------- VOLTAS ----------
        for pos_largada, (cod, pid) in enumerate(grid, 1):
            id_veiculo = get_veiculo(pid)
            if not id_veiculo:
                continue

            hab = HABILIDADE_PILOTO.get(cod, 800)
            estrategia = escolher_estrategia(total_voltas, condicao)

            # Composto inicial
            if condicao == "seco":
                composto_atual = random.choice(["slick_soft", "slick_medium"])
            elif condicao == "umido":
                composto_atual = "intermediario"
            else:
                composto_atual = "chuva"

            # Pitstops planejados
            pits_planejados = {v: (ci, cs) for v, ci, cs in estrategia}

            combustivel = rnd(105, 110)  # kg no início
            idade_pneu = 0
            posicao_atual = pos_largada
            voltas_do_piloto = []
            abandonou_na = None

            if pid in abandonam:
                abandonou_na = random.randint(total_voltas // 4, total_voltas - 5)

            for volta_num in range(1, total_voltas + 1):
                if abandonou_na and volta_num > abandonou_na:
                    break

                sc_ativo = sc_inicio and sc_inicio <= volta_num <= sc_fim
                pit_in  = 1 if volta_num in pits_planejados else 0
                pit_out = 1 if (volta_num - 1) in pits_planejados else 0

                # Troca de pneu ao entrar no pit
                if pit_out and (volta_num - 1) in pits_planejados:
                    _, composto_atual = pits_planejados[volta_num - 1]
                    idade_pneu = 0

                if pit_in:
                    composto_entrada, composto_saida = pits_planejados[volta_num]

                t_ms = gerar_tempo_volta(
                    tempo_base, volta_num, total_voltas,
                    composto_atual, idade_pneu,
                    combustivel, hab, sc_ativo
                )

                # Pit stop adiciona tempo
                if pit_in:
                    t_ms += random.randint(18000, 28000)

                combustivel -= rnd(1.5, 2.2)
                combustivel  = max(combustivel, 0)
                idade_pneu  += 1

                valida = 0 if sc_ativo or pit_in or pit_out else 1

                cur.execute("""INSERT INTO voltas
                    (id_sessao, id_piloto, id_veiculo, numero_volta, tempo_ms, valida,
                     pit_in, pit_out, composto_pneu, idade_pneu_voltas,
                     combustivel_kg, posicao_inicio, posicao_fim)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (id_sessao, pid, id_veiculo, volta_num, t_ms, valida,
                     pit_in, pit_out, composto_atual, idade_pneu,
                     round(combustivel, 2), posicao_atual, posicao_atual))
                id_volta = cur.lastrowid
                voltas_do_piloto.append((id_volta, t_ms, valida, pit_in,
                                          composto_entrada if pit_in else None,
                                          composto_saida  if pit_in else None))

                # Setores (aprox 30/38/32% do tempo)
                for setor_num, frac in enumerate([0.30, 0.38, 0.32], 1):
                    t_setor = int(t_ms * frac + random.randint(-500, 500))
                    vmax    = rnd(200, 360)
                    cur.execute("""INSERT INTO setores_volta
                        (id_volta, numero_setor, tempo_ms, velocidade_max_kmh)
                        VALUES (%s,%s,%s,%s)""", (id_volta, setor_num, t_setor, vmax))

            id_voltas_por_piloto[pid] = voltas_do_piloto

            # ---------- PIT STOPS ----------
            for id_volta, t_ms, valida, pit_in, comp_in, comp_out in voltas_do_piloto:
                if pit_in and comp_in:
                    dur = random.randint(19000, 27000)
                    cur.execute("""INSERT INTO pit_stops
                        (id_volta, duracao_ms, troca_pneu, composto_entrada, composto_saida)
                        VALUES (%s,%s,1,%s,%s)""", (id_volta, dur, comp_in, comp_out))

        # ---------- RESULTADOS ----------
        # Classifica pilotos pelo tempo total (soma das voltas válidas)
        tempos_totais = []
        for pos_largada, (cod, pid) in enumerate(grid, 1):
            voltas = id_voltas_por_piloto.get(pid, [])
            tempo_total = sum(t for _, t, *_ in voltas)
            completou   = len(voltas)
            abandonou   = pid in abandonam
            tempos_totais.append((tempo_total, pos_largada, pid, completou, abandonou))

        tempos_totais.sort(key=lambda x: (x[4], -x[3], x[0]))  # abandono→fim, menos voltas→fim, tempo↑

        lider_tempo = tempos_totais[0][0] if tempos_totais else 0

        for pos_final, (tempo_total, pos_largada, pid, completou, abandonou) in enumerate(tempos_totais, 1):
            id_veiculo = get_veiculo(pid)
            if not id_veiculo:
                continue
            status = "abandonou" if abandonou else "finalizado"
            motivo = random.choice(["Problema mecânico", "Acidente", "Falha elétrica",
                                     "Pressão de óleo", "Sobreaquecimento"]) if abandonou else None
            pontos = PONTOS_F1[pos_final - 1] if pos_final <= 10 and not abandonou else 0

            cur.execute("""INSERT INTO resultados
                (id_sessao, id_piloto, id_veiculo, posicao_largada, posicao_final,
                 voltas_completadas, tempo_total_ms, diferenca_lider_ms,
                 pontos, volta_rapida, status_corrida, motivo_abandono)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,0,%s,%s)""",
                (id_sessao, pid, id_veiculo, pos_largada, pos_final,
                 completou, tempo_total, tempo_total - lider_tempo,
                 pontos, status, motivo))

            pontos_acumulados[pid] = pontos_acumulados.get(pid, 0) + pontos
            if pos_final == 1 and not abandonou:
                estatisticas[pid]["vitorias"] += 1
            if pos_final <= 3 and not abandonou:
                estatisticas[pid]["podios"] += 1

        # ---------- TELEMETRIA (opcional) ----------
        if inserir_telemetria:
            # Telemetria somente do vencedor para não explodir o banco
            vencedor_pid = tempos_totais[0][2] if tempos_totais else None
            if vencedor_pid:
                eq = piloto_equipe.get(vencedor_pid)
                vs = veiculos_por_equipe.get(eq, [])
                id_veiculo = vs[0] if vs else None
                if id_veiculo and id_veiculo in sensor_ids_por_veiculo:
                    sensores_ids = sensor_ids_por_veiculo[id_veiculo][:6]  # apenas 6 sensores
                    voltas_venc = id_voltas_por_piloto.get(vencedor_pid, [])[:5]  # apenas 5 voltas
                    cur.execute("SELECT id_tipo_sensor FROM sensores WHERE id_veiculo=%s", (id_veiculo,))
                    tipo_sensores = [r[0] for r in cur.fetchall()]

                    cur.execute("SELECT id_sensor FROM sensores WHERE id_veiculo=%s", (id_veiculo,))
                    sensor_real_ids = [r[0] for r in cur.fetchall()][:6]

                    if sensor_real_ids:
                        tel_rows = []
                        ts_ms = 0
                        for id_volta, _, _, _, _, _ in voltas_venc:
                            for tick in range(0, 90000, 1000):  # 1 leitura por segundo
                                for id_sensor in sensor_real_ids:
                                    val = rnd(100, 15000, 4)
                                    tel_rows.append((id_sessao, id_volta, id_veiculo,
                                                     vencedor_pid, id_sensor,
                                                     ts_ms + tick, val, 100))
                            ts_ms += 90000

                        run_many(cur, """INSERT INTO telemetria
                            (id_sessao, id_volta, id_veiculo, id_piloto, id_sensor,
                             timestamp_ms, valor, qualidade)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", tel_rows)

        # ---------- ALERTAS DE PISTA ----------
        if sc_inicio:
            ts_ini = sc_inicio * tempo_base
            ts_fim = sc_fim * tempo_base
            cur.execute("""INSERT INTO alertas_pista
                (id_sessao, tipo, timestamp_inicio_ms, timestamp_fim_ms, motivo)
                VALUES (%s,'safety_car',%s,%s,'Incidente em pista')""",
                (id_sessao, ts_ini, ts_fim))
            cur.execute("""INSERT INTO alertas_pista
                (id_sessao, tipo, timestamp_inicio_ms, timestamp_fim_ms, motivo)
                VALUES (%s,'amarelo',%s,%s,'Detritos na pista')""",
                (id_sessao, ts_ini - 5000, ts_ini))

        # ---------- FALHAS ----------
        n_falhas = random.randint(0, 4)
        sistemas = ["motor", "freios", "suspensão", "sistema elétrico",
                    "caixa câmbio", "ERS", "refrigeração", "sensor pneu"]
        descricoes = [
            "Temperatura acima do limite de alerta",
            "Pressão fora do range operacional",
            "Leitura intermitente do sensor",
            "Vibração anormal detectada",
            "Queda de tensão na bateria ERS",
            "Vazamento detectado no sistema de óleo",
        ]
        for _ in range(n_falhas):
            cod_rand, pid_rand = random.choice(pilotos_lista)
            eq = piloto_equipe.get(pid_rand)
            vs = veiculos_por_equipe.get(eq, [])
            id_veiculo_f = vs[0] if vs else None
            if id_veiculo_f:
                cur.execute("""INSERT INTO falhas
                    (id_sessao, id_veiculo, timestamp_ms, tipo, sistema, descricao,
                     valor_lido, valor_esperado, resolvida)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (id_sessao, id_veiculo_f,
                     random.randint(500000, 5000000),
                     random.choice(["critica","alta","media","baixa"]),
                     random.choice(sistemas),
                     random.choice(descricoes),
                     rnd(0, 200), rnd(0, 150), random.randint(0, 1)))

    return pontos_acumulados, estatisticas


def inserir_classificacao(cur, temporadas_ids, pilotos_ids, equipes_ids,
                          piloto_equipe, pontos_acumulados, estatisticas,
                          n_eventos):
    print("  → Classificação do campeonato...")
    cur.execute("SELECT id_piloto, id_equipe FROM pilotos")
    pe = {r[0]: r[1] for r in cur.fetchall()}

    for id_temporada in temporadas_ids:
        ranking = sorted(pontos_acumulados.items(), key=lambda x: -x[1])
        for pos, (pid, pts) in enumerate(ranking, 1):
            eq = pe.get(pid)
            if not eq:
                continue
            st = estatisticas.get(pid, {})
            cur.execute("""INSERT IGNORE INTO classificacao_campeonato
                (id_temporada, id_piloto, id_equipe, posicao, pontos_total,
                 vitorias, poles, pódios, voltas_rapidas)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (id_temporada, pid, eq, pos, round(pts, 2),
                 st.get("vitorias",0), st.get("poles",0),
                 st.get("podios",0), st.get("vr",0)))


def inserir_manutencoes(cur, veiculos_por_equipe):
    print("  → Manutenções e componentes...")
    mecanicos = ["João Silva", "Carlos Mendes", "Hans Müller", "Luigi Ferrari",
                 "James Cooper", "Pierre Dubois", "Mario Rossi", "Ahmed Al-Rashid"]
    tipos = ["preventiva","corretiva","revisao_pos_evento","troca_componente","upgrade","inspecao"]

    todos_veiculos = [v for vs in veiculos_por_equipe.values() for v in vs]
    n_por_veiculo = 3

    for id_veiculo in todos_veiculos:
        data_base = datetime(2026, 3, 1)
        for i in range(n_por_veiculo):
            d_ini = data_base + timedelta(days=14*i + random.randint(0,3))
            d_fim = d_ini + timedelta(hours=random.randint(4, 48))
            custo_est = rnd(5000, 150000)
            custo_real = custo_est * rnd(0.85, 1.2)
            cur.execute("""INSERT INTO manutencoes
                (id_veiculo, tipo, descricao, mecanico_responsavel,
                 data_inicio, data_fim, custo_estimado, custo_real, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'concluida')""",
                (id_veiculo,
                 random.choice(tipos),
                 fake.sentence(nb_words=8),
                 random.choice(mecanicos),
                 d_ini.strftime("%Y-%m-%d %H:%M:%S"),
                 d_fim.strftime("%Y-%m-%d %H:%M:%S"),
                 round(custo_est, 2), round(custo_real, 2)))


# =============================================================================
#  MAIN
# =============================================================================
def main():
    print("=" * 60)
    print("  APEX MOTORSPORT — Populador de Banco de Dados")
    print(f"  Volume: {VOLUME.upper()}")
    print("=" * 60)

    conn = connect()
    cur  = conn.cursor()

    try:
        print("\n[1/8] Referências básicas...")
        inserir_referencias(cur)
        conn.commit()

        print("\n[2/8] Equipes e pilotos...")
        equipes_ids, pilotos_ids, fab_map = inserir_equipes_pilotos(cur)
        conn.commit()

        print("\n[3/8] Circuitos...")
        circ_ids = inserir_circuitos(cur)
        conn.commit()

        print("\n[4/8] Veículos e modelos...")
        veiculos_por_equipe = inserir_veiculos(cur, equipes_ids, fab_map)
        conn.commit()

        print("\n[5/8] Sensores...")
        sensor_ids_por_veiculo = inserir_sensores(cur, veiculos_por_equipe)
        conn.commit()

        print("\n[6/8] Temporadas, eventos e sessões...")
        temporadas_ids, eventos_sessoes = inserir_temporadas_eventos(
            cur, circ_ids,
            n_temporadas=CFG["temporadas"],
            n_eventos=CFG["eventos_por_temp"]
        )
        conn.commit()

        print("\n[7/8] Corridas (voltas, resultados, pit stops, falhas)...")
        cur.execute("SELECT id_piloto, id_equipe FROM pilotos")
        piloto_equipe = {r[0]: r[1] for r in cur.fetchall()}

        pontos, stats = inserir_corridas(
            cur, eventos_sessoes, pilotos_ids, equipes_ids,
            veiculos_por_equipe, sensor_ids_por_veiculo,
            total_voltas=CFG["voltas_corrida"],
            inserir_telemetria=CFG["telemetria"]
        )
        conn.commit()

        print("\n[8/8] Classificação e manutenções...")
        inserir_classificacao(cur, temporadas_ids, pilotos_ids, equipes_ids,
                               piloto_equipe, pontos, stats,
                               CFG["eventos_por_temp"])
        inserir_manutencoes(cur, veiculos_por_equipe)
        conn.commit()

        # ---------- RESUMO ----------
        print("\n" + "=" * 60)
        print("  CONCLUÍDO! Resumo do que foi inserido:")
        print("=" * 60)
        tabelas = ["paises","equipes","pilotos","circuitos","veiculos",
                   "sensores","temporadas","eventos","sessoes","voltas",
                   "setores_volta","pit_stops","resultados","telemetria",
                   "falhas","manutencoes","meteorologia","classificacao_campeonato"]
        for t in tabelas:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            n = cur.fetchone()[0]
            print(f"  {t:<35} {n:>8} registros")
        print("=" * 60)
        print("\n  Banco pronto para análise no Power BI! 🏁")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERRO: {e}")
        import traceback; traceback.print_exc()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
