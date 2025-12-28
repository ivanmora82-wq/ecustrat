import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import io

# 1. CONFIGURACIÓN Y ESTILO (Corrección de Contraste e Iconos)
st.set_page_config(page_title="ECU-STRAT MASTER V27", layout="wide")

st.markdown("""
    <style>
    /* 1) BARRA LATERAL: Etiquetas blancas, fondo azul, INPUTS VISIBLES */
    [data-testid="stSidebar"] { background-color: #1c2e4a; }
    [data-testid="stSidebar"] label { color: #ffffff !important; font-weight: bold; }
    [data-testid="stSidebar"] input { color: #000000 !important; background-color: #ffffff !important; }
    
    /* 2) ICONOS Y TABLAS: Botones pequeños y alineados */
    .stButton>button { padding: 2px 10px; font-size: 14px; border-radius: 4px; }
    .btn-pagar { background-color: #28a745; color: white; }
    .btn-eliminar { background-color: #dc3545; color: white; }
    .stMetric { border-left: 5px solid #d4af37 !important; background: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}
if 'cat_h' not in st.session_state: st.session_state.cat_h = ["Varios"]
if 'cat_p' not in st.session_state: st.session_state.cat_p = ["General"]
if 'cat_c' not in st.session_state: st.session_state.cat_c = ["Cliente General"]

# 3. BARRA LATERAL (IDENTIDAD Y BALANCE GLOBAL)
with st.sidebar:
    st.markdown("<h1 style='color: #d4af37;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    # 7) Espacio para el nombre del local
    nombre_local = st.text_input("🏢 NOMBRE DEL LOCAL", "Mi Empresa")
    sede_act = st.selectbox("📍 GESTIONAR SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    st.session_state.saldos["Banco"] = st.number_input("💵 BANCO ($)", value=float(st.session_state.saldos["Banco"]))
    st.session_state.saldos["Caja Chica"] = st.number_input("🪙 CAJA CHICA ($)", value=float(st.session_state.saldos["Caja Chica"]))
    
    # Cálculo Balance Global (Matriz + Sucursales)
    def calc_global():
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if not st.session_state.db: return base
        df = pd.DataFrame(st.session_state.db)
        ing = df[df['Estado'] == 'Ingreso']['Monto'].sum()
        egr = df[df['Estado'] == 'Pagado']['Monto'].sum()
        return base + ing - egr

    st.metric("BALANCE GENERAL TOTAL", f"$ {round(calc_global(), 2)}")

# 4. TABS
t_v, t_f, t_h, t_p, t_c, t_rep = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTES"])

# --- TAB VENTAS ---
with t_v:
    with st.form("fv", clear_on_submit=True):
        c1, c2 = st.columns(2); fv, mv = c1.date_input("Fecha"), c2.number_input("Monto")
        if st.form_submit_button("Guardar Venta"):
            st.session_state.db.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", "Monto": mv, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Venta" and m['Sede'] == sede_act:
            c1, c2, c3 = st.columns([6, 1, 1])
            c1.write(f"📅 {m['Fecha']} | Venta: ${m['Monto']}")
            if c2.button("✏️", key=f"ed_v_{i}"): pass # Lógica editar
            if c3.button("🗑️", key=f"de_v_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB FIJOS (TABLA CON BOTONES LATERALES) ---
with t_f:
    st.subheader("🏢 Gastos Fijos (Arriendo, Servicios...)")
    with st.form("ff"):
        c1, c2, c3 = st.columns(3)
        cf, mf, vf = c1.text_input("Gasto"), c2.number_input("Monto"), c3.date_input("Vencimiento")
        if st.form_submit_button("Programar Fijo"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": vf, "Tipo": "Fijo", "Concepto": cf, "Monto": mf, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()

    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Fijo" and m['Estado'] == "Pendiente":
            c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
            c1.info(f"{m['Concepto']} - ${m['Monto']} (Vence: {m['Vencimiento']})")
            if c2.button("✅ Pagado", key=f"py_f_{i}"): st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()
            if c3.button("✏️", key=f"ed_f_{i}"): pass
            if c4.button("🗑️", key=f"de_f_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB PROVEEDORES ---
with t_p:
    with st.form("fp"):
        c1, c2, c3 = st.columns(3); pc, pm, pv = c1.selectbox("Proveedor", st.session_state.cat_p), c2.number_input("Monto"), c3.date_input("Vence")
        if st.form_submit_button("Guardar Factura"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": pv, "Tipo": "Prov", "Concepto": pc, "Monto": pm, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Prov" and m['Estado'] == "Pendiente":
            c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
            c1.warning(f"🚛 {m['Concepto']} - ${m['Monto']}")
            if c2.button("✅ Pagado", key=f"py_p_{i}"): st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()
            if c3.button("✏️", key=f"ed_p_{i}"): pass
            if c4.button("🗑️", key=f"de_p_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB COBROS (YA VISIBLE Y FUNCIONAL) ---
with t_c:
    st.subheader("📞 Cuentas por Cobrar")
    with st.form("fc"):
        c1, c2 = st.columns(2); cc, cm = c1.selectbox("Cliente", st.session_state.cat_c), c2.number_input("Monto a Cobrar")
        if st.form_submit_button("Registrar Cobro"):
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Cobro", "Concepto": cc, "Monto": cm, "Sede": sede_act, "Estado": "Por Cobrar"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Cobro" and m['Estado'] == "Por Cobrar":
            c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
            c1.success(f"📞 {m['Concepto']} debe: ${m['Monto']}")
            if c2.button("💰 Recibido", key=f"py_c_{i}"): st.session_state.db[i]['Estado'] = 'Ingreso'; st.rerun()
            if c3.button("✏️", key=f"ed_c_{i}"): pass
            if c4.button("🗑️", key=f"de_c_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB REPORTES ---
with t_rep:
    if st.session_state.db:
        df_r = pd.DataFrame(st.session_state.db)
        r1, r2 = st.columns(2)
        tipo_r = r1.selectbox("Analizar:", ["Ventas por Sede", "Gastos Hormiga", "Deuda Proveedores", "Cuentas por Cobrar"])
        tipo_g = r2.radio("Gráfico:", ["Pastel", "Barras", "Lineal"], horizontal=True)
        
        # Filtrado dinámico
        if "Sede" in tipo_r: res = df_r[df_r['Tipo']=='Venta'].groupby("Sede")["Monto"].sum().reset_index()
        elif "Hormiga" in tipo_r: res = df_r[df_r['Tipo']=='Hormiga'].groupby("Concepto")["Monto"].sum().reset_index()
        elif "Prov" in tipo_r: res = df_r[df_r['Tipo']=='Prov'].groupby("Concepto")["Monto"].sum().reset_index()
        else: res = df_r[df_r['Tipo']=='Cobro'].groupby("Concepto")["Monto"].sum().reset_index()
        
        if not res.empty:
            if tipo_g == "Pastel": fig = px.pie(res, names=res.columns[0], values="Monto")
            elif tipo_g == "Barras": fig = px.bar(res, x=res.columns[0], y="Monto", color="Monto")
            else: fig = px.line(res, x=res.columns[0], y="Monto")
            st.plotly_chart(fig, use_container_width=True)
