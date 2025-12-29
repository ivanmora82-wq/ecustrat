import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# 1. CONFIGURACIÓN Y ESTILO (Blindado para Celulares)
st.set_page_config(page_title="EMI MASTER V29", layout="wide")

st.markdown("""
    <style>
    /* Forzar fondo y color en la barra lateral para móvil */
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #ffffff !important; font-size: 14px; }
    [data-testid="stSidebar"] input { color: #1c2e4a !important; background-color: #ffffff !important; }
    
    /* Métrica de Balance: Visible en cualquier pantalla */
    [data-testid="stMetricValue"] {
        background-color: #d4af37 !important;
        color: #1c2e4a !important;
        padding: 10px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 22px !important;
        text-align: center;
    }
    
    /* Cuadros de sumatoria por pestaña */
    .resaltado-suma {
        background-color: #f1f3f5;
        border-left: 5px solid #1c2e4a;
        padding: 15px;
        margin-bottom: 20px;
        color: #1c2e4a;
        font-weight: bold;
        font-size: 18px;
        border-radius: 5px;
    }

    /* Estética de botones para móvil */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 2em;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}
if 'nombres_fijos' not in st.session_state: st.session_state.nombres_fijos = set()
if 'nombres_hormiga' not in st.session_state: st.session_state.nombres_hormiga = set()
if 'nombres_prov' not in st.session_state: st.session_state.nombres_prov = set()
if 'nombres_cobro' not in st.session_state: st.session_state.nombres_cobro = set()

# 3. BARRA LATERAL (CONTROL)
with st.sidebar:
    st.markdown("<h1 style='color: #d4af37; text-align: center;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    nombre_local = st.text_input("🏢 EMPRESA", "Mi Negocio")
    sede_act = st.selectbox("📍 SEDE ACTUAL", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    st.session_state.saldos["Banco"] = st.number_input("🏦 BANCO", value=float(st.session_state.saldos["Banco"]))
    st.session_state.saldos["Caja Chica"] = st.number_input("💵 CAJA CHICA", value=float(st.session_state.saldos["Caja Chica"]))
    
    def calc_global():
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if not st.session_state.db: return base
        df_all = pd.DataFrame(st.session_state.db)
        ing = df_all[df_all['Estado'].isin(['Ingreso', 'Pagado_Cobro'])]['Monto'].sum()
        egr = df_all[df_all['Estado'] == 'Pagado']['Monto'].sum()
        return base + ing - egr

    st.metric("BALANCE GENERAL", f"$ {round(calc_global(), 2)}")

# 4. TABS
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTES"])

# Lógica de datos por sede
df_full = pd.DataFrame(st.session_state.db) if st.session_state.db else pd.DataFrame()
def get_sede_data(tipo):
    if df_full.empty or tipo not in df_full['Tipo'].values: return pd.DataFrame()
    return df_full[(df_full['Tipo'] == tipo) & (df_all['Sede'] == sede_act)]

# --- TAB VENTAS ---
with tabs[0]:
    with st.form("fv", clear_on_submit=True):
        c1, c2 = st.columns(2); fv, mv = c1.date_input("Fecha", date.today()), c2.number_input("Monto")
        if st.form_submit_button("Guardar Venta"):
            st.session_state.db.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", "Monto": mv, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()
    
    if not df_full.empty:
        data = df_full[(df_full['Tipo'] == 'Venta') & (df_full['Sede'] == sede_act)]
        if not data.empty:
            st.markdown(f"<div class='resaltado-suma'>Ventas en {sede_act}: $ {data['Monto'].sum()}</div>", unsafe_allow_html=True)
            for i, row in data.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"📅 {row['Fecha']} - **${row['Monto']}**")
                if c2.button("🗑️", key=f"del_v_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB PROVEEDORES ---
with tabs[3]:
    with st.form("fp", clear_on_submit=True):
        p_c = st.selectbox("Proveedor", ["Nuevo..."] + list(st.session_state.nombres_prov))
        if p_c == "Nuevo...": p_c = st.text_input("Escribir Nombre Proveedor")
        p_m = st.number_input("Monto Deuda")
        p_v = st.date_input("Fecha Vencimiento")
        if st.form_submit_button("Registrar Deuda"):
            st.session_state.nombres_prov.add(p_c)
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": p_v, "Tipo": "Prov", "Concepto": p_c, "Monto": p_m, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()

    if not df_full.empty:
        data_p = df_full[(df_full['Tipo'] == 'Prov') & (df_full['Sede'] == sede_act) & (df_full['Estado'] == 'Pendiente')]
        st.markdown(f"<div class='resaltado-suma'>Deuda Pendiente {sede_act}: $ {data_p['Monto'].sum()}</div>", unsafe_allow_html=True)
        for i, row in data_p.iterrows():
            dias = (row['Vencimiento'] - date.today()).days
            estilo = "color:red; font-weight:bold;" if dias <= 1 else ""
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"🚛 {row['Concepto']} - ${row['Monto']} \n (Vence en: {dias} días)", unsafe_allow_html=True)
            if c2.button("✅ Pagar", key=f"py_p_{i}"): st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()
            if c3.button("🗑️", key=f"de_p_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB REPORTES ---
with tabs[5]:
    if not df_full.empty:
        st.subheader("📈 Análisis Estratégico")
        op = st.selectbox("Seleccione Análisis", ["Comparativa entre Sedes", "Gastos Hormiga", "Deuda Proveedores"])
        gra = st.radio("Tipo de Gráfico", ["Barras", "Pastel", "Lineal"], horizontal=True)
        
        # Lógica de gráfico según opción... (se mantiene la lógica de la V28 con títulos claros)
        if op == "Comparativa entre Sedes":
            res = df_full[df_full['Tipo']=='Venta'].groupby("Sede")["Monto"].sum().reset_index()
            fig = px.bar(res, x="Sede", y="Monto", title=f"Ingresos Totales por Sede - {nombre_local}", color="Sede", color_discrete_sequence=px.colors.qualitative.Dark2)
            st.plotly_chart(fig, use_container_width=True)
