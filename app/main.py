import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(
        page_title="DASH020925 - Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Check if user is authenticated
    if "token" not in st.session_state:
        # Redirect to login page
        st.switch_page("pages/00_login.py")
    else:
        # Redirect to home page
        st.switch_page("pages/01_inicio.py")

if __name__ == "__main__":
    main()
