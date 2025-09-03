import streamlit as st
from app.services.auth_service import AuthService

def login_form(auth_service: AuthService) -> bool:
    """Render a login form and return True if authentication is successful"""
    st.subheader("Iniciar Sesión")
    
    with st.form("login_form"):
        username = st.text_input("Usuario", key="login_username")
        password = st.text_input("Contraseña", type="password", key="login_password")
        submit_button = st.form_submit_button("Iniciar Sesión")
        
        if submit_button:
            if not username or not password:
                st.error("Por favor, complete todos los campos")
                return False
            
            user = auth_service.authenticate_user(username, password)
            if user:
                token = auth_service.generate_token(user)
                st.session_state.token = token
                st.session_state.user = {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.value
                }
                st.success(f"Bienvenido, {user.username}!")
                st.rerun()
            else:
                st.error("Credenciales inválidas")
    
    return False

def logout_button():
    """Render a logout button"""
    if st.button("Cerrar Sesión", key="logout_button"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def require_auth(auth_service: AuthService, roles: list = None):
    """Decorator to require authentication for a page"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check if user is authenticated
            if "token" not in st.session_state:
                st.error("Por favor, inicie sesión para acceder a esta página")
                login_form(auth_service)
                return
            
            # Verify token
            user = auth_service.get_current_user(st.session_state.token)
            if not user:
                st.error("Sesión expirada o inválida")
                login_form(auth_service)
                return
            
            # Check roles if specified
            if roles and user.role.value not in roles:
                st.error("No tiene permisos para acceder a esta página")
                return
            
            # Call the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator
