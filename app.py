import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Configuración visual para mantener tu diseño
st.set_page_config(page_title="EMI MASTER", layout="wide")

def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        # Extraer secretos
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # --- LIMPIEZA TOTAL DE LLAVE ---
        p_key = creds_dict["private_key"]
        # Eliminamos comillas accidentales, espacios y aseguramos saltos de línea reales
        p_key = p_key.strip().replace('"', '').replace("\\n", "\n")
        
        # Si por alguna razón la llave no termina en salto de línea, lo agregamos
        if not p_key.endswith("\n"):
            p_key += "\n"
            
        creds_dict["private_key"] = p_key
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Asegúrate de que el nombre del documento sea el correcto
        return client.open("Ventas EMI Master").worksheet("Ventas")
    except Exception as e:
        # Esto nos dirá exactamente qué campo falla si persiste el error
        st.error(f"Error de autenticación detallado: {e}")
        return None

# --- DISEÑO DE INTERFAZ (Recuperando tus campos) ---
# Sidebar azul oscuro como en tu primera versión
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a2a44; color: white; }
    .stMetric { background-color: #d4af37; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='color: #FFD700;'>🛡️ EMI MASTER</h2>", unsafe_allow_html=True)
    
    st.write("📍 **PUNTO DE VENTA**")
    sede_act = st.selectbox("Sede", ["Matriz", "Sucursal 1"], label_visibility="collapsed")
    
    st.write("🏦 **BANCO**")
    b_v = st.number_input("Banco", value=1000.0, step=10.0, label_visibility="collapsed")
    
    st.write("💵 **CAJA**")
    c_v = st.number_input("Caja", value=30.0, step=5.0, label_visibility="collapsed")
    
    balance = b_v + c_v
    st.markdown(f"<div class='stMetric'><h4 style='margin:0;'>BALANCE NETO TOTAL</h4><h2 style='margin:0;'>$ {balance}</h2></div>", unsafe_allow_html=True)

# Cuerpo Principal
st.markdown("<h4 style='background-color: #1a2a44; color: white; text-align: center; padding: 5px;'>TOTAL VENTAS MES: $ 0</h4>", unsafe_allow_html=True)

with st.container():
    st.write("Fecha Venta")
    f_v = st.date_input("Fecha", datetime.date.today(), label_visibility="collapsed")
    
    st.write("Valor $")
    m_v = st.number_input("Monto", min_value=0.0, format="%.2f", label_visibility="collapsed")

    if st.button("GUARDAR VENTA", type="secondary"):
        with st.spinner("Procesando..."):
            sheet = conectar()
            if sheet:
                try:
                    nueva_fila = [str(f_v), sede_act, "Venta Diaria", m_v, "PAGADO"]
                    sheet.append_row(nueva_fila)
                    st.success("✅ Venta guardada con éxito")
                except Exception as e:
                    st.error(f"Error al guardar en la hoja: {e}")
