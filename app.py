import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")

# --- ESTILOS UX/UI (Dorado y Negro) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .main-header { text-align: center; padding: 20px; background: #1A1A1A; border-bottom: 3px solid #D4AF37; border-radius: 15px; }
    .stButton>button { width: 100%; height: 50px; border-radius: 10px; background: #D4AF37; color: black; font-weight: bold; }
    .card { background: #1E1E1E; padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN DIRECTA (Sin Base64 para evitar errores ASCII) ---
def conectar_db():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("EMI_DATA_PRO")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# --- INICIO DE APLICACIÓN ---
URL_LOGO = "https://raw.githubusercontent.com/ivanmora82-wq/ecustrat/main/logo.png"

st.markdown(f"""
    <div class="main-header">
        <img src="{URL_LOGO}" width="80">
        <h1 style="color: #D4AF37; margin: 0;">EMI MASTER PRO</h1>
        <p style="color: #888;">Sistema de Gestión de Alta Precisión</p>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONTROL DE TIEMPO Y LOCAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    local_nombre = st.text_input("Nombre del Local", value="EMI Master")
    tipo_local = st.selectbox("Tipo", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.write("---")
    fecha_trabajo = st.date_input("📅 Fecha de Consulta", datetime.date.today())
    
    st.write("---")
    st.header("💰 Saldos Iniciales")
    caja_chica = st.number_input("Caja Chica ($)", value=0.0, format="%.2f")
    bancos = st.number_input("Saldo en Bancos ($)", value=0.0, format="%.2f")

# --- CUERPO PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["💰 VENTAS DEL DÍA", "📉 GASTOS Y PAGOS", "📊 REPORTES"])

with tab1:
    st.subheader(f"Registro de Ventas - {fecha_trabajo}")
    
    # KPIs Rápidos
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        st.markdown(f'<div class="card">💵 Total en Caja<br><h2>$ {caja_chica}</h2></div>', unsafe_allow_html=True)
    with col_k2:
        st.markdown(f'<div class="card">🏦 Total en Bancos<br><h2>$ {bancos}</h2></div>', unsafe_allow_html=True)

    # Formulario de Ventas
    with st.form("form_ventas"):
        col1, col2, col3 = st.columns([2,2,1])
        monto_v = col1.number_input("Monto de Venta ($)", min_value=0.0, format="%.2f")
        metodo_v = col2.selectbox("Destino", ["Efectivo (Caja)", "Banco (Transferencia/Tarjeta)"])
        detalle_v = col3.text_input("Nota")
        
        btn_v = st.form_submit_button("REGISTRAR VENTA")
        
        if btn_v:
            db = conectar_db()
            if db:
                try:
                    sheet = db.worksheet("Movimientos")
                    # Columnas: Fecha, Tipo, Local, Categoria, Monto, Detalle, Metodo
                    fila = [str(fecha_trabajo), "INGRESO", local_nombre, tipo_local, monto_v, detalle_v, metodo_v]
                    sheet.append_row(fila)
                    st.success(f"Venta de ${monto_v} guardada correctamente.")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    # Tabla de Historial del día con opción de búsqueda
    st.write("---")
    st.subheader("🔍 Historial de la Fecha")
    db = conectar_db()
    if db:
        data = db.worksheet("Movimientos").get_all_records()
        df = pd.DataFrame(data)
        if not df.empty:
            # Filtrar por fecha seleccionada
            df_fecha = df[df['Fecha'] == str(fecha_trabajo)]
            st.dataframe(df_fecha, use_container_width=True)
            
            # Botones de Edición (Simulados por ahora)
            st.info("💡 Para editar o eliminar, selecciona la fila en tu Google Sheets 'EMI_DATA_PRO'. Pronto integraremos edición directa aquí.")

# --- PRÓXIMAS FASES ---
with tab2:
    st.info("Módulo de Gastos Hormiga y Fijos: En desarrollo según tu diseño de 'Memoria de Escritura'.")

with tab3:
    st.info("Módulo de Reportes Comparativos: En desarrollo.")
