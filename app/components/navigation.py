import streamlit as st

def render_sidebar_navigation():
    """Render the sidebar navigation"""
    st.sidebar.title("DASH020925")
    st.sidebar.divider()
    
    # Navigation options
    nav_options = {
        "Inicio": "🏠",
        "Productos": "📦",
        "Contenidos": "🖼️",
        "Precios": "💰",
        "Auditoría": "📊",
        "Administración": "⚙️"
    }
    
    # User info if logged in
    if "user" in st.session_state:
        st.sidebar.write(f"**Usuario:** {st.session_state.user['username']}")
        st.sidebar.write(f"**Rol:** {st.session_state.user['role']}")
        st.sidebar.divider()
    
    # Navigation selection
    selected = st.sidebar.radio(
        "Navegación",
        list(nav_options.keys()),
        format_func=lambda x: f"{nav_options[x]} {x}"
    )
    
    return selected
