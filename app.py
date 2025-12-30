import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, datetime

# --- 1. CONEXIÓN ---
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        pk = st.secrets["private_key"].replace('\\n', '\n')
        creds_dict = {
            "type": "service_account", "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"], "private_key": pk,
            "client_email": st.secrets["client_email"], "client_id": st.secrets["client_id"]
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds).open("EMI_DATA_PRO")
    except: return None

def leer(hoja):
    try:
        df = pd.DataFrame(conectar().worksheet(hoja).get_all_records())
        if not df.empty: 
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        return df
    except: return pd.DataFrame()

def cambiar_estado(hoja, index, nuevo_estado):
    try:
        ws = conectar().worksheet(hoja)
        ws.update_cell(index + 2, 5, nuevo_estado) # Columna E para el estado
        st.rerun()
    except: st.error("Error al actualizar estado")

# --- 2. DISEÑO ---
st.set_page_config(page_title="EMI MASTER PRO V49", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 10px; border-radius: 10px; border: 1px solid #FFD700; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 8px; border-radius: 5px; text-align: center; margin-bottom: 10px; border: 1px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BALANCE DINÁMICO ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO", value=0.0)
    c_ini = st.number_input("💵 CAJA", value=0.0)
    
    # Solo suman/restan si el estado es 'PAGADO', 'COBRADO' o es una 'VENTA'
    df_v = leer("Ventas")
    df_f = leer("Fijos")
    df_h = leer("Hormiga")
    df_p = leer("Proveedores")
    df_c = leer("Cobros")

    total_ventas = df_v['Monto'].sum()
    total_pagos = df_f[df_f['Estado'] == 'PAGADO']['Monto'].sum() + \
                  df_p[df_p['Estado'] == 'PAGADO']['Monto'].sum() + \
                  df_h['Monto'].sum()
    total_cobros = df_c[df_c['Estado'] == 'COBRADO']['Monto'].sum()

    st.metric("BALANCE NETO REAL", f"$ {round(b_ini + c_ini + total_ventas + total_cobros - total_pagos, 2)}")

# --- 4. PESTAÑAS CON ACCIONES DE PAGO/COBRO ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

def render_modulo_avanzado(hoja, label, icono_accion, estado_objetivo):
    df = leer(hoja)
    st.markdown(f"<div class='sum-box'>TOTAL ACUMULADO {hoja}: $ {df['Monto'].sum() if not df.empty else 0}</div>", unsafe_allow_html=True)
    
    # Formulario de Registro
    with st.expander(f"➕ Registrar Nuevo {label}"):
        with st.form(f"f_{hoja}"):
            f = st.date_input("Fecha", date.today())
            nom = st.text_input("Nombre / Detalle")
            m = st.number_input("Monto", min_value=0.0)
            if st.form_submit_button("GRABAR"):
                # Se graba como 'PENDIENTE' por defecto
                conectar().worksheet(hoja).append_row([str(f), sede_act, nom, m, "PENDIENTE"])
                st.rerun()

    # Tabla con botones dinámicos
    if not df.empty:
        for i, row in df.iterrows():
            c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
            c1.write(f"📅 {row['Fecha']} | {row['Concepto']}")
            c2.write(f"**$ {row['Monto']}** ({row['Estado']})")
            
            # Botón de Pagar/Cobrar o Revertir
            if row['Estado'] == "PENDIENTE":
                if c3.button(f"{icono_accion} {estado_objetivo}", key=f"btn_{hoja}_{i}"):
                    cambiar_estado(hoja, i, estado_objetivo)
            else:
                if c3.button("🔄 REVERTIR", key=f"rev_{hoja}_{i}"):
                    cambiar_estado(hoja, i, "PENDIENTE")
            
            if c4.button("🗑️", key=f"del_{hoja}_{i}"):
                conectar().worksheet(hoja).delete_rows(i + 2)
                st.rerun()

with tabs[1]: render_modulo_avanzado("Fijos", "Gasto Fijo", "💳", "PAGADO")
with tabs[3]: render_modulo_avanzado("Proveedores", "Proveedor", "💸", "PAGADO")
with tabs[4]: render_modulo_avanzado("Cobros", "Cuenta por Cobrar", "💰", "COBRADO")

# --- 5. REPORTES CON FILTRO DE FECHA ---
with tabs[5]:
    st.header("📊 Inteligencia EMI MASTER")
    col_f1, col_f2 = st.columns(2)
    start_d = col_f1.date_input("Desde", date.today().replace(day=1))
    end_d = col_f2.date_input("Hasta", date.today())

    # Filtrado global por fecha para reportes
    def filtrar(df): return df[(df['Fecha'] >= start_d) & (df['Fecha'] <= end_d)] if not df.empty else df

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚛 Máximo Proveedor")
        df_p_f = filtrar(leer("Proveedores"))
        if not df_p_f.empty:
            res_p = df_p_f.groupby("Concepto")["Monto"].sum().reset_index()
            st.plotly_chart(px.pie(res_p, values="Monto", names="Concepto"), use_container_width=True)

    with col2:
        st.subheader("📞 Mayor Cuenta por Cobrar")
        df_c_f = filtrar(leer("Cobros"))
        if not df_c_f.empty:
            st.plotly_chart(px.bar(df_c_f, x="Concepto", y="Monto", color="Concepto"), use_container_width=True)

    st.subheader("🏢 Ingresos por Sede (Matriz vs Sucursales)")
    df_v_f = filtrar(leer("Ventas"))
    if not df_v_f.empty:
        st.plotly_chart(px.bar(df_v_f.groupby("Sede")["Monto"].sum().reset_index(), x="Sede", y="Monto", color="Sede"), use_container_width=True)
