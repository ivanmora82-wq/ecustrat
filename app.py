import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="EMI MASTER", layout="wide")

def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        # Extraemos los secretos como un diccionario normal
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # LIMPIEZA PROFUNDA DE LA CLAVE (Esto evita el binascii.Error)
        if "private_key" in creds_dict:
            # Elimina comillas accidentales, espacios y arregla saltos de línea
            p_key = creds_dict["private_key"]
            p_key = p_key.replace("\\n", "\n").replace('"', '').strip()
            creds_dict["private_key"] = p_key
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Cambia "NOMBRE_DE_TU_HOJA" por el nombre real de tu archivo de Google Sheets
        return client.open("Ventas EMI Master").worksheet("Ventas")
    except Exception as e:
        st.error(f"Error de autenticación: {e}")
        return None

# --- INTERFAZ ---
st.title("📊 EMI MASTER - V1.9.0")

# Sidebar
with st.sidebar:
    st.header("📍 PUNTO DE VENTA")
    sede_act = st.selectbox("Sede", ["Matriz", "Sucursal 1"])
    
    st.header("🏦 BANCO")
    b_v = st.number_input("Monto Banco", value=1000.0, step=10.0)
    
    st.header("💵 CAJA")
    c_v = st.number_input("Monto Caja", value=30.0, step=5.0)
    
    balance = b_v + c_v
    st.metric("BALANCE NETO TOTAL", f"$ {balance}")

# Formulario Principal
col1, col2 = st.columns(2)
with col1:
    f_v = st.date_input("Fecha Venta", datetime.date.today())
    m_v = st.number_input("Valor de la Venta ($)", min_value=0.0, format="%.2f")

if st.button("GUARDAR VENTA", use_container_width=True):
    with st.spinner("Conectando con Google Sheets..."):
        sheet = conectar()
        if sheet:
            try:
                # Preparamos la fila
                nueva_fila = [str(f_v), sede_act, "Venta Diaria", m_v, "PAGADO"]
                sheet.append_row(nueva_fila)
                st.success("✅ Venta registrada correctamente en el Excel.")
            except Exception as e:
                st.error(f"Error al escribir datos: {e}")

# Mostrar totales (Opcional)
st.info("TOTAL VENTAS MES: $ 0") # Aquí puedes añadir lógica para sumar la columna
