import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# CONFIGURACIÓN DE CONEXIÓN
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
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
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{st.secrets['client_email']}"
    }
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("EMI_DATA_PRO")

def guardar(hoja, fila):
    try: conectar().worksheet(hoja).append_row(fila)
    except Exception as e: st.error(f"Error al guardar: {e}")

def leer(hoja):
    try: return pd.DataFrame(conectar().worksheet(hoja).get_all_records())
    except: return pd.DataFrame()

# INTERFAZ
st.set_page_config(page_title="EMI MASTER CLOUD", layout="wide")

with st.sidebar:
    st.markdown("<h1 style='color: #d4af37;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])

tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS"])

# Ejemplo para Ventas (repite para el resto)
with tabs[0]:
    with st.form("fv", clear_on_submit=True):
        mv = st.number_input("Monto de Venta", min_value=0.0)
        if st.form_submit_button("Registrar en Nube"):
            guardar("Ventas", [str(date.today()), sede_act, "Venta", mv, "Ingreso"])
            st.rerun()
    df = leer("Ventas")
    if not df.empty:
        st.dataframe(df[df['Sede'] == sede_act], use_container_width=True)
