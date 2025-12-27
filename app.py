import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import io

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT PRO V12.1", layout="wide")

# 2. INICIALIZACIÓN DE DATOS
if 'caja_total' not in st.session_state: st.session_state.caja_total = 0.0
if 'db_movimientos' not in st.session_state: st.session_state.db_movimientos = []
if 'cat_hormiga' not in st.session_state: st.session_state.cat_hormiga = ["Taxi", "Almuerzo", "Limpieza", "Fundas"]
if 'cat_proveedores' not in st.session_state: st.session_state.cat_proveedores = ["General"]
if 'cat_clientes' not in st.session_state: st.session_state.cat_clientes = ["Consumidor Final"]

# --- FUNCIÓN PARA EXPORTAR A EXCEL ---
def generar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Movimientos')
    return output.getvalue()

# 3. BARRA LATERAL (ADMINISTRACIÓN Y CATÁLOGOS)
with st.sidebar:
    st.title("🛡️ ECU-STRAT PRO")
    empresa = st.text_input("Nombre de Empresa", "Mi Negocio")
    st.divider()
    st.metric("EFECTIVO EN CAJA", f"$ {round(st.session_state.caja_total, 2)}")
    st.divider()
    
    st.subheader("⚙️ Gestión de Catálogos")
    with st.expander("➕ Conceptos de Gasto"):
        n_h = st.text_input("Nuevo Gasto")
        if st.button("Añadir Gasto"):
            st.session_state.cat_hormiga.append(n_h)
            st.rerun()
    
    with st.expander("➕ Proveedores"):
        n_p = st.text_input("Nuevo Proveedor")
        if st.button("Añadir Proveedor"):
            st.session_state.cat_proveedores.append(n_p)
            st.rerun()

    with st.expander("➕ Clientes (Crédito)"):
        n_c = st.text_input("Nuevo Cliente")
        if st.button("Añadir Cliente"):
            st.session_state.cat_clientes.append(n_c)
            st.rerun()

    st.divider()
    if st.session_state.db_movimientos:
        df_export = pd.DataFrame(st.session_state.db_movimientos)
        st.download_button(label="📊 Descargar Reporte Excel", data=generar_excel(df_export), 
                           file_name=f"Reporte_{empresa}.xlsx", mime="application/vnd.ms-excel")

# 4. CUERPO PRINCIPAL (TABS)
t_caja, t_hormiga, t_prov, t_cobros, t_rep = st.tabs([
    "📅 Ventas/Caja", "🐜 Gastos Hormiga", "🚛 Proveedores", "📞 Cobros", "📈 REPORTES"
])

# --- TAB VENTAS/CAJA ---
with t_caja:
    st.subheader("💰 Registro de Ventas e Ingresos")
    with st.form("f_ventas", clear_on_submit=True):
        colv1, colv2 = st.columns(2)
        v_monto = colv1.number_input("Monto de Venta ($)", min_value=0.0)
        v_desc = colv2.text_input("Nota / Factura #", "Venta Diaria")
        if st.form_submit_button("Registrar Ingreso"):
            st.session_state.caja_total += v_monto
            st.session_state.db_movimientos.append({
                "Fecha": date.today(), "Tipo": "Venta", "Concepto": "Ingreso de Caja", "Monto": v_monto, "Nota": v_desc
            })
            st.rerun()

# --- TAB GASTOS HORMIGA ---
with t_hormiga:
    st.subheader("🐜 Gastos Diarios Menores")
    with st.form("h_form", clear_on_submit=True):
        colh1, colh2 = st.columns(2)
        con = colh1.selectbox("Concepto", st.session_state.cat_hormiga)
        mon = colh2.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Registrar Gasto"):
            st.session_state.caja_total -= mon
            st.session_state.db_movimientos.append({
                "Fecha": date.today(), "Tipo": "Gasto Hormiga", "Concepto": con, "Monto": mon, "Nota": ""
            })
            st.rerun()

# --- TAB PROVEEDORES ---
with t_prov:
    st.subheader("🚛 Cuentas por Pagar (Proveedores)")
    with st.form("p_form", clear_on_submit=True):
        p_sel = st.selectbox("Seleccione Proveedor", st.session_state.cat_proveedores)
        p_mon = st.number_input("Monto Factura ($)", min_value=0.0)
        p_fec = st.date_input("Fecha de Vencimiento")
        if st.form_submit_button("Registrar Deuda"):
            st.session_state.db_movimientos.append({
                "Fecha": p_fec, "Tipo": "Proveedor", "Concepto": p_sel, "Monto": p_mon, "Estado": "Pendiente", "Nota": "Deuda"
            })
            st.rerun()

# --- TAB COBROS ---
with t_cobros:
    st.subheader("📞 Cuentas por Cobrar (Créditos a Clientes)")
    with st.form("c_form", clear_on_submit=True):
        c_sel = st.selectbox("Seleccione Cliente", st.session_state.cat_clientes)
        c_mon = st.number_input("Monto a Cobrar ($)", min_value=0.0)
        c_fec = st.date_input("Fecha Promesa de Pago")
        if st.form_submit_button("Registrar Crédito"):
            st.session_state.db_movimientos.append({
                "Fecha": c_fec, "Tipo": "Cobro", "Concepto": c_sel, "Monto": c_mon, "Estado": "Pendiente", "Nota": "Crédito"
            })
            st.rerun()

# --- TAB REPORTES ---
with t_rep:
    st.header("📈 Análisis Financiero")
    if st.session_state.db_movimientos:
        df_rep = pd.DataFrame(st.session_state.db_movimientos)
        st.plotly_chart(px.bar(df_rep, x="Tipo", y="Monto", color="Tipo", title="Balance por Categoría"), use_container_width=True)
        st.write("### Historial de Movimientos")
        st.dataframe(df_rep, use_container_width=True)
