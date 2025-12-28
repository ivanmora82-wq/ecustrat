import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta

# 1. CONFIGURACIÓN Y ESTILO PROFESIONAL
st.set_page_config(page_title="ECU-STRAT MASTER V23", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #ffffff !important; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 8px; border-left: 5px solid #d4af37; box-shadow: 1px 1px 3px rgba(0,0,0,0.1); }
    .alerta-roja { color: #ffffff; background-color: #ff4b4b; padding: 10px; border-radius: 5px; font-weight: bold; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE BASES DE DATOS
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}
if 'cat_h' not in st.session_state: st.session_state.cat_h = ["Varios"]
if 'cat_p' not in st.session_state: st.session_state.cat_p = ["General"]
if 'cat_c' not in st.session_state: st.session_state.cat_c = ["Cliente General"]

# 3. BARRA LATERAL (CONTROL Y CATÁLOGOS)
with st.sidebar:
    st.markdown("<h1 style='color: #d4af37; text-align: center;'>🛡️ EMI</h1>", unsafe_allow_html=True)
    nombre_empresa = st.text_input("🏢 NOMBRE DE LA EMPRESA", "Mi Negocio")
    sede_act = st.selectbox("📍 SEDE EN OPERACIÓN", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    with st.expander("⚙️ GESTIÓN DE CATÁLOGOS"):
        st.write("Registra nombres aquí para usarlos en las pestañas:")
        tipo_cat = st.selectbox("Categoría", ["Hormiga", "Proveedor", "Cobro (Cliente)"])
        n_cat = st.text_input("Nuevo Nombre")
        if st.button("Añadir a la lista"):
            if n_cat:
                if tipo_cat == "Hormiga": st.session_state.cat_h.append(n_cat)
                elif tipo_cat == "Proveedor": st.session_state.cat_p.append(n_cat)
                else: st.session_state.cat_c.append(n_cat)
                st.rerun()

    st.divider()
    st.session_state.saldos["Banco"] = st.number_input("🏦 Saldo Banco", value=float(st.session_state.saldos["Banco"]))
    st.session_state.saldos["Caja Chica"] = st.number_input("💵 Caja Chica", value=float(st.session_state.saldos["Caja Chica"]))
    
    # BALANCE CONSOLIDADO
    df_all = pd.DataFrame(st.session_state.db)
    def calc_global():
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if df_all.empty: return base
        ing = df_all[df_all['Estado'] == 'Ingreso']['Monto'].sum()
        egr = df_all[df_all['Estado'] == 'Pagado']['Monto'].sum()
        return base + ing - egr

    st.metric("💰 BALANCE GENERAL (GLOBAL)", f"$ {round(calc_global(), 2)}")

# 4. TABS
t_v, t_f, t_h, t_p, t_c, t_rep = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTES"])

# --- TAB VENTAS ---
with t_v:
    st.subheader(f"Registro de Ingresos: {sede_act}")
    with st.form("fv", clear_on_submit=True):
        c1, c2 = st.columns(2)
        fv, mv = c1.date_input("Fecha"), c2.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Guardar Venta"):
            st.session_state.db.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", "Monto": mv, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()
    if not df_all.empty:
        st.write("### Historial de esta sede")
        st.dataframe(df_all[(df_all['Tipo'] == 'Venta') & (df_all['Sede'] == sede_act)], use_container_width=True)

# --- TAB GASTOS FIJOS (CON ALERTAS) ---
with t_f:
    st.subheader("🏢 Gestión de Fijos con Vencimiento")
    with st.form("ff"):
        f1, f2, f3 = st.columns(3)
        f_con = f1.text_input("Concepto (Arriendo, etc.)")
        f_mon = f2.number_input("Monto")
        f_ven = f3.date_input("Fecha Vencimiento")
        if st.form_submit_button("Programar"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": f_ven, "Tipo": "Fijo", "Concepto": f_con, "Monto": f_mon, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Fijo" and m['Estado'] == "Pendiente":
            dias = (m['Vencimiento'] - date.today()).days
            clase = "alerta-roja" if dias <= 1 else ""
            st.markdown(f"<div class='{clase}'>🏢 {m['Concepto']} | ${m['Monto']} | Vence en {dias} días</div>", unsafe_allow_html=True)
            if st.button(f"PAGAR {m['Concepto']} {i}"): m['Estado'] = "Pagado"; st.rerun()

# --- TAB PROVEEDORES ---
with t_p:
    st.subheader("🚛 Cuentas por Pagar")
    with st.form("fp"):
        p1, p2, p3 = st.columns(3)
        p_c = p1.selectbox("Proveedor", st.session_state.cat_p)
        p_m = p2.number_input("Monto")
        p_v = p3.date_input("Vencimiento")
        if st.form_submit_button("Guardar Factura"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": p_v, "Tipo": "Prov", "Concepto": p_c, "Monto": p_m, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    if not df_all.empty:
        total_p = df_all[(df_all['Tipo'] == 'Prov') & (df_all['Estado'] == 'Pendiente')]['Monto'].sum()
        st.metric("DEUDA TOTAL A PROVEEDORES", f"$ {total_p}")

# --- TAB COBROS ---
with t_c:
    st.subheader("📞 Cuentas por Cobrar (Clientes)")
    with st.form("fc"):
        cc1, cc2 = st.columns(2)
        c_cli = cc1.selectbox("Cliente", st.session_state.cat_c)
        c_mon = cc2.number_input("Monto Crédito")
        if st.form_submit_button("Registrar Cobro Pendiente"):
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Cobro", "Concepto": c_cli, "Monto": c_mon, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()

# --- TAB REPORTES (INTELIGENCIA DE NEGOCIO) ---
with t_rep:
    st.header("📈 Análisis Visual Estratégico")
    if not df_all.empty:
        df_r = pd.DataFrame(st.session_state.db)
        
        c_rep1, c_rep2 = st.columns(2)
        rep = c_rep1.selectbox("Seleccione Reporte", ["Ingresos por Sede", "Ranking de Proveedores", "Ranking de Cobros"])
        
        if rep == "Ingresos por Sede":
            res = df_r[df_r['Tipo'] == 'Venta'].groupby("Sede")["Monto"].sum().reset_index()
            st.plotly_chart(px.bar(res, x="Sede", y="Monto", color="Monto", title="¿Qué sede genera más ingresos?"), use_container_width=True)
        
        elif rep == "Ranking de Proveedores":
            res_p = df_r[df_r['Tipo'] == 'Prov'].groupby("Concepto")["Monto"].sum().reset_index()
            st.plotly_chart(px.bar(res_p, x="Concepto", y="Monto", title="Deuda Acumulada por Proveedor", color_discrete_sequence=['#d4af37']), use_container_width=True)

        elif rep == "Ranking de Cobros":
            res_c = df_r[df_r['Tipo'] == 'Cobro'].groupby("Concepto")["Monto"].sum().reset_index()
            st.plotly_chart(px.pie(res_c, names="Concepto", values="Monto", title="Distribución de Cuentas por Cobrar"), use_container_width=True)
