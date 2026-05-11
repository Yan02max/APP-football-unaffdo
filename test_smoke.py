"""
Smoke tests para verificar la integridad del calendario y la clasificación.
Sin framework de testing: solo asserts. Ejecutar con: python test_smoke.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date
from tournament import generar_calendario_round_robin, calcular_clasificacion


# ── Objetos mínimos que simulan los modelos ORM ───────────────────────────────

class EquipoFake:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.abreviacion = nombre[:3].upper()


class PartidoFake:
    def __init__(self, equipo_local_id, equipo_visitante_id, puntos_local=None, puntos_visitante=None):
        self.equipo_local_id = equipo_local_id
        self.equipo_visitante_id = equipo_visitante_id
        self.puntos_local = puntos_local
        self.puntos_visitante = puntos_visitante


# ── Test 1: calendario genera exactamente 30 partidos ─────────────────────────

def test_total_partidos():
    equipos = [EquipoFake(i, f"Equipo{i}") for i in range(1, 7)]
    partidos = generar_calendario_round_robin(equipos, date(2026, 5, 17))
    assert len(partidos) == 30, f"Se esperaban 30 partidos, se generaron {len(partidos)}"
    print("[OK] test_total_partidos: 30 partidos generados")


# ── Test 2: cada equipo juega exactamente 10 partidos ─────────────────────────

def test_partidos_por_equipo():
    equipos = [EquipoFake(i, f"Equipo{i}") for i in range(1, 7)]
    partidos = generar_calendario_round_robin(equipos, date(2026, 5, 17))

    conteo = {i: 0 for i in range(1, 7)}
    for p in partidos:
        conteo[p["equipo_local_id"]] += 1
        conteo[p["equipo_visitante_id"]] += 1

    for equipo_id, total in conteo.items():
        assert total == 10, (
            f"Equipo {equipo_id} juega {total} partidos, se esperaban 10"
        )
    print("[OK] test_partidos_por_equipo: cada equipo juega 10 partidos")


# ── Test 3: cada pareja se enfrenta exactamente 2 veces ───────────────────────

def test_enfrentamientos_dobles():
    equipos = [EquipoFake(i, f"Equipo{i}") for i in range(1, 7)]
    partidos = generar_calendario_round_robin(equipos, date(2026, 5, 17))

    enfrentamientos: dict[frozenset, int] = {}
    for p in partidos:
        par = frozenset([p["equipo_local_id"], p["equipo_visitante_id"]])
        enfrentamientos[par] = enfrentamientos.get(par, 0) + 1

    for par, veces in enfrentamientos.items():
        assert veces == 2, (
            f"La pareja {par} se enfrenta {veces} veces, se esperaban 2"
        )
    print("[OK] test_enfrentamientos_dobles: cada pareja se enfrenta exactamente 2 veces")


# ── Test 4: cálculo de clasificación ─────────────────────────────────────────

def test_calculo_clasificacion():
    equipos = [EquipoFake(1, "A"), EquipoFake(2, "B"), EquipoFake(3, "C")]
    # A gana a B, A empata con C, B pierde con C
    partidos = [
        PartidoFake(1, 2, 21, 7),   # A vence a B
        PartidoFake(1, 3, 14, 14),  # A empata con C
        PartidoFake(2, 3, 0, 14),   # C vence a B
    ]
    tabla = calcular_clasificacion(partidos, equipos)

    # A: 1V 1E 0D = 4 pts, DIF=14
    # C: 1V 1E 0D = 4 pts, DIF=14 (PF=28 > A's PF=35... wait let me recalculate)
    # A: PF=35, PC=21, DIF=14, Pts=4
    # C: PF=28, PC=14, DIF=14, Pts=4
    # B: PF=7, PC=35, DIF=-28, Pts=0
    # Orden por Pts→DIF→PF: A (4,14,35), C (4,14,28), B (0,-28,7)

    assert tabla[0]["equipo"] == "A", f"Esperado A primero, obtenido {tabla[0]['equipo']}"
    assert tabla[1]["equipo"] == "C", f"Esperado C segundo, obtenido {tabla[1]['equipo']}"
    assert tabla[2]["equipo"] == "B", f"Esperado B tercero, obtenido {tabla[2]['equipo']}"
    assert tabla[0]["Pts"] == 4
    assert tabla[2]["Pts"] == 0

    print("[OK] test_calculo_clasificacion: calculo de puntos y orden correcto")


# ── Test 5: jornadas y bloques correctos ──────────────────────────────────────

def test_jornadas_y_bloques():
    equipos = [EquipoFake(i, f"Equipo{i}") for i in range(1, 7)]
    partidos = generar_calendario_round_robin(equipos, date(2026, 5, 17))

    jornadas = {p["jornada"] for p in partidos}
    assert jornadas == set(range(1, 11)), f"Se esperaban jornadas 1-10, se obtuvieron {sorted(jornadas)}"

    bloques = {p["bloque"] for p in partidos}
    assert bloques == {1, 2}, f"Se esperaban bloques 1 y 2, se obtuvieron {bloques}"

    print("[OK] test_jornadas_y_bloques: 10 jornadas con bloques 1 y 2")


# ── Ejecutar todos los tests ──────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_total_partidos,
        test_partidos_por_equipo,
        test_enfrentamientos_dobles,
        test_calculo_clasificacion,
        test_jornadas_y_bloques,
    ]

    errores = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
            errores += 1

    print(f"\n{'Todos los tests pasaron.' if errores == 0 else f'{errores} test(s) fallaron.'}")
    sys.exit(errores)