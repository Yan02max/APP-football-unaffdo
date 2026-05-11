"""Configuración de streamlit-authenticator y helpers de permisos."""
import os
import yaml
import streamlit as st
import streamlit_authenticator as stauth


def cargar_config() -> dict:
    """Carga el archivo config.yaml con credenciales y configuración de cookie."""
    ruta = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(ruta, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def crear_autenticador(config: dict) -> stauth.Authenticate:
    """Crea la instancia de Authenticate a partir del config."""
    return stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )


def esta_autenticado() -> bool:
    """True si el usuario tiene sesión activa."""
    return st.session_state.get("authentication_status") is True


def obtener_rol() -> str | None:
    """Retorna el rol del usuario autenticado ('admin' o 'arbitro'), o None."""
    if not esta_autenticado():
        return None
    username = st.session_state.get("username", "")
    config = cargar_config()
    user_data = config["credentials"]["usernames"].get(username, {})
    return user_data.get("role")


def es_admin() -> bool:
    return obtener_rol() == "admin"


def es_arbitro() -> bool:
    return obtener_rol() in ("admin", "arbitro")


def requiere_login(funcion_pagina):
    """Decorador: muestra aviso si el usuario no está autenticado."""
    def wrapper(*args, **kwargs):
        if not esta_autenticado():
            st.warning("Debes iniciar sesión para acceder a esta sección.")
            return
        funcion_pagina(*args, **kwargs)
    return wrapper


def requiere_admin(funcion_pagina):
    """Decorador: solo permite acceso a usuarios con rol admin."""
    def wrapper(*args, **kwargs):
        if not esta_autenticado():
            st.warning("Debes iniciar sesión para acceder a esta sección.")
            return
        if not es_admin():
            st.error("No tienes permisos para acceder a esta sección.")
            return
        funcion_pagina(*args, **kwargs)
    return wrapper