"""Generador de datos sintéticos para la plataforma psicoeducativa.

Inserta datos realistas y correlacionados en las 4 tablas principales
(estudiantes, cuestionarios_phq9, cuestionarios_gad7, sesiones_seguimiento)
usando la conexión MySQL configurada en .env.

Uso:
    python scripts/generar_datos_sinteticos.py
    python scripts/generar_datos_sinteticos.py --n-estudiantes 200
    python scripts/generar_datos_sinteticos.py --limpiar

El seed esta fijo en 42, con datos reproducibles entre ejecuciones.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Permite importar src.* sin necesidad de pip install -e .
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.repositories.db_config import obtener_conexion  # noqa: E402


SEED = 42

NOMBRES = [
    "Sofía", "Mateo", "Valentina", "Sebastián", "Isabella", "Daniel", "Camila",
    "Andrés", "María", "Juan", "Laura", "Santiago", "Mariana", "Nicolás",
    "Gabriela", "Diego", "Lucía", "Tomás", "Antonella", "Felipe", "Diunis",
    "Eduardo", "Alejandro", "Cenia", "Paula", "Ricardo", "Ana", "Jorge",
]

APELLIDOS = [
    "Pérez", "Gómez", "Rodríguez", "Martínez", "García", "Hernández", "López",
    "Sánchez", "Ramírez", "Torres", "Vargas", "Ruiz", "Castro", "Ortiz",
    "Moreno", "Romero", "Jiménez", "Rojas", "Mendoza", "Restrepo", "Coa",
]

PROGRAMAS = [
    "Ciencias de Datos", "Ingeniería de Sistemas", "Psicología",
    "Administración", "Medicina", "Derecho", "Ingeniería Industrial",
    "Diseño Gráfico", "Comunicación Social", "Contaduría",
]

PSICOLOGOS = ["PSI001", "PSI002", "PSI003", "PSI004"]

MOTIVOS_SESION = [
    "Seguimiento de ansiedad", "Evaluación inicial", "Seguimiento de depresión",
    "Apoyo académico", "Crisis emocional", "Seguimiento posterior a alerta",
]

ESTADOS_SESION = ["AGENDADA", "REALIZADA", "CANCELADA"]


# Generadores por tabla


def generar_estudiantes(cursor, n: int) -> list[str]:
    """Inserta n estudiantes y retorna sus códigos."""
    codigos = []
    ahora = datetime.now()
    for i in range(1, n + 1):
        codigo = f"EST{i:04d}"
        nombre = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
        edad = random.choices(
            range(16, 31), weights=[1, 2, 5, 8, 10, 12, 12, 10, 8, 6, 5, 4, 3, 2, 2]
        )[0]
        semestre = random.choices(range(1, 13), weights=[3, 4, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1])[0]
        programa = random.choice(PROGRAMAS)
        correo = f"{nombre.split()[0].lower()}.{nombre.split()[1].lower()}{i}@uni.edu.co"
        fecha_registro = ahora - timedelta(days=random.randint(0, 730))

        cursor.execute(
            "INSERT INTO estudiantes "
            "(codigo, nombre_completo, edad, semestre, correo, programa, fecha_registro) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (codigo, nombre, edad, semestre, correo, programa, fecha_registro),
        )
        codigos.append(codigo)
    return codigos


def _generar_respuestas_objetivo(num_items: int, puntaje_objetivo: int) -> list[int]:
    """Genera num_items valores 0-3 cuya suma sea aproximadamente puntaje_objetivo."""
    respuestas = [0] * num_items
    restante = min(puntaje_objetivo, num_items * 3)
    indices = list(range(num_items))
    random.shuffle(indices)
    for i in indices:
        if restante <= 0:
            break
        valor = min(3, restante, random.randint(0, 3))
        respuestas[i] = valor
        restante -= valor
    return respuestas


def _clasificar_gad7(puntaje: int) -> str:
    if puntaje >= 15:
        return "Severo"
    if puntaje >= 10:
        return "Moderado"
    if puntaje >= 5:
        return "Leve"
    return "Mínimo"


def _clasificar_phq9(puntaje: int) -> str:
    if puntaje >= 20:
        return "Severa"
    if puntaje >= 15:
        return "Mod. Severa"
    if puntaje >= 10:
        return "Moderada"
    if puntaje >= 5:
        return "Leve"
    return "Mínima"


def generar_cuestionarios(cursor, codigos_estudiantes: list[str]) -> None:
    """Genera cuestionarios GAD-7 y PHQ-9 correlacionados por estudiante.

    Para cada estudiante: genera un 'nivel base' de malestar (0..1) y a partir
    de él calcula los puntajes de GAD-7 y PHQ-9 con algo de ruido. Esto produce
    una correlacion r aproximada de 0.65 a 0.75 entre ambos puntajes.
    """
    ahora = datetime.now()
    for codigo in codigos_estudiantes:
        base = random.betavariate(2, 5)  # sesgo hacia valores bajos
        ruido_gad7 = random.gauss(0, 0.1)
        ruido_phq9 = random.gauss(0, 0.1)

        puntaje_gad7 = int(max(0, min(21, base * 21 + ruido_gad7 * 21)))
        puntaje_phq9 = int(max(0, min(27, base * 27 + ruido_phq9 * 27)))

        respuestas_gad7 = _generar_respuestas_objetivo(7, puntaje_gad7)
        respuestas_phq9 = _generar_respuestas_objetivo(9, puntaje_phq9)
        puntaje_gad7 = sum(respuestas_gad7)
        puntaje_phq9 = sum(respuestas_phq9)

        fecha_aplicacion = ahora - timedelta(days=random.randint(0, 180))

        cursor.execute(
            "INSERT INTO cuestionarios_gad7 "
            "(id, codigo_estudiante, respuestas, puntaje_total, "
            "nivel_severidad, fecha_aplicacion) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                str(uuid.uuid4()),
                codigo,
                json.dumps(respuestas_gad7),
                puntaje_gad7,
                _clasificar_gad7(puntaje_gad7),
                fecha_aplicacion,
            ),
        )

        cursor.execute(
            "INSERT INTO cuestionarios_phq9 "
            "(id, codigo_estudiante, respuestas, puntaje_total, "
            "nivel_severidad, fecha_aplicacion) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                str(uuid.uuid4()),
                codigo,
                json.dumps(respuestas_phq9),
                puntaje_phq9,
                _clasificar_phq9(puntaje_phq9),
                fecha_aplicacion,
            ),
        )


def generar_sesiones(cursor, codigos_estudiantes: list[str]) -> None:
    """Genera sesiones para ~30% de los estudiantes."""
    ahora = datetime.now()
    seleccionados = random.sample(codigos_estudiantes, len(codigos_estudiantes) // 3)
    for codigo in seleccionados:
        for _ in range(random.randint(1, 3)):
            dia = ahora - timedelta(days=random.randint(0, 90))
            fecha_hora = dia.replace(
                hour=random.randint(8, 17),
                minute=random.choice([0, 30]),
                second=0,
                microsecond=0,
            )
            cursor.execute(
                "INSERT INTO sesiones_seguimiento "
                "(id, codigo_estudiante, id_psicologo, fecha_hora, "
                "duracion_minutos, motivo, estado, nota) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    str(uuid.uuid4()),
                    codigo,
                    random.choice(PSICOLOGOS),
                    fecha_hora,
                    random.choice([30, 45, 60, 90]),
                    random.choice(MOTIVOS_SESION),
                    random.choice(ESTADOS_SESION),
                    None,
                ),
            )


def limpiar_tablas(cursor) -> None:
    """Vacía las tablas respetando el orden de las foreign keys."""
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for tabla in [
        "alertas_riesgo",
        "sesiones_seguimiento",
        "cuestionarios_gad7",
        "cuestionarios_phq9",
        "estudiantes",
    ]:
        cursor.execute(f"TRUNCATE TABLE {tabla}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


# Punto de entrada


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-estudiantes", type=int, default=100,
                        help="Número de estudiantes a generar (default: 100)")
    parser.add_argument("--limpiar", action="store_true",
                        help="Vaciar tablas antes de insertar")
    args = parser.parse_args()

    random.seed(SEED)
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        if args.limpiar:
            print("Limpiando tablas...")
            limpiar_tablas(cursor)

        print(f"Generando {args.n_estudiantes} estudiantes...")
        codigos = generar_estudiantes(cursor, args.n_estudiantes)

        print(f"Generando cuestionarios GAD-7 y PHQ-9 ({len(codigos)} de cada uno)...")
        generar_cuestionarios(cursor, codigos)

        print("Generando sesiones de seguimiento...")
        generar_sesiones(cursor, codigos)

        conexion.commit()
        print("Datos sintéticos generados correctamente.")
    except Exception as e:
        conexion.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    main()
