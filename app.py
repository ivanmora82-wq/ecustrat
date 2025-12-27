import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT PRO", layout="wide")

# 2. INICIALIZACIÓN DE DATOS
if 'caja_total' not in st.session_state: st.session_state.caja_total = 0.0
if 'db_proveedores' not in st.session_state: st.session_state.db_proveedores = []
if 'db_cobros' not in st.session_state: st.session_state.db_cobros = []
if 'db_hormiga' not in st.session_state: st.session_state.db_hormiga = []
if 'historial_ventas' not in st.session_state: st.session_state.historial_ventas = []
if 'gastos_fijos' not in st.session_state: 
    st.session_state.gastos_fijos = {"Arriendo": 0.0, "Luz/Agua": 0.0, "Internet": 0.0, "Sueldos": 0.0}

# 3. BARRA LATERAL
st.sidebar.title("🛡️ ECU-STRAT PRO")
if st.session_state.caja_total == 0:
    val_ini = st.sidebar.number_input("Capital Inicial Real ($)", min_value=0.0)
    if st.sidebar.button("Establecer Capital"):
        st.session_state.caja_total = val_ini
        st.rerun()

is_premium = st.sidebar.toggle("🔓 Modo Premium", value=True)
st.sidebar.metric("SALDO REAL EN CAJA", f"$ {round(st.session_state.caja_total, 2)}")

st.title("Inteligencia Financiera ECU-STRAT")

# 4. TABS
t_bal, t_caja, t_fijos, t_hormiga, t_prov, t_cobros, t_rep = st.tabs([
    "📊 Balance", "📅 Caja Diaria", "🏢 Fijos", "🐜 Hormiga", "🚛 Proveedores", "📞 Cobros", "📈 REPORTES"
])

# --- TAB CAJA DIARIA ---
with t_caja:
    st.subheader("Cierre de Caja por Fecha")
    with st.form("caja_dia", clear_on_submit=True):
        fec_v = st.date_input("Fecha de Venta", date.today())
        v_dia = st.number_input("Venta Total ($)", min_value=0.0)
        c_chica = st.number_input("Caja Chica / Inicio ($)", min_value=0.0)
        if st.form_submit_button("Guardar Cierre"):
            neto = v_dia - c_chica
            st.session_state.caja_total += neto
            st.session_state.historial_ventas.append({"Fecha": fec_v, "Monto": neto, "Bruto": v_dia})
            st.rerun()
    
    if st.session_state.historial_ventas:
        st.write("### Historial Reciente")
        for i, v in enumerate(st.session_state.historial_ventas):
            c_v1, c_v2 = st.columns([4, 1])
            c_v1.write(f"📅 {v['Fecha']} | Neto: ${v['Monto']}")
            if c_v2.button("🗑️", key=f"del_v_{i}"):
                st.session_state.caja_total -= v['Monto']
                st.session_state.historial_ventas.pop(i)
                st.rerun()

# --- TAB GASTOS HORMIGA ---
with t_hormiga:
    st.subheader("🐜 Detalle de Gastos Pequeños")
    with st.form("h", clear_on_submit=True):
        con_h = st.text_input("Concepto (Ej: Taxi, Almuerzo)")
        mon_h = st.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Registrar"):
            st.session_state.caja_total -= mon_h
            st.session_state.db_hormiga.append({"Fecha": date.today(), "Concepto": con_h, "Monto": mon_h})
            st.rerun()
    
    for i, h in enumerate(st.session_state.db_hormiga):
        col_h1, col_h2 = st.columns([4, 1])
        col_h1.write(f"🔸 {h['Concepto']}: ${h['Monto']}")
        if col_h2.button("🗑️", key=f"del_h_{i}"):
            st.session_state.caja_total += h['Monto']
            st.session_state.db_hormiga.pop(i)
            st.rerun()

# --- TAB REPORTES (EL CORAZÓN DE LA APP) ---
with t_rep:
    if not is_premium:
        st.error("🔒 Función Premium")
    else:
        st.header("📈 Análisis de Resultados")
        
        # VENTAS EN EL TIEMPO
        if st.session_state.historial_ventas:
            df_v = pd.DataFrame(st.session_state.historial_ventas)
            df_v['Fecha'] = pd.to_datetime(df_v['Fecha'])
            fig_v = px.line(df_v.sort_values('Fecha'), x='Fecha', y='Monto', title="Evolución de Ingresos Netos", markers=True)
            st.plotly_chart(fig_v, use_container_width=True)

        # PROVEEDORES Y GASTOS
        col_rep1, col_rep2 = st.columns(2)
        
        with col_rep1:
            if st.session_state.db_proveedores:
                df_p = pd.DataFrame(st.session_state.db_proveedores)
                df_p_sum = df_p.groupby("Nombre")["Monto"].sum().reset_index()
                st.plotly_chart(px.bar(df_p_sum, x="Nombre", y="Monto", title="Gasto por Proveedor"), use_container_width=True)
        
        with col_rep2:
            if st.session_state.db_hormiga:
                df_h = pd.DataFrame(st.session_state.db_hormiga)
                df_h_sum = df_h.groupby("Concepto")["Monto"].sum().reset_index()
                st.plotly_chart(px.pie(df_h_sum, names="Concepto", values="Monto", title="Detalle Gastos Hormiga", hole=0.3), use_container_width=True)

        # RESUMEN NUMÉRICO
        st.markdown("---")
        t_ing = sum(v['Monto'] for v in st.session_state.historial_ventas)
        t_egr = sum(p['Monto'] for p in st.session_state.db_proveedores if p['Estado'] == 'Pagado') + sum(h['Monto'] for h in st.session_state.db_hormiga)
        
        c_r1, c_r2, c_r3 = st.columns(3)
        c_r1.metric("Ingresos Acumulados", f"$ {t_ing}")
        c_r2.metric("Egresos Acumulados", f"$ {t_egr}")
        c_r3.metric("UTILIDAD NETA", f"$ {round(t_ing - t_egr, 2)}")
