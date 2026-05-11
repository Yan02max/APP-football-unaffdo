"""
App principal UNAFFDO - Gestión de Torneos de Fútbol Americano.
Liga UNAFFDO, República Dominicana.
"""
import streamlit as st
import pandas as pd
from datetime import date

from database import get_session
from models import Equipo, Temporada, Partido
from tournament import calcular_clasificacion
from auth import (
    cargar_config, crear_autenticador,
    esta_autenticado, es_admin, es_arbitro,
)
from init_db import inicializar

# Auto-inicializar la BD si no existe (necesario en Streamlit Cloud)
inicializar()

st.set_page_config(
    page_title="UNAFFDO - Torneos",
    page_icon="🏈",
    layout="wide",
)

# ── Autenticación ──────────────────────────────────────────────────────────────
config = cargar_config()
authenticator = crear_autenticador(config)


def sidebar_auth():
    """Muestra el widget de login/logout en la barra lateral."""
    with st.sidebar:
        st.title("🏈 UNAFFDO")
        st.divider()

        if esta_autenticado():
            nombre = st.session_state.get("name", "Usuario")
            st.success(f"Hola, **{nombre}**")
            authenticator.logout("Cerrar sesión", location="sidebar")
        else:
            authenticator.login(location="sidebar")
            estado = st.session_state.get("authentication_status")
            if estado is False:
                st.error("Usuario o contraseña incorrectos.")
            elif estado is None:
                st.info("Inicia sesión para registrar resultados.")

        st.divider()
        st.subheader("Navegación")
        return st.radio(
            "Ir a:",
            options=_opciones_navegacion(),
            label_visibility="collapsed",
        )


def _opciones_navegacion() -> list[str]:
    """Devuelve las opciones de menú según el rol del usuario."""
    opciones = ["📅 Calendario", "🏆 Clasificación"]
    if es_arbitro():
        opciones.append("⚽ Registrar Resultados")
    if es_admin():
        opciones.append("⚙️ Gestionar Equipos")
    return opciones


# ── Páginas ────────────────────────────────────────────────────────────────────

def pagina_calendario():
    st.title("📅 Calendario UNAFFDO 2026")

    session = get_session()
    try:
        temporada = session.query(Temporada).filter_by(activa=True).first()
        if not temporada:
            st.warning("No hay temporada activa. Ejecuta init_db.py primero.")
            return

        partidos = (
            session.query(Partido)
            .filter_by(temporada_id=temporada.id)
            .order_by(Partido.jornada, Partido.bloque)
            .all()
        )

        equipos_map = {e.id: e for e in session.query(Equipo).all()}

        # Agrupar por domingo → bloque
        domingos: dict[date, dict[int, list]] = {}
        for p in partidos:
            domingos.setdefault(p.fecha, {}).setdefault(p.bloque, []).append(p)

        for fecha in sorted(domingos):
            st.subheader(f"📆 {fecha.strftime('%A %d de %B %Y').capitalize()}")
            for bloque in sorted(domingos[fecha]):
                st.markdown(f"**Bloque {bloque}**")
                filas = []
                for p in domingos[fecha][bloque]:
                    local = equipos_map[p.equipo_local_id].nombre
                    visitante = equipos_map[p.equipo_visitante_id].nombre
                    resultado = (
                        f"{p.puntos_local} - {p.puntos_visitante}"
                        if p.puntos_local is not None
                        else "Pendiente"
                    )
                    filas.append({
                        "Jornada": p.jornada,
                        "Local": local,
                        "Resultado": resultado,
                        "Visitante": visitante,
                    })
                st.table(pd.DataFrame(filas))
    finally:
        session.close()


def pagina_clasificacion():
    st.title("🏆 Tabla de Clasificación")

    session = get_session()
    try:
        temporada = session.query(Temporada).filter_by(activa=True).first()
        if not temporada:
            st.warning("No hay temporada activa.")
            return

        partidos = session.query(Partido).filter_by(temporada_id=temporada.id).all()
        equipos = session.query(Equipo).all()
        tabla = calcular_clasificacion(partidos, equipos)

        filas = []
        for pos, s in enumerate(tabla, 1):
            filas.append({
                "#": pos,
                "Equipo": s["equipo"],
                "PJ": s["PJ"],
                "G": s["G"],
                "E": s["E"],
                "P": s["P"],
                "PF": s["PF"],
                "PC": s["PC"],
                "DIF": s["DIF"],
                "Pts": s["Pts"],
            })

        df = pd.DataFrame(filas).set_index("#")
        st.dataframe(df, use_container_width=True)
        st.caption("Orden: Pts > DIF > PF  |  Victoria=3 pts, Empate=1 pt")
    finally:
        session.close()


