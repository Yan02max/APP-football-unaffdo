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

inicializar()

st.set_page_config(
    page_title="UNAFFDO - Torneos",
    page_icon="🏈",
    layout="wide",
)

# ── CSS global tema oscuro UNAFFDO ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@400;500;600&display=swap');

:root {
    --gold:   #C8A84B;
    --red:    #CC0000;
    --bg:     #0D0D1A;
    --card:   #13131F;
    --row1:   #1A1A2E;
    --row2:   #111120;
    --white:  #FFFFFF;
    --muted:  #8888AA;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: var(--bg) !important;
    color: var(--white) !important;
    font-family: 'Barlow', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: #0A0A14 !important;
    border-right: 1px solid #222235;
}
[data-testid="stSidebar"] * { color: var(--white) !important; }

/* Ocultar decoración por defecto de Streamlit */
[data-testid="stDecoration"] { display: none !important; }
header[data-testid="stHeader"] { background: var(--bg) !important; }
footer { display: none !important; }

/* Tablas nativas */
.stDataFrame { background: var(--card) !important; }

/* ── Componentes personalizados ── */

.unaffdo-header {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: 2px;
    color: var(--white);
    text-transform: uppercase;
    margin-bottom: 0;
    line-height: 1;
}
.unaffdo-sub {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 3px;
    color: var(--gold);
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}
.unaffdo-divider {
    height: 3px;
    background: linear-gradient(90deg, var(--red) 60px, var(--gold) 60px);
    margin-bottom: 1.5rem;
}

