import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta

# 1. CONFIGURACIÓN Y ESTILO DE ALTO CONTRASTE
st.set_page_config(page_title="ECU-STRAT VISION V24", layout="wide")

st.markdown("""
    <style>
    /* Estilo Barra Lateral - Letras Blancas */
    [data-testid="stSidebar"] { background-color: #1c2e4a; }
    [data-testid="stSidebar"] * { color: #ffffff !important; font-size: 16px !important; }
    [data-testid="stSidebar"] h1 { color: #d4af37 !important; font-size: 28px !important; }
    
    /* Alertas y Métricas */
    .alerta-vencido { background-color: #ff4b4b; color: white; padding: 10px; border-radius: 5px; font-weight: bold; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #d4af37; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}
if 'cat_h' not in st.session_state: st.session_state.cat_h = ["Varios", "Suministros"]
if 'cat_p' not in st.session_state: st.session_state.cat_p = ["Distribuidor A"]
if 'cat_c' not in st.session_state: st.session_state.cat_c = ["Cliente A"]

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("<h1>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    empresa = st.text_input("NOMBRE EMPRESA", "Mi Empresa")
    sede_act = st.selectbox("📍 SEDE ACTUAL", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    st.session_state.saldos["Banco"] = st.number_input("BANCO ($)", value=float(st.session_state.saldos["Banco"]))
    st.session_state.saldos["Caja Chica"] = st.number_input("CAJA CHICA ($)", value=float(st.session_state.saldos["Caja Chica"]))
    
    def calc_balance():
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if not st.session_state.db: return base
        df = pd.DataFrame(st.session_state.db)
        ing = df[df['Estado'] == 'Ingreso']['Monto'].sum()
        egr = df[df['Estado'] == 'Pagado']['Monto'].sum()
        return base + ing - egr

    st.metric("BALANCE REAL GLOBAL", f"$ {round(calc_balance(), 2)}")

# 4. TABS
t_v, t_f, t_h, t_p, t_c, t_rep = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTES"])

# FUNCIONES DE APOYO (Editar/Borrar)
def borrar_item(idx):
    st.session_state.db.pop(idx)
    st.rerun()

# --- TAB VENTAS ---
with t_v:
    with st.form("fv"):
        c1, c2 = st.columns(2)
        f_v, m_v = c1.date_input("Fecha"), c2.number_input("Monto Venta ($)", min_value=0.0)
        if st.form_submit_button("Registrar Venta"):
            st.session_state.db.append({"Fecha": f_v, "Tipo": "Venta", "Concepto": "Venta", "Monto": m_v, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()
    
    df_v = pd.DataFrame(st.session_state.db)
    if not df_v.empty:
        st.write("### Detalle de Ventas")
        ventas_sede = df_v[(df_v['Tipo'] == 'Venta') & (df_v['Sede'] == sede_act)]
        st.dataframe(ventas_sede, use_container_width=True)
        for i, row in ventas_sede.iterrows():
            if st.button(f"Borrar Venta {i}", key=f"bv_{i}"): borrar_item(i)

# --- TAB FIJOS (CON SUMATORIA) ---
with t_f:
    with st.form("ff"):
        f1, f2, f3 = st.columns(3)
        c_f, m_f, v_f = f1.text_input("Gasto (Luz, Arriendo...)"), f2.number_input("Monto"), f3.date_input("Vencimiento")
        if st.form_submit_button("Registrar Fijo"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": v_f, "Tipo": "Fijo", "Concepto": c_f, "Monto": m_f, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    df_f = pd.DataFrame(st.session_state.db)
    fijos_pend = df_f[(df_f['Tipo'] == 'Fijo') & (df_f['Estado'] == 'Pendiente')]
    st.metric("TOTAL FIJOS PENDIENTES", f"$ {fijos_pend['Monto'].sum()}")
    st.dataframe(fijos_pend, use_container_width=True)
    for i, row in fijos_pend.iterrows():
        if st.button(f"PAGAR 🔴", key=f"pf_{i}"):
            st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()

# --- TAB HORMIGA (DESPLEGADO) ---
with t_h:
    with st.form("fh"):
        h1, h2 = st.columns(2)
        c_h, m_h = h1.selectbox("Concepto", st.session_state.cat_h), h2.number_input("Monto Hormiga")
        if st.form_submit_button("Registrar Hormiga"):
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Hormiga", "Concepto": c_h, "Monto": m_h, "Sede": sede_act, "Estado": "Pagado"})
            st.rerun()
    
    df_h = pd.DataFrame(st.session_state.db)
    if not df_h.empty:
        hormigas = df_h[df_h['Tipo'] == 'Hormiga']
        st.metric("TOTAL GASTO HORMIGA", f"$ {hormigas['Monto'].sum()}")
        st.dataframe(hormigas, use_container_width=True)

# --- TAB PROVEEDORES (ALERTAS Y BOTÓN PAGO) ---
with t_p:
    with st.form("fp"):
        p1, p2, p3 = st.columns(3)
        p_c, p_m, p_v = p1.selectbox("Proveedor", st.session_state.cat_p), p2.number_input("Monto"), p3.date_input("Vence")
        if st.form_submit_button("Registrar Deuda"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": p_v, "Tipo": "Prov", "Concepto": p_c, "Monto": p_m, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    df_p = pd.DataFrame(st.session_state.db)
    prov_pend = df_p[(df_p['Tipo'] == 'Prov') & (df_p['Estado'] == 'Pendiente')]
    st.metric("TOTAL POR PAGAR PROV", f"$ {prov_pend['Monto'].sum()}")
    
    for i, row in prov_pend.iterrows():
        dias = (row['Vencimiento'] - date.today()).days
        if dias <= 1: st.markdown(f"<div class='alerta-vencido'>⚠️ ¡VENCE EN {dias} DÍAS! {row['Concepto']}</div>", unsafe_allow_html=True)
        c_a, c_b = st.columns([4, 1])
        c_a.write(f"🚛 {row['Concepto']} | ${row['Monto']} | Vence: {row['Vencimiento']}")
        if c_b.button("PAGAR ✅", key=f"ppv_{i}"):
            st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()

# --- TAB REPORTES (FULL FLEXIBILIDAD) ---
with t_rep:
    st.header("📊 Inteligencia y Gráficos")
    if st.session_state.db:
        df_r = pd.DataFrame(st.session_state.db)
        
        sel_rep = st.selectbox("¿Qué desea analizar?", ["Sedes", "Proveedores", "Gasto Hormiga", "Cobros"])
        sel_gra = st.radio("Tipo de Gráfico", ["Barras", "Lineal", "Pastel"], horizontal=True)
        
        # Filtro de datos según reporte
        if sel_rep == "Sedes": res = df_r[df_r['Tipo']=='Venta'].groupby("Sede")["Monto"].sum().reset_index()
        elif sel_rep == "Gasto Hormiga": res = df_r[df_r['Tipo']=='Hormiga'].groupby("Concepto")["Monto"].sum().reset_index()
        elif sel_rep == "Proveedores": res = df_r[df_r['Tipo']=='Prov'].groupby("Concepto")["Monto"].sum().reset_index()
        
        if sel_gra == "Barras": fig = px.bar(res, x=res.columns[0], y="Monto", color="Monto")
        elif sel_gra == "Pastel": fig = px.pie(res, names=res.columns[0], values="Monto")
        else: fig = px.line(res, x=res.columns[0], y="Monto")
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin datos para reportes.")
