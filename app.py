import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta

# 1. CONFIGURACIÓN Y ESTILO DE ALTO CONTRASTE
st.set_page_config(page_title="ECU-STRAT VISION V25", layout="wide")

st.markdown("""
    <style>
    /* Estilo Barra Lateral - Letras Blancas y Legibles */
    [data-testid="stSidebar"] { background-color: #1c2e4a; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    [data-testid="stSidebar"] h1 { color: #d4af37 !important; font-size: 24px !important; }
    
    /* Alertas y Diseño */
    .alerta-vencido { background-color: #ff4b4b; color: white; padding: 12px; border-radius: 8px; font-weight: bold; margin-bottom: 10px; border: 2px solid #ffffff; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #d4af37; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE DATOS (CATÁLOGOS Y DB)
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}
if 'cat_h' not in st.session_state: st.session_state.cat_h = ["Varios", "Suministros"]
if 'cat_p' not in st.session_state: st.session_state.cat_p = ["Distribuidor Principal"]
if 'cat_c' not in st.session_state: st.session_state.cat_c = ["Cliente General"]

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("<h1>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    nombre_empresa = st.text_input("NOMBRE EMPRESA", "Mi Negocio")
    sede_act = st.selectbox("📍 SEDE ACTUAL", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    with st.expander("⚙️ CONFIGURAR CATÁLOGOS"):
        t_cat = st.selectbox("Añadir a:", ["Hormiga", "Proveedor", "Cobro"])
        n_item = st.text_input("Nombre Nuevo")
        if st.button("➕ Guardar"):
            if n_item:
                if t_cat == "Hormiga": st.session_state.cat_h.append(n_item)
                elif t_cat == "Proveedor": st.session_state.cat_p.append(n_item)
                else: st.session_state.cat_c.append(n_item)
                st.rerun()

    st.divider()
    st.session_state.saldos["Banco"] = st.number_input("💵 BANCO ($)", value=float(st.session_state.saldos["Banco"]))
    st.session_state.saldos["Caja Chica"] = st.number_input("🪙 CAJA CHICA ($)", value=float(st.session_state.saldos["Caja Chica"]))
    
    def calc_balance():
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if not st.session_state.db: return base
        df_tmp = pd.DataFrame(st.session_state.db)
        ing = df_tmp[df_tmp['Estado'] == 'Ingreso']['Monto'].sum()
        egr = df_tmp[df_tmp['Estado'] == 'Pagado']['Monto'].sum()
        return base + ing - egr

    st.metric("💰 BALANCE GENERAL GLOBAL", f"$ {round(calc_balance(), 2)}")

# 4. TABS
t_v, t_f, t_h, t_p, t_c, t_rep = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTES"])

# --- TAB VENTAS ---
with t_v:
    with st.form("fv", clear_on_submit=True):
        c1, c2 = st.columns(2)
        f_v, m_v = c1.date_input("Fecha Venta", date.today()), c2.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Guardar Venta"):
            st.session_state.db.append({"Fecha": f_v, "Tipo": "Venta", "Concepto": "Ingreso", "Monto": m_v, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()
    
    if st.session_state.db:
        df = pd.DataFrame(st.session_state.db)
        df_v = df[(df['Tipo'] == 'Venta') & (df['Sede'] == sede_act)]
        if not df_v.empty:
            st.write("### Historial de Ventas")
            st.dataframe(df_v, use_container_width=True)
            for i, row in df_v.iterrows():
                if st.button(f"Eliminar Venta {i}", key=f"del_v_{i}"):
                    st.session_state.db.pop(i); st.rerun()

# --- TAB FIJOS (SUMATORIA Y VENCIMIENTO) ---
with t_f:
    st.subheader("🏢 Registro de Gastos Fijos")
    with st.form("ff"):
        f1, f2, f3 = st.columns(3)
        c_f = f1.text_input("Concepto (Arriendo, Luz...)")
        m_f = f2.number_input("Monto", min_value=0.0)
        v_f = f3.date_input("Vencimiento")
        if st.form_submit_button("Programar"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": v_f, "Tipo": "Fijo", "Concepto": c_f, "Monto": m_f, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    if st.session_state.db:
        df_f = pd.DataFrame(st.session_state.db)
        f_p = df_f[(df_f['Tipo'] == 'Fijo') & (df_f['Estado'] == 'Pendiente')]
        st.metric("TOTAL FIJOS POR PAGAR", f"$ {f_p['Monto'].sum()}")
        for i, row in f_p.iterrows():
            dias = (row['Vencimiento'] - date.today()).days
            clase = "alerta-vencido" if dias <= 1 else ""
            st.markdown(f"<div class='{clase}'>🏢 {row['Concepto']} - ${row['Monto']} (Vence en {dias} días)</div>", unsafe_allow_html=True)
            if st.button(f"PAGAR {row['Concepto']} ##{i}", key=f"pay_f_{i}"):
                st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()

# --- TAB HORMIGA (SUMATORIA) ---
with t_h:
    with st.form("fh"):
        h1, h2 = st.columns(2)
        c_h = h1.selectbox("Concepto", st.session_state.cat_h)
        m_h = h2.number_input("Monto Hormiga ($)", min_value=0.0)
        if st.form_submit_button("Registrar"):
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Hormiga", "Concepto": c_h, "Monto": m_h, "Sede": sede_act, "Estado": "Pagado"})
            st.rerun()
    if st.session_state.db:
        df_h = pd.DataFrame(st.session_state.db)
        list_h = df_h[df_h['Tipo'] == 'Hormiga']
        st.metric("TOTAL GASTO HORMIGA", f"$ {list_h['Monto'].sum()}")
        st.dataframe(list_h, use_container_width=True)

# --- TAB PROVEEDORES ---
with t_p:
    st.subheader("🚛 Deudas a Proveedores")
    with st.form("fp"):
        p1, p2, p3 = st.columns(3)
        p_c = p1.selectbox("Proveedor", st.session_state.cat_p)
        p_m = p2.number_input("Monto Deuda")
        p_v = p3.date_input("Vencimiento Pago")
        if st.form_submit_button("Guardar"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": p_v, "Tipo": "Prov", "Concepto": p_c, "Monto": p_m, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    if st.session_state.db:
        df_p = pd.DataFrame(st.session_state.db)
        list_p = df_p[(df_p['Tipo'] == 'Prov') & (df_p['Estado'] == 'Pendiente')]
        st.metric("TOTAL DEUDA PROVEEDORES", f"$ {list_p['Monto'].sum()}")
        for i, row in list_p.iterrows():
            dias_p = (row['Vencimiento'] - date.today()).days
            if dias_p <= 1: st.markdown(f"<div class='alerta-vencido'>⚠️ URGENTE: {row['Concepto']} vence en {dias_p} días</div>", unsafe_allow_html=True)
            if st.button(f"Marcar como PAGADO: {row['Concepto']} ({i})", key=f"pay_p_{i}"):
                st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()

# --- TAB REPORTES (COMPARATIVA Y RANKINGS) ---
with t_rep:
    st.header("📈 Centro de Inteligencia")
    if st.session_state.db:
        df_r = pd.DataFrame(st.session_state.db)
        col_r1, col_r2 = st.columns(2)
        tipo_rep = col_r1.selectbox("Reporte", ["Comparativa de Sedes", "Ranking Proveedores", "Ranking Hormiga"])
        tipo_graf = col_r2.radio("Visualización", ["Barras", "Pastel", "Lineal"], horizontal=True)

        if tipo_rep == "Comparativa de Sedes":
            res = df_r[df_r['Tipo'] == 'Venta'].groupby("Sede")["Monto"].sum().reset_index()
            fig = px.bar(res, x="Sede", y="Monto", color="Monto", color_continuous_scale='Viridis')
            if tipo_graf == "Pastel": fig = px.pie(res, names="Sede", values="Monto")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ingresa datos para activar los reportes.")
