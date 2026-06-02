#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

# URL de Jornada 1 Apertura 2023
url = "https://www.transfermarkt.com/liga-mx-apertura/spieltag/wettbewerb/MEXA/plus/?saison_id=2023&spieltag=1"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Buscar todos los partidos
partidos_html = soup.find_all("div", class_="responsive-table")

datos_jornada = []

for partido in partidos_html:
    filas = partido.find_all("tr", class_=lambda x: x != "bg_blau_20")
    
    for fila in filas:
        celdas = fila.find_all("td")
        if len(celdas) < 5:
            continue

        # Equipos y resultado
        local = celdas[2].text.strip()
        visitante = celdas[6].text.strip()
        resultado = celdas[4].text.strip()

        try:
            goles_local, goles_visita = map(int, resultado.split(":"))
        except:
            continue  # Partido no jugado

        # Link al detalle del partido (donde están los goles con minuto)
        link_parcial = fila.find("a", href=True)["href"]
        url_detalle = "https://www.transfermarkt.com" + link_parcial

        # Scrapeo de goles con minuto
        res_partido = requests.get(url_detalle, headers=headers)
        soup_partido = BeautifulSoup(res_partido.content, "html.parser")
        time.sleep(1)

        goles_local_1T = goles_local_2T = goles_visita_1T = goles_visita_2T = 0

        eventos = soup_partido.find_all("div", class_="sb-aktion")

        for evento in eventos:
            texto = evento.text.strip()
            minuto_match = re.search(r"(\d+)'", texto)
            if not minuto_match:
                continue

            minuto = int(minuto_match.group(1))
            equipo_gol = "local" if "sb-aktion-home" in evento["class"] else "visita"

            if minuto <= 45:
                if equipo_gol == "local":
                    goles_local_1T += 1
                else:
                    goles_visita_1T += 1
            else:
                if equipo_gol == "local":
                    goles_local_2T += 1
                else:
                    goles_visita_2T += 1

        datos_jornada.append({
            "Local": local,
            "Visitante": visitante,
            "Goles Local 1T": goles_local_1T,
            "Goles Local 2T": goles_local_2T,
            "Goles Visita 1T": goles_visita_1T,
            "Goles Visita 2T": goles_visita_2T,
            "Resultado Final": f"{goles_local}:{goles_visita}"
        })

# Convertir a DataFrame y guardar
df = pd.DataFrame(datos_jornada)
df.to_csv("Apertura2023_Jornada1.csv", index=False)
print(df)


# In[ ]:


import requests
from bs4 import BeautifulSoup
import re

# Encabezado para evitar bloqueos
headers = {
    "User-Agent": "Mozilla/5.0"
}

# Detalle de un partido (el primero de la jornada 1 Apertura 2023)
url_detalle = "https://www.transfermarkt.com/atlas-fc-club-america/index/spielbericht/4060527"  # <- enlace del partido

response = requests.get(url_detalle, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Inicializar contadores
goles_local_1T = goles_local_2T = goles_visita_1T = goles_visita_2T = 0

# Extraer eventos (goles)
eventos = soup.find_all("div", class_="sb-aktion")

for evento in eventos:
    texto = evento.text.strip()
    minuto_match = re.search(r"(\d+)'", texto)
    if not minuto_match:
        continue

    minuto = int(minuto_match.group(1))
    equipo_gol = "local" if "sb-aktion-home" in evento["class"] else "visita"

    # Clasificar según el tiempo
    if minuto <= 45:
        if equipo_gol == "local":
            goles_local_1T += 1
        else:
            goles_visita_1T += 1
    else:
        if equipo_gol == "local":
            goles_local_2T += 1
        else:
            goles_visita_2T += 1

# Mostrar resultados
print("📊 Goles por tiempo:")
print(f"Goles Local 1T: {goles_local_1T}")
print(f"Goles Local 2T: {goles_local_2T}")
print(f"Goles Visita 1T: {goles_visita_1T}")
print(f"Goles Visita 2T: {goles_visita_2T}")


# In[ ]:


import sqlite3
BD = sqlite3.connect("liga mx.db")
c.BD.cursor()

c.execute("CREATE TABLE resultados22\23 (
         Fecha )")

