import streamlit as st
import pandas as pd
from io import StringIO
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.price_service import PriceService
from app.components.navigation import render_sidebar_navigation
from app.components.login import require_auth

st.set_page_config(page_title="Precios - DASH020925", page_icon="💰", layout="wide")

with get_db() as db:
    auth_service = AuthService(db)
    price_service = PriceService(db)
    
    @require_auth(auth_service, roles=["admin", "editor"])
    def main():
        selected_page = render_sidebar_navigation()
        
        st.title("Gestión de Precios")
        
        # Tabs for different actions
        tab1, tab2, tab3 = st.tabs(["Importar Precios", "Historial de Cambios", "Listas de Precios"])
        
        with tab1:
            render_price_importer(price_service)
        
        with tab2:
            render_price_history(price_service)
        
        with tab3:
            render_price_lists(price_service)
    
    def render_price_importer(price_service: PriceService):
        """Render the price import interface"""
        st.subheader("Importar Lista de Precios")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Seleccione archivo CSV o Excel",
            type=['csv', 'xlsx'],
            help="El archivo debe contener columnas 'sku' y 'price'"
        )
        
        if uploaded_file:
            # Read file based on type
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Validate required columns
            if 'sku' not in df.columns or 'price' not in df.columns:
                st.error("El archivo debe contener columnas 'sku' y 'price'")
                return
            
            # Show preview
            st.subheader("Vista Previa del Archivo")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Get import details
            col1, col2 = st.columns(2)
            
            with col1:
                price_list_name = st.text_input("Nombre de la lista de precios *", 
                                              value=f"Importación {pd.Timestamp.now().strftime('%Y-%m-%d')}")
            
            with col2:
                source = st.text_input("Fuente *", value=uploaded_file.name)
            
            if st.button("Analizar Diferencias", key="analyze_prices"):
                try:
                    # Convert DataFrame to CSV string for processing
                    csv_data = df.to_csv(index=False)
                    
                    # Analyze differences
                    diff_report = price_service.import_prices_from_csv(
                        csv_data=csv_data,
                        price_list_name=price_list_name,
                        source=source,
                        imported_by=st.session_state.user["username"]
                    )
                    
                    # Store diff report in session state
                    st.session_state.diff_report = diff_report
                    st.session_state.price_list_name = price_list_name
                    st.session_state.source = source
                    
                except Exception as e:
                    st.error(f"Error al analizar precios: {str(e)}")
            
            # Show diff report if available
            if 'diff_report' in st.session_state:
                render_diff_report(st.session_state.diff_report, price_service)
    
    def render_diff_report(diff_report: dict, price_service: PriceService):
        """Render the price difference report"""
        st.subheader("Reporte de Diferencias")
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Nuevos SKUs", len(diff_report['new_skus']))
        
        with col2:
            st.metric("Precios Actualizados", len(diff_report['updated_prices']))
        
        with col3:
            st.metric("Sin Cambios", len(diff_report['unchanged']))
        
        with col4:
            st.metric("SKUs Inválidos", len(diff_report['invalid_skus']))
        
        # Details tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Nuevos SKUs", "Precios Actualizados", "Sin Cambios", "SKUs Inválidos"])
        
        with tab1:
            if diff_report['new_skus']:
                st.dataframe(pd.DataFrame(diff_report['new_skus']), use_container_width=True)
            else:
                st.info("No hay nuevos SKUs")
        
        with tab2:
            if diff_report['updated_prices']:
                st.dataframe(pd.DataFrame(diff_report['updated_prices']), use_container_width=True)
            else:
                st.info("No hay precios actualizados")
        
        with tab3:
            if diff_report['unchanged']:
                st.dataframe(pd.DataFrame(diff_report['unchanged']), use_container_width=True)
            else:
                st.info("No hay elementos sin cambios")
        
        with tab4:
            if diff_report['invalid_skus']:
                st.warning("Los siguientes SKUs no existen en la base de datos:")
                st.write(", ".join(diff_report['invalid_skus']))
            else:
                st.info("No hay SKUs inválidos")
        
        # Apply changes button
        if diff_report['new_skus'] or diff_report['updated_prices']:
            if st.button("✅ Aplicar Cambios", type="primary"):
                try:
                    # Combine new SKUs and updated prices
                    changes = diff_report['new_skus'] + diff_report['updated_prices']
                    
                    price_list = price_service.apply_price_changes(
                        price_changes=changes,
                        price_list_name=st.session_state.price_list_name,
                        source=st.session_state.source,
                        applied_by=st.session_state.user["username"]
                    )
                    
                    st.success(f"Cambios aplicados exitosamente! Lista de precios ID: {price_list.id}")
                    
                    # Clear session state
                    del st.session_state.diff_report
                    del st.session_state.price_list_name
                    del st.session_state.source
                    
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error al aplicar cambios: {str(e)}")
    
    def render_price_history(price_service: PriceService):
        """Render price history for a specific product"""
        st.subheader("Historial de Precios")
        
        # Product selector
        from app.services.product_service import ProductService
        product_service = ProductService(db)
        products = product_service.get_all_products()
        
        product_options = {f"{p.sku} - {p.name}": p.sku for p in products}
        if not product_options:
            st.info("No hay productos para mostrar.")
            return
            
        selected_key = st.selectbox("Seleccionar Producto", options=list(product_options.keys()))
        
        if selected_key:
            sku = product_options[selected_key]
            price_history = price_service.get_price_history(sku)
            
            if price_history:
                # Convert to DataFrame for better display
                history_data = []
                for item in price_history:
                    history_data.append({
                        "Fecha": item.effective_from.strftime('%Y-%m-%d %H:%M'),
                        "Precio": item.price,
                        "Moneda": item.currency,
                        "Lista de Precios": item.price_list.name,
                        "Fuente": item.price_list.source,
                        "Notas": item.notes
                    })
                
                st.dataframe(pd.DataFrame(history_data), use_container_width=True)
                
                # Price chart
                chart_data = pd.DataFrame([{
                    "Fecha": item.effective_from,
                    "Precio": item.price
                } for item in price_history])
                
                st.line_chart(chart_data.set_index("Fecha"))
            else:
                st.info("No hay historial de precios para este producto")
    
    def render_price_lists(price_service: PriceService):
        """Render historical price lists"""
        st.subheader("Listas de Precios Históricas")
        
        # TODO: Implement price lists view
        st.info("Funcionalidad en desarrollo. Próximamente...")
    
    main()
