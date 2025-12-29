import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# 1. CONFIGURACIÓN Y ESTILO (Optimizado para Celulares)
st.set_page_config(page_title="EMI MASTER V29.1", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #ffffff !important; font-size: 14px; }
    [data-testid="stSidebar"] input { color: #1c2e4a !important; background-color: #ffffff !important; }
    [data-testid="stMetricValue"] {
        background-color: #d4af37 !important;
        color: #1c2e4a !important;
        padding: 10px; border-radius: 10px; font-weight: bold; font-size: 22px !important; text-align: center;
    }
    .resaltado-suma {
        background-color: #f1f3f5; border-left: 5px solid #1c2e4a;
        padding: 15px; margin-bottom: 20px; color: #1c2e4a; font-weight: bold; font-size: 18px; border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}
if 'nombres_fijos' not in st.session_state: st.session_state.nombres_fijos = set()
if 'nombres_hormiga' not in st.session_state: st.session_state.nombres_hormiga = set()
if 'nombres_prov' not in st.session_state: st.session_state.nombres_prov = set()
if 'nombres_cobro' not in st.session_state: st.session_state.nombres_cobro = set()

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("<h1 style='color: #d4af37; text-align: center;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    nombre_local = st.text_input("🏢 EMPRESA", "Mi Negocio")
    sede_act = st.selectbox("📍 SEDE ACTUAL", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    st.session_state.saldos["Banco"] = st.number_input("🏦 BANCO", value=float(st.session_state.saldos["Banco"]))
    st.session_state.saldos["Caja Chica"] = st.number_input("💵 CAJA CHICA", value=float(st.session_state.saldos["Caja Chica"]))
    
    def calc_global():
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if not st.session_state.db: return base
        df_all = pd.DataFrame(st.session_state.db)
        ing = df_all[df_all['Estado'].isin(['Ingreso', 'Pagado_Cobro'])]['Monto'].sum()
        egr = df_all[df_all['Estado'] == 'Pagado']['Monto'].sum()
        return base + ing - egr

    st.metric("BALANCE GENERAL", f"$ {round(calc_global(), 2)}")

# 4. TABS (Ventas, Fijos, Hormiga, Prov, Cobros, Reportes)
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTES"])

# --- TAB VENTAS ---
with tabs[0]:
    with st.form("fv", clear_on_submit=True):
        c1, c2 = st.columns(2); fv, mv = c1.date_input("Fecha", date.today()), c2.number_input("Monto")
        if st.form_submit_button("Guardar Venta"):
            st.session_state.db.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", "Monto": mv, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()
    df_full = pd.DataFrame(st.session_state.db) if st.session_state.db else pd.DataFrame()
    if not df_full.empty:
        data = df_full[(df_full['Tipo'] == 'Venta') & (df_full['Sede'] == sede_act)]
        st.markdown(f"<div class='resaltado-suma'>Ventas en {sede_act}: $ {data['Monto'].sum() if not data.empty else 0}</div>", unsafe_allow_html=True)
        for i, row in data.iterrows():
            c1, c2 = st.columns([5, 1]); c1.write(f"📅 {row['Fecha']} - ${row['Monto']}"); 
            if c2.button("🗑️", key=f"dv_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB FIJOS ---
with tabs[1]:
    st.subheader("🏢 Gastos Fijos")
    with st.form("ff", clear_on_submit=True):
        c1 = st.selectbox("Concepto", ["Nuevo..."] + list(st.session_state.nombres_fijos))
        if c1 == "Nuevo...": c1 = st.text_input("Escribir Nuevo Gasto Fijo")
        m_f, v_f = st.number_input("Monto"), st.date_input("Vencimiento")
        if st.form_submit_button("Programar"):
            st.session_state.nombres_fijos.add(c1)
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": v_f, "Tipo": "Fijo", "Concepto": c1, "Monto": m_f, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    if not df_full.empty:
        df_f = df_full[(df_full['Tipo'] == 'Fijo') & (df_full['Sede'] == sede_act) & (df_full['Estado'] == 'Pendiente')]
        st.markdown(f"<div class='resaltado-suma'>Total Fijos Pendientes: $ {df_f['Monto'].sum()}</div>", unsafe_allow_html=True)
        for i, row in df_f.iterrows():
            c1, c2, c3 = st.columns([4, 1, 1]); c1.info(f"{row['Concepto']} - ${row['Monto']}");
            if c2.button("✅", key=f"pf_{i}"): st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()
            if c3.button("🗑️", key=f"df_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB HORMIGA ---
with tabs[2]:
    st.subheader("🐜 Gastos Hormiga")
    with st.form("fh", clear_on_submit=True):
        c1 = st.selectbox("Concepto", ["Nuevo..."] + list(st.session_state.nombres_hormiga))
        if c1 == "Nuevo...": c1 = st.text_input("Escribir Concepto Hormiga")
        m_h = st.number_input("Monto")
        if st.form_submit_button("Registrar"):
            st.session_state.nombres_hormiga.add(c1)
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Hormiga", "Concepto": c1, "Monto": m_h, "Sede": sede_act, "Estado": "Pagado"})
            st.rerun()
    if not df_full.empty:
        df_h = df_full[(df_full['Tipo'] == 'Hormiga') & (df_full['Sede'] == sede_act)]
        st.markdown(f"<div class='resaltado-suma'>Total Gasto Hormiga: $ {df_h['Monto'].sum()}</div>", unsafe_allow_html=True)
        for i, row in df_h.iterrows():
            c1, c2 = st.columns([5, 1]); c1.write(f"🐜 {row['Concepto']} - ${row['Monto']}");
            if c2.button("🗑️", key=f"dh_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB PROVEEDORES ---
with tabs[3]:
    with st.form("fp", clear_on_submit=True):
        p_c = st.selectbox("Proveedor", ["Nuevo..."] + list(st.session_state.nombres_prov))
        if p_c == "Nuevo...": p_c = st.text_input("Escribir Nombre Proveedor")
        p_m, p_v = st.number_input("Monto"), st.date_input("Vencimiento")
        if st.form_submit_button("Registrar"):
            st.session_state.nombres_prov.add(p_c)
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": p_v, "Tipo": "Prov", "Concepto": p_c, "Monto": p_m, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    if not df_full.empty:
        df_p = df_full[(df_full['Tipo'] == 'Prov') & (df_full['Sede'] == sede_act) & (df_full['Estado'] == 'Pendiente')]
        st.markdown(f"<div class='resaltado-suma'>Deuda Prov Pendiente: $ {df_p['Monto'].sum()}</div>", unsafe_allow_html=True)
        for i, row in df_p.iterrows():
            c1, c2, c3 = st.columns([4, 1, 1]); c1.warning(f"🚛 {row['Concepto']} - ${row['Monto']}")
            if c2.button("✅", key=f"pp_{i}"): st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()
            if c3.button("🗑️", key=f"dp_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB COBROS ---
with tabs[4]:
    with st.form("fc", clear_on_submit=True):
        c_c = st.selectbox("Cliente", ["Nuevo..."] + list(st.session_state.nombres_cobro))
        if c_c == "Nuevo...": c_c = st.text_input("Escribir Nombre Cliente")
        c_m = st.number_input("Monto")
        if st.form_submit_button("Registrar"):
            st.session_state.nombres_cobro.add(c_c)
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Cobro", "Concepto": c_c, "Monto": c_m, "Sede": sede_act, "Estado": "Por Cobrar"})
            st.rerun()
    if not df_full.empty:
        df_c = df_full[(df_full['Tipo'] == 'Cobro') & (df_full['Sede'] == sede_act) & (df_full['Estado'] == 'Por Cobrar')]
        st.markdown(f"<div class='resaltado-suma'>Total por Cobrar: $ {df_c['Monto'].sum()}</div>", unsafe_allow_html=True)
        for i, row in df_c.iterrows():
            c1, c2, c3 = st.columns([4, 1, 1]); c1.success(f"📞 {row['Concepto']} - ${row['Monto']}")
            if c2.button("💰", key=f"pc_{i}"): st.session_state.db[i]['Estado'] = 'Pagado_Cobro'; st.rerun()
            if c3.button("🗑️", key=f"dc_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB REPORTES ---
with tabs[5]:
    if not df_full.empty:
        res = df_full[df_full['Tipo']=='Venta'].groupby("Sede")["Monto"].sum().reset_index()
        fig = px.bar(res, x="Sede", y="Monto", title=f"Ventas por Sede - {nombre_local}", color="Sede")
        st.plotly_chart(fig, use_container_width=True)
