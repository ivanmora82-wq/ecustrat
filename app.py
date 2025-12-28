import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta

# 1. CONFIGURACIÓN Y ESTILO (Contraste mejorado)
st.set_page_config(page_title="ECU-STRAT MASTER V22", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #ffffff !important; font-weight: bold; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 8px; border-left: 5px solid #d4af37; }
    .pago-urgente { color: #ff4b4b; font-weight: bold; border: 1px solid #ff4b4b; padding: 5px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}
if 'cat_h' not in st.session_state: st.session_state.cat_h = ["Taxi", "Almuerzo", "Limpieza"]
if 'cat_p' not in st.session_state: st.session_state.cat_p = ["Distribuidor 1", "Servicios"]
if 'cat_c' not in st.session_state: st.session_state.cat_c = ["Cliente Frecuente"]

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("<h1 style='color: #d4af37;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE ACTUAL", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    st.session_state.saldos["Banco"] = st.number_input("💵 Saldo Banco", value=float(st.session_state.saldos["Banco"]))
    st.session_state.saldos["Caja Chica"] = st.number_input("🪙 Caja Chica", value=float(st.session_state.saldos["Caja Chica"]))
    
    def calc_bal(sede_nombre):
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if not st.session_state.db: return base
        df_tmp = pd.DataFrame(st.session_state.db)
        f = df_tmp if sede_nombre == "TOTAL" else df_tmp[df_tmp['Sede'] == sede_nombre]
        if f.empty: return base
        return base + f[f['Estado'] == 'Ingreso']['Monto'].sum() - f[f['Estado'] == 'Pagado']['Monto'].sum()

    st.metric("BALANCE REAL TOTAL", f"$ {round(calc_bal('TOTAL'), 2)}")

# 4. TABS
t_v, t_f, t_h, t_p, t_c, t_rep = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📈 REPORTES"])

# --- TAB VENTAS (CON EDICIÓN) ---
with t_v:
    with st.form("fv", clear_on_submit=True):
        c1, c2 = st.columns(2)
        fv, mv = c1.date_input("Fecha"), c2.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Guardar Venta"):
            st.session_state.db.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", "Monto": mv, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()
    
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Venta" and m['Sede'] == sede_act:
            col1, col2, col3 = st.columns([4, 1, 1])
            col1.write(f"📅 {m['Fecha']} | ${m['Monto']}")
            if col3.button("🗑️", key=f"dv_{i}"): st.session_state.db.pop(i); st.rerun()

# --- TAB FIJOS (SEPARADOS) ---
with t_f:
    st.subheader("🏢 Gestión de Gastos Fijos")
    conceptos_fijos = ["Arriendo", "Luz", "Agua", "WiFi"]
    col_f = st.columns(len(conceptos_fijos) + 1)
    
    for i, cf in enumerate(conceptos_fijos):
        with col_f[i]:
            m_f = st.number_input(f"{cf} ($)", min_value=0.0, key=f"in_{cf}")
            if st.button(f"Programar {cf}"):
                st.session_state.db.append({"Fecha": date.today(), "Tipo": "Fijo", "Concepto": cf, "Monto": m_f, "Sede": sede_act, "Estado": "Pendiente"})
                st.rerun()
    
    with col_f[-1]:
        otro_c = st.text_input("Otro Concepto")
        otro_m = st.number_input("Monto Otro", min_value=0.0)
        if st.button("Programar Otro"):
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Fijo", "Concepto": otro_c, "Monto": otro_m, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()

    st.divider()
    st.write("### 🔔 Gastos Pendientes de Pago")
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Fijo" and m['Estado'] == "Pendiente":
            c1, c2 = st.columns([5, 1])
            c1.info(f"**{m['Concepto']}** pendiente por cobrar: ${m['Monto']}")
            if c2.button("PAGAR AHORA 🔴", key=f"p_f_{i}"):
                m['Estado'] = "Pagado"; st.rerun()

# --- TAB PROVEEDORES (ALERTAS Y SUMATORIA) ---
with t_p:
    st.subheader("🚛 Deudas con Proveedores")
    df_p = pd.DataFrame(st.session_state.db)
    if not df_p.empty:
        total_deuda = df_p[(df_p['Tipo'] == 'Prov') & (df_p['Estado'] == 'Pendiente')]['Monto'].sum()
        st.metric("TOTAL DEUDA PENDIENTE", f"$ {total_deuda}")

    with st.form("fp"):
        p1, p2, p3 = st.columns(3)
        p_c = p1.selectbox("Proveedor", st.session_state.cat_p)
        p_m = p2.number_input("Monto Deuda")
        p_v = p3.date_input("Vencimiento")
        if st.form_submit_button("Registrar Factura"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": p_v, "Tipo": "Prov", "Concepto": p_c, "Monto": p_m, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()

    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Prov" and m['Estado'] == "Pendiente":
            dias_rest = (m['Vencimiento'] - date.today()).days
            estilo = "pago-urgente" if dias_rest <= 1 else ""
            st.markdown(f"<div class='{estilo}'>🚛 {m['Concepto']} - ${m['Monto']} | Vence en: {dias_rest} días</div>", unsafe_allow_html=True)
            if st.button(f"Confirmar Pago {i}"): m['Estado'] = "Pagado"; st.rerun()

# --- TAB REPORTES (COLORES DINÁMICOS) ---
with t_rep:
    st.header("📈 Análisis Visual")
    if st.session_state.db:
        df_r = pd.DataFrame(st.session_state.db)
        df_v = df_r[df_r['Tipo'] == 'Venta']
        if not df_v.empty:
            res_sede = df_v.groupby("Sede")["Monto"].sum().reset_index()
            # Colores dinámicos: el más alto resalta
            fig = px.bar(res_sede, x="Sede", y="Monto", color="Monto", 
                         color_continuous_scale="Viridis", title="Ingresos por Sede")
            st.plotly_chart(fig, use_container_width=True)
