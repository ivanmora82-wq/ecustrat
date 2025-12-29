import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# 1. CONEXIÓN BLINDADA
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Limpieza de saltos de línea para evitar error base64
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
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{st.secrets['client_email'].replace('@', '%40')}"
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds).open("EMI_DATA_PRO")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def guardar(hoja, fila):
    doc = conectar()
    if doc: doc.worksheet(hoja).append_row(fila)

def leer(hoja):
    doc = conectar()
    if doc:
        data = doc.worksheet(hoja).get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame()

# 2. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="EMI MASTER CLOUD", layout="wide")
st.markdown("<style>[data-testid='stSidebar'] { background-color: #1c2e4a !important; } [data-testid='stMetricValue'] { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 10px; border-radius: 10px; }</style>", unsafe_allow_html=True)

# 3. LÓGICA DE BALANCE AUTOMÁTICO
def calcular_balance_nube():
    total = 0.0
    # Sumar Ventas
    df_v = leer("Ventas")
    if not df_v.empty: total += df_v['Monto'].sum()
    # Restar Fijos pagados
    df_f = leer("Fijos")
    if not df_f.empty: total -= df_f[df_f['Estado'] == 'Pagado']['Monto'].sum()
    # Restar Hormiga
    df_h = leer("Hormiga")
    if not df_h.empty: total -= df_h['Monto'].sum()
    # Restar Prov pagados
    df_p = leer("Proveedores")
    if not df_p.empty: total -= df_p[df_p['Estado'] == 'Pagado']['Monto'].sum()
    # Sumar Cobros recibidos
    df_c = leer("Cobros")
    if not df_c.empty: total += df_c[df_c['Estado'] == 'Cobrado']['Monto'].sum()
    return total

# 4. INTERFAZ
with st.sidebar:
    st.markdown("<h1 style='color: #d4af37;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    banco_base = st.number_input("🏦 SALDO INICIAL BANCO", value=0.0)
    caja_base = st.number_input("💵 SALDO INICIAL CAJA", value=0.0)
    
    balance_nube = calcular_balance_nube()
    st.metric("BALANCE GENERAL REAL", f"$ {round(banco_base + caja_base + balance_nube, 2)}")

tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS"])

with tabs[0]: # VENTAS
    with st.form("fv", clear_on_submit=True):
        mv = st.number_input("Monto de Venta", min_value=0.0)
        if st.form_submit_button("Registrar Venta"):
            guardar("Ventas", [str(date.today()), sede_act, "Venta", mv, "Ingreso"])
            st.rerun()
    st.dataframe(leer("Ventas"))

with tabs[3]: # PROVEEDORES
    with st.form("fp", clear_on_submit=True):
        cp = st.text_input("Proveedor")
        mp = st.number_input("Monto")
        if st.form_submit_button("Guardar Deuda"):
            guardar("Proveedores", [str(date.today()), sede_act, cp, mp, str(date.today()), "Pendiente"])
            st.rerun()
    
    df_p = leer("Proveedores")
    if not df_p.empty:
        for i, row in df_p.iterrows():
            if row['Estado'] == 'Pendiente':
                col1, col2 = st.columns([4,1])
                col1.write(f"🚛 {row['Concepto']} - ${row['Monto']}")
                if col2.button("Pagar", key=f"btn_p_{i}"):
                    # Aquí añadiríamos lógica para actualizar fila en Sheets
                    st.info("Función de actualizar fila en desarrollo")
