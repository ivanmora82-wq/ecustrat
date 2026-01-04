import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import base64

# Configuración de página y diseño original
st.set_page_config(page_title="EMI MASTER", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; color: white; }
    .balance-box { background-color: #d4af37; padding: 20px; border-radius: 10px; color: #1a2a44; font-weight: bold; text-align: center; }
    .stButton>button { width: 100%; background-color: #ffffff; color: black; border: 1px solid #ccc; }
    </style>
    """, unsafe_allow_html=True)

def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # 1. Obtener los secretos
        creds_info = dict(st.secrets["gcp_service_account"])
        
        # 2. LIMPIEZA EXTREMA DE LA LLAVE (Para eliminar el "Incorrect padding")
        p_key = creds_info["private_key"]
        
        # Quitar comillas si se pegaron por error
        p_key = p_key.strip().replace('"', '').replace("'", "")
        
        # Corregir saltos de línea literales
        p_key = p_key.replace("\\n", "\n")
        
        # Asegurar que la llave tenga el encabezado y pie correctos
        if "-----BEGIN PRIVATE KEY-----" not in p_key:
            p_key = "-----BEGIN PRIVATE KEY-----\n" + p_key
        if "-----END PRIVATE KEY-----" not in p_key:
            p_key = p_key + "\n-----END PRIVATE KEY-----\n"
            
        creds_info["private_key"] = p_key
        
        # Autenticación
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Error de conexión crítico: {e}")
        return None

# --- SIDEBAR (Tu diseño original) ---
with st.sidebar:
    st.markdown("<h2 style='color: #FFD700;'>🛡️ EMI MASTER</h2>", unsafe_allow_html=True)
    st.write("📍 **PUNTO DE VENTA**")
    sede = st.selectbox("", ["Matriz", "Sucursal 1"], label_visibility="collapsed")
    st.write("🏦 **BANCO**")
    banco = st.number_input("Banco", value=1000.0, step=1.0, label_visibility="collapsed")
    st.write("💵 **CAJA**")
    caja = st.number_input("Caja", value=30.0, step=1.0, label_visibility="collapsed")
    st.write("BALANCE NETO TOTAL")
    st.markdown(f"<div class='balance-box'>$ {banco + caja}</div>", unsafe_allow_html=True)

# --- CUERPO PRINCIPAL ---
st.markdown("<h4 style='background-color: #1a2a44; color: white; text-align: center; padding: 10px;'>TOTAL VENTAS MES: $ 0</h4>", unsafe_allow_html=True)

with st.container():
    st.write("Fecha Venta")
    fecha = st.date_input("Fecha", datetime.date.today(), label_visibility="collapsed")
    st.write("Valor $")
    monto = st.number_input("Monto", min_value=0.0, value=600.0, label_visibility="collapsed")
    
    if st.button("GUARDAR VENTA"):
        client = conectar()
        if client:
            try:
                # IMPORTANTE: Verifica que el nombre de tu archivo sea exacto
                sheet = client.open("Ventas EMI Master").worksheet("Ventas")
                fila = [str(fecha), sede, "Venta Diaria", monto, "PAGADO"]
                sheet.append_row(fila)
                st.success("✅ Venta guardada correctamente.")
            except Exception as e:
                st.error(f"La conexión funcionó, pero no se pudo escribir: {e}")
