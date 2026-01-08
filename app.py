import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")

# --- ESTILOS VISUALES (Negro, Dorado y Blanco) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .main-header { text-align: center; padding: 20px; background: #1A1A1A; border-bottom: 3px solid #D4AF37; border-radius: 15px; }
    .card { background: #1E1E1E; padding: 20px; border-radius: 12px; border: 1px solid #333; text-align: center; }
    .stButton>button { width: 100%; height: 50px; border-radius: 10px; background: #D4AF37; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN BLINDADA ---
def conectar_db():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Cargamos el diccionario directamente de los secretos
        creds_dict = dict(st.secrets["gcp_service_account"])
        # Limpieza IA de saltos de línea
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds).open("EMI_DATA_PRO")
    except Exception as e:
        st.error(f"⚠️ Error de Conexión: {e}")
        return None

# --- ENCABEZADO CON IDENTIDAD ---
st.markdown(f"""
    <div class="main-header">
        <h1 style="color: #D4AF37; margin: 0;">EMI MASTER PRO</h1>
        <p style="color: #888;">Gestión Inteligente de Negocios</p>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONTROL DE TIEMPO Y SALDOS ---
with st.sidebar:
    st.header("⚙️ Configuración")
    nombre_local = st.text_input("Local:", "EMI Master")
    tipo_local = st.selectbox("Tipo:", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.write("---")
    fecha_trabajo = st.date_input("📅 Fecha de Consulta", datetime.date.today())
    
    st.write("---")
    st.header("💰 Saldos Iniciales")
    caja_chica = st.number_input("Caja Chica ($)", value=0.0)
    saldo_banco = st.number_input("Saldo Banco ($)", value=0.0)

# --- CUERPO PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["💰 VENTAS DEL DÍA", "📉 GASTOS (Fases sig.)", "📊 REPORTES"])

with tab1:
    st.subheader(f"Registro de Ventas para el {fecha_trabajo}")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f'<div class="card">💵 Caja Actual<br><h2>$ {caja_chica:,.2f}</h2></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div class="card">🏦 Banco Actual<br><h2>$ {saldo_banco:,.2f}</h2></div>', unsafe_allow_html=True)

    with st.form("form_ventas"):
        c1, c2, c3 = st.columns([2, 2, 1])
        monto_v = c1.number_input("Monto Cobrado ($)", min_value=0.0)
        destino = c2.selectbox("Destino del Dinero", ["Caja (Efectivo)", "Banco (Transferencia/Tarjeta)"])
        nota = c3.text_input("Detalle")
        
        if st.form_submit_button("REGISTRAR VENTA"):
            db = conectar_db()
            if db:
                try:
                    sheet = db.worksheet("Movimientos")
                    # Guardamos: Fecha, Tipo, Local, Sede, Monto, Detalle, Método
                    fila = [str(fecha_trabajo), "INGRESO", nombre_local, tipo_local, monto_v, nota, destino]
                    sheet.append_row(fila)
                    st.success("✅ Venta registrada correctamente")
                except Exception as e:
                    st.error(f"Error al guardar en la nube: {e}")

    # --- HISTORIAL Y EDICIÓN ---
    st.write("---")
    st.subheader("🔍 Historial de la Fecha")
    db = conectar_db()
    if db:
        try:
            data = db.worksheet("Movimientos").get_all_records()
            df = pd.DataFrame(data)
            if not df.empty:
                # El sistema filtra automáticamente por la fecha elegida en el sidebar
                df_filtrado = df[df['Fecha'] == str(fecha_trabajo)]
                st.dataframe(df_filtrado, use_container_width=True)
            else:
                st.info("No hay datos en la nube aún.")
        except:
            st.warning("Pestaña 'Movimientos' no encontrada en tu Google Sheet.")
