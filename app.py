import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import io

# 1. CONFIGURACIÓN Y ESTILO (Contraste y Botones Alineados)
st.set_page_config(page_title="ECU-STRAT MASTER V27.1", layout="wide")

st.markdown("""
    <style>
    /* Barra Lateral: Etiquetas blancas, inputs con fondo claro y letra oscura */
    [data-testid="stSidebar"] { background-color: #1c2e4a; }
    [data-testid="stSidebar"] label { color: #ffffff !important; font-weight: bold; }
    [data-testid="stSidebar"] input { color: #000000 !important; background-color: #ffffff !important; }
    
    /* Botones pequeños y sobrios alineados */
    .stButton>button { padding: 1px 8px; font-size: 12px; border-radius: 4px; }
    .stMetric { border-left: 5px solid #d4af37 !important; background: white; padding: 10px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("<h1 style='color: #d4af37; text-align: center;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    nombre_local = st.text_input("🏢 NOMBRE DEL LOCAL", "Mi Empresa")
    sede_act = st.selectbox("📍 GESTIONAR SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    st.session_state.saldos["Banco"] = st.number_input("💵 BANCO ($)", value=float(st.session_state.saldos["Banco"]))
    st.session_state.saldos["Caja Chica"] = st.number_input("🪙 CAJA CHICA ($)", value=float(st.session_state.saldos["Caja Chica"]))
    
    # Cálculo Balance Global (Matriz + Sucursales)
    def calc_global():
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if not st.session_state.db: return base
        df_all = pd.DataFrame(st.session_state.db)
        ing = df_all[df_all['Estado'].isin(['Ingreso', 'Pagado_Cobro'])]['Monto'].sum()
        egr = df_all[df_all['Estado'] == 'Pagado']['Monto'].sum()
        return base + ing - egr

    st.metric("BALANCE GENERAL TOTAL", f"$ {round(calc_global(), 2)}")

# 4. TABS
t_v, t_f, t_h, t_p, t_c, t_rep = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTES"])

# --- TAB VENTAS ---
with t_v:
    with st.form("fv", clear_on_submit=True):
        c1, c2 = st.columns(2); fv, mv = c1.date_input("Fecha Venta", date.today()), c2.number_input("Monto")
        if st.form_submit_button("Guardar Venta"):
            st.session_state.db.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", "Monto": mv, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Venta" and m['Sede'] == sede_act:
            c1, c2, c3 = st.columns([6, 1, 1])
            c1.write(f"📅 {m['Fecha']} | Venta: **${m['Monto']}**")
            if c3.button("🗑️", key=f"de_v_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB FIJOS ---
with t_f:
    with st.form("ff", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        cf, mf, vf = c1.text_input("Gasto (Escribir)"), c2.number_input("Monto"), c3.date_input("Vencimiento")
        if st.form_submit_button("Programar Fijo"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": vf, "Tipo": "Fijo", "Concepto": cf, "Monto": mf, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Fijo" and m['Estado'] == "Pendiente":
            c1, c2, c3 = st.columns([6, 1, 1])
            c1.info(f"🏢 {m['Concepto']} - ${m['Monto']} (Vence: {m['Vencimiento']})")
            if c2.button("✅ Pagar", key=f"py_f_{i}"): st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()
            if c3.button("🗑️", key=f"de_f_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB HORMIGA (CORREGIDA VISIBILIDAD) ---
with t_h:
    st.subheader("🐜 Gastos Hormiga Diarios")
    with st.form("fh", clear_on_submit=True):
        c1, c2 = st.columns(2)
        hc, hm = c1.text_input("Concepto Gasto"), c2.number_input("Monto")
        if st.form_submit_button("Registrar Gasto"):
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Hormiga", "Concepto": hc, "Monto": hm, "Sede": sede_act, "Estado": "Pagado"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Hormiga" and m['Sede'] == sede_act:
            c1, c2, c3 = st.columns([6, 1, 1])
            c1.write(f"🐜 {m['Concepto']} - **${m['Monto']}**")
            if c3.button("🗑️", key=f"de_h_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB PROVEEDORES ---
with t_p:
    with st.form("fp", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        pc, pm, pv = c1.text_input("Proveedor (Escribir)"), c2.number_input("Monto"), c3.date_input("Vencimiento")
        if st.form_submit_button("Guardar Deuda"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": pv, "Tipo": "Prov", "Concepto": pc, "Monto": pm, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Prov" and m['Estado'] == "Pendiente":
            c1, c2, c3 = st.columns([6, 1, 1])
            c1.warning(f"🚛 {m['Concepto']} - ${m['Monto']} (Plazo: {m['Vencimiento']})")
            if c2.button("✅ Pagar", key=f"py_p_{i}"): st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()
            if c3.button("🗑️", key=f"de_p_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB COBROS ---
with t_c:
    with st.form("fc", clear_on_submit=True):
        c1, c2 = st.columns(2)
        cc, cm = c1.text_input("Cliente (Escribir)"), c2.number_input("Monto a Cobrar")
        if st.form_submit_button("Registrar Crédito"):
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Cobro", "Concepto": cc, "Monto": cm, "Sede": sede_act, "Estado": "Por Cobrar"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Cobro" and m['Estado'] == "Por Cobrar":
            c1, c2, c3 = st.columns([6, 1, 1])
            c1.success(f"📞 {m['Concepto']} debe: **${m['Monto']}**")
            if c2.button("💰 Cobrado", key=f"py_c_{i}"): st.session_state.db[i]['Estado'] = 'Pagado_Cobro'; st.rerun()
            if c3.button("🗑️", key=f"de_c_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB REPORTES ---
with t_rep:
    if st.session_state.db:
        df_r = pd.DataFrame(st.session_state.db)
        r1, r2 = st.columns(2)
        tipo_r = r1.selectbox("Analizar:", ["Sedes", "Hormiga", "Proveedores", "Cobros"])
        tipo_g = r2.radio("Gráfico:", ["Pastel", "Barras", "Lineal"], horizontal=True)
        
        # Lógica de filtrado
        if "Sede" in tipo_r: res = df_r[df_r['Tipo']=='Venta'].groupby("Sede")["Monto"].sum().reset_index()
        elif "Hormiga" in tipo_r: res = df_r[df_r['Tipo']=='Hormiga'].groupby("Concepto")["Monto"].sum().reset_index()
        elif "Prov" in tipo_r: res = df_r[df_r['Tipo']=='Prov'].groupby("Concepto")["Monto"].sum().reset_index()
        else: res = df_r[df_r['Tipo']=='Cobro'].groupby("Concepto")["Monto"].sum().reset_index()
        
        if not res.empty:
            if tipo_g == "Pastel": fig = px.pie(res, names=res.columns[0], values="Monto")
            elif tipo_g == "Barras": fig = px.bar(res, x=res.columns[0], y="Monto", color="Monto")
            else: fig = px.line(res, x=res.columns[0], y="Monto")
            st.plotly_chart(fig, use_container_width=True)
