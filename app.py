import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# 1. CONEXIÓN PROFESIONAL
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Limpieza técnica de la llave
        pk = st.secrets["private_key"].replace('\\n', '\n')
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

def guardar(hoja, fila):
    try:
        doc = conectar()
        doc.worksheet(hoja).append_row(fila)
        st.success(f"✅ Registrado en {hoja}")
    except: st.error(f"Error al guardar en {hoja}")

# 2. LÓGICA DE BALANCE GENERAL
def calcular_balance(b_ini, c_ini):
    ganancias = 0.0
    gastos = 0.0
    
    # Sumamos Ventas (Ingresos)
    df_v = leer("Ventas")
    if not df_v.empty: ganancias += pd.to_numeric(df_v['Monto'], errors='coerce').sum()
    
    # Restamos Hormiga (Egresos)
    df_h = leer("Hormiga")
    if not df_h.empty: gastos += pd.to_numeric(df_h['Monto'], errors='coerce').sum()
    
    return b_ini + c_ini + ganancias - gastos

# 3. INTERFAZ
st.set_page_config(page_title="EMI MASTER CLOUD", layout="wide")
st.markdown("<style>[data-testid='stSidebar'] { background-color: #1c2e4a !important; } .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 15px; border-radius: 15px; font-weight: bold; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1 style='color: #d4af37;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO INICIAL", value=0.0)
    c_ini = st.number_input("💵 CAJA INICIAL", value=0.0)
    
    res = calcular_balance(b_ini, c_ini)
    st.metric("BALANCE GENERAL REAL", f"$ {round(res, 2)}")

tabs = st.tabs(["💰 VENTAS", "🐜 HORMIGA", "📈 REPORTES"])

with tabs[0]: # VENTAS
    with st.form("fv", clear_on_submit=True):
        mv = st.number_input("Monto de Venta", min_value=0.0)
        if st.form_submit_button("REGISTRAR VENTA"):
            guardar("Ventas", [str(date.today()), sede_act, "Venta", mv, "Ingreso"])
            st.rerun()
    st.dataframe(leer("Ventas"), use_container_width=True)

with tabs[1]: # HORMIGA
    with st.form("fh", clear_on_submit=True):
        mh = st.number_input("Monto Gasto", min_value=0.0)
        if st.form_submit_button("REGISTRAR GASTO"):
            guardar("Hormiga", [str(date.today()), sede_act, "Gasto", mh, "Egreso"])
            st.rerun()
    st.dataframe(leer("Hormiga"), use_container_width=True)
