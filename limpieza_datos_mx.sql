DROP DATABASE IF EXISTS futbol_analitica;
CREATE DATABASE futbol_analitica;
USE futbol_analitica;

-- =========================
-- LIGAS
-- =========================
CREATE TABLE ligas (
    liga_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    pais VARCHAR(50) NOT NULL
);

-- =========================
-- TEMPORADAS
-- =========================
CREATE TABLE temporadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temporada YEAR NOT NULL,
    liga_id INT NOT NULL,
    UNIQUE (temporada, liga_id),
    FOREIGN KEY (liga_id) REFERENCES ligas(liga_id)
);

-- =========================
-- EQUIPOS
-- =========================
CREATE TABLE equipos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    api_equipo_id INT NOT NULL,
    nombre VARCHAR(60) NOT NULL,
    liga_id INT NOT NULL,
    UNIQUE (api_equipo_id, liga_id),
    FOREIGN KEY (liga_id) REFERENCES ligas(liga_id)
);

-- =========================
-- RELACIÓN EQUIPO - TEMPORADA
-- =========================
CREATE TABLE equipo_temporada (
    equipo_id INT NOT NULL,
    temporada_id INT NOT NULL,
    PRIMARY KEY (equipo_id, temporada_id),
    FOREIGN KEY (equipo_id) REFERENCES equipos(id),
    FOREIGN KEY (temporada_id) REFERENCES temporadas(id)
);

-- =========================
-- PARTIDOS
-- =========================
CREATE TABLE partidos (
    partido_id INT AUTO_INCREMENT PRIMARY KEY,
    liga_id INT NOT NULL,
    temporada_id INT NOT NULL,
    fecha DATE NOT NULL,
    jornada VARCHAR(20),
    equipo_local INT NOT NULL,
    equipo_visitante INT NOT NULL,
    goles_local INT,
    goles_visitante INT,
    FOREIGN KEY (liga_id) REFERENCES ligas(liga_id),
    FOREIGN KEY (temporada_id) REFERENCES temporadas(id),
    FOREIGN KEY (equipo_local) REFERENCES equipos(id),
    FOREIGN KEY (equipo_visitante) REFERENCES equipos(id),
    UNIQUE (fecha, equipo_local, equipo_visitante)
);

-- =========================
-- ESTADÍSTICAS POR TEMPORADA
-- =========================
CREATE TABLE estadisticas_equipo (
    equipo_id INT NOT NULL,
    temporada_id INT NOT NULL,
    partidos_jugados INT DEFAULT 0,
    goles_favor INT DEFAULT 0,
    goles_contra INT DEFAULT 0,
    PRIMARY KEY (equipo_id, temporada_id),
    FOREIGN KEY (equipo_id) REFERENCES equipos(id),
    FOREIGN KEY (temporada_id) REFERENCES temporadas(id)
);

-- =========================
-- RATING POISSON
-- =========================
CREATE TABLE rating_poisson (
    equipo_id INT NOT NULL,
    temporada_id INT NOT NULL,
    ataque FLOAT,
    defensa FLOAT,
    PRIMARY KEY (equipo_id, temporada_id),
    FOREIGN KEY (equipo_id) REFERENCES equipos(id),
    FOREIGN KEY (temporada_id) REFERENCES temporadas(id)
);
ALTER TABLE ligas
ADD COLUMN api_liga_id INT UNIQUE;
