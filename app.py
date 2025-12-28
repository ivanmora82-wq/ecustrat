import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import io

# 1. CONFIGURACIÓN ESTÉTICA (CSS para sobriedad y confianza)
st.set_page_config(page_title="ECU-STRAT MASTER V21", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    [data-testid="stSidebar"] { background-color: #1c2e4a; color: white; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #d4af37; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    h1, h2, h3 { color: #1c2e4a; }
    .stButton>button { background-color: #1c2e4a; color: white; border-radius: 5px; border: none; }
    .stButton>button:hover { background-color: #d4af37; color: #1c2e4a; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}
if 'cat_h' not in st.session_state: st.session_state.cat_h = ["Taxi", "Almuerzo"]
if 'cat_p' not in st.session_state: st.session_state.cat_p = ["General"]
if 'cat_c' not in st.session_state: st.session_state.cat_c = ["Consumidor Final"]

# 3. BARRA LATERAL (LOGO Y CONFIGURACIÓN)
with st.sidebar:
    # Espacio para el Logo (Simulado con Icono y Texto estilizado)
    st.markdown("<h1 style='text-align: center; color: #d4af37;'>🛡️ EMI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8em;'>ECU-STRAT MASTER V21</p>", unsafe_allow_html=True)
    
    st.divider()
    sede_act = st.selectbox("📍 GESTIONAR SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    with st.expander("💰 SALDOS INICIALES"):
        st.session_state.saldos["Banco"] = st.number_input("Banco ($)", value=float(st.session_state.saldos["Banco"]))
        st.session_state.saldos["Caja Chica"] = st.number_input("Caja Chica ($)", value=float(st.session_state.saldos["Caja Chica"]))

    with st.expander("⚙️ CATÁLOGOS (Nombres)"):
        tipo_cat = st.selectbox("Categoría", ["Hormiga", "Proveedor", "Cliente"])
        n_cat = st.text_input("Nombre Nuevo")
        if st.button("Guardar en Catálogo"):
            if n_cat:
                if tipo_cat == "Hormiga": st.session_state.cat_h.append(n_cat)
                elif tipo_cat == "Proveedor": st.session_state.cat_p.append(n_cat)
                else: st.session_state.cat_c.append(n_cat)
                st.rerun()

    # BALANCE CONSOLIDADO
    df_all = pd.DataFrame(st.session_state.db)
    def calc_balance(filtro_sede):
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if df_all.empty: return base
        f = df_all if filtro_sede == "TOTAL" else df_all[df_all['Sede'] == filtro_sede]
        ing = f[f['Estado'] == 'Ingreso']['Monto'].sum()
        egr = f[f['Estado'] == 'Pagado']['Monto'].sum()
        return base + ing - egr

    st.metric("BALANCE REAL TOTAL", f"$ {round(calc_balance('TOTAL'), 2)}")

# 4. TABS PRINCIPALES
t_v, t_f, t_h, t_p, t_c, t_rep = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTES"])

# --- TAB VENTAS ---
with t_v:
    st.subheader(f"Registro de Ingresos - {sede_act}")
    with st.form("fv", clear_on_submit=True):
        c1, c2 = st.columns(2)
        fv, mv = c1.date_input("Fecha", date.today()), c2.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Registrar Venta"):
            st.session_state.db.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", "Monto": mv, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()
    if not df_all.empty:
        st.dataframe(df_all[(df_all['Tipo']=='Venta') & (df_all['Sede']==sede_act)], use_container_width=True)

# --- TAB FIJOS (CON BOTÓN ROJO DE PAGO) ---
with t_f:
    st.subheader("Gastos Fijos Pendientes")
    with st.form("ff"):
        f_con = st.text_input("Concepto (Arriendo, Luz...)")
        f_mon = st.number_input("Monto", min_value=0.0)
        if st.form_submit_button("Programar"):
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Fijo", "Concepto": f_con, "Monto": f_mon, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Fijo" and m['Estado'] == "Pendiente":
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.info(f"🏢 {m['Concepto']} - ${m['Monto']}")
            if c2.button("PAGAR AHORA 🔴", key=f"pf_{i}"):
                m['Estado'] = "Pagado"; st.rerun()
            if c3.button("🗑️", key=f"df_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB PROVEEDORES (Ranking y Tiempo) ---
with t_p:
    st.subheader("Gestión de Proveedores")
    with st.form("fp"):
        p_c = st.selectbox("Proveedor", st.session_state.cat_p)
        p_m = st.number_input("Monto")
        p_v = st.date_input("Vencimiento")
        if st.form_submit_button("Registrar"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": p_v, "Tipo": "Prov", "Concepto": p_c, "Monto": p_m, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Prov" and m['Estado'] == "Pendiente":
            plazo = (m['Vencimiento'] - m['Fecha']).days
            st.warning(f"🚛 {m['Concepto']} - ${m['Monto']} | Plazo: {plazo} días")
            if st.button(f"Pagar Deuda {i}"): m['Estado'] = "Pagado"; st.rerun()

# --- TAB REPORTES (FULL ANALYTICS) ---
with t_rep:
    st.header("📈 Centro de Inteligencia")
    if not df_all.empty:
        col_r1, col_r2 = st.columns(2)
        analisis = col_r1.selectbox("Reporte", ["Comparativa de Ingresos (Sedes)", "Ranking de Proveedores", "Mayores Cobros"])
        grafico = col_r2.radio("Tipo de Visualización", ["Barras", "Lineal", "Pastel"], horizontal=True)

        if analisis == "Comparativa de Ingresos (Sedes)":
            res = df_all[df_all['Tipo'] == 'Venta'].groupby("Sede")["Monto"].sum().reset_index()
            fig = px.bar(res, x="Sede", y="Monto", color="Sede", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
        elif analisis == "Ranking de Proveedores":
            res_p = df_all[df_all['Tipo'] == 'Prov'].groupby("Concepto")["Monto"].sum().reset_index()
            st.plotly_chart(px.bar(res_p, x="Concepto", y="Monto", title="Mayor Proveedor", color_discrete_sequence=['#d4af37']), use_container_width=True)
    else:
        st.info("No hay datos para reportes.")
