import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# 1. CONEXIÓN (CON LIMPIEZA DE LLAVE)
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Esto quita cualquier espacio que rompa el base64
        pk = st.secrets["private_key"].strip()
        creds_dict = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": pk,
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds).open("EMI_DATA_PRO")
    except: return None

def leer(hoja):
    try:
        doc = conectar()
        return pd.DataFrame(doc.worksheet(hoja).get_all_records())
    except: return pd.DataFrame()

# 2. LÓGICA DE BALANCE
def calcular_balance_total(b_ini, c_ini):
    total_nube = 0.0
    # Sumamos Ventas
    df_v = leer("Ventas")
    if not df_v.empty: total_nube += pd.to_numeric(df_v['Monto']).sum()
    
    # Restamos Hormiga (Gastos)
    df_h = leer("Hormiga")
    if not df_h.empty: total_nube -= pd.to_numeric(df_h['Monto']).sum()
    
    return b_ini + c_ini + total_nube

# 3. INTERFAZ
st.set_page_config(page_title="EMI MASTER CLOUD", layout="wide")
st.markdown("<style>[data-testid='stSidebar'] { background-color: #1c2e4a !important; } .stMetric { background-color: #d4af37 !important; padding: 15px; border-radius: 15px; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1 style='color: #d4af37;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO INICIAL", value=0.0)
    c_ini = st.number_input("💵 CAJA INICIAL", value=0.0)
    
    # El Balance se actualiza solo
    balance = calcular_balance_total(b_ini, c_ini)
    st.metric("BALANCE REAL", f"$ {round(balance, 2)}")

st.info("💡 Registra una venta para ver cómo sube el balance automáticamente.")
# Aquí irían tus pestañas de Ventas, Fijos, etc.