/* ── Tabla de clasificación ── */
.standings-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Barlow Condensed', sans-serif;
}
.standings-table thead th {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--muted);
    text-transform: uppercase;
    padding: 10px 14px;
    border-bottom: 1px solid #2A2A40;
    text-align: center;
}
.standings-table thead th:nth-child(2) { text-align: left; }
.standings-table tbody tr { border-bottom: 1px solid #1E1E30; }
.standings-table tbody tr:nth-child(odd)  { background: var(--row1); }
.standings-table tbody tr:nth-child(even) { background: var(--row2); }
.standings-table tbody tr:hover { background: #22223A; }
.standings-table td {
    padding: 14px;
    text-align: center;
    font-size: 1rem;
    color: var(--white);
}
.standings-table td.pos {
    font-size: 1.4rem;
    font-weight: 800;
    color: var(--gold);
    width: 48px;
}
.standings-table td.team-name {
    text-align: left;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    white-space: nowrap;
}
.standings-table td.pts {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--gold);
}
.standings-footer {
    font-size: 0.7rem;
    letter-spacing: 2px;
    color: var(--muted);
    text-align: center;
    margin-top: 1.2rem;
    text-transform: uppercase;
}

/* ── Calendario ── */
.day-card {
    background: var(--card);
    border-radius: 4px;
    margin-bottom: 2rem;
    overflow: hidden;
}
.day-header {
    display: flex;
    align-items: stretch;
    background: var(--card);
    border-bottom: 1px solid #2A2A40;
    padding: 0;
}
.day-number-block {
    background: var(--red);
    padding: 14px 22px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 90px;
}
.day-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 3px;
    color: var(--white);
    text-transform: uppercase;
}
.day-num {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: var(--white);
    line-height: 1;
}
.day-info {
    padding: 12px 20px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.day-date {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 1px;
    color: var(--white);
    text-transform: uppercase;
}
.day-jornadas {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 2px;
    color: var(--gold);
    text-transform: uppercase;
}
.block-section { padding: 0 0 8px 0; }
.block-label {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 20px 8px 20px;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 3px;
    color: var(--gold);
    text-transform: uppercase;
}
.block-label::before {
    content: '';
    display: inline-block;
    width: 12px;
    height: 12px;
    background: var(--gold);
    flex-shrink: 0;
}
.match-row {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    border-left: 3px solid var(--gold);
    margin: 4px 20px;
    background: var(--row1);
    border-radius: 2px;
}
.match-team {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 1px;
    color: var(--white);
    text-transform: uppercase;
    flex: 1;
}
.match-team.right { text-align: right; }
.match-at {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--gold);
    padding: 0 20px;
    flex-shrink: 0;
}
.match-result {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--gold);
    padding: 0 20px;
    flex-shrink: 0;
    min-width: 80px;
    text-align: center;
}
.day-footer {
    font-size: 0.65rem;
    letter-spacing: 2px;
    color: var(--muted);
    text-align: center;
    padding: 10px;
    border-top: 1px solid #2A2A40;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)


# ── Autenticación ──────────────────────────────────────────────────────────────
config = cargar_config()
authenticator = crear_autenticador(config)


def sidebar_auth():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:16px 0 8px'>
            <div style='font-family:Barlow Condensed,sans-serif;font-size:1.8rem;
                        font-weight:800;letter-spacing:3px;color:#C8A84B'>UNAFFDO</div>
            <div style='font-size:0.7rem;letter-spacing:2px;color:#8888AA'>
                REPÚBLICA DOMINICANA</div>
        </div>
        """, unsafe_allow_html=True)
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
        return st.radio(
            "Navegación",
            options=_opciones_navegacion(),
            label_visibility="collapsed",
        )


def _opciones_navegacion() -> list[str]:
    opciones = ["📅 Calendario", "🏆 Clasificación"]
    if es_arbitro():
        opciones.append("⚽ Registrar Resultados")
    if es_admin():
        opciones.append("⚙️ Gestionar Equipos")
    return opciones


# ── Páginas ────────────────────────────────────────────────────────────────────

def pagina_calendario():
    st.markdown("""
    <div class='unaffdo-header'>Schedule</div>
    <div class='unaffdo-sub'>Release &middot; Temporada 2026 &middot; Primera División &middot; Masculino</div>
    <div class='unaffdo-divider'></div>
    """, unsafe_allow_html=True)

    session = get_session()
    try:
        temporada = session.query(Temporada).filter_by(activa=True).first()
        if not temporada:
            st.warning("No hay temporada activa.")
            return

        partidos = (
            session.query(Partido)
            .filter_by(temporada_id=temporada.id)
            .order_by(Partido.fecha, Partido.bloque)
            .all()
        )
        equipos_map = {e.id: e for e in session.query(Equipo).all()}

        # Agrupar por domingo → bloque
        domingos: dict[date, dict[int, list]] = {}
        for p in partidos:
            domingos.setdefault(p.fecha, {}).setdefault(p.bloque, []).append(p)

        fechas = sorted(domingos)
        for dia_idx, fecha in enumerate(fechas, 1):
            bloques = domingos[fecha]
            # Calcular jornadas del domingo
            jornadas = sorted({p.jornada for b in bloques.values() for p in b})
            jornadas_str = f"Jornadas {jornadas[0]} &amp; {jornadas[-1]}" if len(jornadas) > 1 else f"Jornada {jornadas[0]}"
            total_partidos = sum(len(b) for b in bloques.values())

            # Construir HTML sin indentación para evitar que Markdown lo trate como código
            bloques_html = ""
            for bloque_num in sorted(bloques):
                matches_html = ""
                for p in bloques[bloque_num]:
                    local = equipos_map[p.equipo_local_id].nombre
                    visitante = equipos_map[p.equipo_visitante_id].nombre
                    if p.puntos_local is not None:
                        mid = f'<span class="match-result">{p.puntos_local} - {p.puntos_visitante}</span>'
                    else:
                        mid = '<span class="match-at">AT</span>'
                    matches_html += (
                        f'<div class="match-row">'
                        f'<span class="match-team">{local}</span>'
                        f'{mid}'
                        f'<span class="match-team right">{visitante}</span>'
                        f'</div>'
                    )
                bloques_html += (
                    f'<div class="block-section">'
                    f'<div class="block-label">Bloque {bloque_num}</div>'
                    f'{matches_html}'
                    f'</div>'
                )

            html = (
                f'<div class="day-card">'
                f'<div class="day-header">'
                f'<div class="day-number-block">'
                f'<span class="day-label">Domingo</span>'
                f'<span class="day-num">{dia_idx}</span>'
                f'</div>'
                f'<div class="day-info">'
                f'<div class="day-date">{fecha.strftime("%d de %b, %Y").upper()}</div>'
                f'<div class="day-jornadas">{jornadas_str}</div>'
                f'</div>'
                f'</div>'
                f'{bloques_html}'
                f'<div class="day-footer">'
                f'UNAFFDO &middot; Rep&uacute;blica Dominicana &middot; '
                f'Domingo {dia_idx} de {len(fechas)} &middot; '
                f'{total_partidos} Partidos &middot; {len(bloques)} Bloques'
                f'</div>'
                f'</div>'
            )
            st.markdown(html, unsafe_allow_html=True)
    finally:
        session.close()


def pagina_clasificacion():
    st.markdown("""
    <div class='unaffdo-header'>Clasificación</div>
    <div class='unaffdo-sub'>Primera División &middot; Masculino</div>
    <div class='unaffdo-divider'></div>
    """, unsafe_allow_html=True)

    session = get_session()
    try:
        temporada = session.query(Temporada).filter_by(activa=True).first()
        if not temporada:
            st.warning("No hay temporada activa.")
            return

        partidos = session.query(Partido).filter_by(temporada_id=temporada.id).all()
        equipos = session.query(Equipo).all()
        tabla = calcular_clasificacion(partidos, equipos)

        filas_html = ""
        for pos, s in enumerate(tabla, 1):
            dif_str = f"+{s['DIF']}" if s['DIF'] > 0 else str(s['DIF'])
            filas_html += (
                f'<tr>'
                f'<td class="pos">{pos}</td>'
                f'<td class="team-name">{s["equipo"]}</td>'
                f'<td>{s["PJ"]}</td><td>{s["G"]}</td><td>{s["P"]}</td>'
                f'<td>{s["PF"]}</td><td>{s["PC"]}</td>'
                f'<td>{dif_str}</td>'
                f'<td class="pts">{s["Pts"]}</td>'
                f'</tr>'
            )

        thead = '<th>#</th><th>Equipo</th><th>PJ</th><th>G</th><th>P</th><th>PF</th><th>PC</th><th>DIF</th><th>PTS</th>'
        footer_txt = 'PJ: Partidos Jugados &middot; G: Ganados &middot; P: Perdidos &middot; PF: Puntos a Favor &middot; PC: Puntos en Contra &middot; DIF: Diferencial<br><br>Temporada Regular &middot; Pre-Temporada'
        st.markdown(
            f'<table class="standings-table"><thead><tr>{thead}</tr></thead><tbody>{filas_html}</tbody></table>'
            f'<div class="standings-footer">{footer_txt}</div>',
            unsafe_allow_html=True,
        )
    finally:
        session.close()


def pagina_registrar_resultados():
    if not es_arbitro():
        st.warning("Debes iniciar sesión para acceder a esta sección.")
        return

    st.markdown("""
    <div class='unaffdo-header'>Registrar Resultados</div>
    <div class='unaffdo-sub'>Panel de árbitros</div>
    <div class='unaffdo-divider'></div>
    """, unsafe_allow_html=True)

    session = get_session()
    try:
        temporada = session.query(Temporada).filter_by(activa=True).first()
        if not temporada:
            st.warning("No hay temporada activa.")
            return

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
        partido = session.get(Partido, partido_id)

        local_nombre = equipos_map[partido.equipo_local_id].nombre
        visitante_nombre = equipos_map[partido.equipo_visitante_id].nombre

        st.markdown(f"""
        <div class="match-row" style="margin:16px 0;font-size:1.2rem;">
            <span class="match-team">{local_nombre}</span>
            <span class="match-at">VS</span>
            <span class="match-team right">{visitante_nombre}</span>
        </div>
        """, unsafe_allow_html=True)

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

    st.markdown("""
    <div class='unaffdo-header'>Gestionar Equipos</div>
    <div class='unaffdo-sub'>Panel de administración</div>
    <div class='unaffdo-divider'></div>
    """, unsafe_allow_html=True)

    session = get_session()
    try:
        equipos = session.query(Equipo).order_by(Equipo.nombre).all()

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
elif pagina_activa == "⚽ Registrar Resultados":
    pagina_registrar_resultados()
elif pagina_activa == "⚙️ Gestionar Equipos":
    pagina_gestionar_equipos()