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

# --- INICIALIZACIÓN DE DATOS (Estado de Sesión) ---
if 'caja_total' not in st.session_state: 
    st.session_state.caja_total = 1000.0
if 'db_proveedores' not in st.session_state: 
    st.session_state.db_proveedores = []
if 'db_cobros' not in st.session_state: 
    st.session_state.db_cobros = []
if 'historial_ventas' not in st.session_state: 
    st.session_state.historial_ventas = []
if 'gastos_hormiga' not in st.session_state: 
    st.session_state.gastos_hormiga = []

# --- BARRA LATERAL ---
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
t_balance, t_caja, t_gastos, t_prov, t_cobros, t_reporte = st.tabs([
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
        'Estado': ['Disponible Real', 'Comprometido (Deuda)', 'En la Calle (Cobros)'],
        'Monto': [st.session_state.caja_total - deuda_p, deuda_p, por_cobrar]
    })
    fig_bal = px.pie(df_bal, names='Estado', values='Monto', hole=0.4, template="plotly_dark")
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
    st.subheader("Gastos Fijos")
    f_c1, f_c2, f_c3, f_c4 = st.columns(4)
    arriendo = f_c1.number_input("Arriendo", value=0.0)
    luz = f_c2.number_input("Luz/Agua", value=0.0)
    wifi = f_c3.number_input("Internet", value=0.0)
    sueldos = f_c4.number_input("Sueldos", value=0.0)
    
    st.markdown("---")
    st.subheader("🐜 Gastos Hormiga (Diarios)")
    h_c1, h_c2 = st.columns(2)
    desc_h = h_c1.text_input("Concepto (Taxi, Refrigerio...)")
    monto_h = h_c2.number_input("Costo Gasto ($)", min_value=0.0, key="hormiga_input")
    if st.button("Registrar Salida"):
        if monto_h > 0:
            st.session_state.caja_total -= monto_h
            st.session_state.gastos_hormiga.append({"Concepto": desc_h, "Monto": monto_h})
            st.rerun()

# --- TAB 4: PROVEEDORES ---
with t_prov:
    st.subheader("Cuentas por Pagar")
    with st.expander("Registrar Factura"):
