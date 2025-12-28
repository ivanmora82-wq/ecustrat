import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import io

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT MASTER V20.1", layout="wide")

# 2. INICIALIZACIÓN DE DATOS
if 'db' not in st.session_state: st.session_state.db = []
if 'saldos' not in st.session_state: st.session_state.saldos = {"Banco": 0.0, "Caja Chica": 0.0}
# Listas maestras para evitar errores de escritura
if 'cat_h' not in st.session_state: st.session_state.cat_h = ["Taxi", "Almuerzo", "Limpieza"]
if 'cat_p' not in st.session_state: st.session_state.cat_p = ["General", "Distribuidora Principal"]
if 'cat_c' not in st.session_state: st.session_state.cat_c = ["Consumidor Final"]

# 3. BARRA LATERAL (ADMINISTRACIÓN Y CATÁLOGOS)
with st.sidebar:
    st.title("🛡️ ECU-STRAT MASTER")
    sede_act = st.selectbox("📍 Sede Actual", ["Matriz", "Sucursal 1", "Sucursal 2"])
    
    st.divider()
    st.subheader("💰 Saldos Iniciales")
    st.session_state.saldos["Banco"] = st.number_input("Banco ($)", value=float(st.session_state.saldos["Banco"]))
    st.session_state.saldos["Caja Chica"] = st.number_input("Caja Chica ($)", value=float(st.session_state.saldos["Caja Chica"]))
    
    st.divider()
    # GESTIÓN DE CATÁLOGOS (Escribir una sola vez)
    st.subheader("⚙️ Configurar Nombres")
    with st.expander("➕ Añadir a Catálogos"):
        tipo_cat = st.selectbox("Categoría", ["Gasto Hormiga", "Proveedor", "Cliente"])
        nuevo_nombre = st.text_input("Nombre nuevo")
        if st.button("Guardar Nombre"):
            if nuevo_nombre:
                if tipo_cat == "Gasto Hormiga": st.session_state.cat_h.append(nuevo_nombre)
                elif tipo_cat == "Proveedor": st.session_state.cat_p.append(nuevo_nombre)
                elif tipo_cat == "Cliente": st.session_state.cat_c.append(nuevo_nombre)
                st.success(f"Añadido: {nuevo_nombre}")
                st.rerun()

    # CÁLCULO DE BALANCE
    def obtener_balance(sede_nombre):
        base = st.session_state.saldos["Banco"] + st.session_state.saldos["Caja Chica"]
        if not st.session_state.db: return base
        df_bal = pd.DataFrame(st.session_state.db)
        filtro = df_bal if sede_nombre == "TOTAL" else df_bal[df_bal['Sede'] == sede_nombre]
        if filtro.empty: return base
        ingresos = filtro[filtro['Estado'] == 'Ingreso']['Monto'].sum()
        egresos = filtro[filtro['Estado'] == 'Pagado']['Monto'].sum()
        return base + ingresos - egresos

    st.divider()
    st.metric("BALANCE CONSOLIDADO", f"$ {round(obtener_balance('TOTAL'), 2)}")

# 4. TABS
t_v, t_f, t_h, t_p, t_c, t_rep = st.tabs(["💰 Ventas", "🏢 Fijos", "🐜 Hormiga", "🚛 Prov", "📞 Cobros", "📈 REPORTES"])

# --- TAB VENTAS ---
with t_v:
    st.subheader("Registro de Ventas")
    with st.form("fv", clear_on_submit=True):
        c1, c2 = st.columns(2)
        fv, mv = c1.date_input("Fecha", date.today()), c2.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Guardar"):
            st.session_state.db.append({"Fecha": fv, "Tipo": "Venta", "Concepto": "Venta", "Monto": mv, "Sede": sede_act, "Estado": "Ingreso"})
            st.rerun()

# --- TAB HORMIGA (USANDO CATÁLOGO) ---
with t_h:
    st.subheader("Gastos Hormiga")
    with st.form("fh"):
        # EL CLIENTE ELIGE, NO ESCRIBE
        h_c = st.selectbox("Seleccione Concepto", st.session_state.cat_h)
        h_m = st.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Registrar"):
            st.session_state.db.append({"Fecha": date.today(), "Tipo": "Hormiga", "Concepto": h_c, "Monto": h_m, "Sede": sede_act, "Estado": "Pagado"})
            st.rerun()

# --- TAB PROVEEDORES (USANDO CATÁLOGO) ---
with t_p:
    st.subheader("Cuentas por Pagar")
    with st.form("fp"):
        p_c = st.selectbox("Seleccione Proveedor", st.session_state.cat_p)
        p_m = st.number_input("Monto", min_value=0.0)
        p_v = st.date_input("Vencimiento")
        if st.form_submit_button("Guardar Deuda"):
            st.session_state.db.append({"Fecha": date.today(), "Vencimiento": p_v, "Tipo": "Prov", "Concepto": p_c, "Monto": p_m, "Sede": sede_act, "Estado": "Pendiente"})
            st.rerun()
    # Listado de deudas
    for i, m in enumerate(st.session_state.db):
        if m['Tipo'] == "Prov" and m['Estado'] == "Pendiente":
            st.info(f"🚛 {m['Concepto']} - ${m['Monto']} (Vence: {m['Vencimiento']})")
            if st.button(f"Pagar Deuda {i}"): m['Estado'] = "Pagado"; st.rerun()

# --- TAB REPORTES ---
with t_rep:
    st.header("📊 Inteligencia de Negocio")
    if st.session_state.db:
        df_rep = pd.DataFrame(st.session_state.db)
        op = st.selectbox("Análisis", ["Ranking Proveedores", "Comparativa Sedes"])
        if op == "Ranking Proveedores":
            res_p = df_rep[df_rep['Tipo'] == 'Prov'].groupby("Concepto")["Monto"].sum().reset_index()
            st.plotly_chart(px.bar(res_p, x="Concepto", y="Monto", title="¿A quién se paga más?"))
