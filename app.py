import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import io

# 1. CONFIGURACIÓN Y ESTILO REFINADO
st.set_page_config(page_title="ECU-STRAT V26", layout="wide")

st.markdown("""
    <style>
    /* Solo etiquetas de la barra lateral en blanco, inputs en negro */
    [data-testid="stSidebar"] label { color: #ffffff !important; font-weight: bold; }
    [data-testid="stSidebar"] input { color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #1c2e4a; }
    
    /* Diseño de tarjetas para filas */
    .fila-registro { border-bottom: 1px solid #ddd; padding: 10px; display: flex; align-items: center; justify-content: space-between; background: white; margin-bottom: 5px; border-radius: 5px; }
    .stMetric { border-left: 5px solid #d4af37 !important; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}
if 'cat_h' not in st.session_state: st.session_state.cat_h = ["Varios"]
if 'cat_p' not in st.session_state: st.session_state.cat_p = ["General"]
if 'cat_c' not in st.session_state: st.session_state.cat_c = ["Cliente General"]

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("<h1 style='color: #d4af37;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    empresa = st.text_input("NOMBRE EMPRESA", "Mi Negocio")
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    st.session_state.saldos["Banco"] = st.number_input("💵 BANCO", value=float(st.session_state.saldos["Banco"]))
    st.session_state.saldos["Caja Chica"] = st.number_input("🪙 CAJA CHICA", value=float(st.session_state.saldos["Caja Chica"]))
    
    def calc_global():
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if not st.session_state.db: return base
        df = pd.DataFrame(st.session_state.db)
        ing = df[df['Estado'] == 'Ingreso']['Monto'].sum()
        egr = df[df['Estado'] == 'Pagado']['Monto'].sum()
        return base + ing - egr

    st.metric("BALANCE GENERAL", f"$ {round(calc_global(), 2)}")
    
    # BOTÓN EXPORTAR EXCEL
    if st.session_state.db:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame(st.session_state.db).to_excel(writer, index=False, sheet_name='Registros')
        st.download_button(label="📥 Descargar Reporte Excel", data=output.getvalue(), file_name=f"Reporte_{empresa}.xlsx")

# 4. TABS
t_v, t_f, t_h, t_p, t_c, t_rep = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTE"])

# --- TAB VENTAS ---
with t_v:
    with st.form("fv", clear_on_submit=True):
        c1, c2 = st.columns(2); fv, mv = c1.date_input("Fecha"), c2.number_input("Monto")
        if st.form_submit_button("Guardar Venta"):
            st.session_state.db.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Ingreso", "Monto": mv, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Venta" and m['Sede'] == sede_act:
            col1, col2 = st.columns([5, 1])
            col1.write(f"📅 {m['Fecha']} | **Monto:** ${m['Monto']}")
            if col2.button("🗑️", key=f"del_v_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB FIJOS (CON SUMATORIA DINÁMICA) ---
with t_f:
    with st.form("ff"):
        c1, c2, c3 = st.columns(3)
        cf, mf, vf = c1.text_input("Gasto"), c2.number_input("Monto"), c3.date_input("Vence")
        if st.form_submit_button("Programar"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": vf, "Tipo": "Fijo", "Concepto": cf, "Monto": mf, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()

    df_f = pd.DataFrame(st.session_state.db) if st.session_state.db else pd.DataFrame()
    if not df_f.empty and 'Tipo' in df_f.columns:
        pend = df_f[(df_f['Tipo'] == 'Fijo') & (df_f['Estado'] == 'Pendiente')]
        st.metric("DEUDA EN FIJOS", f"$ {pend['Monto'].sum()}")
        for i, row in pend.iterrows():
            c1, c2, c3 = st.columns([4, 1, 1])
            c1.warning(f"🏢 {row['Concepto']} - ${row['Monto']} (Vence: {row['Vencimiento']})")
            if c2.button("PAGAR ✅", key=f"pay_f_{i}"): st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()
            if c3.button("🗑️", key=f"del_f_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB PROVEEDORES ---
with t_p:
    with st.form("fp"):
        c1, c2, c3 = st.columns(3)
        pc, pm, pv = c1.selectbox("Proveedor", st.session_state.cat_p), c2.number_input("Deuda"), c3.date_input("Vence Pago")
        if st.form_submit_button("Guardar"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": pv, "Tipo": "Prov", "Concepto": pc, "Monto": pm, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    df_p = pd.DataFrame(st.session_state.db) if st.session_state.db else pd.DataFrame()
    if not df_p.empty and 'Tipo' in df_p.columns:
        pp = df_p[(df_p['Tipo'] == 'Prov') & (df_p['Estado'] == 'Pendiente')]
        st.metric("SUMA DE DEUDAS", f"$ {pp['Monto'].sum()}")
        for i, row in pp.iterrows():
            c1, c2, c3 = st.columns([4, 1, 1])
            c1.info(f"🚛 {row['Concepto']} | ${row['Monto']} | Vence: {row['Vencimiento']}")
            if c2.button("PAGAR", key=f"pay_p_{i}"): st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()
            if c3.button("🗑️", key=f"del_p_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB REPORTES ---
with t_rep:
    if st.session_state.db:
        df_r = pd.DataFrame(st.session_state.db)
        tipo_graf = st.radio("Gráfico:", ["Barras", "Pastel", "Líneas"], horizontal=True)
        rep = st.selectbox("Análisis:", ["Sedes", "Hormiga", "Proveedores"])
        
        if rep == "Sedes": res = df_r[df_r['Tipo']=='Venta'].groupby("Sede")["Monto"].sum().reset_index()
        elif rep == "Hormiga": res = df_r[df_r['Tipo']=='Hormiga'].groupby("Concepto")["Monto"].sum().reset_index()
        else: res = df_r[df_r['Tipo']=='Prov'].groupby("Concepto")["Monto"].sum().reset_index()
        
        if not res.empty:
            if tipo_graf == "Barras": fig = px.bar(res, x=res.columns[0], y="Monto", color="Monto")
            elif tipo_graf == "Pastel": fig = px.pie(res, names=res.columns[0], values="Monto")
            else: fig = px.line(res, x=res.columns[0], y="Monto")
            st.plotly_chart(fig, use_container_width=True)
