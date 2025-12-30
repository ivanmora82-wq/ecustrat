import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- CONFIGURACIÓN DE CONEXIÓN ---
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
        st.success(f"✅ Registrado con éxito")
    except: st.error("❌ Error al conectar con la nube")

# --- DISEÑO Y COLORES (CORRECCIÓN DE VISIBILIDAD) ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")

st.markdown("""
    <style>
    /* Fondo de la barra lateral */
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    /* Color de letras en la barra azul (Dorado legible) */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { 
        color: #d4af37 !important; 
        font-weight: bold; 
        font-size: 1.1rem;
    }
    /* Estilo del Balance General */
    .stMetric { 
        background-color: #d4af37 !important; 
        color: #1c2e4a !important; 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    /* Arreglo para que los inputs se vean bien */
    input { color: #1c2e4a !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SELECCIONAR SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO INICIAL", value=0.0)
    c_ini = st.number_input("💵 CAJA INICIAL", value=0.0)
    
    # Cálculo de Balance en Tiempo Real
    df_v = leer("Ventas")
    total_v = pd.to_numeric(df_v['Monto'], errors='coerce').sum() if not df_v.empty else 0.0
    
    st.metric("BALANCE GENERAL REAL", f"$ {round(b_ini + c_ini + total_v, 2)}")

# --- PESTAÑAS (TODOS LOS CAMPOS RECUPERADOS) ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS"])

with tabs[0]: # VENTAS
    with st.form("f_v", clear_on_submit=True):
        m = st.number_input("Monto de Venta", min_value=0.0)
        if st.form_submit_button("REGISTRAR VENTA"):
            guardar("Ventas", [str(date.today()), sede_act, "Venta", m, "Ingreso"])
            st.rerun()
    st.dataframe(leer("Ventas"), use_container_width=True)

with tabs[1]: # FIJOS
    with st.form("f_f", clear_on_submit=True):
        conc = st.text_input("Concepto (Arriendo, Luz, etc)")
        m = st.number_input("Monto Fijo", min_value=0.0)
        if st.form_submit_button("REGISTRAR GASTO FIJO"):
            guardar("Fijos", [str(date.today()), sede_act, conc, m, "Pagado"])
            st.rerun()
    st.dataframe(leer("Fijos"), use_container_width=True)

with tabs[2]: # HORMIGA
    with st.form("f_h", clear_on_submit=True):
        conc = st.text_input("Gasto Hormiga")
        m = st.number_input("Monto Hormiga", min_value=0.0)
        if st.form_submit_button("REGISTRAR HORMIGA"):
            guardar("Hormiga", [str(date.today()), sede_act, conc, m, "Gasto"])
            st.rerun()
    st.dataframe(leer("Hormiga"), use_container_width=True)

with tabs[3]: # PROVEEDORES
    with st.form("f_p", clear_on_submit=True):
        prov = st.text_input("Nombre del Proveedor")
        m = st.number_input("Monto Factura", min_value=0.0)
        if st.form_submit_button("REGISTRAR DEUDA"):
            guardar("Proveedores", [str(date.today()), sede_act, prov, m, "Pendiente"])
            st.rerun()
    st.dataframe(leer("Proveedores"), use_container_width=True)

with tabs[4]: # COBROS
    with st.form("f_c", clear_on_submit=True):
        cli = st.text_input("Nombre del Cliente")
        m = st.number_input("Monto por Cobrar", min_value=0.0)
        if st.form_submit_button("REGISTRAR COBRO"):
            guardar("Cobros", [str(date.today()), sede_act, cli, m, "Pendiente"])
            st.rerun()
    st.dataframe(leer("Cobros"), use_container_width=True)
