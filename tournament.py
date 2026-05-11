"""Lógica de torneo: generación de calendario y cálculo de clasificación."""
from datetime import date, timedelta


def generar_calendario_round_robin(equipos: list, fecha_inicio: date) -> list[dict]:
    """
    Genera el calendario completo round-robin ida y vuelta usando el método del círculo (Berger).

    Con 6 equipos produce 10 jornadas (5 por vuelta), 3 partidos por jornada = 30 en total.
    Se juegan 2 jornadas por domingo: la 1ª es bloque 1, la 2ª es bloque 2.

    Retorna lista de dicts con claves:
      jornada, bloque, fecha, equipo_local_id, equipo_visitante_id
    """
    n = len(equipos)
    assert n % 2 == 0, "Se requiere número par de equipos"

    ids = [e.id for e in equipos]

    # Método del círculo: fijar ids[0], rotar el resto
    fijo = ids[0]
    rotativos = ids[1:]

    rondas_ida = []
    for _ in range(n - 1):
        lista = [fijo] + rotativos
        parejas = [(lista[i], lista[n - 1 - i]) for i in range(n // 2)]
        rondas_ida.append(parejas)
        # Rotar: último al frente
        rotativos = [rotativos[-1]] + rotativos[:-1]

    # Vuelta: invertir local/visitante
    rondas_vuelta = [[(v, l) for l, v in ronda] for ronda in rondas_ida]
    todas_rondas = rondas_ida + rondas_vuelta  # 10 rondas en total

    partidos = []
    for idx_ronda, parejas in enumerate(todas_rondas):
        jornada = idx_ronda + 1
        # 2 jornadas por domingo → domingo = (jornada - 1) // 2
        domingo = (jornada - 1) // 2
        fecha = fecha_inicio + timedelta(weeks=domingo)
        # Bloque 1 = jornadas impares del domingo, bloque 2 = jornadas pares
        bloque = 1 if (jornada % 2 == 1) else 2

        for local_id, visitante_id in parejas:
            partidos.append({
                "jornada": jornada,
                "bloque": bloque,
                "fecha": fecha,
                "equipo_local_id": local_id,
                "equipo_visitante_id": visitante_id,
            })

    return partidos


def calcular_clasificacion(partidos: list, equipos: list) -> list[dict]:
    """
    Calcula la tabla de clasificación a partir de los partidos jugados.

    Sistema de puntos: 3 por victoria, 1 por empate, 0 por derrota.
    Orden: Pts DESC, DIF DESC, PF DESC.

    partidos: lista de objetos Partido con puntos_local/puntos_visitante (None = no jugado)
    equipos:  lista de objetos Equipo
    """
    stats = {e.id: {
        "equipo": e.nombre,
        "abrev": e.abreviacion,
        "PJ": 0, "G": 0, "E": 0, "P": 0,
        "PF": 0, "PC": 0, "DIF": 0, "Pts": 0,
    } for e in equipos}

    for partido in partidos:
        if partido.puntos_local is None or partido.puntos_visitante is None:
            continue  # partido pendiente

        pl = partido.puntos_local
        pv = partido.puntos_visitante
        lid = partido.equipo_local_id
        vid = partido.equipo_visitante_id

        stats[lid]["PJ"] += 1
        stats[vid]["PJ"] += 1
        stats[lid]["PF"] += pl
        stats[lid]["PC"] += pv
        stats[vid]["PF"] += pv
        stats[vid]["PC"] += pl

        if pl > pv:
            stats[lid]["G"] += 1
            stats[lid]["Pts"] += 3
            stats[vid]["P"] += 1
        elif pl < pv:
            stats[vid]["G"] += 1
            stats[vid]["Pts"] += 3
            stats[lid]["P"] += 1
        else:
            stats[lid]["E"] += 1
            stats[vid]["E"] += 1
            stats[lid]["Pts"] += 1
            stats[vid]["Pts"] += 1

    for s in stats.values():
        s["DIF"] = s["PF"] - s["PC"]

    tabla = sorted(
        stats.values(),
        key=lambda x: (x["Pts"], x["DIF"], x["PF"]),
        reverse=True,
    )
    return tabla