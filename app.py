import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT PRO", layout="wide")

# 2. INICIALIZACIÓN
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
    val_ini = st.sidebar.number_input("Capital Inicial ($)", min_value=0.0)
    if st.sidebar.button("Establecer Capital"):
        st.session_state.caja_total = val_ini
        st.rerun()

is_premium = st.sidebar.toggle("🔓 Activar Modo Premium", value=True) # Activado para pruebas
st.sidebar.metric("BALANCE REAL", f"$ {round(st.session_state.caja_total, 2)}")

# 4. TABS
t_bal, t_caja, t_fijos, t_hormiga, t_prov, t_cobros, t_rep = st.tabs([
    "📊 Balance", "📅 Caja Diaria", "🏢 Gastos Fijos", "🐜 Hormiga", "🚛 Proveedores", "📞 Cobros", "📈 REPORTES"
])

# --- CAJA DIARIA CON FECHA (PUNTO 4) ---
with t_caja:
    st.subheader("Cierre de Caja Diario")
    with st.form("caja_dia"):
        fec_v = st.date_input("Fecha de la Venta", date.today())
        v_dia = st.number_input("Venta Total ($)", min_value=0.0)
        c_chica = st.number_input("Caja Chica / Inicio ($)", min_value=0.0)
        if st.form_submit_button("Cerrar Día"):
            neto = v_dia - c_chica
            st.session_state.caja_total += neto
            st.session_state.historial_ventas.append({"Fecha": fec_v, "Monto": neto, "Bruto": v_dia})
            st.success(f"Venta de {fec_v} guardada.")
            st.rerun()

# --- PROVEEDORES ---
with t_prov:
    st.subheader("🚛 Registro de Deudas")
    with st.form("p"):
        p_nom = st.text_input("Proveedor")
        p_val = st.number_input("Monto", min_value=0.0)
        p_fec = st.date_input("Fecha de Pago")
        if st.form_submit_button("Guardar"):
            st.session_state.db_proveedores.append({"Nombre": p_nom, "Monto": p_val, "Fecha": p_fec, "Estado": "Pendiente"})
            st.rerun()
    for i, p in enumerate(st.session_state.db_proveedores):
        if p['Estado'] == "Pendiente":
            color = "red" if p['Fecha'] <= date.today() else "blue"
            st.markdown(f":{color}[**Pagar a {p['Nombre']}** - ${p['Monto']} - Vence: {p['Fecha']}]")
            if st.button(f"Pagar {p['Nombre']} {i}"):
                st.session_state.caja_total -= p['Monto']
                p['Estado'] = "Pagado"
                st.rerun()

# --- HORMIGA ---
with t_hormiga:
    st.subheader("🐜 Gastos Hormiga")
    with st.form("h"):
        con_h = st.text_input("Concepto")
        mon_h = st.number_input("Monto", min_value=0.0)
        if st.form_submit_button("Añadir"):
            st.session_state.caja_total -= mon_h
            st.session_state.db_hormiga.append({"Fecha": date.today(), "Concepto": con_h, "Monto": mon_h})
            st.rerun()

# --- REPORTES AVANZADOS (PUNTO 5) ---
with t_rep:
    if not is_premium:
        st.error("🔒 Función Premium")
    else:
        st.subheader("📊 Centro de Inteligencia de Negocios")
        
        # FILTRO DE TIEMPO
        col_r1, col_r2 = st.columns(2)
        
        # 1. GRÁFICO DE VENTAS (TENDENCIA DIARIA)
        if st.session_state.historial_ventas:
            df_v = pd.DataFrame(st.session_state.historial_ventas)
            df_v['Fecha'] = pd.to_datetime(df_v['Fecha'])
            fig_v = px.line(df_v, x='Fecha', y='Monto', title="📈 Tendencia de Ventas (Neto)", markers=True)
            st.plotly_chart(fig_v, use_container_width=True)
        
        # 2. GRÁFICO DE PROVEEDORES (A quién le compro más)
        if st.session_state.db_proveedores:
            df_p = pd.DataFrame(st.session_state.db_proveedores)
            df_p_sum = df_p.groupby("Nombre")["Monto"].sum().reset_index()
            fig_p = px.bar(df_p_sum, x="Nombre", y="Monto", title="🚛 Ranking de Proveedores (Gasto Acumulado)", color="Monto")
            st.plotly_chart(fig_p, use_container_width=True)
            
        # 3. GRÁFICO GASTO HORMIGA (Fugas de dinero)
        if st.session_state.db_hormiga:
            df_h = pd.DataFrame(st.session_state.db_hormiga)
            df_h_sum = df_h.groupby("Concepto")["Monto"].sum().reset_index()
            fig_h = px.pie(df_h_sum, names="Concepto", values="Monto", title="🐜 Distribución Gasto Hormiga", hole=0.4)
            st.plotly_chart(fig_h, use_container_width=True)

        # RESUMEN TOTAL
        st.markdown("---")
        st.subheader("📝 Resumen de Operación")
        t_ingresos = sum(v['Monto'] for v in st.session_state.historial_ventas)
        t_egresos = sum(p['Monto'] for p in st.session_state.db_proveedores if p['Estado'] == 'Pagado') + sum(h['Monto'] for h in st.session_state.db_hormiga)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Ingresos Totales", f"$ {t_ingresos}")
        c2.metric("Egresos Totales", f"$ {t_egresos}")
        c3.metric("Utilidad Operativa", f"$ {t_ingresos - t_egresos}")
