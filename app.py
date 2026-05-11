"""App principal UNAFFDO - Gestión de Torneos de Fútbol Americano."""
import streamlit as st
import pandas as pd
from datetime import date

from database import get_session
from models import Equipo, Temporada, Partido
from tournament import calcular_clasificacion
from auth import (
    verificar_login, hacer_login, hacer_logout,
    esta_autenticado, es_admin, es_arbitro,
)
from init_db import inicializar

inicializar()

st.set_page_config(
    page_title="UNAFFDO - Torneos",
    page_icon="🏈",
    layout="wide",
)

# ── CSS global ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@400;500;600&display=swap');

:root {
    --gold:  #C8A84B;
    --red:   #CC0000;
    --bg:    #0D0D1A;
    --card:  #13131F;
    --row1:  #1A1A2E;
    --row2:  #111120;
    --white: #FFFFFF;
    --muted: #8888AA;
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: var(--bg) !important;
    color: var(--white) !important;
    font-family: 'Barlow', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #0A0A14 !important;
    border-right: 1px solid #222235;
}
[data-testid="stSidebar"] * { color: var(--white) !important; }
[data-testid="stDecoration"] { display: none !important; }
header[data-testid="stHeader"] { background: var(--bg) !important; }
footer { display: none !important; }

/* ── Headers ── */
.unaffdo-header {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 3rem; font-weight: 800;
    letter-spacing: 2px; color: var(--white);
    text-transform: uppercase; margin-bottom: 0; line-height: 1;
}
.unaffdo-sub {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.85rem; font-weight: 600;
    letter-spacing: 3px; color: var(--gold);
    text-transform: uppercase; margin-bottom: 1.5rem;
}
.unaffdo-divider {
    height: 3px;
    background: linear-gradient(90deg, var(--red) 60px, var(--gold) 60px);
    margin-bottom: 1.5rem;
}

