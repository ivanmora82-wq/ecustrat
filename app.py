import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. CONFIGURACIÓN DE SEGURIDAD (Credenciales de Google)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = {
    "type": "service_account",
    "project_id": "fabled-ranger-480412-b9",
    "private_key_id": "5be77e02ce33b4b12f69dfdda644de61e5ff3d54",
    "private_key": st.secrets["private_key"] if "private_key" in st.secrets else "PASTE_PRIVATE_KEY_HERE",
    "client_email": "emi-database@fabled-ranger-480412-b9.iam.gserviceaccount.com",
    "client_id": "102764735047338306868",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/emi-database%40fabled-ranger-480412-b9.iam.gserviceaccount.com"
}

# Conexión con Google Sheets
def conectar_google():
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("EMI_DATA_PRO")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# 2. INTERFAZ Y ESTILO
st.set_page_config(page_title="EMI MASTER CLOUD", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #ffffff !important; }
    [data-testid="stMetricValue"] { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIONES DE BASE DE DATOS
def guardar_en_nube(hoja_nombre, datos):
    doc = conectar_google()
    if doc:
        hoja = doc.worksheet(hoja_nombre)
        hoja.append_row(datos)

def leer_de_nube(hoja_nombre):
    doc = conectar_google()
    if doc:
        hoja = doc.worksheet(hoja_nombre)
        return pd.DataFrame(hoja.get_all_records())
    return pd.DataFrame()

# 4. CUERPO DE LA APP (Lógica de Negocio)
with st.sidebar:
    st.markdown("<h1 style='color: #d4af37; text-align: center;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    nombre_local = st.text_input("🏢 EMPRESA", "Mi Negocio")
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    # Saldos iniciales (guardados en nube opcionalmente)
    banco = st.number_input("🏦 BANCO", value=0.0)
    caja = st.number_input("💵 CAJA CHICA", value=0.0)

# TABS PRINCIPALES
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTES"])

# --- TAB VENTAS ---
with tabs[0]:
    with st.form("form_ventas", clear_on_submit=True):
        f_v = st.date_input("Fecha", date.today())
        m_v = st.number_input("Monto de Venta", min_value=0.0)
        if st.form_submit_button("Registrar Venta en Nube"):
            guardar_en_nube("Ventas", [str(f_v), sede_act, "Venta", m_v, "Ingreso"])
            st.success("✅ Venta guardada en Google Sheets")
            st.rerun()

    st.write("### Historial Reciente (Desde Google)")
    df_v = leer_de_nube("Ventas")
    if not df_v.empty:
        st.dataframe(df_v[df_v['Sede'] == sede_act], use_container_width=True)

# --- TAB REPORTES ---
with tabs[5]:
    st.subheader("📊 Análisis Consolidado Cloud")
    df_ventas = leer_de_nube("Ventas")
    if not df_ventas.empty:
        res = df_ventas.groupby("Sede")["Monto"].sum().reset_index()
        fig = px.bar(res, x="Sede", y="Monto", title="Ventas Totales por Sede (Datos Reales)", color="Sede")
        st.plotly_chart(fig, use_container_width=True)
