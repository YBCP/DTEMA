# 2. config.py - Configuración de la página y estilos

import streamlit as st

def setup_page():
    """Configura la página de Streamlit."""
    st.set_page_config(
        page_title="Tablero de Control de Cronogramas",
        page_icon="📊",
        layout="wide"
    )

def load_css():
    """Carga los estilos CSS personalizados."""
    st.markdown("""
    <style>
        .main {
            padding: 1rem;
        }
        .title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1E3A8A;
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: #f1f5f9;
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        }
        .subtitle {
            font-size: 1.5rem;
            font-weight: 600;
            color: #334155;
            margin: 1rem 0;
        }
        .info-box {
            background-color: #e0f2fe;
            border-left: 4px solid #0ea5e9;
            padding: 1rem;
            border-radius: 0.25rem;
            margin: 1rem 0;
        }
        .warning-box {
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 1rem;
            border-radius: 0.25rem;
            margin: 1rem 0;
        }
        .error-box {
            background-color: #fee2e2;
            border-left: 4px solid #ef4444;
            padding: 1rem;
            border-radius: 0.25rem;
            margin: 1rem 0;
        }
        .vencido {
            background-color: #fee2e2;
        }
        .proximo {
            background-color: #fef3c7;
        }
        .normal {
            background-color: #ffffff;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f1f5f9;
            border-radius: 4px 4px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #e0f2fe;
            border-bottom: 2px solid #0ea5e9;
        }
        /* Estilos adicionales para campos de fecha */
        .date-field {
            font-family: monospace;
            color: #1E3A8A;
        }
        /* Formateo para fechas en tablas */
        .date-column {
            font-weight: 500;
            color: #1E40AF;
        }
    </style>
    """, unsafe_allow_html=True)
