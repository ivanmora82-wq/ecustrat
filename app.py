import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN A LA NUBE ---
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
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
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds).open("EMI_DATA_PRO")
    except: return None

def leer(hoja):
    try:
        doc = conectar()
        return pd.DataFrame(doc.worksheet(hoja).get_all_records())
    except: return pd.DataFrame()

def guardar(hoja, fila):
    try:
        doc = conectar()
        doc.worksheet(hoja).append_row(fila)
        st.success(f"✅ Registrado en {hoja}")
    except: st.error("❌ Error de red")

# --- 2. DISEÑO Y COLORES (VISIBILIDAD MEJORADA) ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")

st.markdown("""
    <style>
    /* Barra lateral azul oscuro */
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    /* Letras Doradas Fuertes para que se vean bien */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { 
        color: #FFD700 !important; 
        font-weight: 800 !important;
        font-size: 1.2rem !important;
    }
    /* Estilo del cuadro de Balance */
    .stMetric { 
        background-color: #d4af37 !important; 
        color: #1c2e4a !important; 
        padding: 15px; 
        border-radius: 12px;
        border: 2px solid #FFD700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE BALANCE ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO INICIAL", value=0.0)
    c_ini = st.number_input("💵 CAJA INICIAL", value=0.0)
    
    # Cálculo automático
    df_v = leer("Ventas")
    total_v = pd.to_numeric(df_v['Monto'], errors='coerce').sum() if not df_v.empty else 0.0
    df_h = leer("Hormiga")
    total_h = pd.to_numeric(df_h['Monto'], errors='coerce').sum() if not df_h.empty else 0.0
    
    st.metric("BALANCE REAL", f"$ {round(b_ini + c_ini + total_v - total_h, 2)}")

# --- 4. PESTAÑAS (REPORTES RECUPERADO) ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

with tabs[0]: # VENTAS
    with st.form("f_v", clear_on_submit=True):
        m = st.number_input("Monto de Venta", min_value=0.0)
        if st.form_submit_button("REGISTRAR VENTA"):
            guardar("Ventas", [str(date.today()), sede_act, "Venta", m, "Ingreso"])
            st.rerun()
    st.dataframe(leer("Ventas"), use_container_width=True)

with tabs[2]: # HORMIGA
    with st.form("f_h", clear_on_submit=True):
        conc = st.text_input("Gasto Hormiga")
        m = st.number_input("Monto Gasto", min_value=0.0)
        if st.form_submit_button("REGISTRAR GASTO"):
            guardar("Hormiga", [str(date.today()), sede_act, conc, m, "Egreso"])
            st.rerun()
    st.dataframe(leer("Hormiga"), use_container_width=True)

with tabs[5]: # --- REPORTE (AQUÍ ESTÁ DE VUELTA) ---
    st.subheader("📊 Análisis de Negocio Cloud")
    df_rep = leer("Ventas")
    if not df_rep.empty:
        # Gráfica de Ventas por Sede
        fig = px.pie(df_rep, values='Monto', names='Sede', title="Distribución de Ventas por Sede", hole=.3)
        st.plotly_chart(fig, use_container_width=True)
        
        # Resumen diario
        df_rep['Fecha'] = pd.to_datetime(df_rep['Fecha'])
        ventas_dia = df_rep.groupby('Fecha')['Monto'].sum().reset_index()
        fig2 = px.line(ventas_dia, x='Fecha', y='Monto', title="Evolución de Ventas Diarias")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Aún no hay datos suficientes para generar reportes.")

# (Aquí se incluyen Fijos, Proveedores y Cobros igual que antes)
