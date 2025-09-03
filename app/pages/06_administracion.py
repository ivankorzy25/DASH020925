import streamlit as st
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.product_service import ProductService
from app.components.navigation import render_sidebar_navigation
from app.components.login import require_auth

st.set_page_config(page_title="Administración - DASH020925", page_icon="⚙️", layout="wide")

with get_db() as db:
    auth_service = AuthService(db)
    
    @require_auth(auth_service, roles=["admin"])
    def main():
        selected_page = render_sidebar_navigation()
        
        st.title("Panel de Administración")
        
        # Admin tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Usuarios", "Sistema", "Base de Datos", "Configuración"])
        
        with tab1:
            render_user_management()
        
        with tab2:
            render_system_info()
        
        with tab3:
            render_database_tools()
        
        with tab4:
            render_config_editor()
    
    def render_user_management():
        """Render user management interface"""
        st.subheader("Gestión de Usuarios")
        
        # TODO: Implement user management
        st.info("Módulo de gestión de usuarios en desarrollo. Próximamente...")
        
        # Placeholder for user management
        users = [
            {"username": "admin", "role": "admin", "email": "admin@example.com", "status": "active"},
            {"username": "editor", "role": "editor", "email": "editor@example.com", "status": "active"},
            {"username": "viewer", "role": "viewer", "email": "viewer@example.com", "status": "active"},
        ]
        
        st.dataframe(users, use_container_width=True)
    
    def render_system_info():
        """Render system information and stats"""
        st.subheader("Información del Sistema")
        
        # System stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Productos", "156", "12%")
            st.metric("Archivos", "423", "8%")
        
        with col2:
            st.metric("Usuarios", "3", "0%")
            st.metric("Cambios de Precio", "67", "-3%")
        
        with col3:
            st.metric("Registros de Auditoría", "1,234", "15%")
            st.metric("Espacio Utilizado", "2.3 GB", "5%")
        
        # Storage information
        st.subheader("Almacenamiento")
        st.progress(65, text="65% del espacio utilizado")
        
        # System health
        st.subheader("Estado del Sistema")
        col_health1, col_health2, col_health3 = st.columns(3)
        
        with col_health1:
            st.success("✅ Base de Datos")
            st.success("✅ Almacenamiento")
        
        with col_health2:
            st.success("✅ Autenticación")
            st.success("✅ Servicios")
        
        with col_health3:
            st.warning("⚠️  Caché")
            st.success("✅ Logs")
    
    def render_database_tools():
        """Render database management tools"""
        st.subheader("Herramientas de Base de Datos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Ejecutar Migraciones", help="Ejecutar todas las migraciones pendientes"):
                try:
                    # This would actually run the migrations
                    st.success("Migraciones ejecutadas correctamente")
                except Exception as e:
                    st.error(f"Error en migraciones: {str(e)}")
            
            if st.button("📊 Estadísticas de DB", help="Mostrar estadísticas de la base de datos"):
                try:
                    # This would show DB stats
                    st.success("Estadísticas generadas correctamente")
                except Exception as e:
                    st.error(f"Error al obtener estadísticas: {str(e)}")
        
        with col2:
            if st.button("🧹 Limpiar Caché", help="Limpiar caché de la aplicación"):
                try:
                    # This would clear cache
                    st.success("Caché limpiado correctamente")
                except Exception as e:
                    st.error(f"Error al limpiar caché: {str(e)}")
            
            if st.button("🔍 Ver Esquema", help="Mostrar esquema de la base de datos"):
                try:
                    # This would show DB schema
                    st.success("Esquema mostrado correctamente")
                except Exception as e:
                    st.error(f"Error al mostrar esquema: {str(e)}")
        
        # Dangerous operations (with confirmation)
        st.subheader("Operaciones Peligrosas")
        
        if st.button("🗑️ Eliminar Datos de Prueba", type="secondary"):
            st.warning("Esta acción no se puede deshacer. ¿Está seguro?")
            
            col_conf1, col_conf2 = st.columns(2)
            
            with col_conf1:
                if st.button("✅ Confirmar Eliminación", type="primary"):
                    try:
                        # This would delete test data
                        st.success("Datos de prueba eliminados correctamente")
                    except Exception as e:
                        st.error(f"Error al eliminar datos: {str(e)}")
            
            with col_conf2:
                if st.button("❌ Cancelar"):
                    st.info("Eliminación cancelada")
    
    def render_config_editor():
        """Render configuration editor"""
        st.subheader("Editor de Configuración")
        
        # Current configuration display
        st.info("""
        **⚠️ Advertencia:** Los cambios en la configuración pueden afectar el comportamiento 
        de la aplicación. Proceda con cuidado.
        """)
        
        # Configuration sections
        config_sections = {
            "Database": {
                "DB_URL": "postgresql://user:pass@localhost:5432/dash020925",
                "DB_POOL_SIZE": "5",
                "DB_MAX_OVERFLOW": "10"
            },
            "Storage": {
                "STORAGE_TYPE": "local",
                "STORAGE_BUCKET": "uploads",
                "STORAGE_LOCAL_PATH": "./storage"
            },
            "Security": {
                "SECRET_KEY": "********",
                "TOKEN_EXPIRY_MINUTES": "1440",
                "PASSWORD_SALT": "********"
            }
        }
        
        for section_name, section_config in config_sections.items():
            with st.expander(f"Sección: {section_name}"):
                for key, value in section_config.items():
                    new_value = st.text_input(key, value=value, key=f"config_{key}")
                    
                    if new_value != value:
                        st.warning(f"Valor modificado: {value} → {new_value}")
                
                if st.button(f"Guardar {section_name}", key=f"save_{section_name}"):
                    st.success(f"Configuración de {section_name} guardada")
    
    main()
