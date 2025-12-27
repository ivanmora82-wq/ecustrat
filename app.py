import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT PRO", layout="wide")

# 2. INICIALIZACIÓN DE DATOS
if 'caja_total' not in st.session_state: st.session_state.caja_total = 0.0
if 'db_proveedores' not in st.session_state: st.session_state.db_proveedores = []
if 'db_cobros' not in st.session_state: st.session_state.db_cobros = []
if 'db_hormiga' not in st.session_state: st.session_state.db_hormiga = []
if 'historial_ventas' not in st.session_state: st.session_state.historial_ventas = []
if 'gastos_fijos' not in st.session_state: 
    st.session_state.gastos_fijos = {"Arriendo": 0.0, "Luz/Agua": 0.0, "Internet": 0.0, "Sueldos": 0.0}

# 3. BARRA LATERAL (PERSONALIZACIÓN DEL LOCAL)
st.sidebar.title("🛡️ ECU-STRAT PRO")
nombre_local = st.sidebar.text_input("Nombre del Local/Negocio", "Mi Negocio")
tipo_sede = st.sidebar.selectbox("Tipo de Sede", ["Matriz", "Sucursal 1", "Sucursal 2", "Punto de Venta"])

if st.session_state.caja_total == 0:
    val_ini = st.sidebar.number_input("Capital Inicial Real ($)", min_value=0.0)
    if st.sidebar.button("Establecer Capital"):
        st.session_state.caja_total = val_ini
        st.rerun()

is_premium = st.sidebar.toggle("🔓 Modo Premium", value=True)
st.sidebar.markdown("---")
st.sidebar.metric("SALDO EN CAJA", f"$ {round(st.session_state.caja_total, 2)}")
st.sidebar.info(f"📍 {nombre_local} - {tipo_sede}")

st.title(f"Sistema Financiero: {nombre_local}")

# 4. TODAS LAS PESTAÑAS (TABS) - ASEGURANDO VISIBILIDAD
t_bal, t_caja, t_fijos, t_hormiga, t_prov, t_cobros, t_rep = st.tabs([
    "📊 Balance", "📅 Caja Diaria", "🏢 Gastos Fijos", "🐜 Gastos Hormiga", "🚛 Proveedores", "📞 Cobros", "📈 REPORTES"
])

# --- TAB BALANCE ---
with t_bal:
    deuda = sum(p['Monto'] for p in st.session_state.db_proveedores if p['Estado'] == 'Pendiente')
    cobro = sum(c['Total'] - c['Abonos'] for c in st.session_state.db_cobros if c['Estado'] == 'Pendiente')
    c1, c2, c3 = st.columns(3)
    c1.metric("Disponible", f"$ {round(st.session_state.caja_total, 2)}")
    c2.metric("Deudas", f"$ {round(deuda, 2)}", delta_color="inverse")
    c3.metric("Por Cobrar", f"$ {round(cobro, 2)}")

# --- TAB CAJA DIARIA ---
with t_caja:
    st.subheader("Cierre de Caja")
    with st.form("caja_dia", clear_on_submit=True):
        fec_v = st.date_input("Fecha", date.today())
        v_dia = st.number_input("Venta Total ($)", min_value=0.0)
        c_chica = st.number_input("Caja Chica ($)", min_value=0.0)
        if st.form_submit_button("Guardar"):
            neto = v_dia - c_chica
            st.session_state.caja_total += neto
            st.session_state.historial_ventas.append({"Fecha": fec_v, "Monto": neto})
            st.rerun()

# --- TAB GASTOS FIJOS ---
with t_fijos:
    st.subheader("🏢 Gastos Fijos Mensuales")
    with st.form("fijos_form"):
        colf1, colf2 = st.columns(2)
        arr = colf1.number_input("Arriendo", value=st.session_state.gastos_fijos["Arriendo"])
        luz = colf2.number_input("Luz/Agua", value=st.session_state.gastos_fijos["Luz/Agua"])
        int_ = colf1.number_input("Internet", value=st.session_state.gastos_fijos["Internet"])
        sue = colf2.number_input("Sueldos", value=st.session_state.gastos_fijos["Sueldos"])
        if st.form_submit_button("Actualizar y Pagar Fijos"):
            total_f = arr + luz + int_ + sue
            st.session_state.caja_total -= total_f
            st.success(f"Pagado ${total_f}")
            st.rerun()

# --- TAB PROVEEDORES ---
with t_prov:
    st.subheader("🚛 Gestión de Proveedores")
    with st.form("prov_form", clear_on_submit=True):
        p_n = st.text_input("Nombre Proveedor")
        p_m = st.number_input("Monto Factura", min_value=0.0)
        p_f = st.date_input("Fecha de Vencimiento")
        if st.form_submit_button("Registrar Deuda"):
            st.session_state.db_proveedores.append({"Nombre": p_n, "Monto": p_m, "Fecha": p_f, "Estado": "Pendiente"})
            st.rerun()
    for i, p in enumerate(st.session_state.db_proveedores):
        if p['Estado'] == "Pendiente":
            st.warning(f"Pagar a {p['Nombre']}: ${p['Monto']} (Vence: {p['Fecha']})")
            if st.button(f"Pagar {i}"):
                st.session_state.caja_total -= p['Monto']
                p['Estado'] = "Pagado"
                st.rerun()

# --- TAB COBROS ---
with t_cobros:
    st.subheader("📞 Cuentas por Cobrar")
    with st.form("cobro_form", clear_on_submit=True):
        c_n = st.text_input("Nombre Cliente")
        c_m = st.number_input("Monto Total", min_value=0.0)
        if st.form_submit_button("Registrar Crédito"):
            st.session_state.db_cobros.append({"Cliente": c_n, "Total": c_m, "Abonos": 0.0, "Estado": "Pendiente"})
            st.rerun()

# --- TAB REPORTES DINÁMICOS ---
with t_rep:
    st.header("📈 Centro de Reportes")
    tipo_rep = st.selectbox("Seleccione el tipo de Reporte", ["Ventas por Fecha", "Análisis de Gastos Hormiga", "Resumen de Proveedores"])
    
    if tipo_rep == "Ventas por Fecha" and st.session_state.historial_ventas:
        df_v = pd.DataFrame(st.session_state.historial_ventas)
        st.plotly_chart(px.line(df_v, x='Fecha', y='Monto', title="Evolución de Ventas"), use_container_width=True)
    
    elif tipo_rep == "Análisis de Gastos Hormiga" and st.session_state.db_hormiga:
        df_h = pd.DataFrame(st.session_state.db_hormiga)
        st.plotly_chart(px.pie(df_h, names="Concepto", values="Monto", title="Distribución de Gastos"), use_container_width=True)
        
    elif tipo_rep == "Resumen de Proveedores" and st.session_state.db_proveedores:
        df_p = pd.DataFrame(st.session_state.db_proveedores)
        st.plotly_chart(px.bar(df_p, x="Nombre", y="Monto", color="Estado", title="Historial con Proveedores"), use_container_width=True)
