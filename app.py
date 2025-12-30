import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN Y ACCIONES ---
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        pk = st.secrets["private_key"].replace('\\n', '\n')
        creds_dict = {
            "type": "service_account", "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"], "private_key": pk,
            "client_email": st.secrets["client_email"], "client_id": st.secrets["client_id"]
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds).open("EMI_DATA_PRO")
    except: return None

def leer(hoja):
    try:
        df = pd.DataFrame(conectar().worksheet(hoja).get_all_records())
        if not df.empty: df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

def guardar(hoja, fila):
    try: conectar().worksheet(hoja).append_row(fila); st.success(f"✅ Grabado en {hoja}")
    except: st.error("❌ Error al grabar")

def eliminar_fila(hoja, index):
    try: 
        conectar().worksheet(hoja).delete_rows(index + 2)
        st.rerun()
    except: st.error("No se pudo borrar")

# --- 2. DISEÑO Y BARRA LATERAL ---
st.set_page_config(page_title="EMI MASTER PRO V48", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 15px; border-radius: 12px; border: 2px solid #FFD700; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px; font-weight: bold; border: 1px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 SALDO BANCO", value=0.0)
    c_ini = st.number_input("💵 SALDO CAJA", value=0.0)
    
    # Cálculos globales
    v_t = leer("Ventas")['Monto'].sum() if not leer("Ventas").empty else 0
    f_t = leer("Fijos")['Monto'].sum() if not leer("Fijos").empty else 0
    h_t = leer("Hormiga")['Monto'].sum() if not leer("Hormiga").empty else 0
    st.metric("BALANCE NETO", f"$ {round(b_ini + c_ini + v_t - f_t - h_t, 2)}")

# --- 3. PESTAÑAS OPERATIVAS ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

def modulo_operativo(hoja, alias, label_nombre):
    df = leer(hoja)
    nombres_grabados = df['Concepto'].unique().tolist() if not df.empty else []
    
    with st.form(f"f_{alias}"):
        col_f, col_n = st.columns(2)
        f = col_f.date_input("Fecha de Registro", date.today())
        nom = col_n.selectbox(f"Seleccionar {label_nombre}", ["Nuevo..."] + nombres_grabados)
        if nom == "Nuevo...": nom = st.text_input(f"Nombre de {label_nombre}")
        m = st.number_input("Monto $", min_value=0.0)
        if st.form_submit_button(f"GRABAR {hoja.upper()}"):
            guardar(hoja, [str(f), sede_act, nom, m, "Activo"])
            st.rerun()
    
    # Muestra sumatoria total antes de la tabla
    total_val = df['Monto'].sum() if not df.empty else 0
    st.markdown(f"<div class='sum-box'>📈 TOTAL ACUMULADO EN {hoja.upper()}: $ {total_val}</div>", unsafe_allow_html=True)
    
    if not df.empty:
        for i, row in df.iterrows():
            c1, c2, c3, c4 = st.columns([4, 2, 1, 1])
            c1.write(f"📅 {row['Fecha']} | **{row['Concepto']}**")
            c2.write(f"$ {row['Monto']}")
            if c3.button("📝", key=f"e_{alias}_{i}"): st.info("Editar directamente en Sheets")
            if c4.button("🗑️", key=f"d_{alias}_{i}"): eliminar_fila(hoja, i)

with tabs[0]: modulo_operativo("Ventas", "v", "Venta")
with tabs[1]: modulo_operativo("Fijos", "f", "Gasto Fijo")
with tabs[2]: modulo_operativo("Hormiga", "h", "Gasto Hormiga")
with tabs[3]: modulo_operativo("Proveedores", "p", "Proveedor")
with tabs[4]: modulo_operativo("Cobros", "c", "Cliente")

# --- 4. CENTRO DE REPORTES (SOLICITADOS ANTERIORMENTE) ---
with tabs[5]:
    st.header("📊 Inteligencia de Negocio")
    t_g = st.radio("Estilo de Gráfico:", ["Barras", "Pastel", "Lineal"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # Reporte 1: Mayor Proveedor
        df_p = leer("Proveedores")
        if not df_p.empty:
            st.subheader("🚛 Top Proveedores")
            res_p = df_p.groupby("Concepto")["Monto"].sum().reset_index()
            if t_g == "Barras": fig1 = px.bar(res_p, x="Concepto", y="Monto", color="Concepto")
            elif t_g == "Pastel": fig1 = px.pie(res_p, values="Monto", names="Concepto")
            else: fig1 = px.line(res_p, x="Concepto", y="Monto")
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Reporte 2: Mayor Gasto Hormiga
        df_h = leer("Hormiga")
        if not df_h.empty:
            st.subheader("🐜 Gastos Hormiga")
            res_h = df_h.groupby("Concepto")["Monto"].sum().reset_index()
            fig2 = px.bar(res_h, x="Concepto", y="Monto") if t_g != "Pastel" else px.pie(res_h, values="Monto", names="Concepto")
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🏢 Rendimiento por Sede (Matriz vs Sucursales)")
    df_v = leer("Ventas")
    if not df_v.empty:
        fig_s = px.bar(df_v.groupby("Sede")["Monto"].sum().reset_index(), x="Sede", y="Monto", color="Sede")
        st.plotly_chart(fig_s, use_container_width=True)
