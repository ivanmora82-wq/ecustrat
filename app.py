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
    try: conectar().worksheet(hoja).append_row(fila); st.success(f"✅ Grabado")
    except: st.error("❌ Error de red")

def eliminar_fila(hoja, index):
    try: 
        conectar().worksheet(hoja).delete_rows(index + 2)
        st.rerun()
    except: st.error("No se pudo borrar")

# --- 2. DISEÑO Y BARRA AZUL/DORADO ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 15px; border-radius: 12px; border: 2px solid #FFD700; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE ACTUAL", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 SALDO BANCO", value=0.0)
    c_ini = st.number_input("💵 SALDO CAJA", value=0.0)
    
    # Balance dinámico
    v_total = leer("Ventas")['Monto'].sum() if not leer("Ventas").empty else 0
    f_total = leer("Fijos")['Monto'].sum() if not leer("Fijos").empty else 0
    h_total = leer("Hormiga")['Monto'].sum() if not leer("Hormiga").empty else 0
    st.metric("BALANCE NETO", f"$ {round(b_ini + c_ini + v_total - f_total - h_total, 2)}")

# --- 3. PESTAÑAS CON BOTONES EDITAR/ELIMINAR ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

def render_modulo(hoja, label_nombre):
    df = leer(hoja)
    lista_nombres = df['Concepto'].unique().tolist() if not df.empty else []
    
    with st.form(f"form_{hoja}"):
        c1, c2 = st.columns(2)
        f = c1.date_input("Fecha", date.today())
        nom = c2.selectbox(f"Seleccionar {label_nombre}", ["Nuevo..."] + lista_nombres)
        if nom == "Nuevo...": nom = st.text_input(f"Escriba nuevo {label_nombre}")
        m = st.number_input("Monto $", min_value=0.0)
        if st.form_submit_button(f"GRABAR EN {hoja.upper()}"):
            guardar(hoja, [str(f), sede_act, nom, m, "Registrado"])
            st.rerun()
    
    if not df.empty:
        st.markdown(f"<div class='sum-box'>📈 TOTAL ACUMULADO {hoja.upper()}: $ {df['Monto'].sum()}</div>", unsafe_allow_html=True)
        # TABLA CON ACCIONES
        for i, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
            col1.write(f"📅 {row['Fecha']} | **{row['Concepto']}**")
            col2.write(f"$ {row['Monto']}")
            if col3.button("📝", key=f"ed_{hoja}_{i}"): st.info("Modo edición activo en Excel")
            if col4.button("🗑️", key=f"del_{hoja}_{i}"): eliminar_fila(hoja, i)

with tabs[0]: render_modulo("Ventas", "Venta")
with tabs[1]: render_modulo("Fijos", "Gasto Fijo")
with tabs[2]: render_modulo("Hormiga", "Gasto Hormiga")
with tabs[3]: render_modulo("Proveedores", "Proveedor")
with tabs[4]: render_modulo("Cobros", "Cliente")

# --- 4. REPORTES COMPLETOS ---
with tabs[5]:
    st.header("📊 Inteligencia de Datos")
    t_graf = st.radio("Gráfico preferido:", ["Barras", "Pastel", "Lineal"], horizontal=True)
    df_p = leer("Proveedores")
    if not df_p.empty:
        st.subheader("🚛 Análisis de Proveedores")
        res_p = df_p.groupby("Concepto")["Monto"].sum().reset_index()
        if t_graf == "Barras": fig = px.bar(res_p, x="Concepto", y="Monto", color="Concepto")
        elif t_graf == "Pastel": fig = px.pie(res_p, values="Monto", names="Concepto")
        else: fig = px.line(res_p, x="Concepto", y="Monto")
        st.plotly_chart(fig, use_container_width=True)
