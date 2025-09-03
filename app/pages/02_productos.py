import streamlit as st
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.product_service import ProductService
from app.components.navigation import render_sidebar_navigation
from app.components.login import require_auth

st.set_page_config(page_title="Productos - DASH020925", page_icon="📦", layout="wide")

with get_db() as db:
    auth_service = AuthService(db)
    product_service = ProductService(db)
    
    @require_auth(auth_service, roles=["admin", "editor", "viewer"])
    def main():
        selected_page = render_sidebar_navigation()
        
        st.title("Gestión de Productos")
        
        # Product list
        products = product_service.get_all_products()
        
        # Search and filters
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input("Buscar productos", placeholder="SKU o nombre...")
        
        with col2:
            status_filter = st.selectbox("Estado", ["Todos", "Activo", "Inactivo", "Borrador"])
        
        # Filter products
        filtered_products = products
        if search_query:
            filtered_products = [p for p in filtered_products 
                               if search_query.lower() in p.sku.lower() 
                               or search_query.lower() in p.name.lower()]
        
        if status_filter != "Todos":
            status_map = {"Activo": "active", "Inactivo": "inactive", "Borrador": "draft"}
            filtered_products = [p for p in filtered_products if p.status.value == status_map[status_filter]]
        
        # Display products
        st.subheader(f"Productos ({len(filtered_products)})")
        
        for product in filtered_products:
            with st.expander(f"{product.sku} - {product.name}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Precio:** ${product.price} {product.currency}")
                    st.write(f"**Estado:** {product.status.value}")
                    st.write(f"**Creado:** {product.created_at.strftime('%Y-%m-%d')}")
                
                with col2:
                    st.write(f"**Descripción:** {product.description or 'Sin descripción'}")
                    
                    if st.button("Editar", key=f"edit_{product.id}"):
                        st.session_state.editing_product = product.id
                
                if st.session_state.get("editing_product") == product.id:
                    edit_product_form(product_service, product)
    
    def edit_product_form(product_service, product):
        """Render a form to edit a product"""
        with st.form(f"edit_form_{product.id}"):
            new_name = st.text_input("Nombre", value=product.name)
            new_description = st.text_area("Descripción", value=product.description or "")
            new_price = st.number_input("Precio", value=float(product.price), min_value=0.0, step=0.01)
            new_currency = st.selectbox("Moneda", ["USD", "EUR", "GBP"], 
                                      index=["USD", "EUR", "GBP"].index(product.currency))
            new_status = st.selectbox("Estado", ["active", "inactive", "draft"], 
                                    index=["active", "inactive", "draft"].index(product.status.value))
            
            if st.form_submit_button("Guardar cambios"):
                try:
                    product_service.update_product(
                        product.id,
                        name=new_name,
                        description=new_description,
                        price=new_price,
                        currency=new_currency,
                        status=new_status,
                        updated_by=st.session_state.user["username"]
                    )
                    st.success("Producto actualizado correctamente")
                    st.session_state.editing_product = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar producto: {e}")
    
    main()
