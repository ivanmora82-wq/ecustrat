import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de pantalla
st.set_page_config(page_title="ECU-STRAT", layout="wide", initial_sidebar_state="collapsed")

# Estilo personalizado para parecer App Móvil
st.markdown("""
    <style>
    .main { background-color: #121212; color: white; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #2E7D32; color: white; }
    .stMetric { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ ECU-STRAT")
st.caption("Inteligencia Financiera para la Pyme Ecuatoriana")

# --- ESTADO DE CAJA ---
st.subheader("💰 Saldo Actual")
caja_hoy = st.number_input("Efectivo + Banco hoy ($)", value=1500.0)

# --- TABS PARA NAVEGACIÓN TIPO APP ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "💸 Gastos/SRI", "📞 Cobros", "🚀 Crecer"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        # Aquí sumaremos deudas luego
        st.metric("Saldo Real", f"$ {caja_hoy}", delta="Disponible")
    with col2:
        st.metric("Salud Financiera", "85%", delta="Estable")
    
    st.markdown("---")
    st.write("### Proyección de Caja")
    chart_data = pd.DataFrame([caja_hoy, caja_hoy*0.9, caja_hoy*1.1, caja_hoy*0.8], columns=["Saldo"])
    st.line_chart(chart_data)

with tab2:
    st.subheader("Registro de Egresos")
    cat_sri = st.selectbox("Régimen SRI", ["RIMPE Popular", "RIMPE Emprendedor", "General"])
    
    with st.expander("Fijos (Arriendo, Luz, Sueldos)"):
        fijos = st.number_input("Total Fijos Mensuales ($)", value=800.0)
    
    with st.expander("Hormiga (Taxis, Buses, Varios)"):
        viajes = st.number_input("Nº de viajes/taxis al mes", value=10)
        costo_v = st.number_input("Costo promedio ($)", value=3.0)
        total_hormiga = viajes * costo_v
        st.write(f"Fuga mensual: ${total_hormiga}")

with tab3:
    st.subheader("Cuentas por Cobrar")
    if 'deudas' not in st.session_state:
        st.session_state.deudas = [{"cliente": "Cliente A", "monto": 200.0, "vence": "2025-10-25"}]
    
    for d in st.session_state.deudas:
        c1, c2 = st.columns([2, 1])
        c1.write(f"**{d['cliente']}** - ${d['monto']}")
        if c2.button("Cobrado", key=d['cliente']):
            st.success("¡Dinero a Caja!")

with tab4:
    st.subheader("Simulador de Decisiones")
    opcion = st.radio("¿Qué quieres calcular?", ["Nueva Contratación", "Evento Especial"])
    
    if opcion == "Nueva Contratación":
        sueldo = st.number_input("Sueldo Ofrecido ($)", value=460.0)
        margen = st.slider("Tu margen (%)", 10, 100, 30)
        costo_real = sueldo * 1.25
        venta_nec = costo_real / (margen/100)
        st.warning(f"Necesitas vender ${round(venta_nec, 2)} adicionales.")
    else:
        gasto_ev = st.number_input("Inversión en Evento ($)", value=100.0)
        st.info(f"El evento debe generar mínimo ${round(gasto_ev/0.3, 2)} en ventas.")

st.sidebar.markdown("Iván - ECU-STRAT 2025")