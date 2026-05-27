-- ============================================================================
-- Schema de la Plataforma de Apoyo Psicoeducativo
-- ============================================================================
-- Ejecutar este script en MySQL Workbench una vez por integrante para crear
-- la base de datos local con las tablas necesarias.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS bienestar_universitario
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE bienestar_universitario;

-- ============================================================================
-- Tabla: estudiantes (Integrante: Alejandro)
-- ============================================================================
CREATE TABLE IF NOT EXISTS estudiantes (
    codigo VARCHAR(20) PRIMARY KEY,
    nombre_completo VARCHAR(120) NOT NULL,
    edad INT NOT NULL,
    semestre INT NOT NULL,
    correo VARCHAR(120) NOT NULL,
    programa VARCHAR(80) NOT NULL,
    fecha_registro DATETIME NOT NULL
);

-- ============================================================================
-- Tabla: cuestionarios_phq9 (Integrante: Eduardo)
-- ============================================================================
CREATE TABLE IF NOT EXISTS cuestionarios_phq9 (
    id VARCHAR(40) PRIMARY KEY,
    codigo_estudiante VARCHAR(20) NOT NULL,
    respuestas JSON NOT NULL,
    puntaje_total INT NOT NULL,
    nivel_severidad VARCHAR(40) NOT NULL,
    fecha_aplicacion DATETIME NOT NULL,
    FOREIGN KEY (codigo_estudiante) REFERENCES estudiantes(codigo)
        ON DELETE CASCADE
);

-- ============================================================================
-- Tabla: cuestionarios_gad7 (Integrante: Diunis)
-- ============================================================================
CREATE TABLE IF NOT EXISTS cuestionarios_gad7 (
    id VARCHAR(40) PRIMARY KEY,
    codigo_estudiante VARCHAR(20) NOT NULL,
    respuestas JSON NOT NULL,
    puntaje_total INT NOT NULL,
    nivel_severidad VARCHAR(40) NOT NULL,
    fecha_aplicacion DATETIME NOT NULL,
    FOREIGN KEY (codigo_estudiante) REFERENCES estudiantes(codigo)
        ON DELETE CASCADE
);

-- ============================================================================
-- Tabla: sesiones_seguimiento (Integrante: Ceni)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sesiones_seguimiento (
    id VARCHAR(40) PRIMARY KEY,
    codigo_estudiante VARCHAR(20) NOT NULL,
    id_psicologo VARCHAR(20) NOT NULL,
    fecha_hora DATETIME NOT NULL,
    duracion_minutos INT NOT NULL,
    motivo TEXT,
    estado VARCHAR(20) NOT NULL,
    nota TEXT,
    FOREIGN KEY (codigo_estudiante) REFERENCES estudiantes(codigo)
        ON DELETE CASCADE
);

-- ============================================================================
-- Tabla: alertas_riesgo (generadas automáticamente por los business services)
-- ============================================================================
CREATE TABLE IF NOT EXISTS alertas_riesgo (
    id VARCHAR(40) PRIMARY KEY,
    codigo_estudiante VARCHAR(20) NOT NULL,
    tipo VARCHAR(40) NOT NULL,
    puntaje INT NOT NULL,
    prioridad VARCHAR(20) NOT NULL,
    fecha DATETIME NOT NULL,
    atendida BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (codigo_estudiante) REFERENCES estudiantes(codigo)
        ON DELETE CASCADE
);

-- ============================================================================
-- Verificar creación
-- ============================================================================
SHOW TABLES;
