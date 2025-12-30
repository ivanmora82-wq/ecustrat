import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN Y CACHÉ (VELOCIDAD TURBO) ---
@st.cache_resource(show_spinner=False)
def conectar_gs():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = {
        "type": "service_account",
        "project_id": "fabled-ranger-480412-b9",
        "private_key_id": "5be77e02ce33b4b12f69dfdda644de61e5ff3d54",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCqgXfcDtZY14MI\nvxK1rB3irY3EAWUCXy1AJgrLZA4fY3Y1AJ2RkGas9FT8contqzOCISENmHKRUUWe\nnCOjZI8E7awOSJ8/6mmuiGp9tkXiPdSSKmwgPGm9vfSCsZ8XTE22VyNNYHLVHcpC\nW7FM076/sRxlRpX4VQx5lafz2BbX+ehAQy/pKhlZgy2ompl9HH3GLt8shoXB6Np2\nkjRtwXngjV16+awj7qBjGpjJYZbDZLBkreV0RHdDG8urcMkYbgw/0rhpw3thHFBF\nvpcCPriyADYZml5RYSyIfE48uETq1d6Nz+wpQLbE8FqQUkTQX4086crVnh184xPG\nCM3Gpva5AgMBAAECggEARjUYTw72+M8IwA25XQAZsDBpeudeGbtqDQt9D2HMJOWW\nE14FA56zgIz8/5QEMk5336HXk9sNdcPCyHwfepSaBVv+KEWD+VQDHyBBxTDMFswB\n3wvDyQRHQB9a8oPD79p191prCV3o+tMQ6QELgQiBdzos6JDHiOEwSVIzvYbhZR1w\nkcanR9TwD1Zzv2IHSk35WG01brKE4D3A0eNROCz+AmTEx9BAeB3QLruNqibNltyS\nYrLK4oJ6P4NBohLgkKJeGr8FIAmKOtA02jBWF0o5NbHzGTvLfJFXTUNDrGrejIWm\nyy7ILvEHqCRB3zwV8bLdi4i38MxmMxQ3jq6x9+gqTwKBgQDS7LuLv59Xbnnc/HO3\nCJvjiMjDqtfF9jpLqb1ViQ7jd0dZ8LeX7qOd791z/7Otn9LydcmhSjlf+HlvDXMo\nKYtFpUmSzjMJNrEIz51jmUNuSZJE3KiZnDC7VrQUkwb5iFyM90jp0g5ibDIyuH6Z\npf7BNbuVS5NNGJqopfjOuI0phwKBgQDO8X5TLO5wT91F2/11tkjVkKl6SucgkgpK\n3FTPdDo9NI3PsyxlCjAlPxkvkT53AR88klf7lF7Dz0yY1bXFcS9CUSfn7h6eZfPi\nX5yMIJnNRqkVZ2XZSkqX2LZIMJiT2BsE5mwv5wtVf2WL0AxZZeYRHDlWTkJlWaPF\n3E1eR8XtvwKBgAosYutdpbjY2kXfY1Frt+EkotJVNi0VMECgAkLS5oXwJd/frWtF\nllyyyhKjPa5dLBaHud7uro/Dc0/47Rn9zvrf+wl6qpmCKs3K/cNlDAyQvd5Wakdm\ci9HAk6PvOFiQ1yFPN4SRKFYqJ8rqOeOSxhUmCSeTY+FZUhHIRYPbreXAoGBAIcQ\nyxhSXRVkqtDrslPfs03gaxzsQknZx2nwwFHeVByabmw/TxxrN903f6KyM4jMbKzF\n/zKuNeOrKx0dbtP8+ZFZEqinm8haVoFLUguLQ5bdJYJYx/q4KFNPGDmprgvgolHi\nan4hWB5nVcmY8lZu0WgdebbAwUkQ5nk/PifoxGBVAoGAYPMLrEuJlpnJM6SJ4pfd\nx/ggxcwRkCo9duUzkAndSS+q4326v6llE7PNLBONzksP4DJntG1saa0xZISSqueX\nKYPHsPn0nlseGFR1yNFXZg32FsIlKeLsCkIgrwtge7Qjccc7F8gOO7faV6strfq+\nKFggcG+4j6j1Xu1LpRniQy4=\n-----END PRIVATE KEY-----\n",
        "client_email": "emi-database@fabled-ranger-480412-b9.iam.gserviceaccount.com",
        "client_id": "102764735047338306868"
    }
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds).open("EMI_DATA_PRO")

def leer_datos(hoja):
    try:
        ws = conectar_gs().worksheet(hoja)
        df = pd.DataFrame(ws.get_all_records())
        if not df.empty:
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        return df
    except: return pd.DataFrame()

