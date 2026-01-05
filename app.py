import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pandas as pd
import altair as alt
import base64
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="EMI MASTER - PRO", layout="wide")

# Estilos visuales solicitados
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; color: white; }
    .balance-box { background-color: #d4af37; padding: 20px; border-radius: 10px; color: #1a2a44; font-weight: bold; text-align: center; font-size: 24px; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

def conectar_db():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Recuperar la cadena Base64 de los secretos
        encoded_creds = st.secrets["gcp_service_account"]["encoded_creds"]
        # Decodificar
        decoded_creds = base64.b64decode(encoded_creds).decode("utf-8")
        creds_dict = json.loads(decoded_creds)
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # Nombre exacto de tu archivo detectado
        return client.open("EMI_DATA_PRO")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #FFD700;'>🛡️ EMI MASTER</h2>", unsafe_allow_html=True)
    st.write("📍 **PUNTO DE VENTA**")
    sede_act = st.selectbox("Seleccionar Sede", ["Matriz", "Sucursal 1"], label_visibility="collapsed")
    
    st.write("🏦 **BANCO**")
    banco = st.number_input("Banco", value=1000.0, step=10.0, label_visibility="collapsed")
    
    st.write("💵 **CAJA**")
    caja = st.number_input("Caja", value=30.0, step=5.0, label_visibility="collapsed")
    
    st.write("BALANCE NETO TOTAL")
    st.markdown(f"<div class='balance-box'>$ {banco + caja}</div>", unsafe_allow_html=True)

# --- CUERPO PRINCIPAL ---
st.title("Sistema de Gestión EMI_DATA_PRO")

tab1, tab2, tab3 = st.tabs(["📝 REGISTRO", "📊 REPORTES", "📈 GRÁFICOS"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📈 Ingresos")
        with st.form("form_ingresos"):
            f_i = st.date_input("Fecha", datetime.date.today())
            m_i = st.number_input("Monto $", min_value=0.0, step=1.0)
            det_i = st.selectbox("Método", ["Efectivo", "Transferencia", "Tarjeta"])
            if st.form_submit_button("Guardar Ingreso"):
                db = conectar_db()
                if db:
                    db.worksheet("Movimientos").append_row([str(f_i), "INGRESO", "Venta", m_i, sede_act, det_i])
                    st.success("Ingreso guardado")

    with col_b:
        st.subheader("📉 Egresos")
        with st.form("form_egresos"):
            f_e = st.date_input("Fecha Gasto", datetime.date.today())
            m_e = st.number_input("Monto Gasto $", min_value=0.0, step=1.0)
            cat_e = st.selectbox("Categoría", ["Proveedores", "Servicios", "Sueldos", "Otros"])
            det_e = st.text_input("Detalle")
            if st.form_submit_button("Guardar Egreso"):
                db = conectar_db()
                if db:
                    db.worksheet("Movimientos").append_row([str(f_e), "EGRESO", cat_e, m_e, sede_act, det_e])
                    st.warning("Egreso guardado")

with tab2:
    if st.button("Actualizar Historial"):
        db = conectar_db()
        if db:
            data = db.worksheet("Movimientos").get_all_records()
            df = pd.DataFrame(data)
            if not df.empty:
                st.dataframe(df.sort_index(ascending=False), use_container_width=True)

with tab3:
    if st.button("Generar Gráfico de Flujo"):
        db = conectar_db()
        if db:
            data = db.worksheet("Movimientos").get_all_records()
            df = pd.DataFrame(data)
            if not df.empty:
                df['Monto'] = pd.to_numeric(df['Monto'])
                df_grafico = df.groupby(['Fecha', 'Tipo'])['Monto'].sum().reset_index()
                
                chart = alt.Chart(df_grafico).mark_bar().encode(
                    x='Fecha:T',
                    y='Monto:Q',
                    color=alt.Color('Tipo:N', scale=alt.Scale(domain=['INGRESO', 'EGRESO'], range=['#2ecc71', '#e74c3c'])),
                    tooltip=['Fecha', 'Tipo', 'Monto']
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
