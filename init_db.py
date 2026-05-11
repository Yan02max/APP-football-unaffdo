"""
Script de inicialización de la base de datos.
Uso: python init_db.py
     python init_db.py --reset
"""
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text, inspect as sa_inspect
from database import engine, get_session, Base
from models import Equipo, Temporada, Partido
from tournament import generar_calendario_round_robin

EQUIPOS_MASCULINO = [
    {"nombre": "Sky Runners",    "abreviacion": "SKY", "color_principal": "#87CEEB", "color_secundario": "#FFFFFF", "categoria": "Masculino"},
    {"nombre": "Spartans",       "abreviacion": "SPA", "color_principal": "#8B0000", "color_secundario": "#FFD700", "categoria": "Masculino"},
    {"nombre": "SD Sharks",      "abreviacion": "SDS", "color_principal": "#008080", "color_secundario": "#C0C0C0", "categoria": "Masculino"},
    {"nombre": "Dagaz",          "abreviacion": "DAG", "color_principal": "#4B0082", "color_secundario": "#FFFFFF", "categoria": "Masculino"},
    {"nombre": "Black Ops",      "abreviacion": "BLK", "color_principal": "#1C1C1C", "color_secundario": "#FF4500", "categoria": "Masculino"},
    {"nombre": "Suicide Squads", "abreviacion": "SUI", "color_principal": "#DC143C", "color_secundario": "#000000", "categoria": "Masculino"},
]

FECHA_INICIO = date(2026, 5, 17)


def _migrar_schema():
    """Agrega columnas nuevas a tablas existentes sin perder datos (SQLite)."""
    inspector = sa_inspect(engine)
    tablas = inspector.get_table_names()

    migraciones = [
        ("equipos",   "categoria", "VARCHAR(50) NOT NULL DEFAULT 'Masculino'"),
        ("temporadas","categoria", "VARCHAR(50) NOT NULL DEFAULT 'Masculino'"),
    ]
    for tabla, columna, definicion in migraciones:
        if tabla not in tablas:
            continue
        cols = [c["name"] for c in inspector.get_columns(tabla)]
        if columna not in cols:
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}"))
                conn.commit()
            print(f"[OK] Columna '{columna}' agregada a '{tabla}'.")


def _crear_temporada_y_calendario(session, nombre, categoria, fecha_inicio, equipos):
    """Crea una Temporada y genera su calendario round-robin."""
    n = len(equipos)
    # Calcular fecha_fin: (n-1) semanas de duración (2 jornadas por domingo)
    semanas = n - 1
    fecha_fin = fecha_inicio + timedelta(weeks=semanas - 1)

    temporada = Temporada(
        nombre=nombre,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        activa=True,
        categoria=categoria,
    )
    session.add(temporada)
    session.flush()

    partidos_data = generar_calendario_round_robin(equipos, fecha_inicio)
    for pd in partidos_data:
        session.add(Partido(
            temporada_id=temporada.id,
            jornada=pd["jornada"],
            bloque=pd["bloque"],
            fecha=pd["fecha"],
            equipo_local_id=pd["equipo_local_id"],
            equipo_visitante_id=pd["equipo_visitante_id"],
        ))
    return temporada, len(partidos_data)


def inicializar(reset: bool = False):
    if reset:
        print("Eliminando tablas existentes...")
        Base.metadata.drop_all(engine)

    print("Creando tablas...")
    Base.metadata.create_all(engine)
    _migrar_schema()

    session = get_session()
    try:
        if session.query(Equipo).count() > 0:
            # Restaurar categoría de los equipos originales si fue cambiada por error
            cambiados = 0
            for datos in EQUIPOS_MASCULINO:
                eq = session.query(Equipo).filter_by(nombre=datos["nombre"]).first()
                if eq and eq.categoria != datos["categoria"]:
                    eq.categoria = datos["categoria"]
                    cambiados += 1
            if cambiados:
                session.commit()
                print(f"[OK] {cambiados} categorías de equipos originales restauradas.")
            print("La BD ya contiene datos. Usa --reset para reiniciar.")
            return

        print("Insertando equipos Masculino...")
        equipos = []
        for datos in EQUIPOS_MASCULINO:
            e = Equipo(**datos)
            session.add(e)
            equipos.append(e)
        session.flush()

        print("Generando temporada y calendario Masculino...")
        _, n = _crear_temporada_y_calendario(
            session, "UNAFFDO 2026 - Masculino", "Masculino", FECHA_INICIO, equipos
        )

        session.commit()
        print(f"[OK] {n} partidos generados.")
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