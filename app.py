import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; }
    .btn-edit { background-color: #FFD700; color: black; }
    .btn-del { background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. FUNCIONES DE BASE DE DATOS (Simulación de edición/borrado) ---
# Nota: En la versión final, estas funciones conectan con tu Google Sheet
def borrar_registro(hoja, index):
    st.warning(f"Borrando fila {index} en {hoja}...")
    # Lógica de gspread: worksheet.delete_rows(index + 2) 

def editar_registro(hoja, index):
    st.info(f"Editando fila {index} en {hoja}...")

# --- 2. COMPONENTE DE TABLA CON ACCIONES ---
def tabla_con_acciones(df, nombre_hoja):
    if df.empty:
        st.write("No hay datos registrados.")
        return
    
    # Encabezados
    cols = st.columns([3, 2, 1, 1])
    cols[0].write("**Detalle/Nombre**")
    cols[1].write("**Monto**")
    cols[2].write("**Editar**")
    cols[3].write("**Eliminar**")
    
    for i, row in df.iterrows():
        c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
        c1.write(f"{row.get('Concepto', 'Sin nombre')}")
        c2.write(f"${row['Monto']}")
        if c3.button("📝", key=f"ed_{nombre_hoja}_{i}"):
            editar_registro(nombre_hoja, i)
        if c4.button("🗑️", key=f"del_{nombre_hoja}_{i}"):
            borrar_registro(nombre_hoja, i)

# --- 3. ESTRUCTURA DE PESTAÑAS ---
tabs = st.tabs(["🏢 FIJOS", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

with tabs[0]: # FIJOS
    st.subheader("Gestión de Gastos Fijos")
    with st.expander("➕ Añadir Nuevo Fijo"):
        with st.form("f"):
            n = st.text_input("Nombre (ej. Arriendo)")
            m = st.number_input("Monto", min_value=0.0)
            if st.form_submit_button("Guardar"):
                st.success("Grabado")
    
    # Aquí llamamos a la tabla con los botones a los costados
    df_fijos = pd.DataFrame({"Concepto": ["Internet", "Arriendo"], "Monto": [50, 450]})
    tabla_con_acciones(df_fijos, "Fijos")

with tabs[1]: # PROVEEDORES
    st.subheader("Gestión de Proveedores")
    with st.expander("➕ Registrar Factura"):
        prov = st.text_input("Nombre del Proveedor")
        m_p = st.number_input("Valor", key="prov_m")
        if st.button("Grabar Proveedor"): st.success("Ok")
    
    df_prov = pd.DataFrame({"Concepto": ["Distribuidora X", "Importadora Y"], "Monto": [1200, 800]})
    tabla_con_acciones(df_prov, "Proveedores")

# --- 4. REPORTES CON SELECTOR DE GRÁFICO ---
with tabs[3]:
    st.header("📊 Reportes Personalizados")
    tipo = st.selectbox("Formato de Gráfico", ["Pastel", "Barras", "Lineal"])
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("**Reporte: Proveedor al que más compramos**")
        # Lógica de agrupación y gráfico...
        st.info("Gráfico de Proveedores aquí")
        
    with col_b:
        st.write("**Reporte: Mayor Gasto Hormiga**")
        st.info("Gráfico de Gastos Hormiga aquí")