/* ── Clasificación ── */
.standings-table { width:100%; border-collapse:collapse; font-family:'Barlow Condensed',sans-serif; }
.standings-table thead th { font-size:.75rem; font-weight:700; letter-spacing:2px; color:var(--muted); text-transform:uppercase; padding:10px 14px; border-bottom:1px solid #2A2A40; text-align:center; }
.standings-table thead th:nth-child(2) { text-align:left; }
.standings-table tbody tr { border-bottom:1px solid #1E1E30; }
.standings-table tbody tr:nth-child(odd)  { background:var(--row1); }
.standings-table tbody tr:nth-child(even) { background:var(--row2); }
.standings-table tbody tr:hover { background:#22223A; }
.standings-table td { padding:14px; text-align:center; font-size:1rem; color:var(--white); }
.standings-table td.pos  { font-size:1.4rem; font-weight:800; color:var(--gold); width:48px; }
.standings-table td.team-name { text-align:left; font-size:1.1rem; font-weight:700; letter-spacing:1px; text-transform:uppercase; white-space:nowrap; }
.standings-table td.pts  { font-size:1.2rem; font-weight:800; color:var(--gold); }
.standings-footer { font-size:.7rem; letter-spacing:2px; color:var(--muted); text-align:center; margin-top:1.2rem; text-transform:uppercase; }

/* ── Calendario ── */
.day-card { background:var(--card); border-radius:4px; margin-bottom:2rem; overflow:hidden; }
.day-header { display:flex; align-items:stretch; background:var(--card); border-bottom:1px solid #2A2A40; }
.day-number-block { background:var(--red); padding:14px 22px; display:flex; flex-direction:column; align-items:center; justify-content:center; min-width:90px; }
.day-label { font-family:'Barlow Condensed',sans-serif; font-size:.7rem; font-weight:700; letter-spacing:3px; color:var(--white); text-transform:uppercase; }
.day-num   { font-family:'Barlow Condensed',sans-serif; font-size:3rem; font-weight:800; color:var(--white); line-height:1; }
.day-info  { padding:12px 20px; display:flex; flex-direction:column; justify-content:center; }
.day-date  { font-family:'Barlow Condensed',sans-serif; font-size:1.5rem; font-weight:700; letter-spacing:1px; color:var(--white); text-transform:uppercase; }
.day-jornadas { font-size:.75rem; font-weight:600; letter-spacing:2px; color:var(--gold); text-transform:uppercase; }
.block-section { padding:0 0 8px 0; }
.block-label { display:flex; align-items:center; gap:10px; padding:12px 20px 8px; font-family:'Barlow Condensed',sans-serif; font-size:.75rem; font-weight:700; letter-spacing:3px; color:var(--gold); text-transform:uppercase; }
.block-label::before { content:''; display:inline-block; width:12px; height:12px; background:var(--gold); flex-shrink:0; }
.match-row { display:flex; align-items:center; padding:12px 20px; border-left:3px solid var(--gold); margin:4px 20px; background:var(--row1); border-radius:2px; }
.match-team { font-family:'Barlow Condensed',sans-serif; font-size:1.05rem; font-weight:700; letter-spacing:1px; color:var(--white); text-transform:uppercase; flex:1; }
.match-team.right { text-align:right; }
.match-at { font-family:'Barlow Condensed',sans-serif; font-size:.8rem; font-weight:700; letter-spacing:2px; color:var(--gold); padding:0 20px; flex-shrink:0; }
.match-result { font-family:'Barlow Condensed',sans-serif; font-size:1rem; font-weight:700; color:var(--gold); padding:0 20px; flex-shrink:0; min-width:80px; text-align:center; }
.day-footer { font-size:.65rem; letter-spacing:2px; color:var(--muted); text-align:center; padding:10px; border-top:1px solid #2A2A40; text-transform:uppercase; }

/* ── Login page ── */
.login-bg {
    position: fixed; inset: 0; z-index: 0;
    background: linear-gradient(135deg, #060b1f 0%, #0d2060 45%, #091540 100%);
}
.login-blob1 {
    position: fixed; width: 520px; height: 520px; border-radius: 43% 57% 70% 30% / 42% 38% 62% 58%;
    background: radial-gradient(circle, rgba(30,100,220,.35) 0%, transparent 70%);
    top: -140px; right: -100px; z-index: 1; pointer-events: none;
    animation: morph 10s ease-in-out infinite alternate;
}
.login-blob2 {
    position: fixed; width: 420px; height: 420px; border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
    background: radial-gradient(circle, rgba(20,80,200,.3) 0%, transparent 70%);
    bottom: -120px; left: -80px; z-index: 1; pointer-events: none;
    animation: morph 13s ease-in-out infinite alternate-reverse;
}
@keyframes morph {
    0%   { border-radius: 43% 57% 70% 30% / 42% 38% 62% 58%; }
    50%  { border-radius: 60% 40% 55% 45% / 50% 60% 40% 50%; }
    100% { border-radius: 30% 70% 40% 60% / 55% 45% 55% 45%; }
}
.login-card {
    position: relative; z-index: 10;
    background: rgba(255,255,255,0.97);
    border-radius: 20px;
    padding: 44px 40px 36px;
    box-shadow: 0 32px 80px rgba(0,0,0,.55), 0 0 0 1px rgba(255,255,255,.08);
    max-width: 400px; margin: 0 auto;
}
.login-logo {
    width: 72px; height: 72px;
    background: linear-gradient(135deg, #1565c0, #42a5f5);
    border-radius: 50%; margin: 0 auto 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem; box-shadow: 0 8px 24px rgba(21,101,192,.5);
}
.login-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.8rem; font-weight: 700;
    color: #111; text-align: center; margin-bottom: 6px; letter-spacing: 1px;
}
.login-brand {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: .75rem; font-weight: 600; letter-spacing: 4px;
    color: #1565c0; text-align: center; margin-bottom: 28px; text-transform: uppercase;
}
/* Inputs dentro del card de login */
.login-card input {
    background: #f0f5ff !important; border: 1.5px solid #dde3f5 !important;
    border-radius: 10px !important; color: #222 !important; font-size: .95rem !important;
}
.login-card input:focus { border-color: #1565c0 !important; box-shadow: 0 0 0 3px rgba(21,101,192,.15) !important; }
.login-card label { color: #444 !important; font-size: .85rem !important; font-weight: 600 !important; }
.login-card button[kind="primaryFormSubmit"],
.login-card button[data-testid="baseButton-primaryFormSubmit"] {
    background: linear-gradient(90deg, #1565c0 0%, #1976d2 100%) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-size: 1rem !important;
    font-weight: 700 !important; letter-spacing: 2px !important;
    padding: .65rem !important; width: 100% !important;
    box-shadow: 0 6px 18px rgba(21,101,192,.4) !important;
    transition: opacity .2s !important; text-transform: uppercase !important;
}
.login-card button:hover { opacity: .9 !important; }
.login-card [data-testid="stForm"] { border: none !important; padding: 0 !important; }
.login-error { color: #cc0000; font-size: .85rem; text-align: center; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
def sidebar_nav():
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:16px 0 8px">'
            '<div style="font-family:Barlow Condensed,sans-serif;font-size:1.8rem;'
            'font-weight:800;letter-spacing:3px;color:#C8A84B">UNAFFDO</div>'
            '<div style="font-size:.7rem;letter-spacing:2px;color:#8888AA">REPÚBLICA DOMINICANA</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.divider()

        if esta_autenticado():
            nombre = st.session_state.get("name", "Usuario")
            st.success(f"**{nombre}**")
            if st.button("Cerrar sesión", use_container_width=True):
                hacer_logout()
                st.rerun()
        else:
            st.info("Sin sesión activa")

        st.divider()
        opciones = ["📅 Calendario", "🏆 Clasificación"]
        if es_arbitro():
            opciones.append("⚽ Registrar Resultados")
        if es_admin():
            opciones.append("⚙️ Gestionar Equipos")

        return st.radio("Ir a:", opciones, label_visibility="collapsed")


# ── Página login ───────────────────────────────────────────────────────────────
def pagina_login():
    st.markdown(
        '<style>[data-testid="stSidebar"]{display:none!important}'
        '[data-testid="stSidebarCollapsedControl"]{display:none!important}</style>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="login-bg"></div>'
        '<div class="login-blob1"></div>'
        '<div class="login-blob2"></div>',
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(
            '<div class="login-card">'
            '<div class="login-logo">🏈</div>'
            '<div class="login-title">Login</div>'
            '<div class="login-brand">UNAFFDO · República Dominicana</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        with st.container():
            st.markdown('<div class="login-card" style="margin-top:-16px;padding-top:24px;">', unsafe_allow_html=True)
            with st.form("login_form", border=False):
                username = st.text_input("Usuario", placeholder="Ingresa tu usuario")
                password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
                submit = st.form_submit_button("Sign in", use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)

        if submit:
            if verificar_login(username, password):
                hacer_login(username)
                st.rerun()
            else:
                st.markdown('<div class="login-error">Usuario o contraseña incorrectos.</div>', unsafe_allow_html=True)


# ── Helper: renderiza el calendario de una temporada ──────────────────────────
def _render_calendario(session, temporada):
    partidos = (
        session.query(Partido)
        .filter_by(temporada_id=temporada.id)
        .order_by(Partido.fecha, Partido.bloque)
        .all()
    )
    equipos_map = {e.id: e for e in session.query(Equipo).filter_by(categoria=temporada.categoria).all()}

    domingos: dict[date, dict[int, list]] = {}
    for p in partidos:
        domingos.setdefault(p.fecha, {}).setdefault(p.bloque, []).append(p)

    fechas = sorted(domingos)
    if not fechas:
        st.info("No hay partidos programados aún para esta categoría.")
        return

    for dia_idx, fecha in enumerate(fechas, 1):
        bloques = domingos[fecha]
        jornadas = sorted({p.jornada for b in bloques.values() for p in b})
        jornadas_str = (
            f"Jornadas {jornadas[0]} &amp; {jornadas[-1]}"
            if len(jornadas) > 1 else f"Jornada {jornadas[0]}"
        )
        total_partidos = sum(len(b) for b in bloques.values())

        bloques_html = ""
        for bloque_num in sorted(bloques):
            matches_html = ""
            for p in bloques[bloque_num]:
                local = equipos_map[p.equipo_local_id].nombre
                visitante = equipos_map[p.equipo_visitante_id].nombre
                mid = (
                    f'<span class="match-result">{p.puntos_local} - {p.puntos_visitante}</span>'
                    if p.puntos_local is not None
                    else '<span class="match-at">AT</span>'
                )
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
            f'</div></div>'
            f'{bloques_html}'
            f'<div class="day-footer">'
            f'UNAFFDO &middot; Rep&uacute;blica Dominicana &middot; '
            f'Domingo {dia_idx} de {len(fechas)} &middot; '
            f'{total_partidos} Partidos &middot; {len(bloques)} Bloques'
            f'</div></div>'
        )
        st.markdown(html, unsafe_allow_html=True)


# ── Página calendario ──────────────────────────────────────────────────────────
def pagina_calendario():
    st.markdown(
        "<div class='unaffdo-header'>Schedule</div>"
        "<div class='unaffdo-sub'>Temporada 2026 &middot; Primera Divisi&oacute;n</div>"
        "<div class='unaffdo-divider'></div>",
        unsafe_allow_html=True,
    )
    session = get_session()
    try:
        temporadas = session.query(Temporada).filter_by(activa=True).order_by(Temporada.categoria).all()
        if not temporadas:
            st.warning("No hay temporada activa.")
            return

        if len(temporadas) > 1:
            tabs = st.tabs([t.categoria for t in temporadas])
            for tab, temporada in zip(tabs, temporadas):
                with tab:
                    _render_calendario(session, temporada)
        else:
            _render_calendario(session, temporadas[0])
    finally:
        session.close()


# ── Helper: renderiza la tabla de clasificación de una temporada ───────────────
def _render_clasificacion(session, temporada):
    partidos = session.query(Partido).filter_by(temporada_id=temporada.id).all()
    equipos  = session.query(Equipo).filter_by(categoria=temporada.categoria).all()
    tabla    = calcular_clasificacion(partidos, equipos)

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
    footer = (
        'PJ: Partidos Jugados &middot; G: Ganados &middot; P: Perdidos &middot; '
        'PF: Puntos a Favor &middot; PC: Puntos en Contra &middot; DIF: Diferencial'
        '<br><br>Temporada Regular &middot; Pre-Temporada'
    )
    st.markdown(
        f'<table class="standings-table"><thead><tr>{thead}</tr></thead><tbody>{filas_html}</tbody></table>'
        f'<div class="standings-footer">{footer}</div>',
        unsafe_allow_html=True,
    )


# ── Página clasificación ───────────────────────────────────────────────────────
def pagina_clasificacion():
    st.markdown(
        "<div class='unaffdo-header'>Clasificaci&oacute;n</div>"
        "<div class='unaffdo-sub'>Primera Divisi&oacute;n</div>"
        "<div class='unaffdo-divider'></div>",
        unsafe_allow_html=True,
    )
    session = get_session()
    try:
        temporadas = session.query(Temporada).filter_by(activa=True).order_by(Temporada.categoria).all()
        if not temporadas:
            st.warning("No hay temporada activa.")
            return

        if len(temporadas) > 1:
            tabs = st.tabs([t.categoria for t in temporadas])
            for tab, temporada in zip(tabs, temporadas):
                with tab:
                    _render_clasificacion(session, temporada)
        else:
            _render_clasificacion(session, temporadas[0])
    finally:
        session.close()


# ── CSS extra: marcador IFAF ───────────────────────────────────────────────────
SCORING_CSS = """
<style>
.score-board {
    display:flex; align-items:stretch; gap:12px;
    background:var(--card); border-radius:8px;
    padding:20px; margin:16px 0;
}
.score-team-block { flex:1; text-align:center; }
.score-team-name {
    font-family:'Barlow Condensed',sans-serif;
    font-size:1.1rem; font-weight:700; letter-spacing:2px;
    color:var(--gold); text-transform:uppercase; margin-bottom:8px;
}
.score-display {
    font-family:'Barlow Condensed',sans-serif;
    font-size:5rem; font-weight:800; color:var(--white);
    line-height:1; margin:4px 0 12px;
}
.score-sep {
    font-family:'Barlow Condensed',sans-serif;
    font-size:3rem; font-weight:700; color:var(--muted);
    align-self:center; padding:0 8px;
}
.ifaf-legend {
    display:flex; flex-wrap:wrap; gap:8px;
    background:var(--row2); border-radius:6px;
    padding:12px 16px; margin-bottom:16px;
    font-family:'Barlow Condensed',sans-serif;
}
.ifaf-badge {
    background:var(--row1); border:1px solid #2A2A40;
    border-radius:4px; padding:4px 10px;
    font-size:.8rem; font-weight:600; letter-spacing:1px; color:var(--white);
}
.ifaf-badge span { color:var(--gold); font-weight:800; margin-right:4px; }
</style>
"""

# ── Página registrar resultados ────────────────────────────────────────────────
def pagina_registrar_resultados():
    if not es_arbitro():
        st.warning("Debes iniciar sesión para acceder a esta sección.")
        return

    st.markdown(
        "<div class='unaffdo-header'>Registrar Resultados</div>"
        "<div class='unaffdo-sub'>Panel de &aacute;rbitros &middot; IFAF 2026</div>"
        "<div class='unaffdo-divider'></div>",
        unsafe_allow_html=True,
    )
    st.markdown(SCORING_CSS, unsafe_allow_html=True)

    session = get_session()
    try:
        temporadas_activas = session.query(Temporada).filter_by(activa=True).all()
        if not temporadas_activas:
            st.warning("No hay temporada activa.")
            return

        ids_temporadas = [t.id for t in temporadas_activas]
        temporadas_map = {t.id: t for t in temporadas_activas}

        pendientes = (
            session.query(Partido)
            .filter(Partido.temporada_id.in_(ids_temporadas), Partido.puntos_local.is_(None))
            .order_by(Partido.temporada_id, Partido.jornada, Partido.bloque)
            .all()
        )
        if not pendientes:
            st.success("Todos los partidos han sido registrados.")
            return

        equipos_map = {e.id: e for e in session.query(Equipo).all()}
        cat_label = lambda p: temporadas_map[p.temporada_id].categoria
        opciones = {
            f"[{cat_label(p)}] J{p.jornada} B{p.bloque} | {equipos_map[p.equipo_local_id].nombre} vs {equipos_map[p.equipo_visitante_id].nombre}": p.id
            for p in pendientes
        }

        seleccion  = st.selectbox("Seleccionar partido:", list(opciones.keys()))
        partido_id = opciones[seleccion]
        partido    = session.get(Partido, partido_id)

        local_nombre     = equipos_map[partido.equipo_local_id].nombre
        visitante_nombre = equipos_map[partido.equipo_visitante_id].nombre

        if st.session_state.get("scoring_partido_id") != partido_id:
            st.session_state["scoring_partido_id"] = partido_id
            st.session_state["score_local"]     = 0
            st.session_state["score_visitante"] = 0

        sl = st.session_state["score_local"]
        sv = st.session_state["score_visitante"]

        # ── Marcador visual ──
        st.markdown(
            f'<div class="score-board">'
            f'<div class="score-team-block">'
            f'<div class="score-team-name">{local_nombre}</div>'
            f'<div class="score-display">{sl}</div>'
            f'</div>'
            f'<div class="score-sep">—</div>'
            f'<div class="score-team-block">'
            f'<div class="score-team-name">{visitante_nombre}</div>'
            f'<div class="score-display">{sv}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Leyenda IFAF ──
        st.markdown(
            '<div class="ifaf-legend">'
            '<div class="ifaf-badge"><span>TD</span>Touchdown = 6 pts</div>'
            '<div class="ifaf-badge"><span>Conv 1pt</span>Desde 5 yds = 1 pt</div>'
            '<div class="ifaf-badge"><span>Conv 2pts</span>Desde 10 yds = 2 pts</div>'
            '<div class="ifaf-badge"><span>Safety</span>= 2 pts</div>'
            '<div class="ifaf-badge"><span>Int. Conv.</span>Def. intercepta = 2 pts</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # ── Botones de anotación ──
        ANOTACIONES = [
            ("TD",       "Touchdown",         6),
            ("Conv 1pt", "Conversión 1 pt",   1),
            ("Conv 2pt", "Conversión 2 pts",  2),
            ("Safety",   "Safety / Int.Conv", 2),
        ]

        col_l, col_sep, col_r = st.columns([5, 1, 5])

        with col_l:
            st.markdown(f"**{local_nombre}**")
            btn_cols = st.columns(len(ANOTACIONES))
            for i, (key, label, pts) in enumerate(ANOTACIONES):
                with btn_cols[i]:
                    if st.button(f"+{pts}\n{key}", key=f"L_{key}", use_container_width=True):
                        st.session_state["score_local"] += pts
                        st.rerun()
            if st.button("↩ Corrección -1", key="L_corr", use_container_width=True):
                st.session_state["score_local"] = max(0, st.session_state["score_local"] - 1)
                st.rerun()

        with col_sep:
            st.markdown("<div style='height:100%;border-left:1px solid #2A2A40;margin:0 auto;width:1px'></div>",
                        unsafe_allow_html=True)

        with col_r:
            st.markdown(f"**{visitante_nombre}**")
            btn_cols = st.columns(len(ANOTACIONES))
            for i, (key, label, pts) in enumerate(ANOTACIONES):
                with btn_cols[i]:
                    if st.button(f"+{pts}\n{key}", key=f"V_{key}", use_container_width=True):
                        st.session_state["score_visitante"] += pts
                        st.rerun()
            if st.button("↩ Corrección -1", key="V_corr", use_container_width=True):
                st.session_state["score_visitante"] = max(0, st.session_state["score_visitante"] - 1)
                st.rerun()

        st.divider()

        # ── Guardar ──
        col_reset, col_save = st.columns([1, 3])
        with col_reset:
            if st.button("Reiniciar marcador", use_container_width=True):
                st.session_state["score_local"]     = 0
                st.session_state["score_visitante"] = 0
                st.rerun()
        with col_save:
            if st.button(
                f"Guardar  {local_nombre} {sl} — {sv} {visitante_nombre}",
                type="primary", use_container_width=True,
            ):
                partido.puntos_local     = sl
                partido.puntos_visitante = sv
                session.commit()
                for k in ["score_local", "score_visitante", "scoring_partido_id"]:
                    st.session_state.pop(k, None)
                st.success(f"Resultado guardado: {local_nombre} {sl} — {sv} {visitante_nombre}")
                st.rerun()
    finally:
        session.close()


# ── Helper: formularios de edición de equipos ─────────────────────────────────
def _render_equipo_forms(session, equipos_lista):
    CATEGORIAS = ["Masculino", "Femenino"]
    for equipo in equipos_lista:
        with st.expander(f"{equipo.nombre} ({equipo.abreviacion})"):
            with st.form(key=f"form_{equipo.id}"):
                nombre = st.text_input("Nombre", value=equipo.nombre)
                col_a, col_cat = st.columns([2, 1])
                with col_a:
                    abrev = st.text_input("Abreviación", value=equipo.abreviacion)
                with col_cat:
                    idx_cat = CATEGORIAS.index(equipo.categoria) if equipo.categoria in CATEGORIAS else 0
                    categoria = st.selectbox("Categoría", CATEGORIAS, index=idx_cat, key=f"cat_{equipo.id}")
                col1, col2 = st.columns(2)
                with col1:
                    color1 = st.color_picker("Color principal", value=equipo.color_principal)
                with col2:
                    color2 = st.color_picker("Color secundario", value=equipo.color_secundario)
                logo = st.text_input("Ruta del logo (opcional)", value=equipo.logo_path or "")
                if st.form_submit_button("Guardar cambios"):
                    equipo.nombre           = nombre
                    equipo.abreviacion      = abrev
                    equipo.color_principal  = color1
                    equipo.color_secundario = color2
                    equipo.logo_path        = logo or None
                    equipo.categoria        = categoria
                    session.commit()
                    st.success("Equipo actualizado.")
                    st.rerun()


# ── Página gestionar equipos ───────────────────────────────────────────────────
def pagina_gestionar_equipos():
    if not es_admin():
        st.error("Solo el administrador puede gestionar equipos.")
        return

    st.markdown(
        "<div class='unaffdo-header'>Gestionar Equipos</div>"
        "<div class='unaffdo-sub'>Panel de administraci&oacute;n</div>"
        "<div class='unaffdo-divider'></div>",
        unsafe_allow_html=True,
    )

    # ── Agregar nuevo equipo ──────────────────────────────────────────────────
    st.subheader("Agregar equipo")
    with st.form("form_nuevo_equipo"):
        col_n, col_a = st.columns([3, 1])
        with col_n:
            nuevo_nombre = st.text_input("Nombre del equipo")
        with col_a:
            nuevo_abrev = st.text_input("Abreviación (3 letras)")
        col_c1, col_c2, col_cat = st.columns(3)
        with col_c1:
            nuevo_color1 = st.color_picker("Color principal", value="#000000")
        with col_c2:
            nuevo_color2 = st.color_picker("Color secundario", value="#FFFFFF")
        with col_cat:
            nueva_categoria = st.selectbox("Categoría", ["Masculino", "Femenino"])
        if st.form_submit_button("Agregar equipo", type="primary"):
            if not nuevo_nombre.strip() or not nuevo_abrev.strip():
                st.error("Nombre y abreviación son obligatorios.")
            else:
                s = get_session()
                try:
                    s.add(Equipo(
                        nombre=nuevo_nombre.strip(),
                        abreviacion=nuevo_abrev.strip().upper(),
                        color_principal=nuevo_color1,
                        color_secundario=nuevo_color2,
                        categoria=nueva_categoria,
                    ))
                    s.commit()
                    st.success(f"Equipo '{nuevo_nombre.strip()}' agregado a categoría {nueva_categoria}.")
                    st.rerun()
                except Exception as exc:
                    s.rollback()
                    st.error(f"Error: {exc}")
                finally:
                    s.close()

    st.divider()

    # ── Equipos existentes por categoría ─────────────────────────────────────
    session = get_session()
    try:
        todos = session.query(Equipo).order_by(Equipo.categoria, Equipo.nombre).all()
        categorias_presentes = sorted({e.categoria for e in todos})

        if len(categorias_presentes) > 1:
            tabs = st.tabs(categorias_presentes)
            for tab, cat in zip(tabs, categorias_presentes):
                with tab:
                    _render_equipo_forms(session, [e for e in todos if e.categoria == cat])
        else:
            _render_equipo_forms(session, todos)

        # ── Generar calendario Femenino si no existe aún ─────────────────────
        equipos_fem = [e for e in todos if e.categoria == "Femenino"]
        tem_fem = session.query(Temporada).filter_by(categoria="Femenino", activa=True).first()

        if equipos_fem and not tem_fem:
            n_fem = len(equipos_fem)
            st.divider()
            if n_fem >= 2 and n_fem % 2 == 0:
                st.subheader("Generar calendario Femenino")
                st.info(f"{n_fem} equipos listos. Elige la fecha de inicio y genera el calendario.")
                with st.form("form_gen_cal_fem"):
                    fecha_ini_fem = st.date_input("Fecha de inicio", value=date.today())
                    nombre_tem_fem = st.text_input("Nombre de la temporada", value="UNAFFDO 2026 - Femenino")
                    if st.form_submit_button("Generar calendario Femenino", type="primary"):
                        from init_db import _crear_temporada_y_calendario
                        s2 = get_session()
                        try:
                            equipos_fem2 = s2.query(Equipo).filter_by(categoria="Femenino").all()
                            _, n_p = _crear_temporada_y_calendario(
                                s2, nombre_tem_fem, "Femenino", fecha_ini_fem, equipos_fem2
                            )
                            s2.commit()
                            st.success(f"Calendario Femenino generado: {n_p} partidos.")
                            st.rerun()
                        except Exception as exc:
                            s2.rollback()
                            st.error(f"Error: {exc}")
                        finally:
                            s2.close()
            else:
                st.info(
                    f"Hay {n_fem} equipo(s) en categoría Femenino. "
                    "Se necesita un número par (mínimo 2) para generar el calendario."
                )
    finally:
        session.close()

    # ── Zona de peligro ──────────────────────────────────────────────────────
    st.markdown(
        '<div style="margin-top:2.5rem;border:1px solid #660000;border-radius:8px;padding:20px 24px;">'
        '<div style="font-family:Barlow Condensed,sans-serif;font-size:1.4rem;font-weight:800;'
        'letter-spacing:2px;color:#CC0000;text-transform:uppercase;margin-bottom:4px;">Zona de Peligro</div>'
        '<div style="font-size:.8rem;color:#8888AA;margin-bottom:16px;">Estas acciones no se pueden deshacer.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Borrar todos los resultados (mantiene el calendario)"):
        st.warning(
            "Esto pone a NULL los marcadores de todos los partidos. "
            "El calendario, los equipos y la temporada se conservan."
        )
        confirmar1 = st.checkbox(
            "Entiendo que se borrarán todos los resultados registrados",
            key="confirm_borrar_resultados",
        )
        if st.button("Borrar resultados", type="primary", disabled=not confirmar1, key="btn_borrar_res"):
            s3 = get_session()
            try:
                s3.query(Partido).update({"puntos_local": None, "puntos_visitante": None})
                s3.commit()
                st.success("Resultados eliminados. La tabla de posiciones está en cero.")
                st.rerun()
            finally:
                s3.close()

    with st.expander("Reinicio completo del torneo (borra TODO y regenera)"):
        st.error(
            "Esto elimina equipos, temporada, partidos y resultados, "
            "y vuelve a crear la base de datos desde cero con los datos originales."
        )
        confirmar2 = st.checkbox(
            "Entiendo que se perderán TODOS los datos del torneo",
            key="confirm_reset_total",
        )
        if st.button("Reiniciar torneo completo", type="primary", disabled=not confirmar2, key="btn_reset_total"):
            from init_db import inicializar
            inicializar(reset=True)
            st.success("Torneo reiniciado. Equipos y calendario regenerados.")
            st.rerun()


# ── Punto de entrada ───────────────────────────────────────────────────────────
if not esta_autenticado():
    pagina_login()
    st.stop()

pagina_activa = sidebar_nav()

if pagina_activa == "📅 Calendario":
    pagina_calendario()
elif pagina_activa == "🏆 Clasificación":
    pagina_clasificacion()
elif pagina_activa == "⚽ Registrar Resultados":
    pagina_registrar_resultados()
elif pagina_activa == "⚙️ Gestionar Equipos":
    pagina_gestionar_equipos()