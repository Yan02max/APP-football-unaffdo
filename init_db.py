"""
Script de inicialización de la base de datos.
Crea las tablas, inserta los 6 equipos y genera el calendario round-robin.

Uso: python init_db.py
     python init_db.py --reset   (elimina y recrea la BD)
"""
import sys
import os
from datetime import date

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(__file__))

from database import engine, get_session, Base
from models import Equipo, Temporada, Partido
from tournament import generar_calendario_round_robin

EQUIPOS_DEMO = [
    {"nombre": "Sky Runners",    "abreviacion": "SKY", "color_principal": "#87CEEB", "color_secundario": "#FFFFFF"},
    {"nombre": "Spartans",       "abreviacion": "SPA", "color_principal": "#8B0000", "color_secundario": "#FFD700"},
    {"nombre": "SD Sharks",      "abreviacion": "SDS", "color_principal": "#008080", "color_secundario": "#C0C0C0"},
    {"nombre": "Dagaz",          "abreviacion": "DAG", "color_principal": "#4B0082", "color_secundario": "#FFFFFF"},
    {"nombre": "Black Ops",      "abreviacion": "BLK", "color_principal": "#1C1C1C", "color_secundario": "#FF4500"},
    {"nombre": "Suicide Squads", "abreviacion": "SUI", "color_principal": "#DC143C", "color_secundario": "#000000"},
]

FECHA_INICIO = date(2026, 5, 17)  # Primer domingo de la temporada


def inicializar(reset: bool = False):
    if reset:
        print("Eliminando tablas existentes...")
        Base.metadata.drop_all(engine)

    print("Creando tablas...")
    Base.metadata.create_all(engine)

    session = get_session()
    try:
        # Evitar duplicar datos si ya existen
        if session.query(Equipo).count() > 0:
            print("La BD ya contiene datos. Usa --reset para reiniciar.")
            return

        # Insertar equipos
        print("Insertando equipos...")
        equipos = []
        for datos in EQUIPOS_DEMO:
            equipo = Equipo(**datos)
            session.add(equipo)
            equipos.append(equipo)
        session.flush()  # Obtener IDs antes de generar calendario

        # Crear temporada
        print("Creando temporada UNAFFDO 2026...")
        temporada = Temporada(
            nombre="UNAFFDO 2026",
            fecha_inicio=FECHA_INICIO,
            fecha_fin=date(2026, 6, 14),
            activa=True,
        )
        session.add(temporada)
        session.flush()

        # Generar calendario
        print("Generando calendario round-robin (método Berger)...")
        partidos_data = generar_calendario_round_robin(equipos, FECHA_INICIO)

        for pd_data in partidos_data:
            partido = Partido(
                temporada_id=temporada.id,
                jornada=pd_data["jornada"],
                bloque=pd_data["bloque"],
                fecha=pd_data["fecha"],
                equipo_local_id=pd_data["equipo_local_id"],
                equipo_visitante_id=pd_data["equipo_visitante_id"],
            )
            session.add(partido)

        session.commit()
        print(f"[OK] {len(partidos_data)} partidos generados correctamente.")
        print("[OK] Base de datos inicializada.")

    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    inicializar(reset=reset)