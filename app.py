import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="ECU-STRAT MASTER V28", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a; }
    [data-testid="stSidebar"] label { color: #ffffff !important; font-weight: bold; }
    [data-testid="stSidebar"] input { color: #000000 !important; background-color: #ffffff !important; }
    .stMetric { border-left: 5px solid #d4af37 !important; background: #f8f9fa; padding: 10px; border-radius: 8px; }
    .resaltado-suma { font-size: 20px; font-weight: bold; color: #1c2e4a; background: #e9ecef; padding: 10px; border-radius: 5px; margin-bottom: 15px; border-bottom: 3px solid #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE MEMORIA Y CATÁLOGOS
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}
# Catálogos para evitar duplicidad
if 'nombres_fijos' not in st.session_state: st.session_state.nombres_fijos = set()
if 'nombres_hormiga' not in st.session_state: st.session_state.nombres_hormiga = set()
if 'nombres_prov' not in st.session_state: st.session_state.nombres_prov = set()
if 'nombres_cobro' not in st.session_state: st.session_state.nombres_cobro = set()

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("<h1 style='color: #d4af37; text-align: center;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    nombre_local = st.text_input("🏢 NOMBRE DEL LOCAL", "Mi Negocio")
    sede_act = st.selectbox("📍 GESTIONAR SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    st.session_state.saldos["Banco"] = st.number_input("💵 BANCO ($)", value=float(st.session_state.saldos["Banco"]))
    st.session_state.saldos["Caja Chica"] = st.number_input("🪙 CAJA CHICA ($)", value=float(st.session_state.saldos["Caja Chica"]))
    
    def calc_global():
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if not st.session_state.db: return base
        df_all = pd.DataFrame(st.session_state.db)
        # Ingresos: Ventas y Cobros recibidos
        ing = df_all[df_all['Estado'].isin(['Ingreso', 'Pagado_Cobro'])]['Monto'].sum()
        # Egresos: Fijos, Hormiga y Prov pagados
        egr = df_all[df_all['Estado'] == 'Pagado']['Monto'].sum()
        return base + ing - egr

    st.metric("BALANCE GENERAL (TODO EL GRUPO)", f"$ {round(calc_global(), 2)}")

# 4. TABS
t_v, t_f, t_h, t_p, t_c, t_rep = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTES"])

# FILTRO DE DATOS POR SEDE ACTUAL
df_full = pd.DataFrame(st.session_state.db) if st.session_state.db else pd.DataFrame()
def get_sede_data(tipo):
    if df_full.empty or tipo not in df_full['Tipo'].values: return pd.DataFrame()
    return df_full[(df_full['Tipo'] == tipo) & (df_full['Sede'] == sede_act)]

# --- TAB VENTAS ---
with t_v:
    with st.form("fv", clear_on_submit=True):
        c1, c2 = st.columns(2); fv, mv = c1.date_input("Fecha Venta", date.today()), c2.number_input("Monto")
        if st.form_submit_button("Guardar Venta"):
            st.session_state.db.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", "Monto": mv, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()
    
    data = get_sede_data("Venta")
    if not data.empty:
        st.markdown(f"<div class='resaltado-suma'>Suma Total de Ventas en {sede_act}: $ {data['Monto'].sum()}</div>", unsafe_allow_html=True)
        for i, row in data.iterrows():
            c1, c2, c3 = st.columns([6, 1, 1])
            c1.write(f"📅 {row['Fecha']} | Venta: **${row['Monto']}**")
            if c3.button("🗑️", key=f"del_v_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB FIJOS ---
with t_f:
    with st.form("ff", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        # Opción de elegir existente o escribir nuevo
        cf = c1.selectbox("Concepto (Existente)", ["Nuevo..."] + list(st.session_state.nombres_fijos))
        if cf == "Nuevo...": cf = c1.text_input("Escriba Nuevo Concepto")
        mf, vf = c2.number_input("Monto"), c3.date_input("Vencimiento")
        if st.form_submit_button("Programar Fijo"):
            st.session_state.nombres_fijos.add(cf)
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": vf, "Tipo": "Fijo", "Concepto": cf, "Monto": mf, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    data = get_sede_data("Fijo")
    if not data.empty:
        pend = data[data['Estado'] == 'Pendiente']
        st.markdown(f"<div class='resaltado-suma'>Total Fijos Pendientes ({sede_act}): $ {pend['Monto'].sum()}</div>", unsafe_allow_html=True)
        for i, row in data.iterrows():
            if row['Estado'] == 'Pendiente':
                c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
                c1.info(f"🏢 {row['Concepto']} - ${row['Monto']} (Vence: {row['Vencimiento']})")
                if c2.button("✅ Pagar", key=f"py_f_{i}"): st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()
                if c4.button("🗑️", key=f"de_f_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB HORMIGA ---
with t_h:
    with st.form("fh", clear_on_submit=True):
        c1, c2 = st.columns(2)
        hc = c1.selectbox("Gasto (Existente)", ["Nuevo..."] + list(st.session_state.nombres_hormiga))
        if hc == "Nuevo...": hc = c1.text_input("Escriba Concepto")
        hm = c2.number_input("Monto")
        if st.form_submit_button("Registrar"):
            st.session_state.nombres_hormiga.add(hc)
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Hormiga", "Concepto": hc, "Monto": hm, "Sede": sede_act, "Estado": "Pagado"})
            st.rerun()
    
    data = get_sede_data("Hormiga")
    if not data.empty:
        st.markdown(f"<div class='resaltado-suma'>Total Gasto Hormiga ({sede_act}): $ {data['Monto'].sum()}</div>", unsafe_allow_html=True)
        for i, row in data.iterrows():
            c1, c2, c3 = st.columns([6, 1, 1])
            c1.write(f"🐜 {row['Concepto']} - **${row['Monto']}**")
            if c3.button("🗑️", key=f"de_h_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB PROVEEDORES ---
with t_p:
    with st.form("fp", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        pc = c1.selectbox("Proveedor", ["Nuevo..."] + list(st.session_state.nombres_prov))
        if pc == "Nuevo...": pc = c1.text_input("Nombre Proveedor")
        pm, pv = c2.number_input("Monto"), c3.date_input("Vencimiento")
        if st.form_submit_button("Guardar"):
            st.session_state.nombres_prov.add(pc)
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": pv, "Tipo": "Prov", "Concepto": pc, "Monto": pm, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    
    data = get_sede_data("Prov")
    if not data.empty:
        pend = data[data['Estado'] == 'Pendiente']
        st.markdown(f"<div class='resaltado-suma'>Deuda Total Proveedores ({sede_act}): $ {pend['Monto'].sum()}</div>", unsafe_allow_html=True)
        for i, row in data.iterrows():
            if row['Estado'] == 'Pendiente':
                c1, c2, c3 = st.columns([6, 1, 1])
                c1.warning(f"🚛 {row['Concepto']} - ${row['Monto']} (Vence: {row['Vencimiento']})")
                if c2.button("✅ Pagar", key=f"py_p_{i}"): st.session_state.db[i]['Estado'] = 'Pagado'; st.rerun()
                if c3.button("🗑️", key=f"de_p_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB COBROS ---
with t_c:
    with st.form("fc", clear_on_submit=True):
        c1, c2 = st.columns(2)
        cc = c1.selectbox("Cliente", ["Nuevo..."] + list(st.session_state.nombres_cobro))
        if cc == "Nuevo...": cc = c1.text_input("Nombre Cliente")
        cm = c2.number_input("Monto")
        if st.form_submit_button("Registrar"):
            st.session_state.nombres_cobro.add(cc)
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Cobro", "Concepto": cc, "Monto": cm, "Sede": sede_act, "Estado": "Por Cobrar"})
            st.rerun()
    
    data = get_sede_data("Cobro")
    if not data.empty:
        st.markdown(f"<div class='resaltado-suma'>Total Pendiente de Cobro ({sede_act}): $ {data[data['Estado']=='Por Cobrar']['Monto'].sum()}</div>", unsafe_allow_html=True)
        for i, row in data.iterrows():
            if row['Estado'] == 'Por Cobrar':
                c1, c2, c3 = st.columns([6, 1, 1])
                c1.success(f"📞 {row['Concepto']} debe: **${row['Monto']}**")
                if c2.button("💰 Recibir", key=f"py_c_{i}"): st.session_state.db[i]['Estado'] = 'Pagado_Cobro'; st.rerun()
                if c3.button("🗑️", key=f"de_c_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB REPORTES ---
with t_rep:
    if st.session_state.db:
        df_r = pd.DataFrame(st.session_state.db)
        r1, r2 = st.columns(2)
        analisis = r1.selectbox("¿Qué desea comparar?", ["Ventas entre Sedes", "Gastos Hormiga por Concepto", "Deudas por Proveedor", "Créditos por Cliente"])
        grafico = r2.radio("Tipo de Gráfico", ["Barras", "Pastel", "Lineal"], horizontal=True)
        
        # Colores de alto contraste
        color_map = px.colors.qualitative.Dark24
        
        if "Sedes" in analisis:
            res = df_r[df_r['Tipo']=='Venta'].groupby("Sede")["Monto"].sum().reset_index()
            titulo = f"Comparativa de Ingresos Totales por Sede: {nombre_local}"
        elif "Hormiga" in analisis:
            res = df_r[df_r['Tipo']=='Hormiga'].groupby("Concepto")["Monto"].sum().reset_index()
            titulo = f"Distribución de Gastos Hormiga por Categoría en {sede_act}"
        elif "Proveedor" in analisis:
            res = df_r[df_r['Tipo']=='Prov'].groupby("Concepto")["Monto"].sum().reset_index()
            titulo = "Ranking de Cuentas por Pagar a Proveedores"
        else:
            res = df_r[df_r['Tipo']=='Cobro'].groupby("Concepto")["Monto"].sum().reset_index()
            titulo = "Cartera de Clientes Pendientes por Cobrar"
        
        if not res.empty:
            if grafico == "Pastel": fig = px.pie(res, names=res.columns[0], values="Monto", title=titulo, color_discrete_sequence=color_map)
            elif grafico == "Barras": fig = px.bar(res, x=res.columns[0], y="Monto", title=titulo, color=res.columns[0], color_discrete_sequence=color_map)
            else: fig = px.line(res, x=res.columns[0], y="Monto", title=titulo, markers=True)
            st.plotly_chart(fig, use_container_width=True)
