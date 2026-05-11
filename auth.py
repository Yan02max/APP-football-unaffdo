"""Autenticación manual con bcrypt + helpers de permisos."""
import os
import yaml
import bcrypt
import streamlit as st


def cargar_config() -> dict:
    ruta = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(ruta, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def verificar_login(username: str, password: str) -> bool:
    """Verifica usuario/contraseña contra el config.yaml usando bcrypt."""
    config = cargar_config()
    users = config["credentials"]["usernames"]
    if username not in users:
        return False
    hashed = users[username]["password"]
    return bcrypt.checkpw(password.encode(), hashed.encode())


def hacer_login(username: str) -> None:
    """Establece el estado de sesión tras credenciales correctas."""
    config = cargar_config()
    user_data = config["credentials"]["usernames"][username]
    st.session_state["authentication_status"] = True
    st.session_state["username"] = username
    st.session_state["name"] = user_data["name"]


def hacer_logout() -> None:
    for key in ["authentication_status", "username", "name"]:
        st.session_state.pop(key, None)


def esta_autenticado() -> bool:
    return st.session_state.get("authentication_status") is True


def obtener_rol() -> str | None:
    if not esta_autenticado():
        return None
    username = st.session_state.get("username", "")
    config = cargar_config()
    return config["credentials"]["usernames"].get(username, {}).get("role")


def es_admin() -> bool:
    return obtener_rol() == "admin"


def es_arbitro() -> bool:
    return obtener_rol() in ("admin", "arbitro")