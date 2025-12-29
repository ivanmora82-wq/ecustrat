import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# 1. CONFIGURACIÓN DE CONEXIÓN (Lee de los Secrets que ya guardaste)
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds_dict = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"],
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{st.secrets['client_email'].replace('@', '%40')}"
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("EMI_DATA_PRO")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def guardar(hoja_nombre, fila):
    doc = conectar()
    if doc:
        try:
            hoja = doc.worksheet(hoja_nombre)
            hoja.append_row(fila)
            st.success(f"✅ Guardado en {hoja_nombre}")
        except:
            st.error(f"⚠️ La pestaña '{hoja_nombre}' no existe en tu Excel.")

def leer(hoja_nombre):
    doc = conectar()
    if doc:
        try:
            return pd.DataFrame(doc.worksheet(hoja_nombre).get_all_records())
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# 2. INTERFAZ Y ESTILO
st.set_page_config(page_title="EMI MASTER CLOUD", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1 style='color: #d4af37;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])

tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS"])

# --- TAB VENTAS ---
with tabs[0]:
    with st.form("fv", clear_on_submit=True):
        mv = st.number_input("Monto de Venta", min_value=0.0)
        if st.form_submit_button("Registrar Venta"):
            guardar("Ventas", [str(date.today()), sede_act, "Venta", mv, "Ingreso"])
            st.rerun()
    
    st.write("### Historial en la Nube")
    df = leer("Ventas")
    if not df.empty:
        st.dataframe(df[df['Sede'] == sede_act], use_container_width=True)
    else:
        st.info("No hay datos en la pestaña 'Ventas'.")

# (Nota: Puedes repetir la lógica de 'Ventas' para las otras pestañas)
