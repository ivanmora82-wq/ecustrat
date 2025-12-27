import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="ECU-STRAT PRO", layout="wide")

# 2. INICIALIZACIÓN DE BASES DE DATOS (Session State)
if 'caja_total' not in st.session_state: st.session_state.caja_total = 0.0
if 'db_proveedores' not in st.session_state: st.session_state.db_proveedores = []
if 'db_cobros' not in st.session_state: st.session_state.db_cobros = []
if 'db_hormiga' not in st.session_state: st.session_state.db_hormiga = []
if 'historial_ventas' not in st.session_state: st.session_state.historial_ventas = []
if 'gastos_fijos' not in st.session_state: 
    st.session_state.gastos_fijos = {"Arriendo": 0.0, "Luz/Agua": 0.0, "Internet": 0.0, "Sueldos": 0.0}

# 3. BARRA LATERAL (CONFIGURACIÓN DEL LOCAL)
st.sidebar.title("🛡️ ECU-STRAT PRO")
nombre_empresa = st.sidebar.text_input("Nombre de la Empresa", "Mi Negocio")
sede = st.sidebar.selectbox("Identificación de Sede", ["Matriz", "Sucursal Sur", "Sucursal Norte", "Bodega"])

if st.session_state.caja_total == 0:
    st.sidebar.subheader("💰 Configuración Inicial")
    val_ini = st.sidebar.number_input("Capital en Efectivo Actual ($)", min_value=0.0)
    if st.sidebar.button("Cargar Capital Inicial"):
        st.session_state.caja_total = val_ini
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.metric("SALDO DISPONIBLE", f"$ {round(st.session_state.caja_total, 2)}")
st.sidebar.write(f"📍 **{nombre_empresa}** - {sede}")
is_premium = st.sidebar.toggle("🔓 Modo Premium", value=True)

st.title(f"🏢 Sistema de Gestión: {nombre_empresa}")
st.info(f"Punto de Control: {sede} | Fecha: {date.today()}")

# 4. PESTAÑAS PRINCIPALES
t_bal, t_caja, t_fijos, t_hormiga, t_prov, t_cobros, t_rep = st.tabs([
    "📊 Balance", "📅 Caja Diaria", "🏢 Gastos Fijos", "🐜 Hormiga", "🚛 Proveedores", "📞 Cobros", "📈 REPORTES"
])

# --- TAB 1: BALANCE ---
with t_bal:
    deuda_total = sum(p['Monto'] for p in st.session_state.db_proveedores if p['Estado'] == 'Pendiente')
    cobro_total = sum(c['Total'] - c['Abonos'] for c in st.session_state.db_cobros if c['Estado'] == 'Pendiente')
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Dinero en Mano/Banco", f"$ {round(st.session_state.caja_total, 2)}")
    c2.metric("Deudas Pendientes", f"$ {round(deuda_total, 2)}", delta="- Salida", delta_color="inverse")
    c3.metric("Créditos Otorgados", f"$ {round(cobro_total, 2)}", delta="+ Entrada")

# --- TAB 2: CAJA DIARIA ---
with t_caja:
    st.subheader("Cierre de Operación Diaria")
    with st.form("caja_form", clear_on_submit=True):
        f_venta = st.date_input("Fecha Contable", date.today())
        v_total = st.number_input("Venta Bruta Total ($)", min_value=0.0)
        c_chica = st.number_input("Caja Chica / Inicio de Día ($)", min_value=0.0)
        if st.form_submit_button("Registrar Venta Neta"):
            neto = v_total - c_chica
            st.session_state.caja_total += neto
            st.session_state.historial_ventas.append({"Fecha": f_venta, "Monto": neto, "Bruto": v_total})
            st.rerun()

# --- TAB 3: GASTOS FIJOS ---
with t_fijos:
    st.subheader("🏢 Gastos Operativos Mensuales")
    with st.form("fijos_form"):
        colf1, colf2 = st.columns(2)
        st.session_state.gastos_fijos["Arriendo"] = colf1.number_input("Arriendo", value=st.session_state.gastos_fijos["Arriendo"])
        st.session_state.gastos_fijos["Luz/Agua"] = colf2.number_input("Luz/Agua", value=st.session_state.gastos_fijos["Luz/Agua"])
        st.session_state.gastos_fijos["Internet"] = colf1.number_input("Internet", value=st.session_state.gastos_fijos["Internet"])
        st.session_state.gastos_fijos["Sueldos"] = colf2.number_input("Sueldos", value=st.session_state.gastos_fijos["Sueldos"])
        if st.form_submit_button("Confirmar Pago de Gastos Fijos"):
            total_f = sum(st.session_state.gastos_fijos.values())
            st.session_state.caja_total -= total_f
            st.success(f"Se han descontado ${total_f} del balance.")
            st.rerun()

