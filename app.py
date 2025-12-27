import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="ECU-STRAT PRO", layout="wide")

# 2. INICIALIZACIÓN DE BASES DE DATOS (Session State)
if 'caja_total' not in st.session_state:
    st.session_state.caja_total = 1000.0
if 'db_proveedores' not in st.session_state:
    st.session_state.db_proveedores = []
if 'db_cobros' not in st.session_state:
    st.session_state.db_cobros = []
if 'db_hormiga' not in st.session_state:
    st.session_state.db_hormiga = []
if 'historial_ventas' not in st.session_state:
    st.session_state.historial_ventas = []

# 3. BARRA LATERAL (CONTROL)
st.sidebar.title("🛡️ ECU-STRAT PRO")
empresa_nom = st.sidebar.text_input("Nombre de Empresa", "Mi Negocio")
sucursal_nom = st.sidebar.selectbox("Sede", ["Matriz", "Sucursal 1", "Sucursal 2"])
is_premium = st.sidebar.toggle("🔓 Activar Modo Premium", value=False)
st.sidebar.markdown("---")
st.sidebar.metric("Balance Real en Caja", f"$ {round(st.session_state.caja_total, 2)}")

st.title(f"Gestión de {empresa_nom}")
st.caption(f"Sede: {sucursal_nom} | Inteligencia Financiera")

# 4. PESTAÑAS (TABS)
t_bal, t_caja, t_hormiga, t_prov, t_cobros, t_rep = st.tabs([
    "📊 Balance", "📦 Caja Diaria", "🐜 Gastos Hormiga", "🚛 Proveedores", "📞 Cobros", "📈 Reportes"
])

# --- TAB 1: BALANCE GENERAL ---
with t_bal:
    deuda_p = sum(p['Monto'] for p in st.session_state.db_proveedores if p['Estado'] == 'Pendiente')
    por_cobrar = sum(c['Total'] - c['Abonos'] for c in st.session_state.db_cobros if c['Estado'] == 'Pendiente')
    
    col_b1, col_b2, col_b3 = st.columns(3)
    col_b1.metric("Efectivo Actual", f"$ {round(st.session_state.caja_total, 2)}")
    col_b2.metric("Deudas a Pagar", f"$ {round(deuda_p, 2)}", delta_color="inverse")
    col_b3.metric("Cuentas por Cobrar", f"$ {round(por_cobrar, 2)}")
    
    st.markdown("---")
    df_bal = pd.DataFrame({
        'Estado': ['Disponible', 'Deuda', 'Cobros Pendientes'],
        'Monto': [st.session_state.caja_total - deuda_p, deuda_p, por_cobrar]
    })
    fig_bal = px.pie(df_bal, names='Estado', values='Monto', hole=0.4, template="plotly_dark", title="Distribución de Capital")
    st.plotly_chart(fig_bal, use_container_width=True)

# --- TAB 2: CAJA DIARIA ---
with t_caja:
    st.subheader("Cierre de Caja y Sencillo")
    with st.form("cierre_caja"):
        v_bruta = st.number_input("Venta Total del Día ($)", min_value=0.0)
        sencillo = st.number_input("Sencillo para mañana ($)", min_value=0.0)
        if st.form_submit_button("🚀 Finalizar Día"):
            neto = v_bruta - sencillo
            st.session_state.caja_total += neto
            st.session_state.historial_ventas.append({"Fecha": datetime.now(), "Monto": neto})
            st.success(f"Se sumaron ${neto} a la caja.")
            st.rerun()

