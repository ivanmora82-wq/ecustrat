import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT ULTIMATE V19", layout="wide")

# 2. INICIALIZACIÓN
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}
if 'cat_h' not in st.session_state: st.session_state.cat_h = ["Taxi", "Almuerzo"]
if 'cat_p' not in st.session_state: st.session_state.cat_p = ["General"]
if 'cat_c' not in st.session_state: st.session_state.cat_c = ["Consumidor Final"]

# 3. BARRA LATERAL (CONTROL FINANCIERO)
with st.sidebar:
    st.title("🛡️ ECU-STRAT MASTER")
    sede_act = st.selectbox("📍 Sede Actual", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    st.subheader("💰 Configuración de Saldos")
    st.session_state.saldos["Banco"] = st.number_input("Saldo en Banco ($)", value=st.session_state.saldos["Banco"])
    st.session_state.saldos["Caja Chica"] = st.number_input("Saldo Caja Chica ($)", value=st.session_state.saldos["Caja Chica"])
    
    # CÁLCULO DE BALANCE REAL (CONSOLIDADO)
    df = pd.DataFrame(st.session_state.db)
    def obtener_balance(sede=None):
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if df.empty: return base
        filtro = df if sede == "TOTAL" else df[df['Sede'] == sede]
        ing = filtro[filtro['Tipo'] == 'Venta']['Monto'].sum()
        egr = filtro[filtro['Estado'] == 'Pagado']['Monto'].sum()
        return base + ing - egr

    st.divider()
    st.metric("BALANCE REAL (Consolidado)", f"$ {round(obtener_balance('TOTAL'), 2)}")
    st.metric(f"Balance {sede_act}", f"$ {round(obtener_balance(sede_act), 2)}")

# 4. TABS
t_v, t_f, t_h, t_p, t_c, t_rep = st.tabs(["💰 Ventas", "🏢 Fijos", "🐜 Hormiga", "🚛 Prov", "📞 Cobros", "📈 REPORTES"])

# --- TAB VENTAS ---
with t_v:
    with st.form("fv"):
        c1, c2 = st.columns(2)
        fv, mv = c1.date_input("Fecha", date.today()), c2.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Registrar Venta"):
            st.session_state.db.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", "Monto": mv, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()
    if not df.empty: st.write("### Historial de Ventas"), st.dataframe(df[df['Tipo']=='Venta'])

# --- TAB FIJOS (CON BOTÓN DE PAGO) ---
with t_f:
    st.subheader("Gastos Estructurales")
    with st.form("ff"):
        f_c = st.text_input("Concepto (Luz, Agua, etc.)")
        f_m = st.number_input("Monto", min_value=0.0)
        if st.form_submit_button("Programar Gasto Fijo"):
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Gasto Fijo", "Concepto": f_c, "Monto": f_m, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    # Listado de Fijos con botón de pago
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Gasto Fijo" and m['Estado'] == "Pendiente":
            col1, col2 = st.columns([4, 1])
            col1.info(f"🏢 {m['Concepto']} - ${m['Monto']}")
            if col2.button("PAGAR AHORA 🔴", key=f"pf_{i}"):
                m['Estado'] = "Pagado"; st.rerun()

# --- TAB PROVEEDORES (CÁLCULO DE PLAZO) ---
with t_p:
    st.subheader("Cuentas por Pagar")
    with st.form("fp"):
        p_c = st.selectbox("Proveedor", st.session_state.cat_p); p_m = st.number_input("Monto")
        p_v = st.date_input("Vencimiento")
        if st.form_submit_button("Registrar Deuda"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": p_v, "Tipo": "Prov", "Concepto": p_c, "Monto": p_m, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Prov" and m['Estado'] == "Pendiente":
            plazo = (m['Vencimiento'] - m['Fecha']).days
            st.warning(f"🚛 {m['Concepto']} - ${m['Monto']} (Plazo: {plazo} días)")
            if st.button("Pagar Deuda", key=f"pp_{i}"): m['Estado'] = "Pagado"; st.rerun()

# --- TAB REPORTES (MULTIGRÁFICOS) ---
with t_rep:
    st.header("📊 Inteligencia de Negocio")
    if not df.empty:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        col_r1, col_r2 = st.columns(2)
        tipo_an = col_r1.selectbox("Analizar:", ["Sedes (Matriz vs Sucursal)", "Ranking Proveedores", "Día de Mayor Venta", "Mayores Clientes"])
        tipo_gr = col_r2.selectbox("Gráfico:", ["Barras", "Líneas", "Pastel"])

        if tipo_an == "Sedes (Matriz vs Sucursal)":
            res = df[df['Tipo'] == 'Venta'].groupby("Sede")["Monto"].sum().reset_index()
            if tipo_gr == "Barras": fig = px.bar(res, x="Sede", y="Monto", color="Sede")
            elif tipo_gr == "Pastel": fig = px.pie(res, names="Sede", values="Monto")
            st.plotly_chart(fig, use_container_width=True)
            
        elif tipo_an == "Ranking Proveedores":
            res_p = df[df['Tipo'] == 'Prov'].groupby("Concepto")["Monto"].sum().reset_index()
            st.plotly_chart(px.bar(res_p, x="Concepto", y="Monto", title="¿A quién le debemos más?"), use_container_width=True)
    else:
        st.info("No hay datos suficientes para reportes.")
