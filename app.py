import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN REFORZADA A LA NUBE ---
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Limpieza técnica de la llave para evitar errores de base64
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
        df = pd.DataFrame(doc.worksheet(hoja).get_all_records())
        if not df.empty:
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

def guardar(hoja, fila):
    try:
        doc = conectar()
        doc.worksheet(hoja).append_row(fila)
        st.success(f"✅ Registrado en {hoja}")
    except: st.error("❌ Error de red")

# --- 2. DISEÑO Y VISIBILIDAD (DORADO FUERTE SOBRE AZUL) ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")

st.markdown("""
    <style>
    /* Barra lateral azul oscuro */
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    /* Letras Doradas Brillantes para máxima visibilidad */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { 
        color: #FFD700 !important; 
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }
    /* Estilo del Balance General */
    .stMetric { 
        background-color: #d4af37 !important; 
        color: #1c2e4a !important; 
        padding: 15px; 
        border-radius: 12px;
        border: 2px solid #FFD700;
        font-weight: bold;
    }
    /* Estilo de las pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        color: #1c2e4a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL Y BALANCE GENERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SELECCIONAR SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 SALDO BANCO INICIAL", value=0.0)
    c_ini = st.number_input("💵 SALDO CAJA INICIAL", value=0.0)
    
    # Cálculo automático desde la nube
    df_v_bal = leer("Ventas")
    df_h_bal = leer("Hormiga")
    total_v = df_v_bal['Monto'].sum() if not df_v_bal.empty else 0.0
    total_h = df_h_bal['Monto'].sum() if not df_h_bal.empty else 0.0
    
    balance_neto = b_ini + c_ini + total_v - total_h
    st.metric("BALANCE GENERAL REAL", f"$ {round(balance_neto, 2)}")

# --- 4. TODAS LAS PESTAÑAS RECUPERADAS ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

with tabs[0]: # VENTAS
    with st.form("f_v", clear_on_submit=True):
        m = st.number_input("Monto de Venta", min_value=0.0)
        if st.form_submit_button("REGISTRAR VENTA"):
            guardar("Ventas", [str(date.today()), sede_act, "Venta", m, "Ingreso"])
            st.rerun()
    st.dataframe(leer("Ventas"), use_container_width=True)

with tabs[1]: # FIJOS
    with st.form("f_f", clear_on_submit=True):
        conc_f = st.text_input("Concepto (Arriendo, Luz, etc)")
        m_f = st.number_input("Monto Gasto Fijo", min_value=0.0)
        if st.form_submit_button("REGISTRAR GASTO FIJO"):
            guardar("Fijos", [str(date.today()), sede_act, conc_f, m_f, "Egreso"])
            st.rerun()
    st.dataframe(leer("Fijos"), use_container_width=True)

with tabs[2]: # HORMIGA
    with st.form("f_h", clear_on_submit=True):
        conc_h = st.text_input("Descripción Gasto Hormiga")
        m_h = st.number_input("Monto Gasto Hormiga", min_value=0.0)
        if st.form_submit_button("REGISTRAR GASTO HORMIGA"):
            guardar("Hormiga", [str(date.today()), sede_act, conc_h, m_h, "Egreso"])
            st.rerun()
    st.dataframe(leer("Hormiga"), use_container_width=True)

with tabs[3]: # PROVEEDORES
    with st.form("f_p", clear_on_submit=True):
        prov = st.text_input("Nombre del Proveedor")
        m_p = st.number_input("Monto de Factura", min_value=0.0)
        if st.form_submit_button("REGISTRAR DEUDA"):
            guardar("Proveedores", [str(date.today()), sede_act, prov, m_p, "Pendiente"])
            st.rerun()
    st.dataframe(leer("Proveedores"), use_container_width=True)

with tabs[4]: # COBROS
    with st.form("f_c", clear_on_submit=True):
        cli = st.text_input("Nombre del Cliente")
        m_c = st.number_input("Monto por Cobrar", min_value=0.0)
        if st.form_submit_button("REGISTRAR COBRO"):
            guardar("Cobros", [str(date.today()), sede_act, cli, m_c, "Pendiente"])
            st.rerun()
    st.dataframe(leer("Cobros"), use_container_width=True)

with tabs[5]: # REPORTES (COMPARATIVA Y GRÁFICAS)
    st.subheader("📊 Análisis de Flujos y Sedes")
    df_v = leer("Ventas")
    df_h = leer("Hormiga")
    
    col1, col2 = st.columns(2)
    with col1:
        if not df_v.empty and not df_h.empty:
            resumen = pd.DataFrame({
                'Categoría': ['Ingresos (Ventas)', 'Egresos (Gastos)'],
                'Total': [df_v['Monto'].sum(), df_h['Monto'].sum()]
            })
            fig_comp = px.bar(resumen, x='Categoría', y='Total', color='Categoría', 
                             color_discrete_map={'Ingresos (Ventas)': '#2ecc71', 'Egresos (Gastos)': '#e74c3c'},
                             title="Ventas vs Gastos (Hormiga)")
            st.plotly_chart(fig_comp, use_container_width=True)
    with col2:
        if not df_v.empty:
            fig_sede = px.pie(df_v, values='Monto', names='Sede', title="Ventas por Sede", hole=.3)
            st.plotly_chart(fig_sede, use_container_width=True)
