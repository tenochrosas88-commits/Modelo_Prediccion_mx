import pandas as pd
import numpy as np
import statsmodels.api as sm
import mysql.connector as mysql

# ===============================
# 1) Conectar y traer datos
# ===============================
conexion = mysql.connect(
    host="localhost",
    user="root",
    password="Tenoch2504.",
    database="ligamx_2016_2024"
)

query = "SELECT * FROM vista_partidos_plana"
df = pd.read_sql(query, conexion)

# ===============================
# 2) Preparar variables
# ===============================
df['liguilla'] = df['fase'].astype(str).str.contains('[A-Za-z]', regex=True).astype(int)
df['jornada'] = pd.to_numeric(df['fase'], errors='coerce')
df.drop(columns=['fase', 'id_partido'], inplace=True)

X = df[["Equipo_Casa", "Equipo_Visitante", "casa_medio_tiempo", "visita_medio_tiempo", "tipo_juego"]]
X = pd.get_dummies(X, columns=["Equipo_Casa", "Equipo_Visitante", "tipo_juego"], drop_first=True)

# Dummies a eliminar (depuradas según tus resultados previos)
dummies_eliminar = [
    "Equipo_Casa_Cruz Azul", "Equipo_Casa_Jaguares de Chiapas", "Equipo_Casa_Leon",
    "Equipo_Casa_Lobos Buap", "Equipo_Casa_Monarcas", "Equipo_Casa_Monterrey",
    "Equipo_Casa_Necaxa", "Equipo_Casa_Pachuca", "Equipo_Casa_Pumas",
    "Equipo_Casa_Santos Laguna", "Equipo_Casa_Tigres", "Equipo_Casa_Tijuana",
    "Equipo_Casa_Toluca",
    "Equipo_Visitante_Atlas", "Equipo_Visitante_Chivas", "Equipo_Visitante_Cruz Azul",
    "Equipo_Visitante_Jaguares de Chiapas", "Equipo_Visitante_Leon", "Equipo_Visitante_Monarcas",
    "Equipo_Visitante_Monterrey", "Equipo_Visitante_Necaxa", "Equipo_Visitante_Pachuca",
    "Equipo_Visitante_Pumas", "Equipo_Visitante_Tigres", "Equipo_Visitante_Toluca",
    "tipo_juego_Liguilla"
]
X = X.drop(columns=dummies_eliminar, errors="ignore")

# ===============================
# 3) Definir y y agregar constante
# ===============================
y_local = df["casa_goles"]
y_visita = df["visita_goles"]

X_const = sm.add_constant(X)
X_const = X_const.astype(float)
y_local = y_local.astype(float)
y_visita = y_visita.astype(float)

# ===============================
# 4) Ajustar modelos Poisson
# ===============================
modelo_local = sm.GLM(y_local, X_const, family=sm.families.Poisson())
resultado_local = modelo_local.fit()

modelo_visitante = sm.GLM(y_visita, X_const, family=sm.families.Poisson())
resultado_visitante = modelo_visitante.fit()

# ===============================
# 5) Listas de equipos para dummies
# ===============================
equipos_casa = [col.replace("Equipo_Casa_","") for col in X_const.columns if "Equipo_Casa_" in col]
equipos_visita = [col.replace("Equipo_Visitante_","") for col in X_const.columns if "Equipo_Visitante_" in col]

# ===============================
# 6) Función para generar dummies automáticamente
# ===============================
def generar_dummies(local, visitante, casa_medio=0, visita_medio=0):
    data = {'const':[1],'casa_medio_tiempo':[casa_medio],'visita_medio_tiempo':[visita_medio]}
    
    for eq in equipos_casa:
        col = f"Equipo_Casa_{eq}"
        data[col] = [1 if eq==local else 0]
        
    for eq in equipos_visita:
        col = f"Equipo_Visitante_{eq}"
        data[col] = [1 if eq==visitante else 0]
    
    # Agregar columnas faltantes como 0
    for col in X_const.columns:
        if col not in data:
            data[col] = [0]
    
    return pd.DataFrame(data)[X_const.columns]

# ===============================
# 7) Función para pronosticar un partido
# ===============================
def pronostico_partido(local, visitante, casa_medio=0, visita_medio=0, simulaciones=10000):
    partido = generar_dummies(local, visitante, casa_medio, visita_medio)
    
    lam_local = resultado_local.predict(partido)[0]
    lam_visitante = resultado_visitante.predict(partido)[0]
    
    resultados = [(np.random.poisson(lam_local), np.random.poisson(lam_visitante))
                  for _ in range(simulaciones)]
    df_res = pd.DataFrame(resultados, columns=['local','visitante'])
    
    prob_local_gana = (df_res['local'] > df_res['visitante']).mean()
    prob_empate = (df_res['local'] == df_res['visitante']).mean()
    prob_visitante_gana = (df_res['local'] < df_res['visitante']).mean()
    
    return {
        "local": local,
        "visitante": visitante,
        "goles_esperados_local": lam_local,
        "goles_esperados_visitante": lam_visitante,
        "prob_local_gana": prob_local_gana,
        "prob_empate": prob_empate,
        "prob_visitante_gana": prob_visitante_gana
    }

# ===============================
# 8) Pronóstico de toda la jornada
# ===============================
partidos = df[['Equipo_Casa','Equipo_Visitante','casa_medio_tiempo','visita_medio_tiempo']].drop_duplicates()
resultados_jornada = []

for idx, row in partidos.iterrows():
    res = pronostico_partido(row['Equipo_Casa'], row['Equipo_Visitante'],
                             casa_medio=row['casa_medio_tiempo'],
                             visita_medio=row['visita_medio_tiempo'])
    resultados_jornada.append(res)

df_resultados_jornada = pd.DataFrame(resultados_jornada)

# ===============================
# 9) Mostrar resultados
# ===============================
print(df_resultados_jornada)