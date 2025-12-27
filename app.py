import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT PRO", layout="wide")

# 2. BASES DE DATOS (En memoria)
if 'caja_total' not in st.session_state: st.session_state.caja_total = 1000.0
if 'db_proveedores' not in st.session_state: st.session_state.db_proveedores = []
if 'db_cobros' not in st.session_state: st.session_state.db_cobros = []
if 'db_hormiga' not in st.session_state: st.session_state.db_hormiga = []
if 'historial_ventas' not in st.session_state: st.session_state.historial_ventas = []

# 3. BARRA LATERAL
st.sidebar.title("🛡️ ECU-STRAT PRO")
empresa = st.sidebar.text_input("Empresa", "Mi Negocio")
is_premium = st.sidebar.toggle("🔓 Modo Premium", value=False)
st.sidebar.metric("Balance Real", f"$ {round(st.session_state.caja_total, 2)}")

st.title(f"Gestión de {empresa}")

# 4. TABS
t_bal, t_caja, t_hormiga, t_prov, t_cobros, t_rep = st.tabs([
    "📊 Balance", "📦 Caja Diaria", "🐜 Gastos Hormiga", "🚛 Proveedores", "📞 Cobros", "📈 Reportes"
])

# --- GASTOS HORMIGA (ENTRADAS INFINITAS) ---
with t_hormiga:
    st.subheader("Registro de Gastos Diarios")
    with st.form("form_hormiga", clear_on_submit=True):
        col_h1, col_h2 = st.columns(2)
        concepto = col_h1.text_input("Concepto (Ej: Taxi, Jabón, Fundas)")
        monto = col_h2.number_input("Monto ($)", min_value=0.0, step=0.5)
        if st.form_submit_state := st.form_submit_button("Añadir Gasto"):
            if monto > 0:
                st.session_state.caja_total -= monto
                st.session_state.db_hormiga.append({
                    "Fecha": datetime.now().strftime("%Y-%m-%d"),
                    "Concepto": concepto.capitalize(),
                    "Monto": monto
                })
                st.rerun()

    if st.session_state.db_hormiga:
        df_h = pd.DataFrame(st.session_state.db_hormiga)
        st.write("### Detalle de Gastos")
        st.table(df_h)
        
        # Reporte de en qué gastó más
        st.write("### 🔍 ¿En qué gastas más?")
        resumen_h = df_h.groupby("Concepto")["Monto"].sum().reset_index()
        fig_h = px.bar(resumen_h, x="Concepto", y="Monto", color="Concepto", template="plotly_dark")
        st.plotly_chart(fig_h, use_container_width=True)

# --- PROVEEDORES (CANTIDAD INFINITA) ---
with t_prov:
    st.subheader("Mis Proveedores")
    with st.form("form_prov", clear_on_submit=True):
        p_nom = st.text_input("Nombre del Proveedor")
        p_val = st.number_input("Monto de Factura", min_value=0.0)
        if st.form_submit_button("Registrar Nuevo Proveedor"):
            st.session_state.db_proveedores.append({"Nombre": p_nom, "Monto": p_val, "Estado": "Pendiente"})
            st.rerun()
    
    for i, p in enumerate(st.session_state.db_proveedores):
        if p['Estado'] == "Pendiente":
            col_p1, col_p2 = st.columns([3, 1])
            col_p1.write(f"🚛 **{p['Nombre']}**: ${p['Monto']}")
            if col_p2.button(f"Pagar {i}", key=f"btnp_{i}"):
                st.session_state.caja_total -= p['Monto']
                st.session_state.db_proveedores[i]['Estado'] = "Pagado"
                st.rerun()

# --- COBROS (MÚLTIPLES CLIENTES) ---
with t_cobros:
    st.subheader("Cuentas por Cobrar")
    with st.form("form_cobros", clear_on_submit=True):
        c_cli = st.text_input("Nombre del Cliente")
        c_val = st.number_input("Monto a Cobrar", min_value=0.0)
        if st.form_submit_button("Registrar Nuevo Cobro"):
            st.session_state.db_cobros.append({"Cliente": c_cli, "Total": c_val, "Abonos": 0.0, "Estado": "Pendiente"})
            st.rerun()

    for i, c in enumerate(st.session_state.db_cobros):
        if c['Estado'] == "Pendiente":
            col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
            col_c1.write(f"👤 **{c['Cliente']}** (Falta: ${c['Total'] - c['Abonos']})")
            abono = col_c2.number_input(f"Abono de {c['Cliente']}", key=f"abono_{i}")
            if col_c3.button(f"Cobrar {i}", key=f"btnc_{i}"):
                st.session_state.db_cobros[i]['Abonos'] += abono
                st.session_state.caja_total += abono
                if st.session_state.db_cobros[i]['Abonos'] >= c['Total']:
                    st.session_state.db_cobros[i]['Estado'] = "Pagado"
                st.rerun()

# --- REPORTES (PERIODOS) ---
with t_rep:
    if not is_premium:
        st.error("🔒 Reportes Quincenales y Mensuales son funciones Premium.")
    else:
        st.success("Acceso Premium: Reporte Detallado")
        if st.session_state.db_hormiga:
            df_rep = pd.DataFrame(st.session_state.db_hormiga)
            st.write("### Resumen de Gastos por Categoría")
            fig_rep = px.pie(df_rep, names="Concepto", values="Monto", hole=0.5, title="Distribución de Gastos Hormiga")
            st.plotly_chart(fig_rep, use_container_width=True)
