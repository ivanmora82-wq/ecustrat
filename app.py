import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import io

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT PRO V12", layout="wide")

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

# 3. BARRA LATERAL (ADMINISTRACIÓN Y DESCARGAS)
with st.sidebar:
    st.title("🛡️ ECU-STRAT PRO")
    empresa = st.text_input("Nombre de Empresa", "Mi Negocio")
    st.divider()
    st.metric("EFECTIVO REAL DISPONIBLE", f"$ {round(st.session_state.caja_total, 2)}")
    st.divider()
    
    # GESTIÓN DE CATÁLOGOS
    st.subheader("⚙️ Configurar Catálogos")
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

    st.divider()
    
    # BOTÓN DE DESCARGA EXCEL
    st.subheader("📥 Exportar Datos")
    if st.session_state.db_movimientos:
        df_export = pd.DataFrame(st.session_state.db_movimientos)
        excel_data = generar_excel(df_export)
        st.download_button(
            label="📊 Descargar Reporte Excel",
            data=excel_data,
            file_name=f"Reporte_{empresa}_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Sin datos para exportar")

# 4. CUERPO PRINCIPAL (TABS)
t_caja, t_hormiga, t_prov, t_cobros, t_rep = st.tabs([
    "📅 Ventas/Caja", "🐜 Gastos Hormiga", "🚛 Proveedores", "📞 Cobros", "📈 REPORTES"
])

# --- GASTOS HORMIGA ---
with t_hormiga:
    st.subheader("🐜 Registro de Gastos Diarios")
    with st.form("h_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        con = col1.selectbox("Concepto (Catálogo)", st.session_state.cat_hormiga)
        mon = col2.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Registrar"):
            st.session_state.caja_total -= mon
            st.session_state.db_movimientos.append({
                "Fecha": date.today(), "Tipo": "Gasto Hormiga", "Concepto": con, "Monto": mon
            })
            st.rerun()
    
    # Lista con opción de Borrar
    for i, m in enumerate(st.session_state.db_movimientos):
        if m['Tipo'] == "Gasto Hormiga":
            c_l1, c_l2, c_l3 = st.columns([3, 1, 1])
            c_l1.write(f"🔸 {m['Concepto']}")
            c_l2.write(f"${m['Monto']}")
            if c_l3.button("🗑️", key=f"del_{i}"):
                st.session_state.caja_total += m['Monto']
                st.session_state.db_movimientos.pop(i)
                st.rerun()

# --- PROVEEDORES ---
with t_prov:
    st.subheader("🚛 Cuentas por Pagar")
    with st.form("p_form", clear_on_submit=True):
        prov_sel = st.selectbox("Proveedor", st.session_state.cat_proveedores)
        mon_p = st.number_input("Monto Factura ($)", min_value=0.0)
        f_p = st.date_input("Fecha Límite")
        if st.form_submit_button("Registrar Deuda"):
            st.session_state.db_movimientos.append({
                "Fecha": f_p, "Tipo": "Proveedor", "Concepto": prov_sel, "Monto": mon_p, "Estado": "Pendiente"
            })
            st.rerun()

# --- REPORTES ---
with t_rep:
    st.header("📈 Análisis Financiero")
    rango = st.selectbox("Rango", ["Diario", "Quincenal", "Mensual"])
    
    if st.session_state.db_movimientos:
        df_rep = pd.DataFrame(st.session_state.db_movimientos)
        # Resumen gráfico
        st.plotly_chart(px.bar(df_rep.groupby("Concepto")["Monto"].sum().reset_index(), 
                               x="Concepto", y="Monto", title="Gasto por Concepto"), use_container_width=True)