# --- TAB 4: GASTOS HORMIGA ---
with t_hormiga:
    st.subheader("🐜 Registro de Gastos Menores")
    with st.form("hormiga_form", clear_on_submit=True):
        h_concepto = st.text_input("Descripción del Gasto")
        h_monto = st.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Añadir Gasto Hormiga"):
            st.session_state.caja_total -= h_monto
            st.session_state.db_hormiga.append({"Fecha": date.today(), "Concepto": h_concepto, "Monto": h_monto})
            st.rerun()

# --- TAB 5: PROVEEDORES ---
with t_prov:
    st.subheader("🚛 Cuentas por Pagar (Proveedores)")
    with st.form("prov_form", clear_on_submit=True):
        p_n = st.text_input("Nombre del Proveedor")
        p_m = st.number_input("Valor de Factura ($)", min_value=0.0)
        p_f = st.date_input("Fecha Límite de Pago")
        if st.form_submit_button("Registrar Deuda"):
            st.session_state.db_proveedores.append({"Nombre": p_n, "Monto": p_m, "Fecha": p_f, "Estado": "Pendiente"})
            st.rerun()
    
    for i, p in enumerate(st.session_state.db_proveedores):
        if p['Estado'] == "Pendiente":
            color = "red" if p['Fecha'] <= date.today() else "blue"
            st.markdown(f":{color}[**Pagar a {p['Nombre']}** - ${p['Monto']} - Vence: {p['Fecha']}]")
            if st.button(f"Pagar {p['Nombre']} {i}", key=f"pay_{i}"):
                st.session_state.caja_total -= p['Monto']
                p['Estado'] = "Pagado"
                st.rerun()

# --- TAB 6: COBROS ---
with t_cobros:
    st.subheader("📞 Cuentas por Cobrar (Clientes)")
    with st.form("cobro_form", clear_on_submit=True):
        c_n = st.text_input("Nombre del Cliente")
        c_m = st.number_input("Monto del Crédito ($)", min_value=0.0)
        c_f = st.date_input("Fecha de Cobro Esperada")
        if st.form_submit_button("Registrar Crédito"):
            st.session_state.db_cobros.append({"Cliente": c_n, "Total": c_m, "Abonos": 0.0, "Fecha": c_f, "Estado": "Pendiente"})
            st.rerun()

# --- TAB 7: REPORTES AVANZADOS ---
with t_rep:
    st.header("📈 Centro de Análisis de Datos")
    opcion_rep = st.selectbox("Seleccione el Reporte que desea visualizar:", 
                              ["Tendencia de Ventas Diarias", "Distribución de Gastos Hormiga", "Ranking de Proveedores", "Resumen de Utilidad"])
    
    if opcion_rep == "Tendencia de Ventas Diarias" and st.session_state.historial_ventas:
        df_v = pd.DataFrame(st.session_state.historial_ventas)
        st.plotly_chart(px.line(df_v, x='Fecha', y='Monto', title="Evolución de Ingresos Netos", markers=True), use_container_width=True)
        
    elif opcion_rep == "Distribución de Gastos Hormiga" and st.session_state.db_hormiga:
        df_h = pd.DataFrame(st.session_state.db_hormiga)
        st.plotly_chart(px.pie(df_h, names="Concepto", values="Monto", title="¿En qué se gasta más el diario?", hole=0.4), use_container_width=True)
        
    elif opcion_rep == "Ranking de Proveedores" and st.session_state.db_proveedores:
        df_p = pd.DataFrame(st.session_state.db_proveedores)
        st.plotly_chart(px.bar(df_p, x="Nombre", y="Monto", color="Estado", title="Análisis de Proveedores"), use_container_width=True)

    elif opcion_rep == "Resumen de Utilidad":
        t_ing = sum(v['Monto'] for v in st.session_state.historial_ventas)
        t_egr = sum(p['Monto'] for p in st.session_state.db_proveedores if p['Estado'] == 'Pagado') + sum(h['Monto'] for h in st.session_state.db_hormiga)
        st.metric("UTILIDAD NETA TOTAL", f"$ {round(t_ing - t_egr, 2)}")
