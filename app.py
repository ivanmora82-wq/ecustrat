import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import io

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT MASTER V18.2", layout="wide")

# 2. INICIALIZACIÓN DE DATOS
if 'db_movimientos' not in st.session_state: st.session_state.db_movimientos = []
if 'cat_hormiga' not in st.session_state: st.session_state.cat_hormiga = ["Taxi", "Almuerzo", "Suministros"]
if 'cat_proveedores' not in st.session_state: st.session_state.cat_proveedores = ["General"]
if 'cat_clientes' not in st.session_state: st.session_state.cat_clientes = ["Consumidor Final"]
if 'cat_fijos' not in st.session_state: st.session_state.cat_fijos = ["Arriendo", "Luz", "Agua", "WIFI", "Sueldos"]

# 3. BARRA LATERAL
with st.sidebar:
    st.title("🛡️ ECU-STRAT MASTER")
    nombre_emp = st.text_input("Empresa", "Mi Negocio")
    sede_actual = st.selectbox("📍 Sede Actual", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    with st.expander("⚙️ Gestión de Catálogos"):
        tipo_cat = st.selectbox("Añadir a:", ["Gasto Hormiga", "Proveedor", "Cliente", "Gasto Fijo"])
        nuevo_item = st.text_input("Nombre del nuevo concepto")
        if st.button("➕ Guardar en Catálogo"):
            if nuevo_item:
                if tipo_cat == "Gasto Hormiga": st.session_state.cat_hormiga.append(nuevo_item)
                elif tipo_cat == "Proveedor": st.session_state.cat_proveedores.append(nuevo_item)
                elif tipo_cat == "Cliente": st.session_state.cat_clientes.append(nuevo_item)
                elif tipo_cat == "Gasto Fijo": st.session_state.cat_fijos.append(nuevo_item)
                st.rerun()

    def calc_bal(s):
        if not st.session_state.db_movimientos: return 0.0
        df = pd.DataFrame(st.session_state.db_movimientos)
        d = df[df['Sede'] == s]
        if d.empty: return 0.0
        ing = d[d['Tipo']=='Venta']['Monto'].sum()
        egr = d[d['Estado']=='Pagado']['Monto'].sum()
        return ing - egr

    st.metric(f"BALANCE {sede_actual.upper()}", f"$ {round(calc_bal(sede_actual), 2)}")

# 4. TABS PRINCIPALES
t_v, t_f, t_h, t_p, t_c, t_sim, t_rep = st.tabs([
    "💰 Ventas", "🏢 Fijos", "🐜 Hormiga", "🚛 Prov", "📞 Cobros", "🚀 SIM", "📈 REP"
])

# --- TAB VENTAS ---
with t_v:
    st.subheader(f"Ingresos - {sede_actual}")
    with st.form("f_v", clear_on_submit=True):
        c1, c2 = st.columns(2)
        fv, mv = c1.date_input("Fecha", date.today()), c2.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Guardar Venta"):
            st.session_state.db_movimientos.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", "Monto": mv, "Sede": sede_actual, "Estado": "Ingreso"})
            st.rerun()
    if st.session_state.db_movimientos:
        df = pd.DataFrame(st.session_state.db_movimientos)
        st.dataframe(df[(df['Tipo'] == "Venta") & (df['Sede'] == sede_actual)], use_container_width=True)

# --- TAB FIJOS ---
with t_f:
    st.subheader("🏢 Gastos Operativos")
    with st.form("f_f", clear_on_submit=True):
        f_c = st.selectbox("Concepto Fijo", st.session_state.cat_fijos)
        f_m = st.number_input("Monto Fijo ($)", min_value=0.0)
        if st.form_submit_button("Pagar Fijo"):
            st.session_state.db_movimientos.append({"Fecha": date.today(), "Tipo": "Gasto Fijo", "Concepto": f_c, "Monto": f_m, "Sede": sede_actual, "Estado": "Pagado"})
            st.rerun()

# --- TAB HORMIGA ---
with t_h:
    st.subheader("🐜 Gastos Hormiga")
    with st.form("f_h", clear_on_submit=True):
        h_c = st.selectbox("Concepto", st.session_state.cat_hormiga)
        h_m = st.number_input("Monto Gasto ($)", min_value=0.0)
        if st.form_submit_button("Registrar Gasto"):
            st.session_state.db_movimientos.append({"Fecha": date.today(), "Tipo": "Hormiga", "Concepto": h_c, "Monto": h_m, "Sede": sede_actual, "Estado": "Pagado"})
            st.rerun()

# --- TAB PROVEEDORES ---
with t_p:
    st.subheader("🚛 Cuentas por Pagar")
    with st.form("f_p", clear_on_submit=True):
        p_c = st.selectbox("Proveedor", st.session_state.cat_proveedores)
        p_m = st.number_input("Monto Deuda", min_value=0.0)
        p_v = st.date_input("Vencimiento")
        if st.form_submit_button("Guardar Deuda"):
            st.session_state.db_movimientos.append({"Fecha": date.today(), "Vencimiento": p_v, "Tipo": "Proveedor", "Concepto": p_c, "Monto": p_m, "Sede": sede_actual, "Estado": "Pendiente"})
            st.rerun()
    for i, m in enumerate(st.session_state.db_movimientos):
        if m['Tipo'] == "Proveedor" and m['Estado'] == "Pendiente":
            st.warning(f"Deuda con {m['Concepto']}: ${m['Monto']}")
            if st.button(f"Pagar {i}"): m['Estado'] = "Pagado"; st.rerun()

# --- TAB COBROS ---
with t_c:
    st.subheader("📞 Cuentas por Cobrar")
    with st.form("f_cob", clear_on_submit=True):
        c_c = st.selectbox("Cliente", st.session_state.cat_clientes)
        c_m = st.number_input("Monto Crédito", min_value=0.0)
        if st.form_submit_button("Guardar Crédito"):
            st.session_state.db_movimientos.append({"Fecha": date.today(), "Tipo": "Cobro", "Concepto": c_c, "Monto": c_m, "Sede": sede_actual, "Estado": "Pendiente"})
            st.rerun()

# --- TAB SIMULADOR ---
with t_sim:
    st.header("🚀 Simulador de Crecimiento")
    v_actual = 0.0
    if st.session_state.db_movimientos:
        df_sim = pd.DataFrame(st.session_state.db_movimientos)
        if 'Tipo' in df_sim.columns:
            v_actual = df_sim[(df_sim['Tipo'] == 'Venta') & (df_sim['Sede'] == sede_actual)]['Monto'].sum()
    c_inv = st.number_input("Costo nueva inversión ($)", min_value=0.0, value=100.0)
    margen = st.slider("Margen (%)", 10, 90, 30)
    necesidad = c_inv / (margen / 100)
    st.metric("Venta extra necesaria", f"$ {round(necesidad, 2)}")

# --- TAB REPORTES ---
with t_rep:
    st.header("📊 Análisis")
    if st.session_state.db_movimientos:
        df_r = pd.DataFrame(st.session_state.db_movimientos)
        st.plotly_chart(px.bar(df_r.groupby("Sede")["Monto"].sum().reset_index(), x="Sede", y="Monto", color="Sede"))