def pagina_registrar_resultados():
    if not es_arbitro():
        st.warning("Debes iniciar sesión para acceder a esta sección.")
        return

    st.title("Registrar Resultados")

    session = get_session()
    try:
        temporada = session.query(Temporada).filter_by(activa=True).first()
        if not temporada:
            st.warning("No hay temporada activa.")
            return

        # Solo partidos pendientes
        pendientes = (
            session.query(Partido)
            .filter(
                Partido.temporada_id == temporada.id,
                Partido.puntos_local.is_(None),
            )
            .order_by(Partido.jornada, Partido.bloque)
            .all()
        )

        if not pendientes:
            st.success("Todos los partidos han sido registrados.")
            return

        equipos_map = {e.id: e for e in session.query(Equipo).all()}

        opciones = {
            f"J{p.jornada} B{p.bloque} | {equipos_map[p.equipo_local_id].nombre} vs {equipos_map[p.equipo_visitante_id].nombre}": p.id
            for p in pendientes
        }

        seleccion = st.selectbox("Seleccionar partido:", list(opciones.keys()))
        partido_id = opciones[seleccion]

        # Recargar el partido en esta sesión
        partido = session.get(Partido, partido_id)

        local_nombre = equipos_map[partido.equipo_local_id].nombre
        visitante_nombre = equipos_map[partido.equipo_visitante_id].nombre

        col1, col2 = st.columns(2)
        with col1:
            pts_local = st.number_input(f"Puntos {local_nombre}", min_value=0, step=1, key="pts_l")
        with col2:
            pts_visitante = st.number_input(f"Puntos {visitante_nombre}", min_value=0, step=1, key="pts_v")

        if st.button("Guardar resultado", type="primary"):
            partido.puntos_local = int(pts_local)
            partido.puntos_visitante = int(pts_visitante)
            session.commit()
            st.success(f"Resultado guardado: {local_nombre} {pts_local} - {pts_visitante} {visitante_nombre}")
            st.rerun()
    finally:
        session.close()


def pagina_gestionar_equipos():
    if not es_admin():
        st.error("Solo el administrador puede gestionar equipos.")
        return

    st.title("⚙️ Gestionar Equipos")

    session = get_session()
    try:
        equipos = session.query(Equipo).order_by(Equipo.nombre).all()

        st.subheader("Equipos registrados")
        for equipo in equipos:
            with st.expander(f"{equipo.nombre} ({equipo.abreviacion})"):
                with st.form(key=f"form_{equipo.id}"):
                    nombre = st.text_input("Nombre", value=equipo.nombre)
                    abrev = st.text_input("Abreviación", value=equipo.abreviacion)
                    col1, col2 = st.columns(2)
                    with col1:
                        color1 = st.color_picker("Color principal", value=equipo.color_principal)
                    with col2:
                        color2 = st.color_picker("Color secundario", value=equipo.color_secundario)
                    logo = st.text_input("Ruta del logo (opcional)", value=equipo.logo_path or "")

                    if st.form_submit_button("Guardar cambios"):
                        equipo.nombre = nombre
                        equipo.abreviacion = abrev
                        equipo.color_principal = color1
                        equipo.color_secundario = color2
                        equipo.logo_path = logo or None
                        session.commit()
                        st.success("Equipo actualizado.")
                        st.rerun()
    finally:
        session.close()


# ── Punto de entrada ──────────────────────────────────────────────────────────
pagina_activa = sidebar_auth()

if pagina_activa == "📅 Calendario":
    pagina_calendario()
elif pagina_activa == "🏆 Clasificación":
    pagina_clasificacion()
elif pagina_activa == "Registrar Resultados":
    pagina_registrar_resultados()
elif pagina_activa == "⚙️ Gestionar Equipos":
    pagina_gestionar_equipos()