from __future__ import annotations
import hmac
import bcrypt
import streamlit as st

def _auth_config():
    try:
        cfg = st.secrets["auth"]
        return {"username": str(cfg.get("username","owner")), "password_hash": str(cfg.get("password_hash","")), "display_name": str(cfg.get("display_name","Owner"))}
    except Exception:
        return {"username":"demo","password_hash":"","display_name":"Modo Demo"}

def require_login() -> bool:
    cfg = _auth_config()
    if not cfg["password_hash"]:
        st.session_state.authenticated = True
        st.session_state.display_name = cfg["display_name"]
        st.session_state.demo_login = True
        return True
    if st.session_state.get("authenticated"):
        return True
    st.markdown("""<div class="login-shell"><div class="eyebrow">OWNER OS</div><div class="login-title">Ingreso privado</div><div class="login-subtitle">Acceso protegido</div></div>""", unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar", use_container_width=True)
    if submitted:
        valid_user = hmac.compare_digest(username.strip(), cfg["username"])
        try: valid_pass = bcrypt.checkpw(password.encode("utf-8"), cfg["password_hash"].encode("utf-8"))
        except Exception: valid_pass = False
        if valid_user and valid_pass:
            st.session_state.authenticated = True
            st.session_state.display_name = cfg["display_name"]
            st.rerun()
        else:
            st.error("Credenciales incorrectas.")
    st.stop()

def logout_button():
    if st.session_state.get("demo_login"):
        st.sidebar.caption("Modo demo sin login")
        return
    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        for key in ["authenticated","display_name","demo_login"]:
            st.session_state.pop(key, None)
        st.rerun()