# --- 2. DISEÑO ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 10px; border-radius: 10px; border: 1px solid #FFD700; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 5px; border-radius: 5px; text-align: center; margin-bottom: 10px; font-weight: bold; }
    .icon-btn { font-size: 1.2rem; cursor: pointer; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGICA TEMPORAL ---
hoy = date.today()
primer_dia = hoy.replace(day=1)

with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO", value=0.0)
    c_ini = st.number_input("💵 CAJA", value=0.0)
    
    # Lectura optimizada
    df_v = leer_datos("Ventas"); df_f = leer_datos("Fijos"); df_h = leer_datos("Hormiga"); df_p = leer_datos("Proveedores"); df_c = leer_datos("Cobros")
    
    # Balance Real (Optimizado)
    v_t = df_v['Monto'].sum() if not df_v.empty else 0
    f_p = df_f[df_f['Estado'] == 'PAGADO']['Monto'].sum() if not df_f.empty else 0
    p_p = df_p[df_p['Estado'] == 'PAGADO']['Monto'].sum() if not df_p.empty else 0
    h_p = df_h[df_h['Estado'] == 'PAGADO']['Monto'].sum() if not df_h.empty else 0
    c_p = df_c[df_c['Estado'] == 'COBRADO']['Monto'].sum() if not df_c.empty else 0

    st.metric("BALANCE NETO ACTUAL", f"$ {round(b_ini + c_ini + v_t + c_p - f_p - p_p - h_p, 2)}")

# --- 4. RENDERIZADO CON ICONOS COMPACTOS ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

def render_fila_iconos(hoja, alias, label, icn_ok, txt_ok):
    df = leer_datos(hoja)
    # Filtro de Arrastre (Mes actual o Pendientes)
    df_v = df[(df['Fecha'] >= primer_dia) | (df['Estado'] == 'PENDIENTE')] if not df.empty else pd.DataFrame()
    
    st.markdown(f"<div class='sum-box'>📊 TOTAL {hoja.upper()}: $ {df_v['Monto'].sum() if not df_v.empty else 0}</div>", unsafe_allow_html=True)
    
    # Formulario con Sugerencias
    memoria = df['Concepto'].unique().tolist() if not df.empty else []
    with st.expander(f"➕ Registrar {label}"):
        with st.form(f"f_{alias}", clear_on_submit=True):
            col_f, col_n = st.columns(2)
            f = col_f.date_input("Fecha", hoy)
            n = col_n.selectbox(f"{label}", ["Nuevo..."] + memoria)
            if n == "Nuevo...": n = st.text_input(f"Nombre del {label}")
            m = st.number_input("Monto", min_value=0.0)
            if st.form_submit_button("GRABAR"):
                conectar_gs().worksheet(hoja).append_row([str(f), sede_act, n, m, "PENDIENTE"])
                st.cache_data.clear(); st.rerun()

    if not df_v.empty:
        for i, row in df_v.iterrows():
            c1, c2, c3, c4, c5 = st.columns([4, 2, 1, 1, 1])
            c1.write(f"{row['Fecha']} | {row['Concepto']}")
            c2.write(f"**${row['Monto']}**")
            
            # Botón Acción (Icono)
            if row['Estado'] == "PENDIENTE":
                if c3.button(icn_ok, key=f"ok_{alias}_{i}", help=f"Marcar {txt_ok}"):
                    conectar_gs().worksheet(hoja).update_cell(i + 2, 5, txt_ok)
                    st.cache_data.clear(); st.rerun()
            else:
                if c3.button("🔄", key=f"rev_{alias}_{i}", help="Revertir"):
                    conectar_gs().worksheet(hoja).update_cell(i + 2, 5, "PENDIENTE")
                    st.cache_data.clear(); st.rerun()
            
            c4.button("📝", key=f"ed_{alias}_{i}", help="Editar registro")
            if c5.button("🗑️", key=f"del_{alias}_{i}", help="Eliminar permanentemente"):
                conectar_gs().worksheet(hoja).delete_rows(i + 2)
                st.cache_data.clear(); st.rerun()

# --- VENTAS CON EDICIÓN Y ELIMINACIÓN ---
with tabs[0]:
    df_v_mes = df_v[df_v['Fecha'] >= primer_dia] if not df_v.empty else pd.DataFrame()
    st.markdown(f"<div class='sum-box'>💰 TOTAL VENTAS MES: $ {df_v_mes['Monto'].sum() if not df_v_mes.empty else 0}</div>", unsafe_allow_html=True)
    with st.form("fv"):
        f_v = st.date_input("Fecha", hoy); m_v = st.number_input("Monto", min_value=0.0)
        if st.form_submit_button("GRABAR VENTA"):
            conectar_gs().worksheet("Ventas").append_row([str(f_v), sede_act, "Venta Diaria", m_v, "PAGADO"])
            st.cache_data.clear(); st.rerun()
    
    if not df_v_mes.empty:
        for i, row in df_v_mes.iterrows():
            c1, c2, c3, c4 = st.columns([5, 2, 1, 1])
            c1.write(f"{row['Fecha']} | {row['Concepto']}")
            c2.write(f"**${row['Monto']}**")
            c3.button("📝", key=f"ed_v_{i}")
            if c4.button("🗑️", key=f"del_v_{i}"):
                conectar_gs().worksheet("Ventas").delete_rows(i + 2)
                st.cache_data.clear(); st.rerun()

with tabs[1]: render_fila_iconos("Fijos", "f", "Gasto Fijo", "💸", "PAGADO")
with tabs[2]: render_fila_iconos("Hormiga", "h", "Gasto Hormiga", "💸", "PAGADO")
with tabs[3]: render_fila_iconos("Proveedores", "p", "Proveedor", "💸", "PAGADO")
with tabs[4]: render_fila_iconos("Cobros", "c", "Cuenta Cobro", "💰", "COBRADO")

with tabs[5]:
    st.header("📊 Inteligencia de Negocio")
    rep = st.selectbox("Elegir Análisis:", ["Seleccionar...", "Máximo Proveedor", "Gasto Hormiga Fuerte", "Comparativa: Matriz vs Sucursales", "Diferencia Ventas vs Gastos"])
    # Filtros de fecha y lógica de reportes se mantienen igual...
