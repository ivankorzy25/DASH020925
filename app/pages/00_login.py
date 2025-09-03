import streamlit as st
from app.database import get_db
from app.services.auth_service import AuthService
from app.components.login import login_form

st.set_page_config(page_title="Login - DASH020925", page_icon="🔐", layout="centered")

st.title("DASH020925")
st.subheader("Sistema de Gestión de Contenidos y Precios")

with get_db() as db:
    auth_service = AuthService(db)
    
    # Show login form
    if "token" in st.session_state:
        st.success("Ya has iniciado sesión.")
        if st.button("Ir al Dashboard"):
            st.switch_page("pages/01_inicio.py")
    else:
        login_form(auth_service)
    
    # Demo credentials (remove in production)
    st.divider()
    with st.expander("Credenciales de Demo"):
        st.write("**Admin:** admin / admin123")
        st.write("**Editor:** editor / editor123")
        st.write("**Visualizador:** viewer / viewer123")
