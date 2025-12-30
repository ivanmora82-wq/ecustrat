import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN Y LÓGICA DE DATOS ---
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
    except: st.error("❌ Error de conexión")

def eliminar_fila(hoja, index):
    try:
        doc = conectar()
        ws = doc.worksheet(hoja)
        ws.delete_rows(index + 2) # +2 por encabezado y base 0
        st.warning(f"🗑️ Registro eliminado")
        st.rerun()
    except: st.error("No se pudo eliminar")

# --- 2. DISEÑO Y VISIBILIDAD ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 15px; border-radius: 12px; border: 2px solid #FFD700; }
    .row-style { border-bottom: 1px solid #ddd; padding: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO INICIAL", value=0.0)
    c_ini = st.number_input("💵 CAJA INICIAL", value=0.0)
    
    # Sumatorias para Balance
    total_v = leer("Ventas")['Monto'].sum() if not leer("Ventas").empty else 0
    total_h = leer("Hormiga")['Monto'].sum() if not leer("Hormiga").empty else 0
    st.metric("BALANCE GENERAL REAL", f"$ {round(b_ini + c_ini + total_v - total_h, 2)}")

# --- 4. PESTAÑAS OPERATIVAS ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

# Función para renderizar tablas con acciones
def render_tabla_acciones(nombre_hoja):
    df = leer(nombre_hoja)
    if not df.empty:
        st.write(f"### Registros en {nombre_hoja}")
        cols_h = st.columns([3, 2, 1, 1])
        cols_h[0].write("**Detalle**")
        cols_h[1].write("**Monto**")
        for i, row in df.iterrows():
            c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
            c1.write(f"{row.get('Concepto', row.get('Nombre', 'Registro'))}")
            c2.write(f"${row['Monto']}")
            if c3.button("📝", key=f"e_{nombre_hoja}_{i}"): st.info("Edición en desarrollo")
            if c4.button("🗑️", key=f"d_{nombre_hoja}_{i}"): eliminar_fila(nombre_hoja, i)

with tabs[0]: # VENTAS
    with st.form("v"):
        m = st.number_input("Monto de Venta")
        if st.form_submit_button("GRABAR VENTA"):
            guardar("Ventas", [str(date.today()), sede_act, "Venta", m, "Ingreso"])
            st.rerun()
    render_tabla_acciones("Ventas")

with tabs[1]: # FIJOS
    with st.form("f"):
        nom = st.text_input("Nombre del Gasto Fijo")
        m = st.number_input("Monto")
        if st.form_submit_button("GRABAR FIJO"):
            guardar("Fijos", [str(date.today()), sede_act, nom, m, "Egreso"])
            st.rerun()
    render_tabla_acciones("Fijos")

with tabs[3]: # PROVEEDORES
    with st.form("p"):
        prov = st.text_input("Nombre Proveedor")
        m = st.number_input("Monto Factura")
        if st.form_submit_button("GRABAR DEUDA"):
            guardar("Proveedores", [str(date.today()), sede_act, prov, m, "Pendiente"])
            st.rerun()
    render_tabla_acciones("Proveedores")

# --- 5. REPORTES AVANZADOS ---
with tabs[5]:
    st.header("📊 Inteligencia de Negocio")
    tipo_g = st.radio("Formato de Gráficos:", ["Barras", "Pastel", "Lineal"], horizontal=True)
    
    df_v = leer("Ventas")
    df_p = leer("Proveedores")
    df_h = leer("Hormiga")

    col1, col2 = st.columns(2)
    with col1:
        if not df_p.empty:
            st.subheader("🚛 Mayor Proveedor")
            res_p = df_p.groupby("Nombre")["Monto"].sum().reset_index()
            fig = px.bar(res_p, x="Nombre", y="Monto") if tipo_g=="Barras" else px.pie(res_p, values="Monto", names="Nombre")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not df_h.empty:
            st.subheader("🐜 Mayor Gasto Hormiga")
            res_h = df_h.groupby("Concepto")["Monto"].sum().reset_index()
            fig2 = px.bar(res_h, x="Concepto", y="Monto", color_discrete_sequence=['#e74c3c'])
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🏢 Comparativa Matriz vs Sucursales")
    if not df_v.empty:
        fig_s = px.bar(df_v.groupby("Sede")["Monto"].sum().reset_index(), x="Sede", y="Monto", color="Sede")
        st.plotly_chart(fig_s, use_container_width=True)
