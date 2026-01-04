import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def conectar_google_sheets():
    # Definir el alcance (scope)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Cargar los secretos desde Streamlit
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # --- PASO CRUCIAL PARA EVITAR EL BINASCII ERROR ---
        # Limpiamos la clave privada de posibles errores de escape
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        # Autenticación
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Abrir la hoja (asegúrate de que el nombre sea exacto)
        sheet = client.open("NOMBRE_DE_TU_EXCEL").sheet1
        return sheet
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# --- Interfaz de Usuario ---
st.title("EMI MASTER - Registro de Ventas")

# Sidebar con inputs
with st.sidebar:
    st.header("PUNTO DE VENTA")
    sede = st.selectbox("Sede", ["Matriz", "Sucursal 1"])
    banco = st.number_input("BANCO", value=1000.0)
    caja = st.number_input("CAJA", value=50.0)
    st.write(f"**BALANCE NETO TOTAL: $ {banco + caja}**")

# Formulario principal
with st.container():
    fecha_venta = st.date_input("Fecha Venta")
    valor_venta = st.number_input("Valor $", min_value=0.0, step=10.0)

    if st.button("GUARDAR VENTA"):
        sheet = conectar_google_sheets()
        if sheet:
            try:
                # Datos a enviar (ajusta el orden según tus columnas)
                fila = [str(fecha_venta), sede, "Venta Diaria", valor_venta, "PAGADO"]
                sheet.append_row(fila)
                st.success("¡Venta guardada exitosamente!")
            except Exception as e:
                st.error(f"Error al guardar: {e}")
