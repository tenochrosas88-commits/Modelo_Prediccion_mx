import requests
import mysql.connector

# ======================
# CONFIGURACIÓN API
# ======================
API_KEY = "7636d7a2fa912589feddd1ffbc029d7e"
BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

# ======================
# CONFIGURACIÓN BD
# ======================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Tenoch2504.",
    "database": "futbol_analitica"
}

# ======================
# LIGAS A PROCESAR
# ======================
LIGAS = {
    "Premier League": 39,
    "La Liga": 140,
    "Serie A": 135,
    "Bundesliga": 78,
    "Ligue 1": 61,
    "Liga MX": 262,
    "Champions League": 2
}

# ======================
# CONEXIÓN BD
# ======================
def conectar_bd():
    return mysql.connector.connect(**DB_CONFIG)

# ======================
# ASEGURAR LIGA
# ======================
def asegurar_liga(api_liga_id):
    r = requests.get(
        f"{BASE_URL}/leagues",
        headers=HEADERS,
        params={"id": api_liga_id}
    )
    r.raise_for_status()
    liga = r.json()["response"][0]

    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT IGNORE INTO ligas (api_liga_id, nombre, pais)
        VALUES (%s, %s, %s)
    """, (
        liga["league"]["id"],
        liga["league"]["name"],
        liga["country"]["name"]
    ))

    conn.commit()

    cursor.execute("""
        SELECT liga_id FROM ligas WHERE api_liga_id = %s
    """, (api_liga_id,))
    liga_id = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return liga_id

# ======================
# TEMPORADAS
# ======================
def obtener_temporadas(liga_api_id):
    r = requests.get(
        f"{BASE_URL}/leagues",
        headers=HEADERS,
        params={"id": liga_api_id}
    )
    r.raise_for_status()
    seasons = r.json()["response"][0]["seasons"]
    return [s["year"] for s in seasons]

def insertar_temporadas(liga_id, temporadas):
    conn = conectar_bd()
    cursor = conn.cursor()

    for t in temporadas:
        cursor.execute("""
            INSERT IGNORE INTO temporadas (temporada, liga_id)
            VALUES (%s, %s)
        """, (t, liga_id))

    conn.commit()
    cursor.close()
    conn.close()

def obtener_temporada_id(liga_id, temporada):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM temporadas
        WHERE liga_id = %s AND temporada = %s
    """, (liga_id, temporada))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0]

# ======================
# EQUIPOS
# ======================
def obtener_equipos(liga_api_id, temporada):
    r = requests.get(
        f"{BASE_URL}/teams",
        headers=HEADERS,
        params={"league": liga_api_id, "season": temporada}
    )
    r.raise_for_status()
    return r.json()["response"]

def insertar_equipos(liga_id, equipos):
    conn = conectar_bd()
    cursor = conn.cursor()

    for e in equipos:
        cursor.execute("""
            INSERT IGNORE INTO equipos (api_equipo_id, nombre, liga_id)
            VALUES (%s, %s, %s)
        """, (
            e["team"]["id"],
            e["team"]["name"],
            liga_id
        ))

    conn.commit()
    cursor.close()
    conn.close()

# ======================
# MAIN
# ======================
if __name__ == "__main__":

    for nombre, liga_api_id in LIGAS.items():
        print(f"\n⚽ Procesando {nombre}")

        liga_id = asegurar_liga(liga_api_id)

        temporadas = obtener_temporadas(liga_api_id)
        insertar_temporadas(liga_id, temporadas)

        temporada_actual = max(temporadas)
        temporada_id = obtener_temporada_id(liga_id, temporada_actual)

        equipos = obtener_equipos(liga_api_id, temporada_actual)
        insertar_equipos(liga_id, equipos)

        print("  ✅ OK")

    print("\n🏁 Carga completa y consistente")
