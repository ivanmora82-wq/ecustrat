import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import io

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT ULTIMATE V18", layout="wide")

# 2. INICIALIZACIÓN DE DATOS (CATÁLOGOS Y MOVIMIENTOS)
if 'db_movimientos' not in st.session_state: st.session_state.db_movimientos = []
if 'cat_hormiga' not in st.session_state: st.session_state.cat_hormiga = ["Taxi", "Almuerzo", "Suministros"]
if 'cat_proveedores' not in st.session_state: st.session_state.cat_proveedores = ["Distribuidora Principal"]
if 'cat_clientes' not in st.session_state: st.session_state.cat_clientes = ["Consumidor Final"]
if 'cat_fijos' not in st.session_state: st.session_state.cat_fijos = ["Arriendo", "Luz", "Agua", "WIFI", "Sueldos"]

# 3. BARRA LATERAL (CONTROL MAESTRO)
with st.sidebar:
    st.title("🛡️ ECU-STRAT MASTER")
    nombre_emp = st.text_input("Empresa", "Mi Negocio")
    sede_actual = st.selectbox("📍 Sede Actual", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    with st.expander("⚙️ Gestión de Catálogos"):
        tipo_cat = st.selectbox("Añadir a:", ["Gasto Hormiga", "Proveedor", "Cliente", "Gasto Fijo"])
        nuevo_item = st.text_input("Nombre del nuevo concepto")
        if st.button("➕ Guardar en Catálogo"):
            if tipo_cat == "Gasto Hormiga": st.session_state.cat_hormiga.append(nuevo_item)
            elif tipo_cat == "Proveedor": st.session_state.cat_proveedores.append(nuevo_item)
            elif tipo_cat == "Cliente": st.session_state.cat_clientes.append(nuevo_item)
            elif tipo_cat == "Gasto Fijo": st.session_state.cat_fijos.append(nuevo_item)
            st.rerun()

    # CÁLCULO DE BALANCE EN VIVO
    df_all = pd.DataFrame(st.session_state.db_movimientos)
    def calc_bal(s):
        if df_all.empty: return 0.0
        d = df_all[df_all['Sede'] == s]
        ing = d[d['Tipo']=='Venta']['Monto'].sum() + d[(d['Tipo']=='Cobro') & (d['Estado']=='Pagado')]['Monto'].sum()
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
        c1, c2, c3 = st.columns(3)
        fv = c1.date_input("Fecha", date.today())
        mv = c2.number_input("Monto ($)", min_value=0.0)
        nv = c3.text_input("Nota", "Venta Diaria")
        if st.form_submit_button("Guardar Venta"):
            st.session_state.db_movimientos.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", "Monto": mv, "Sede": sede_actual, "Estado": "Ingreso", "Nota": nv})
            st.rerun()
    # Historial para editar/borrar
    for i, m in enumerate(st.session_state.db_movimientos):
        if m['Tipo'] == "Venta" and m['Sede'] == sede_actual:
            col1, col2, col3 = st.columns([4, 1, 1])
            col1.write(f"📅 {m['Fecha']} - ${m['Monto']} ({m['Nota']})")
            if col3.button("🗑️", key=f"dv_{i}"):
                st.session_state.db_movimientos.pop(i); st.rerun()

# --- TAB GASTOS FIJOS ---
with t_f:
    st.subheader("Pagos de Estructura")
    with st.form("f_f", clear_on_submit=True):
        f_c = st.selectbox("Concepto Fijo", st.session_state.cat_fijos)
        f_m = st.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Pagar Gasto Fijo"):
            st.session_state.db_movimientos.append({"Fecha": date.today(), "Tipo": "Gasto Fijo", "Concepto": f_c, "Monto": f_m, "Sede": sede_actual, "Estado": "Pagado"})
            st.rerun()

# --- TAB SIMULADOR ---
with t_sim:
    st.header("🚀 Simulador de Crecimiento")
    v_actual = df_all[(df_all['Tipo'] == 'Venta') & (df_all['Sede'] == sede_actual)]['Monto'].sum()
    c_inv = st.number_input("Costo de la nueva inversión/personal ($)", min_value=1.0)
    margen = st.slider("Margen de Ganancia (%)", 10, 90, 30)
    necesidad = c_inv / (margen / 100)
    st.metric("Venta mensual extra necesaria", f"$ {round(necesidad, 2)}")
    if v_actual > 0:
        st.warning(f"Debes incrementar tus ventas en un **{round((necesidad/v_actual)*100, 1)}%**")

# --- TAB REPORTES ---
with t_rep:
    st.header("📊 Análisis de Negocio")
    if not df_all.empty:
        op = st.selectbox("Ver:", ["Día más fuerte", "Ranking Proveedores", "Comparativa Sedes"])
        if op == "Día más fuerte":
            df_all['Fecha'] = pd.to_datetime(df_all['Fecha'])
            df_all['Dia'] = df_all['Fecha'].dt.day_name()
            st.plotly_chart(px.bar(df_all[df_all['Tipo']=='Venta'], x="Dia", y="Monto", title="Ventas por Día"))
        elif op == "Comparativa Sedes":
            st.plotly_chart(px.bar(df_all.groupby("Sede")["Monto"].sum().reset_index(), x="Sede", y="Monto", color="Sede"))