# --- TAB 3: GASTOS HORMIGA (ENTRADAS INFINITAS) ---
with t_hormiga:
    st.subheader("Registro de Gastos Diarios")
    with st.form("form_hormiga", clear_on_submit=True):
        col_h1, col_h2 = st.columns(2)
        concepto_h = col_h1.text_input("Concepto (Ej: Taxi, Jabón, Fundas)")
        monto_h = col_h2.number_input("Monto ($)", min_value=0.0, step=0.1)
        if st.form_submit_button("➕ Añadir Gasto"):
            if monto_h > 0:
                st.session_state.caja_total -= monto_h
                st.session_state.db_hormiga.append({
                    "Fecha": datetime.now().strftime("%Y-%m-%d"),
                    "Concepto": concepto_h.capitalize(),
                    "Monto": monto_h
                })
                st.rerun()

    if st.session_state.db_hormiga:
        df_h = pd.DataFrame(st.session_state.db_hormiga)
        st.write("### Detalle de Gastos")
        st.dataframe(df_h, use_container_width=True)
        
        st.write("### 🔍 Análisis: ¿En qué gastas más?")
        resumen_h = df_h.groupby("Concepto")["Monto"].sum().reset_index()
        fig_h = px.bar(resumen_h, x="Concepto", y="Monto", color="Concepto", template="plotly_dark")
        st.plotly_chart(fig_h, use_container_width=True)

# --- TAB 4: PROVEEDORES ---
with t_prov:
    st.subheader("Mis Proveedores")
    with st.form("form_prov", clear_on_submit=True):
        p_nom = st.text_input("Nombre del Proveedor")
        p_val = st.number_input("Monto de Factura ($)", min_value=0.0)
        if st.form_submit_button("Registrar Nuevo Proveedor"):
            if p_nom and p_val > 0:
                st.session_state.db_proveedores.append({"Nombre": p_nom, "Monto": p_val, "Estado": "Pendiente"})
                st.rerun()
    
    st.markdown("---")
    for i, p in enumerate(st.session_state.db_proveedores):
        if p['Estado'] == "Pendiente":
            c_p1, c_p2 = st.columns([3, 1])
            c_p1.write(f"🚛 **{p['Nombre']}**: ${p['Monto']}")
            if c_p2.button(f"Marcar Pagado", key=f"btnp_{i}"):
                st.session_state.caja_total -= p['Monto']
                st.session_state.db_proveedores[i]['Estado'] = "Pagado"
                st.rerun()

# --- TAB 5: COBROS ---
with t_cobros:
    st.subheader("Cuentas por Cobrar")
    with st.form("form_cobros", clear_on_submit=True):
        c_cli = st.text_input("Nombre del Cliente")
        c_val = st.number_input("Monto del Crédito ($)", min_value=0.0)
        if st.form_submit_button("Registrar Venta a Crédito"):
            if c_cli and c_val > 0:
                st.session_state.db_cobros.append({"Cliente": c_cli, "Total": c_val, "Abonos": 0.0, "Estado": "Pendiente"})
                st.rerun()

    st.markdown("---")
    for i, c in enumerate(st.session_state.db_cobros):
        if c['Estado'] == "Pendiente":
            col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
            col_c1.write(f"👤 **{c['Cliente']}** (Falta: ${round(c['Total'] - c['Abonos'], 2)})")
            abono_val = col_c2.number_input(f"Abono", key=f"ab_{i}", min_value=0.0)
            if col_c3.button(f"Cobrar", key=f"btnc_{i}"):
                st.session_state.db_cobros[i]['Abonos'] += abono_val
                st.session_state.caja_total += abono_val
                if st.session_state.db_cobros[i]['Abonos'] >= c['Total']:
                    st.session_state.db_cobros[i]['Estado'] = "Pagado"
                st.rerun()

# --- TAB 6: REPORTES PREMIUM ---
with t_rep:
    if not is_premium:
        st.error("🔒 Reportes Detallados Bloqueados")
        st.info("Activa el Modo Premium para ver el análisis mensual y quincenal.")
        st.markdown("[📲 Solicitar Activación Premium](https://wa.me/593XXXXXXXXX)")
    else:
        st.success("Acceso Premium Activo")
        if st.session_state.db_hormiga:
            df_rep = pd.DataFrame(st.session_state.db_hormiga)
            fig_rep = px.pie(df_rep, names="Concepto", values="Monto", title="Distribución Mensual de Gastos")
            st.plotly_chart(fig_rep, use_container_width=True)
        else:
            st.info("No hay datos suficientes para generar reportes.")
