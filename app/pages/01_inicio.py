import streamlit as st
from app.database import get_db
from app.services.auth_service import AuthService
from app.components.navigation import render_sidebar_navigation
from app.components.login import require_auth

st.set_page_config(page_title="Inicio - DASH020925", page_icon="🏠", layout="wide")

with get_db() as db:
    auth_service = AuthService(db)
    
    @require_auth(auth_service)
    def main():
        selected_page = render_sidebar_navigation()
        
        st.title("Dashboard Principal")
        st.write("Bienvenido al sistema de gestión de contenidos y precios")
        
        # KPIs and stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Productos", "125", "12%")
        
        with col2:
            st.metric("Archivos", "348", "8%")
        
        with col3:
            st.metric("Cambios de Precio", "42", "-3%")
        
        # Recent activity
        st.subheader("Actividad Reciente")
        st.dataframe({
            "Fecha": ["2024-01-15", "2024-01-15", "2024-01-14"],
            "Acción": ["Importación de precios", "Subida de imagen", "Actualización de producto"],
            "Usuario": ["admin", "editor", "editor"],
            "Detalles": ["25 productos actualizados", "product_123.jpg", "SKU: PROD001"]
        }, use_container_width=True)
    
    main()
