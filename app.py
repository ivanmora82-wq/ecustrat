import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# 1. CONEXIÓN SEGURA
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Limpiamos la llave de cualquier error de pegado
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
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{st.secrets['client_email'].replace('@', '%40')}"
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds).open("EMI_DATA_PRO")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# 2. FUNCIONES DE LECTURA Y ESCRITURA
def guardar(hoja, fila):
    doc = conectar()
    if doc:
        try:
            doc.worksheet(hoja).append_row(fila)
            st.success(f"✅ Guardado en {hoja}")
        except:
            st.error(f"⚠️ Crea la pestaña '{hoja}' en tu Excel primero.")

def leer(hoja):
    doc = conectar()
    if doc:
        try:
            return pd.DataFrame(doc.worksheet(hoja).get_all_records())
        except: return pd.DataFrame()
    return pd.DataFrame()

# 3. INTERFAZ PROFESIONAL
st.set_page_config(page_title="EMI MASTER CLOUD", layout="wide")

# Estilo para el Balance
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: white !important; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 15px; border-radius: 15px; border: 2px solid #ffffff; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1 style='color: #d4af37; text-align: center;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE ACTUAL", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    banco_ini = st.number_input("🏦 SALDO BANCO INICIAL", value=0.0)
    caja_ini = st.number_input
