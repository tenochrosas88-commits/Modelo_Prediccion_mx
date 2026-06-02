import pandas as pd
import numpy as np
import mysql.connector as mysql

# ===============================
# 1) CONEXIÓN A MYSQL
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
# 2) ESPERANZAS COMO LOCAL
# ===============================

local = (
    df
    .groupby("Equipo_Casa")
    .agg(
        goles_anotados_local=("casa_goles", "mean"),
        goles_recibidos_local=("visita_goles", "mean"),
        partidos_local=("casa_goles", "count")
    )
    .reset_index()
    .rename(columns={"Equipo_Casa": "equipo"})
)

# ===============================
# 3) ESPERANZAS COMO VISITANTE
# ===============================

visitante = (
    df
    .groupby("Equipo_Visitante")
    .agg(
        goles_anotados_visita=("visita_goles", "mean"),
        goles_recibidos_visita=("casa_goles", "mean"),
        partidos_visita=("visita_goles", "count")
    )
    .reset_index()
    .rename(columns={"Equipo_Visitante": "equipo"})
)

# ===============================
# 4) UNIR LOCAL + VISITANTE
# ===============================

resumen_local_visita = pd.merge(
    local,
    visitante,
    on="equipo",
    how="outer"
)

# ===============================
# 5) ESPERANZAS TOTALES
# ===============================

df_total = pd.concat([
    df[["Equipo_Casa", "casa_goles", "visita_goles"]]
        .rename(columns={
            "Equipo_Casa": "equipo",
            "casa_goles": "goles_anotados",
            "visita_goles": "goles_recibidos"
        }),
    df[["Equipo_Visitante", "visita_goles", "casa_goles"]]
        .rename(columns={
            "Equipo_Visitante": "equipo",
            "visita_goles": "goles_anotados",
            "casa_goles": "goles_recibidos"
        })
])

resumen_total = (
    df_total
    .groupby("equipo")
    .agg(
        goles_anotados=("goles_anotados", "mean"),
        goles_recibidos=("goles_recibidos", "mean"),
        partidos_totales=("goles_anotados", "count")
    )
    .reset_index()
)

# ===============================
# 6) EXPORTAR A EXCEL (CORRECTO)
# ===============================

with pd.ExcelWriter(
    "esperanzas_goles_ligamx.xlsx",
    engine="openpyxl"
) as writer:

    resumen_local_visita.to_excel(
        writer,
        sheet_name="Local_Visitante",
        index=False
    )

    resumen_total.to_excel(
        writer,
        sheet_name="Totales",
        index=False
    )

print("Archivo 'esperanzas_goles_ligamx.xlsx' creado correctamente")


