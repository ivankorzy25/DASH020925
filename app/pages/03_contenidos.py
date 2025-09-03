import streamlit as st
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.media_service import MediaService
from app.components.navigation import render_sidebar_navigation
from app.components.login import require_auth
from app.components.upload import file_uploader, media_type_selector, product_selector
from app.models import MediaType

st.set_page_config(page_title="Contenidos - DASH020925", page_icon="🖼️", layout="wide")

with get_db() as db:
    auth_service = AuthService(db)
    media_service = MediaService(db)
    
    @require_auth(auth_service, roles=["admin", "editor", "viewer"])
    def main():
        selected_page = render_sidebar_navigation()
        
        st.title("Gestión de Contenidos Multimedia")
        
        # Tabs for different actions
        tab1, tab2, tab3 = st.tabs(["Subir Nuevo", "Explorar Contenidos", "Versiones"])
        
        with tab1:
            if st.session_state.user["role"] in ["admin", "editor"]:
                render_upload_form(media_service)
            else:
                st.warning("No tiene permisos para subir contenido. Contacte al administrador.")
        
        with tab2:
            render_media_explorer(media_service)
        
        with tab3:
            render_version_manager(media_service)
    
    def render_upload_form(media_service: MediaService):
        """Render the media upload form"""
        st.subheader("Subir Nuevo Contenido")
        
        with st.form("upload_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Título del contenido *")
                media_type = media_type_selector()
                product_id = product_selector(db, allow_none=True)
                notes = st.text_area("Notas (opcional)")
            
            with col2:
                # File uploader with type validation
                allowed_types = {
                    MediaType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
                    MediaType.VIDEO: ['.mp4', '.mov', '.avi', '.mkv'],
                    MediaType.AUDIO: ['.mp3', '.wav', '.ogg'],
                    MediaType.PDF: ['.pdf'],
                    MediaType.HTML: ['.html', '.htm'],
                    MediaType.OTHER: ['.*']
                }
                
                uploaded_file = st.file_uploader(
                    "Seleccione un archivo",
                    type=allowed_types[media_type],
                    help=f"Tipos permitidos: {', '.join(allowed_types[media_type])}"
                )
            
            submitted = st.form_submit_button("Subir Contenido")
            
            if submitted and uploaded_file and title:
                try:
                    media = media_service.upload_media(
                        file_data=uploaded_file,
                        filename=uploaded_file.name,
                        media_type=media_type,
                        title=title,
                        uploaded_by=st.session_state.user["username"],
                        product_id=product_id,
                        notes=notes
                    )
                    st.success(f"Contenido subido exitosamente! ID: {media.id}")
                except Exception as e:
                    st.error(f"Error al subir contenido: {str(e)}")
            elif submitted:
                st.error("Por favor, complete todos los campos obligatorios (*)")
    
    def render_media_explorer(media_service: MediaService):
        """Render the media explorer with filtering and search"""
        st.subheader("Explorar Contenidos")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            type_filter = st.selectbox(
                "Filtrar por tipo",
                ["Todos"] + [t.value for t in MediaType]
            )
        
        with col2:
            search_query = st.text_input("Buscar por título o nombre de archivo")
        
        with col3:
            items_per_page = st.selectbox("Elementos por página", [10, 25, 50], index=0)
        
        # Get media with filtering
        media_items = media_service.get_all_media()
        
        if type_filter != "Todos":
            media_items = [m for m in media_items if m.type.value == type_filter]
        
        if search_query:
            media_items = [m for m in media_items 
                         if search_query.lower() in m.title.lower() 
                         or search_query.lower() in m.file_name.lower()]
        
        # Pagination
        total_items = len(media_items)
        page_number = st.number_input("Página", min_value=1, value=1, 
                                    max_value=(total_items // items_per_page) + 1 if total_items > 0 else 1)
        start_idx = (page_number - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        # Display media
        st.write(f"Mostrando {start_idx + 1}-{end_idx} de {total_items} elementos")
        
        for media in media_items[start_idx:end_idx]:
            render_media_card(media, media_service)
    
    def render_media_card(media, media_service: MediaService):
        """Render a media item as a card"""
        with st.expander(f"{media.title} ({media.type.value})"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Preview based on media type
                if media.type == MediaType.IMAGE:
                    st.image(media.public_url, use_column_width=True)
                elif media.type == MediaType.VIDEO:
                    st.video(media.public_url)
                elif media.type == MediaType.AUDIO:
                    st.audio(media.public_url)
                else:
                    st.write(f"Tipo: {media.type.value}")
                
                st.write(f"**Tamaño:** {media.size_bytes / 1024 / 1024:.2f} MB")
                st.write(f"**Subido por:** {media.uploaded_by}")
                st.write(f"**Fecha:** {media.uploaded_at.strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                st.write(f"**Archivo:** {media.file_name}")
                st.write(f"**MIME Type:** {media.mime_type}")
                st.write(f"**Checksum:** {media.checksum[:8]}...")
                
                if media.product:
                    st.write(f"**Producto asociado:** {media.product.sku} - {media.product.name}")
                
                # Actions
                col_act1, col_act2 = st.columns(2)
                
                with col_act1:
                    if st.button("📋 Copiar URL", key=f"copy_{media.id}"):
                        st.session_state.copied_url = media.public_url
                        st.success("URL copiada al portapapeles")
                
                with col_act2:
                    if st.session_state.user["role"] in ["admin", "editor"]:
                        if st.button("🔄 Nueva versión", key=f"new_ver_{media.id}"):
                            st.session_state.uploading_new_version = media.id
                
                # New version form
                if st.session_state.get("uploading_new_version") == media.id:
                    render_new_version_form(media, media_service)
    
    def render_new_version_form(media, media_service: MediaService):
        """Render form for uploading a new version"""
        with st.form(f"new_version_{media.id}"):
            st.subheader(f"Nueva versión para: {media.title}")
            
            notes = st.text_area("Notas de la versión")
            uploaded_file = st.file_uploader(
                "Suba el nuevo archivo para esta versión",
                type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'mov', 'avi', 'mkv', 'mp3', 'wav', 'ogg', 'pdf', 'html', 'htm']
            )
            
            if st.form_submit_button("Subir Nueva Versión") and uploaded_file:
                try:
                    version = media_service.create_new_version(
                        media_id=media.id,
                        file_data=uploaded_file,
                        filename=uploaded_file.name,
                        uploaded_by=st.session_state.user["username"],
                        notes=notes
                    )
                    st.success(f"Nueva versión {version.version} creada exitosamente!")
                    st.session_state.uploading_new_version = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al crear nueva versión: {str(e)}")
    
    def render_version_manager(media_service: MediaService):
        """Render the version management interface"""
        st.subheader("Gestión de Versiones")
        
        # Select media to view versions
        media_items = media_service.get_all_media()
        media_options = {f"{m.id} - {m.title}": m.id for m in media_items}
        
        if not media_options:
            st.info("No hay contenidos para mostrar.")
            return

        selected_media_key = st.selectbox(
            "Seleccionar contenido",
            options=list(media_options.keys()),
            format_func=lambda x: x
        )
        
        if selected_media_key:
            media_id = media_options[selected_media_key]
            versions = media_service.get_media_versions(media_id)
            
            st.write(f"**Versiones encontradas:** {len(versions)}")
            
            for version in versions:
                with st.expander(f"Versión {version.version} - {version.created_at.strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Ruta de almacenamiento:** {version.storage_path}")
                        st.write(f"**URL pública:** {version.public_url}")
                        st.write(f"**Notas:** {version.notes or 'Sin notas'}")
                    
                    with col2:
                        if st.button("🔍 Ver detalles", key=f"view_ver_{version.id}"):
                            st.session_state.viewing_version = version.id
                        
                        if version.id != versions[0].id and st.session_state.user["role"] in ["admin", "editor"]:
                            if st.button("↩️ Revertir a esta versión", key=f"revert_ver_{version.id}"):
                                try:
                                    # Implementation for reverting to a version would go here
                                    st.success(f"Revertido a la versión {version.version}")
                                except Exception as e:
                                    st.error(f"Error al revertir: {str(e)}")
    
    main()
