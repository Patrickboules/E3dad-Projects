# app.py (main entry point)
import streamlit as st
from poll_app import run_poll
from poll_app.components import inject_styles

# Page configuration
st.set_page_config(
    page_title="مشاريع اعداد 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject the orange / light-mode / RTL stylesheet
inject_styles()

# Run the poll
run_poll()
