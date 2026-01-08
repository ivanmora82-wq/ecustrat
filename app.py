import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")

# --- ESTILOS VISUALES CORPORATIVOS ---
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
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds).open("EMI_DATA_PRO")
    except Exception as e:
        st.error(f"⚠️ Error de Conexión: {e}")
        return None

# --- ENCABEZADO ---
st.markdown(f"""
    <div class="main-header">
        <h1 style="color: #D4AF37; margin: 0;">EMI MASTER PRO</h1>
        <p style="color: #888;">Gestión con Auto-Aprendizaje de Proveedores</p>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONTROL DE TIEMPO Y SALDOS ---
with st.sidebar:
    st.header("⚙️ Configuración")
    nombre_local = st.text_input("Local:", "EMI Master")
    tipo_local = st.selectbox("Tipo:", ["Matriz", "Sucursal 1", "Sucursal 2"])
    fecha_trabajo = st.date_input("📅 Fecha de Consulta", datetime.date.today())
    
    st.write("---")
    st.header("💰 Estado de Caja")
    caja_chica = st.number_input("Caja Chica ($)", value=0.0)
    saldo_banco = st.number_input("Saldo Banco ($)", value=0.0)

# --- CUERPO PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["💰 VENTAS", "💸 GASTOS Y PAGOS", "📊 REPORTES"])

db = conectar_db()

# --- MODULO DE VENTAS ---
with tab1:
    st.subheader(f"Registro de Ventas - {fecha_trabajo}")
    with st.form("form_ventas"):
        c1, c2, c3 = st.columns([2, 2, 1])
        monto_v = c1.number_input("Monto Cobrado ($)", min_value=0.0, key="v_monto")
        destino = c2.selectbox("Destino", ["Caja (Efectivo)", "Banco (Transferencia)"])
        nota = c3.text_input("Nota/Cliente")
        if st.form_submit_button("REGISTRAR VENTA"):
            if db:
                fila = [str(fecha_trabajo), "INGRESO", nombre_local, tipo_local, monto_v, nota, destino]
                db.worksheet("Movimientos").append_row(fila)
                st.success("Venta guardada.")

# --- MODULO DE GASTOS CON AUTO-APRENDIZAJE ---
with tab2:
    st.subheader("📉 Registro de Gastos (Hormiga y Fijos)")
    
    # 1. Lógica de Memoria: Extraer nombres de proveedores previos
    proveedores_conocidos = ["Nuevo Proveedor..."]
    if db:
        try:
            data_gastos = db.worksheet("Movimientos").get_all_records()
            df_g = pd.DataFrame(data_gastos)
            if not df_g.empty:
                # Extraemos nombres únicos de la columna 'Detalle' donde el Tipo sea 'EGRESO'
                nombres = df_g[df_g['Tipo'] == 'EGRESO']['Detalle'].unique().tolist()
                proveedores_conocidos.extend(nombres)
        except: pass

    with st.form("form_gastos"):
        col_g1, col_g2 = st.columns(2)
        
        # El sistema sugiere nombres ya usados
        seleccion = col_g1.selectbox("Seleccionar Proveedor Registrado:", proveedores_conocidos)
        
        # Si no está en la lista, permite escribir uno nuevo
        nombre_final = ""
        if seleccion == "Nuevo Proveedor...":
            nombre_final = col_g1.text_input("Nombre del nuevo proveedor/gasto:")
        else:
            nombre_final = seleccion

        monto_g = col_g2.number_input("Valor del Gasto ($)", min_value=0.0)
        tipo_g = st.radio("Tipo de Gasto:", ["Hormiga (Diario)", "Fijo (Mensual)"], horizontal=True)
        
        c_p1, c_p2 = st.columns(2)
        pagado = c_p1.checkbox("¿Pagado ahora? (Se debita de Bancos)")
        fecha_pago_sug = c_p2.date_input("Fecha programada de pago", fecha_trabajo)

        if st.form_submit_button("REGISTRAR GASTO"):
            if db and nombre_final:
                metodo_g = "Banco" if pagado else "Pendiente"
                fila_g = [str(fecha_trabajo), "EGRESO", nombre_local, tipo_local, monto_g, nombre_final, metodo_g, tipo_g]
                db.worksheet("Movimientos").append_row(fila_g)
                st.warning(f"Gasto de {nombre_final} registrado.")
                if pagado: st.info("Monto debitado virtualmente del Saldo en Bancos.")

# --- MODULO DE REPORTES (Vista Previa) ---
with tab3:
    st.subheader("📊 Análisis y Comparativa")
    if db:
        data = db.worksheet("Movimientos").get_all_records()
        df = pd.DataFrame(data)
        if not df.empty:
            df_hoy = df[df['Fecha'] == str(fecha_trabajo)]
            st.write(f"Resumen del día {fecha_trabajo}:")
            st.dataframe(df_hoy)
            
            # Cálculo de Totales
            ingresos = pd.to_numeric(df_hoy[df_hoy['Tipo'] == 'INGRESO']['Monto']).sum()
            egresos = pd.to_numeric(df_hoy[df_hoy['Tipo'] == 'EGRESO']['Monto']).sum()
            st.metric("Balance Neto del Día", f"$ {ingresos - egresos}", delta=f"{ingresos} Ingresos")
