import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import io

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT ULTIMATE V18.1", layout="wide")

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

    # CÁLCULO DE BALANCE SEGURO
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
        c1, c2, c3 = st.columns(3)
        fv = c1.date_input("Fecha", date.today())
        mv = c2.number_input("Monto ($)", min_value=0.0)
        nv = c3.text_input("Nota", "Venta Diaria")
        if st.form_submit_button("Guardar Venta"):
            st.session_state.db_movimientos.append({
                "Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", 
                "Monto": mv, "Sede": sede_actual, "Estado": "Ingreso", "Nota": nv
            })
            st.rerun()
    
    if st.session_state.db_movimientos:
        df_v = pd.DataFrame(st.session_state.db_movimientos)
        df_v_sede = df_v[(df_v['Tipo'] == "Venta") & (df_v['Sede'] == sede_actual)]
        st.write("### Historial de Ventas")
        st.dataframe(df_v_sede, use_container_width=True)

# --- TAB SIMULADOR (CORREGIDO) ---
with t_sim:
    st.header("🚀 Simulador de Crecimiento")
    
    # Validación para evitar el KeyError
    v_actual = 0.0
    if st.session_state.db_movimientos:
        df_sim = pd.DataFrame(st.session_state.db_movimientos)
        if not df_sim.empty and 'Tipo' in df_sim.columns:
            v_actual = df_sim[(df_sim['Tipo'] == 'Venta') & (df_sim['Sede'] == sede_actual)]['Monto'].sum()
    
    c_inv = st.number_input("Costo de la nueva inversión/personal ($)", min_value=0.0, value=100.0)
    margen = st.slider("Margen de Ganancia (%)", 10, 90, 30)
    
    if margen > 0:
        necesidad = c_inv / (margen / 100)
        st.metric("Venta mensual extra necesaria", f"$ {round(necesidad, 2)}")
        
        if v_actual > 0:
            crecimiento = (necesidad / v_actual) * 100
            st.warning(f"Debes incrementar tus ventas en un **{round(crecimiento, 1)}%**")
        else:
            st.info("ℹ️ Registra ventas primero para calcular el % de incremento necesario.")

# --- TAB REPORTES ---
with t_rep:
    st.header("📊 Análisis de Negocio")
    if st.session_state.db_movimientos:
        df_rep = pd.DataFrame(st.session_state.db_movimientos)
        op = st.selectbox("Ver:", ["Estructura de Gastos", "Comparativa Sedes"])
        if op == "Estructura de Gastos":
            fig = px.pie(df_rep, values="Monto", names="Tipo", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        elif op == "Comparativa Sedes":
            res_sede = df_rep.groupby("Sede")["Monto"].sum().reset_index()
            st.plotly_chart(px.bar(res_sede, x="Sede", y="Monto", color="Sede"), use_container_width=True)
    else:
        st.info("No hay datos para mostrar gráficos.")
