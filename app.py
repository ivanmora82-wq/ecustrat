import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN TÉCNICA OPTIMIZADA ---
@st.cache_resource(show_spinner=False)
def conectar_nube():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        pk = st.secrets["private_key"].replace('\\n', '\n').strip()
        creds_dict = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": pk,
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"]
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Error de Llave: {e}")
        return None

def obtener_hoja(nombre_hoja):
    try:
        client = conectar_nube()
        if client:
            return client.open("EMI_DATA_PRO").worksheet(nombre_hoja)
    except: return None

def leer_datos(nombre_hoja):
    try:
        ws = obtener_hoja(nombre_hoja)
        if ws:
            df = pd.DataFrame(ws.get_all_records())
            if not df.empty:
                df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
                df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            return df
    except: return pd.DataFrame()

# --- 2. INTERFAZ Y REPOSITORIO DE ÓRDENES ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 15px; border-radius: 10px; border: 1px solid #FFD700; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #FFD700; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL (CONTROL DE BALANCE) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 SALDO BANCO", value=0.0)
    c_ini = st.number_input("💵 SALDO CAJA", value=0.0)
    
    # Cálculos para el Balance
    df_v = leer_datos("Ventas")
    df_f = leer_datos("Fijos")
    df_h = leer_datos("Hormiga")
    df_p = leer_datos("Proveedores")
    df_c = leer_datos("Cobros")

    v_tot = df_v['Monto'].sum() if not df_v.empty else 0
    f_pag = df_f[df_f['Estado'] == 'PAGADO']['Monto'].sum() if not df_f.empty else 0
    p_pag = df_p[df_p['Estado'] == 'PAGADO']['Monto'].sum() if not df_p.empty else 0
    h_tot = df_h['Monto'].sum() if not df_h.empty else 0
    c_pag = df_c[df_c['Estado'] == 'COBRADO']['Monto'].sum() if not df_c.empty else 0

    st.metric("BALANCE NETO", f"$ {round(b_ini + c_ini + v_tot + c_pag - f_pag - p_pag - h_tot, 2)}")

# --- 4. PESTAÑAS (MANTIENE TODAS LAS ÓRDENES) ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

def render_modulo(hoja, alias, label, icono, est_final):
    df = leer_datos(hoja)
    st.markdown(f"<div class='sum-box'>TOTAL {hoja.upper()}: $ {df['Monto'].sum() if not df.empty else 0}</div>", unsafe_allow_html=True)
    
    with st.expander(f"➕ Registrar {label}"):
        with st.form(f"form_{alias}"):
            f_reg = st.date_input("Fecha", date.today())
            det = st.text_input("Detalle/Nombre")
            m_reg = st.number_input("Monto $", min_value=0.0)
            if st.form_submit_button("GRABAR"):
                ws = obtener_hoja(hoja)
                if ws:
                    ws.append_row([str(f_reg), sede_act, det, m_reg, "PENDIENTE"])
                    st.rerun()

    if not df.empty:
        for i, row in df.iterrows():
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            c1.write(f"📅 {row['Fecha']} | **{row['Concepto']}**")
            c2.write(f"$ {row['Monto']} ({row['Estado']})")
            if row['Estado'] == "PENDIENTE":
                if c3.button(f"{icono} {est_final}", key=f"btn_{alias}_{i}"):
                    obtener_hoja(hoja).update_cell(i + 2, 5, est_final)
                    st.rerun()
            else:
                if c3.button("🔄 REVERTIR", key=f"rev_{alias}_{i}"):
                    obtener_hoja(hoja).update_cell(i + 2, 5, "PENDIENTE")
                    st.rerun()
            if c4.button("🗑️", key=f"del_{alias}_{i}"):
                obtener_hoja(hoja).delete_rows(i + 2)
                st.rerun()

with tabs[1]: render_modulo("Fijos", "f", "Gasto Fijo", "💳", "PAGADO")
with tabs[3]: render_modulo("Proveedores", "p", "Proveedor", "💸", "PAGADO")
with tabs[4]: render_modulo("Cobros", "c", "Cobro Cliente", "💰", "COBRADO")

# --- 5. REPORTES (SEGÚN ÓRDENES ANTERIORES) ---
with tabs[5]:
    st.header("📊 Inteligencia EMI")
    col_a, col_b = st.columns(2)
    inicio = col_a.date_input("Desde", date.today().replace(day=1))
    fin = col_b.date_input("Hasta", date.today())
    
    df_p_f = leer_datos("Proveedores")
    if not df_p_f.empty:
        df_p_f = df_p_f[(df_p_f['Fecha'] >= inicio) & (df_p_f['Fecha'] <= fin)]
        if not df_p_f.empty:
            st.subheader("🚛 Máximo Proveedor")
            fig = px.pie(df_p_f.groupby("Concepto")["Monto"].sum().reset_index(), values="Monto", names="Concepto")
            st.plotly_chart(fig, use_container_width=True)
