import streamlit as st
import json
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.audit_service import get_audit_logs
from app.components.navigation import render_sidebar_navigation
from app.components.login import require_auth

st.set_page_config(page_title="Auditoría - DASH020925", page_icon="📊", layout="wide")

with get_db() as db:
    auth_service = AuthService(db)
    
    @require_auth(auth_service, roles=["admin", "editor"])
    def main():
        selected_page = render_sidebar_navigation()
        
        st.title("Registro de Auditoría")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            entity_filter = st.selectbox(
                "Filtrar por entidad",
                ["Todas"] + ["product", "media", "price_list", "user"]
            )
        
        with col2:
            action_filter = st.selectbox(
                "Filtrar por acción",
                ["Todas"] + ["create", "update", "delete", "price_update"]
            )
        
        with col3:
            actor_filter = st.text_input("Filtrar por usuario")
        
        with col4:
            items_per_page = st.selectbox("Elementos por página", [20, 50, 100], index=0)
        
        # Get audit logs with filters
        audit_logs = get_audit_logs(
            db=db,
            entity=entity_filter if entity_filter != "Todas" else None,
            action=action_filter if action_filter != "Todas" else None,
            actor=actor_filter if actor_filter else None,
            limit=items_per_page
        )
        
        # Display audit logs
        st.subheader(f"Registros de Auditoría ({len(audit_logs)})")
        
        for log in audit_logs:
            with st.expander(f"{log.entity}.{log.action} - {log.created_at.strftime('%Y-%m-%d %H:%M')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Entidad:** {log.entity}")
                    st.write(f"**ID de Entidad:** {log.entity_id}")
                    st.write(f"**Acción:** {log.action}")
                    st.write(f"**Usuario:** {log.actor}")
                    st.write(f"**Fecha:** {log.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
                with col2:
                    st.write("**Payload:**")
                    try:
                        payload = json.loads(log.payload_json)
                        st.json(payload, expanded=False)
                    except:
                        st.text(log.payload_json)
    
    main()
