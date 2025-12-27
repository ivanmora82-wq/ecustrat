import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import io

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT PRO V13", layout="wide")

# 2. INICIALIZACIÓN DE DATOS
if 'caja_total' not in st.session_state: st.session_state.caja_total = 0.0
if 'db_movimientos' not in st.session_state: st.session_state.db_movimientos = []
if 'cat_hormiga' not in st.session_state: st.session_state.cat_hormiga = ["Taxi", "Almuerzo", "Limpieza", "Fundas"]
if 'cat_proveedores' not in st.session_state: st.session_state.cat_proveedores = ["General"]
if 'cat_clientes' not in st.session_state: st.session_state.cat_clientes = ["Consumidor Final"]
if 'gastos_fijos' not in st.session_state: 
    st.session_state.gastos_fijos = {"Arriendo": 0.0, "Luz/Agua": 0.0, "Internet": 0.0, "Sueldos": 0.0}

# --- FUNCIONES DE APOYO ---
def generar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# 3. BARRA LATERAL
with st.sidebar:
    st.title("🛡️ ECU-STRAT PRO")
    empresa = st.text_input("Empresa", "Mi Negocio")
    st.divider()
    st.metric("EFECTIVO EN CAJA", f"$ {round(st.session_state.caja_total, 2)}")
    
    st.subheader("⚙️ Catálogos")
    with st.expander("➕ Conceptos/Proveedores"):
        n_h = st.text_input("Nuevo Gasto")
        if st.button("Añadir Gasto"): st.session_state.cat_hormiga.append(n_h); st.rerun()
        n_p = st.text_input("Nuevo Proveedor")
        if st.button("Añadir Proveedor"): st.session_state.cat_proveedores.append(n_p); st.rerun()
    
    if st.session_state.db_movimientos:
        st.download_button("📊 Descargar Excel", data=generar_excel(pd.DataFrame(st.session_state.db_movimientos)), file_name="Reporte.xlsx")

# 4. TABS PRINCIPALES
t_caja, t_fijos, t_hormiga, t_prov, t_cobros, t_rep = st.tabs([
    "💰 Ventas", "🏢 Fijos", "🐜 Hormiga", "🚛 Proveedores", "📞 Cobros", "📈 REPORTES"
])

# --- TAB VENTAS ---
with t_caja:
    st.subheader("Registro de Ventas")
    with st.form("f_ventas", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        v_fec = c1.date_input("Fecha Venta", date.today())
        v_mon = c2.number_input("Monto ($)", min_value=0.0)
        v_not = c3.text_input("Referencia", "Venta Diaria")
        if st.form_submit_button("Guardar Venta"):
            st.session_state.caja_total += v_mon
            st.session_state.db_movimientos.append({"Fecha": v_fec, "Tipo": "Venta", "Concepto": "Ingreso", "Monto": v_mon, "Nota": v_not})
            st.rerun()
    
    # Historial de ventas con edición/borrado
    st.write("---")
    for i, m in enumerate(st.session_state.db_movimientos):
        if m['Tipo'] == "Venta":
            with st.expander(f"📝 Venta: {m['Fecha']} - ${m['Monto']}"):
                new_m = st.number_input("Editar Monto", value=float(m['Monto']), key=f"ev_{i}")
                if st.button("Actualizar", key=f"bv_{i}"):
                    st.session_state.caja_total = st.session_state.caja_total - m['Monto'] + new_m
                    m['Monto'] = new_m
                    st.rerun()
                if st.button("Eliminar 🗑️", key=f"dv_{i}"):
                    st.session_state.caja_total -= m['Monto']
                    st.session_state.db_movimientos.pop(i); st.rerun()

# --- TAB GASTOS FIJOS ---
with t_fijos:
    st.subheader("🏢 Gastos Mensuales (Estructura)")
    colf1, colf2 = st.columns(2)
    st.session_state.gastos_fijos["Arriendo"] = colf1.number_input("Arriendo", value=st.session_state.gastos_fijos["Arriendo"])
    st.session_state.gastos_fijos["Sueldos"] = colf2.number_input("Sueldos", value=st.session_state.gastos_fijos["Sueldos"])
    total_f = sum(st.session_state.gastos_fijos.values())
    st.metric("Total Comprometido", f"$ {total_f}")
    if st.button("🚨 PAGAR GASTOS FIJOS (Restar de Caja)"):
        st.session_state.caja_total -= total_f
        st.session_state.db_movimientos.append({"Fecha": date.today(), "Tipo": "Gasto Fijo", "Concepto": "Pago Mensual", "Monto": total_f, "Nota": "Liquidación Fijos"})
        st.success("Pagado"); st.rerun()

# --- TAB HORMIGA (CORREGIDA) ---
with t_hormiga:
    st.subheader("🐜 Gastos Diarios")
    with st.form("f_hormiga", clear_on_submit=True):
        ch1, ch2, ch3 = st.columns(3)
        h_fec = ch1.date_input("Fecha", date.today())
        h_con = ch2.selectbox("Concepto", st.session_state.cat_hormiga)
        h_mon = ch3.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Guardar Gasto"):
            st.session_state.caja_total -= h_mon
            st.session_state.db_movimientos.append({"Fecha": h_fec, "Tipo": "Gasto Hormiga", "Concepto": h_con, "Monto": h_mon, "Nota": ""})
            st.rerun()
    
    st.write("---")
    for i, m in enumerate(st.session_state.db_movimientos):
        if m['Tipo'] == "Gasto Hormiga":
            with st.expander(f"🐜 {m['Concepto']} - ${m['Monto']}"):
                new_mh = st.number_input("Editar Monto", value=float(m['Monto']), key=f"eh_{i}")
                if st.button("Actualizar", key=f"bh_{i}"):
                    st.session_state.caja_total = st.session_state.caja_total + m['Monto'] - new_mh
                    m['Monto'] = new_mh; st.rerun()
                if st.button("Eliminar 🗑️", key=f"dh_{i}"):
                    st.session_state.caja_total += m['Monto']
                    st.session_state.db_movimientos.pop(i); st.rerun()

# --- TAB REPORTES ---
with t_rep:
    st.subheader("📈 Centro de Reportes Inteligentes")
    tipo_r = st.selectbox("Tipo de Análisis", ["Balance General", "Ventas vs Gastos", "Detalle de Movimientos"])
    rango = st.radio("Período", ["Hoy", "Quincenal", "Mensual"], horizontal=True)
    
    if st.session_state.db_movimientos:
        df = pd.DataFrame(st.session_state.db_movimientos)
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        
        # Filtrado de fechas
        inicio = date.today() - timedelta(days=0 if rango=="Hoy" else 15 if rango=="Quincenal" else 30)
        df_f = df[df['Fecha'] >= inicio]
        
        if tipo_r == "Balance General":
            fig = px.pie(df_f, values="Monto", names="Tipo", hole=0.4, title=f"Distribución de Dinero ({rango})")
            st.plotly_chart(fig, use_container_width=True)
        elif tipo_r == "Detalle de Movimientos":
            st.dataframe(df_f, use_container_width=True)
