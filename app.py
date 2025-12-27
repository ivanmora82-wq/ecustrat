import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT PRO", layout="wide")

# 2. INICIALIZACIÓN DE DATOS
if 'caja_total' not in st.session_state:
    st.session_state.caja_total = 1000.0
if 'db_proveedores' not in st.session_state:
    st.session_state.db_proveedores = []
if 'db_cobros' not in st.session_state:
    st.session_state.db_cobros = []
if 'historial_ventas' not in st.session_state:
    st.session_state.historial_ventas = []
if 'gastos_hormiga' not in st.session_state:
    st.session_state.gastos_hormiga = []

# 3. BARRA LATERAL
st.sidebar.title("ECU-STRAT PRO")
empresa = st.sidebar.text_input("Empresa", "Mi Negocio")
sucursal = st.sidebar.selectbox("Sede", ["Matriz", "Sucursal 1", "Sucursal 2"])
is_premium = st.sidebar.toggle("🔓 Modo Premium", value=False)
st.sidebar.metric("Balance Disponible", f"$ {round(st.session_state.caja_total, 2)}")

st.title(f"🛡️ {empresa} - {sucursal}")

# 4. TABS
t_balance, t_caja, t_gastos, t_prov, t_cobros, t_reporte = st.tabs([
    "📊 Balance", "📦 Caja Diaria", "💸 Gastos", "🚛 Proveedores", "📞 Cobros", "📈 Reportes"
])

with t_balance:
    deuda_p = sum(p['Monto'] for p in st.session_state.db_proveedores if p['Estado'] == 'Pendiente')
    por_cobrar = sum(c['Total'] - c['Abonos'] for c in st.session_state.db_cobros if c['Estado'] == 'Pendiente')
    c1, c2, c3 = st.columns(3)
    c1.metric("Efectivo + Banco", f"$ {round(st.session_state.caja_total, 2)}")
    c2.metric("Deuda (Por Pagar)", f"$ {round(deuda_p, 2)}", delta_color="inverse")
    c3.metric("En la Calle (Por Cobrar)", f"$ {round(por_cobrar, 2)}")
    st.markdown("---")
    df_bal = pd.DataFrame({
        'Estado': ['Disponible', 'Deuda', 'Cobros'],
        'Monto': [st.session_state.caja_total - deuda_p, deuda_p, por_cobrar]
    })
    fig_bal = px.pie(df_bal, names='Estado', values='Monto', hole=0.4, template="plotly_dark")
    st.plotly_chart(fig_bal, use_container_width=True)

with t_caja:
    st.subheader("Cierre de Caja")
    v_bruta = st.number_input("Venta del Día ($)", min_value=0.0)
    sencillo = st.number_input("Sencillo para mañana ($)", min_value=0.0)
    if st.button("Finalizar Día"):
        neto = v_bruta - sencillo
        st.session_state.caja_total += neto
        st.session_state.historial_ventas.append({"Fecha": datetime.now(), "Monto": neto})
        st.success("Día cerrado con éxito.")
        st.rerun()

with t_gastos:
    st.subheader("Gastos Fijos")
    col_f1, col_f2 = st.columns(2)
    arriendo = col_f1.number_input("Arriendo", value=0.0)
    luz = col_f2.number_input("Luz/Agua", value=0.0)
    wifi = col_f1.number_input("Internet", value=0.0)
    sueldos = col_f2.number_input("Sueldos", value=0.0)
    st.markdown("---")
    st.subheader("🐜 Gastos Hormiga")
    desc_h = st.text_input("Concepto")
    monto_h = st.number_input("Monto ($)", min_value=0.0, key="hormiga")
    if st.button("Registrar Gasto"):
        st.session_state.caja_total -= monto_h
        st.session_state.gastos_hormiga.append({"Concepto": desc_h, "Monto": monto_h})
        st.rerun()

with t_prov:
    st.subheader("Proveedores")
    p_nom = st.text_input("Nombre Proveedor")
    p_mon = st.number_input("Monto Factura", min_value=0.0)
    if st.button("Guardar Factura"):
        st.session_state.db_proveedores.append({"Proveedor": p_nom, "Monto": p_mon, "Estado": "Pendiente"})
        st.rerun()
    for i, p in enumerate(st.session_state.db_proveedores):
        if p['Estado'] == "Pendiente":
            st.write(f"⚠️ {p['Proveedor']}: ${p['Monto']}")
            if st.button(f"Pagar a {p['Proveedor']}", key=f"p_{i}"):
                st.session_state.caja_total -= p['Monto']
                st.session_state.db_proveedores[i]['Estado'] = "Pagado"
                st.rerun()

with t_cobros:
    st.subheader("Cobranzas")
    cl_nom = st.text_input("Cliente")
    cl_mon = st.number_input("Monto Crédito", min_value=0.0)
    if st.button("Guardar Crédito"):
        st.session_state.db_cobros.append({"Cliente": cl_nom, "Total": cl_mon, "Abonos": 0.0, "Estado": "Pendiente"})
        st.rerun()
    for i, c in enumerate(st.session_state.db_cobros):
        if c['Estado'] == "Pendiente":
            st.write(f"👤 {c['Cliente']} - Pendiente: ${c['Total'] - c['Abonos']}")
            ab = st.number_input(f"Abono de {c['Cliente']}", key=f"ab_{i}")
            if st.button(f"Cobrar Abono {i}"):
                st.session_state.db_cobros[i]['Abonos'] += ab
                st.session_state.caja_total += ab
                if st.session_state.db_cobros[i]['Abonos'] >= c['Total']:
                    st.session_state.db_cobros[i]['Estado'] = "Pagado"
                st.rerun()

with t_reporte:
    if not is_premium:
        st.error("🔒 Función Premium")
        st.info("Suscríbete por $15/mes para ver reportes detallados.")
    else:
        st.success("Acceso Premium")
        total_v = sum(v['Monto'] for v in st.session_state.historial_ventas)
        total_g = arriendo + luz + wifi + sueldos + sum(h['Monto'] for h in st.session_state.gastos_hormiga)
        st.metric("Ventas Totales", f"$ {total_v}")
        st.metric("Gastos Totales", f"$ {total_g}")
        st.bar_chart(pd.DataFrame({"Monto": [total_v, total_g]}, index=["Ingresos", "Egresos"]))
