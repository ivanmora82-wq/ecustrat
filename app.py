import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN BLINDADA ---
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Limpieza de llave para evitar error base64
        pk = st.secrets["private_key"].replace('\\n', '\n').strip()
        creds_dict = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": pk,
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"]
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

def guardar(hoja, fila):
    try: conectar().worksheet(hoja).append_row(fila); st.rerun()
    except: st.error("Error al grabar")

def actualizar_estado(hoja, index, nuevo_estado):
    try:
        ws = conectar().worksheet(hoja)
        ws.update_cell(index + 2, 5, nuevo_estado)
        st.rerun()
    except: st.error("Error al actualizar")

# --- 2. DISEÑO ---
st.set_page_config(page_title="EMI MASTER PRO V50", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label, .dorado { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 15px; border-radius: 12px; border: 2px solid #FFD700; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #FFD700; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL (BALANCE REAL) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE SELECCIONADA", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 SALDO BANCO", value=0.0)
    c_ini = st.number_input("💵 SALDO CAJA", value=0.0)
    
    # Lógica contable: Solo suma/resta lo PAGADO o COBRADO
    df_v = leer("Ventas")
    df_f = leer("Fijos")
    df_h = leer("Hormiga")
    df_p = leer("Proveedores")
    df_c = leer("Cobros")

    v_total = df_v['Monto'].sum()
    f_total = df_f[df_f['Estado'] == 'PAGADO']['Monto'].sum()
    p_total = df_p[df_p['Estado'] == 'PAGADO']['Monto'].sum()
    h_total = df_h['Monto'].sum() # Hormiga siempre resta
    c_total = df_c[df_c['Estado'] == 'COBRADO']['Monto'].sum()

    balance_neto = b_ini + c_ini + v_total + c_total - f_total - p_total - h_total
    st.metric("BALANCE GENERAL REAL", f"$ {round(balance_neto, 2)}")

# --- 4. PESTAÑAS OPERATIVAS ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

def render_modulo(hoja, label, icn, est_ok):
    df = leer(hoja)
    st.markdown(f"<div class='sum-box'>TOTAL {hoja}: $ {df['Monto'].sum() if not df.empty else 0}</div>", unsafe_allow_html=True)
    
    with st.expander(f"➕ Registrar {label}"):
        with st.form(f"form_{hoja}"):
            f_r = st.date_input("Fecha", date.today())
            nom = st.text_input("Detalle / Nombre")
            m_r = st.number_input("Monto $", min_value=0.0)
            if st.form_submit_button("GRABAR"):
                guardar(hoja, [str(f_r), sede_act, nom, m_r, "PENDIENTE"])
    
    if not df.empty:
        for i, row in df.iterrows():
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            c1.write(f"📅 {row['Fecha']} | **{row['Concepto']}**")
            c2.write(f"$ {row['Monto']} ({row['Estado']})")
            if row['Estado'] == "PENDIENTE":
                if c3.button(f"{icn} {est_ok}", key=f"ok_{hoja}_{i}"): actualizar_estado(hoja, i, est_ok)
            else:
                if c3.button("🔄 REVERTIR", key=f"rev_{hoja}_{i}"): actualizar_estado(hoja, i, "PENDIENTE")
            if c4.button("🗑️", key=f"del_{hoja}_{i}"): 
                conectar().worksheet(hoja).delete_rows(i + 2); st.rerun()

with tabs[0]: # VENTAS (Siempre suma)
    df_ventas = leer("Ventas")
    st.markdown(f"<div class='sum-box'>TOTAL VENTAS: $ {df_ventas['Monto'].sum()}</div>", unsafe_allow_html=True)
    with st.form("fv"):
        f_v = st.date_input("Fecha", date.today())
        m_v = st.number_input("Monto Venta", min_value=0.0)
        if st.form_submit_button("GRABAR VENTA"):
            guardar("Ventas", [str(f_v), sede_act, "Venta Directa", m_v, "PAGADO"])
    st.dataframe(df_ventas, use_container_width=True)

with tabs[1]: render_modulo("Fijos", "Gasto Fijo", "💳", "PAGADO")
with tabs[2]: # HORMIGA
    df_h = leer("Hormiga")
    st.markdown(f"<div class='sum-box'>TOTAL HORMIGA: $ {df_h['Monto'].sum()}</div>", unsafe_allow_html=True)
    with st.form("fh"):
        f_h = st.date_input("Fecha", date.today())
        n_h = st.text_input("Descripción Gasto")
        m_h = st.number_input("Monto", min_value=0.0)
        if st.form_submit_button("GRABAR GASTO"):
            guardar("Hormiga", [str(f_h), sede_act, n_h, m_h, "PAGADO"])
    st.dataframe(df_h, use_container_width=True)
with tabs[3]: render_modulo("Proveedores", "Proveedor", "💸", "PAGADO")
with tabs[4]: render_modulo("Cobros", "Cobro Cliente", "💰", "COBRADO")

# --- 5. REPORTES AVANZADOS POR FECHA ---
with tabs[5]:
    st.header("📊 Centro de Inteligencia")
    c_f1, c_f2 = st.columns(2)
    inicio = c_f1.date_input("Desde", date.today().replace(day=1))
    fin = c_f2.date_input("Hasta", date.today())
    tipo = st.radio("Gráfico:", ["Barras", "Pastel", "Lineal"], horizontal=True)

    def filt(df): return df[(df['Fecha'] >= inicio) & (df['Fecha'] <= fin)] if not df.empty else df
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚛 Máximo Proveedor")
        df_p_f = filt(leer("Proveedores"))
        if not df_p_f.empty:
            res_p = df_p_f.groupby("Concepto")["Monto"].sum().reset_index()
            fig1 = px.bar(res_p, x="Concepto", y="Monto") if tipo=="Barras" else px.pie(res_p, values="Monto", names="Concepto")
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("🐜 Gasto Hormiga Fuerte")
        df_h_f = filt(leer("Hormiga"))
        if not df_h_f.empty:
            res_h = df_h_f.groupby("Concepto")["Monto"].sum().reset_index()
            fig2 = px.bar(res_h, x="Concepto", y="Monto", color_discrete_sequence=['#e74c3c'])
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🏢 Diferencia Matriz vs Sucursales")
    df_v_f = filt(leer("Ventas"))
    if not df_v_f.empty:
        st.plotly_chart(px.bar(df_v_f.groupby("Sede")["Monto"].sum().reset_index(), x="Sede", y="Monto", color="Sede"), use_container_width=True)
