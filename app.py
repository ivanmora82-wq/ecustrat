import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ECU-STRAT STRATEGIC V17", layout="wide")

# 2. INICIALIZACIÓN
if 'db_movimientos' not in st.session_state: st.session_state.db_movimientos = []
if 'cat_fijos' not in st.session_state: st.session_state.cat_fijos = ["Agua", "Luz", "WIFI", "Arriendo", "Sueldos"]

# 3. BARRA LATERAL
with st.sidebar:
    st.title("🛡️ ECU-STRAT STRATEGIC")
    sede_actual = st.selectbox("📍 Sede Actual", ["Matriz", "Sucursal 1", "Sucursal 2"])
    st.divider()
    
    # Balance para cálculos
    df_all = pd.DataFrame(st.session_state.db_movimientos)
    ventas_mes = 0.0
    if not df_all.empty:
        ventas_mes = df_all[(df_all['Tipo'] == 'Venta') & (df_all['Sede'] == sede_actual)]['Monto'].sum()
    
    st.metric(f"Ventas Acumuladas {sede_actual}", f"$ {round(ventas_mes, 2)}")

# 4. TABS
t_v, t_f, t_h, t_sim, t_rep = st.tabs(["💰 Ventas", "🏢 Fijos", "🐜 Hormiga", "🚀 SIMULADOR", "📈 REPORTES"])

# --- TAB SIMULADOR (LA NUEVA HERRAMIENTA) ---
with t_sim:
    st.header("🚀 Simulador de Nuevos Gastos y Personal")
    st.info("Usa esta herramienta antes de contratar a alguien o hacer una compra grande.")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        tipo_inversion = st.selectbox("¿Qué desea añadir?", ["Nuevo Personal (Fijo)", "Personal por Horas", "Nueva Maquinaria/Gasto Especial"])
        costo_nuevo = st.number_input("Costo mensual de este nuevo gasto ($)", min_value=1.0)
        margen_producto = st.slider("Tu margen de ganancia promedio (%)", 10, 90, 30, help="Si vendes algo a $10 y te cuesta $7, tu margen es 30%")

    # CÁLCULOS ESTRATÉGICOS
    # Para cubrir un gasto de $X con un margen de Y%, necesitas vender: X / (Y/100)
    necesidad_venta_extra = costo_nuevo / (margen_producto / 100)
    
    with col_s2:
        st.subheader("📊 Resultados del Análisis")
        st.write(f"Para cubrir este nuevo costo de **${costo_nuevo}** sin perder dinero:")
        st.metric("Venta Extra Mensual Necesaria", f"$ {round(necesidad_venta_extra, 2)}")
        
        if ventas_mes > 0:
            porcentaje_subir = (necesidad_venta_extra / ventas_mes) * 100
            st.warning(f"📈 Tus ventas actuales deben subir un **{round(porcentaje_subir, 1)}%**")
        else:
            st.info("Registra ventas en la pestaña 'Ventas' para calcular el % de incremento necesario.")

    st.divider()
    st.write("### 💡 Recomendación Estratégica")
    diario_extra = necesidad_venta_extra / 30
    st.success(f"Para contratar a este personal, tu equipo debe vender **${round(diario_extra, 2)} adicionales cada día**.")

# --- TAB REPORTES (COMPARATIVA Y PRESUPUESTO) ---
with t_rep:
    st.subheader("📊 Análisis de Viabilidad")
    if not df_all.empty:
        # Gráfico comparativo de Gastos vs Ventas
        df_res = df_all.groupby("Tipo")["Monto"].sum().reset_index()
        st.plotly_chart(px.bar(df_res, x="Tipo", y="Monto", color="Tipo", title="Estructura de Costos Actual"), use_container_width=True)
    else:
        st.info("No hay datos suficientes.")

# --- EL RESTO DE TABS (Mantienen la lógica de la V16) ---
with t_v:
    st.write("Use esta pestaña para registrar sus ventas diarias...")
    # (Aquí va el código de ventas que ya tenemos)
