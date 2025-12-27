import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ECU-STRAT PRO", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="metric-container"] {
        background-color: #1e2130;
        border: 1px solid #31333f;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS (Simulación de Base de Datos) ---
if 'caja_total' not in st.session_state: st.session_state.caja_total = 1000.0
if 'db_proveedores' not in st.session_state: st.session_state.db_proveedores = []
if 'db_cobros' not in st.session_state: st.session_state.db_cobros = []
if 'historial_ventas' not in st.session_state: st.session_state.historial_ventas = []
if 'gastos_hormiga' not in st.session_state: st.session_state.gastos_hormiga = []

# --- BARRA LATERAL (CONTROL DE ACCESO Y EMPRESA) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/553/553813.png", width=100)
st.sidebar.title("ECU-STRAT PRO")
empresa = st.sidebar.text_input("Empresa", "Mi Negocio")
sucursal = st.sidebar.selectbox("Sede", ["Matriz", "Sucursal 1", "Sucursal 2"])

st.sidebar.markdown("---")
is_premium = st.sidebar.toggle("🔓 Modo Premium (Demo)", value=False)
st.sidebar.metric("Balance Disponible", f"$ {round(st.session_state.caja_total, 2)}")

# --- CABECERA ---
st.title(f"🛡️ {empresa}")
st.caption(f"Panel de Control Financiero | {sucursal}")

# --- TABS DE NAVEGACIÓN ---
t_balance, t_caja, t_gastos, t_prov, t_cobros, t_premium = st.tabs([
    "📊 Balance", "📦 Caja Diaria", "💸 Gastos", "🚛 Proveedores", "📞 Cobros", "📈 Reportes Pro"
])

# --- TAB 1: BALANCE ---
with t_balance:
    deuda_p = sum(p['Monto'] for p in st.session_state.db_proveedores if p['Estado'] == 'Pendiente')
    por_cobrar = sum(c['Total'] - c['Abonos'] for c in st.session_state.db_cobros if c['Estado'] == 'Pendiente')
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Efectivo + Banco", f"$ {round(st.session_state.caja_total, 2)}")
    c2.metric("Por Pagar (Deuda)", f"$ {round(deuda_p, 2)}", delta_color="inverse")
    c3.metric("Por Cobrar", f"$ {round(por_cobrar, 2)}")
    
    st.markdown("---")
    st.subheader("Visualización de Liquidez")
    df_bal = pd.DataFrame({
        'Estado': ['Disponible', 'Comprometido', 'En la Calle'],
        'Monto': [st.session_state.caja_total - deuda_p, deuda_p, por_cobrar]
    })
    fig_bal = px.pie(df_bal, names='Estado', values='Monto', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_bal, use_container_width=True)

# --- TAB 2: CAJA DIARIA ---
with t_caja:
    st.subheader("Cierre de Caja")
    col_c1, col_c2 = st.columns(2)
    v_bruta = col_c1.number_input("Venta del Día ($)", min_value=0.0)
    sencillo = col_c2.number_input("Sencillo para mañana ($)", min_value=0.0)
    
    if st.button("Finalizar Día"):
        neto = v_bruta - sencillo
        st.session_state.caja_total += neto
        st.session_state.historial_ventas.append({"Fecha": datetime.now(), "Monto": neto})
        st.success(f"Se sumaron ${neto} a la cuenta principal.")
        st.rerun()

# --- TAB 3: GASTOS ---
with t_gastos:
