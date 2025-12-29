import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. CONFIGURACIÓN Y ESTILO (Optimizado para Celulares)
st.set_page_config(page_title="EMI MASTER CLOUD", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #ffffff !important; }
    [data-testid="stMetricValue"] { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 10px; border-radius: 10px; }
    .resaltado-suma { background-color: #f1f3f5; border-left: 5px solid #d4af37; padding: 12px; margin-bottom: 15px; color: #1c2e4a; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN A GOOGLE SHEETS
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Intentamos leer la llave desde los Secrets de Streamlit
    try:
        creds_dict = {
            "type": "service_account",
            "project_id": "fabled-ranger-480412-b9",
            "private_key": st.secrets["private_key"],
            "client_email": "emi-database@fabled-ranger-480412-b9.iam.gserviceaccount.com",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("EMI_DATA_PRO")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def guardar(hoja_nombre, fila):
    try:
        doc = conectar()
        if doc:
            hoja = doc.worksheet(hoja_nombre)
            hoja.append_row(fila)
            st.success(f"✅ Registrado en {hoja_nombre}")
    except Exception as e:
        st.error(f"No se pudo guardar: {e}")

def leer(hoja_nombre):
    try:
        doc = conectar()
        if doc:
            return pd.DataFrame(doc.worksheet(hoja_nombre).get_all_records())
    except:
        return pd.DataFrame()

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("<h1 style='color: #d4af37; text-align: center;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    nombre_local = st.text_input("🏢 EMPRESA", "Mi Negocio")
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
# 4. TABS
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTES"])

# --- TAB VENTAS ---
with tabs[0]:
    with st.form("f_v", clear_on_submit=True):
        m_v = st.number_input("Monto Venta", min_value=0.0)
        if st.form_submit_button("Registrar en Nube"):
            guardar("Ventas", [str(date.today()), sede_act, "Venta", m_v, "Ingreso"])
            st.rerun()
    
    df_v = leer("Ventas")
    if not df_v.empty:
        df_sede = df_v[df_v['Sede'] == sede_act]
        st.markdown(f"<div class='resaltado-suma'>Ventas en {sede_act}: $ {df_sede['Monto'].sum() if not df_sede.empty else 0}</div>", unsafe_allow_html=True)
        st.dataframe(df_sede, use_container_width=True)

# --- TAB PROVEEDORES ---
with tabs[3]:
    with st.form("f_p", clear_on_submit=True):
        cp = st.text_input("Nombre Proveedor")
        mp = st.number_input("Monto")
        vp = st.date_input("Vencimiento")
        if st.form_submit_button("Guardar Deuda"):
            guardar("Proveedores", [str(date.today()), sede_act, cp, mp, str(vp), "Pendiente"])
            st.rerun()
    
    df_p = leer("Proveedores")
    if not df_p.empty:
        pend = df_p[(df_p['Sede'] == sede_act) & (df_p['Estado'] == 'Pendiente')]
        st.markdown(f"<div class='resaltado-suma'>Total por Pagar: $ {pend['Monto'].sum() if not pend.empty else 0}</div>", unsafe_allow_html=True)
        st.dataframe(pend, use_container_width=True)
