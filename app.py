import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Configuración de página
st.set_page_config(page_title="EMI MASTER", layout="wide")

# Estilos para recuperar tu diseño original
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; color: white; }
    .balance-box {
        background-color: #d4af37; 
        padding: 20px; 
        border-radius: 10px; 
        color: #1a2a44;
        font-weight: bold;
    }
    .stButton>button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Cargamos los secretos
        creds_info = st.secrets["gcp_service_account"]
        
        # Limpieza de seguridad para la clave privada
        if isinstance(creds_info, st.runtime.secrets.AttrDict):
            creds_dict = dict(creds_info)
        else:
            creds_dict = creds_info

        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# --- SIDEBAR ---
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

col1, col2 = st.columns([1, 1])
with col1:
    fecha = st.date_input("Fecha Venta", datetime.date.today())
    monto = st.number_input("Valor $", min_value=0.0, value=600.0)
    
    if st.button("GUARDAR VENTA"):
        client = conectar()
        if client:
            try:
                # Cambia "NOMBRE_DE_TU_EXCEL" por el nombre real de tu archivo
                sheet = client.open("Ventas EMI Master").worksheet("Ventas")
                fila = [str(fecha), sede, "Venta Diaria", monto, "PAGADO"]
                sheet.append_row(fila)
                st.success("✅ ¡Venta guardada!")
            except Exception as e:
                st.error(f"Error al escribir: {e}")
