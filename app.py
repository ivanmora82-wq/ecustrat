import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN SEGURA ---
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = {
        "type": "service_account",
        "project_id": "fabled-ranger-480412-b9",
        "private_key_id": "5be77e02ce33b4b12f69dfdda644de61e5ff3d54",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCqgXfcDtZY14MI\nvxK1rB3irY3EAWUCXy1AJgrLZA4fY3Y1AJ2RkGas9FT8contqzOCISENmHKRUUWe\nnCOjZI8E7awOSJ8/6mmuiGp9tkXiPdSSKmwgPGm9vfSCsZ8XTE22VyNNYHLVHcpC\nW7FM076/sRxlRpX4VQx5lafz2BbX+ehAQy/pKhlZgy2ompl9HH3GLt8shoXB6Np2\nkjRtwXngjV16+awj7qBjGpjJYZbDZLBkreV0RHdDG8urcMkYbgw/0rhpw3thHFBF\nvpcCPriyADYZml5RYSyIfE48uETq1d6Nz+wpQLbE8FqQUkTQX4086crVnh184xPG\nCM3Gpva5AgMBAAECggEARjUYTw72+M8IwA25XQAZsDBpeudeGbtqDQt9D2HMJOWW\nE14FA56zgIz8/5QEMk5336HXk9sNdcPCyHwfepSaBVv+KEWD+VQDHyBBxTDMFswB\n3wvDyQRHQB9a8oPD79p191prCV3o+tMQ6QELgQiBdzos6JDHiOEwSVIzvYbhZR1w\nkcanR9TwD1Zzv2IHSk35WG01brKE4D3A0eNROCz+AmTEx9BAeB3QLruNqibNltyS\nYrLK4oJ6P4NBohLgkKJeGr8FIAmKOtA02jBWF0o5NbHzGTvLfJFXTUNDrGrejIWm\nyy7ILvEHqCRB3zwV8bLdi4i38MxmMxQ3jq6x9+gqTwKBgQDS7LuLv59Xbnnc/HO3\ CJvjiMjDqtfF9jpLqb1ViQ7jd0dZ8LeX7qOd791z/7Otn9LydcmhSjlf+HlvDXMo\nKYtFpUmSzjMJNrEIz51jmUNuSZJE3KiZnDC7VrQUkwb5iFyM90jp0g5ibDIyuH6Z\npf7BNbuVS5NNGJqopfjOuI0phwKBgQDO8X5TLO5wT91F2/11tkjVkKl6SucgkgpK\n3FTPdDo9NI3PsyxlCjAlPxkvkT53AR88klf7lF7Dz0yY1bXFcS9CUSfn7h6eZfPi\nX5yMIJnNRqkVZ2XZSkqX2LZIMJiT2BsE5mwv5wtVf2WL0AxZZeYRHDlWTkJlWaPF\n3E1eR8XtvwKBgAosYutdpbjY2kXfY1Frt+EkotJVNi0VMECgAkLS5oXwJd/frWtF\nllyyyhKjPa5dLBaHud7uro/Dc0/47Rn9zvrf+wl6qpmCKs3K/cNlDAyQvd5Wakdm\nci9HAk6PvOFiQ1yFPN4SRKFYqJ8rqOeOSxhUmCSeTY+FZUhHIRYPbreXAoGBAIcQ\nyxhSXRVkqtDrslPfs03gaxzsQknZx2nwwFHeVByabmw/TxxrN903f6KyM4jMbKzF\n/zKuNeOrKx0dbtP8+ZFZEqinm8haVoFLUguLQ5bdJYJYx/q4KFNPGDmprgvgolHi\nan4hWB5nVcmY8lZu0WgdebbAwUkQ5nk/PifoxGBVAoGAYPMLrEuJlpnJM6SJ4pfd\nx/ggxcwRkCo9duUzkAndSS+q4326v6llE7PNLBONzksP4DJntG1saa0xZISSqueX\nKYPHsPn0nlseGFR1yNFXZg32FsIlKeLsCkIgrwtge7Qjccc7F8gOO7faV6strfq+\nKFggcG+4j6j1Xu1LpRniQy4=\n-----END PRIVATE KEY-----\n",
        "client_email": "emi-database@fabled-ranger-480412-b9.iam.gserviceaccount.com",
        "client_id": "102764735047338306868"
    }
    try:
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

# --- 2. DISEÑO ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 10px; border-radius: 10px; border: 1px solid #FFD700; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #FFD700; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. BALANCE LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE SELECCIONADA", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO", value=0.0)
    c_ini = st.number_input("💵 CAJA", value=0.0)
    
    df_v = leer("Ventas"); df_f = leer("Fijos"); df_h = leer("Hormiga"); df_p = leer("Proveedores"); df_c = leer("Cobros")
    
    v_t = df_v['Monto'].sum() if not df_v.empty else 0
    f_p = df_f[df_f['Estado'] == 'PAGADO']['Monto'].sum() if not df_f.empty else 0
    p_p = df_p[df_p['Estado'] == 'PAGADO']['Monto'].sum() if not df_p.empty else 0
    h_t = df_h['Monto'].sum() if not df_h.empty else 0
    c_p = df_c[df_c['Estado'] == 'COBRADO']['Monto'].sum() if not df_c.empty else 0

    st.metric("BALANCE NETO REAL", f"$ {round(b_ini + c_ini + v_t + c_p - f_p - p_p - h_t, 2)}")

# --- 4. PESTAÑAS Y FORMULARIOS (MANTENIENDO SUMATORIAS) ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

def render_modulo(hoja, alias, label, icn, est_ok):
    df = leer(hoja)
    # Sumatoria total visible
    st.markdown(f"<div class='sum-box'>📈 TOTAL ACUMULADO {hoja.upper()}: $ {df['Monto'].sum() if not df.empty else 0}</div>", unsafe_allow_html=True)
    
    # Autocompletado: Leer nombres existentes para evitar errores de tipeo
    nombres_sugeridos = df['Concepto'].unique().tolist() if not df.empty else []
    
    with st.expander(f"➕ Registrar Nuevo {label}", expanded=True):
        with st.form(f"f_{alias}", clear_on_submit=True):
            col1, col2 = st.columns(2)
            f_r = col1.date_input("Fecha", date.today())
            nom = col2.selectbox(f"Seleccionar {label}", ["Nuevo..."] + nombres_sugeridos)
            if nom == "Nuevo...":
                nom = st.text_input(f"Escriba Nombre de {label}")
            m_r = st.number_input("Monto $", min_value=0.0)
            if st.form_submit_button("GRABAR"):
                conectar().worksheet(hoja).append_row([str(f_r), sede_act, nom, m_r, "PENDIENTE"])
                st.rerun()

    if not df.empty:
        for i, row in df.iterrows():
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            c1.write(f"📅 {row['Fecha']} | **{row['Concepto']}**")
            c2.write(f"$ {row['Monto']} ({row['Estado']})")
            if row['Estado'] == "PENDIENTE":
                if c3.button(f"{icn} {est_ok}", key=f"ok_{alias}_{i}"):
                    conectar().worksheet(hoja).update_cell(i + 2, 5, est_ok); st.rerun()
            else:
                if c3.button("🔄 REVERTIR", key=f"rev_{alias}_{i}"):
                    conectar().worksheet(hoja).update_cell(i + 2, 5, "PENDIENTE"); st.rerun()
            if c4.button("🗑️", key=f"del_{alias}_{i}"):
                conectar().worksheet(hoja).delete_rows(i + 2); st.rerun()

with tabs[0]: # VENTAS (Especial)
    df_ventas = leer("Ventas")
    st.markdown(f"<div class='sum-box'>💰 TOTAL VENTAS: $ {df_ventas['Monto'].sum()}</div>", unsafe_allow_html=True)
    with st.expander("➕ Registrar Venta", expanded=True):
        with st.form("fv"):
            f_v = st.date_input("Fecha", date.today())
            m_v = st.number_input("Monto Venta", min_value=0.0)
            if st.form_submit_button("GRABAR VENTA"):
                conectar().worksheet("Ventas").append_row([str(f_v), sede_act, "Venta Directa", m_v, "PAGADO"])
                st.rerun()
    st.dataframe(df_ventas, use_container_width=True)

with tabs[1]: render_modulo("Fijos", "f", "Gasto Fijo", "💳", "PAGADO")
with tabs[2]: render_modulo("Hormiga", "h", "Gasto Hormiga", "🐜", "PAGADO")
with tabs[3]: render_modulo("Proveedores", "p", "Proveedor", "💸", "PAGADO")
with tabs[4]: render_modulo("Cobros", "c", "Cuenta Cobro", "💰", "COBRADO")

# --- 5. REPORTES AVANZADOS CON SELECTOR DE FECHAS ---
with tabs[5]:
    st.header("📊 Inteligencia de Negocio")
    c1, c2 = st.columns(2)
    start = c1.date_input("Desde", date.today().replace(day=1))
    end = c2.date_input("Hasta", date.today())
    
    def filtrar(df): return df[(df['Fecha'] >= start) & (df['Fecha'] <= end)] if not df.empty else df

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🚛 Máximo Proveedor")
        df_pf = filtrar(leer("Proveedores"))
        if not df_pf.empty:
            st.plotly_chart(px.pie(df_pf.groupby("Concepto")["Monto"].sum().reset_index(), values="Monto", names="Concepto"), use_container_width=True)
        
        st.subheader("📅 Día de Mayor Venta")
        if not df_v.empty:
            df_vf = filtrar(df_v)
            st.plotly_chart(px.line(df_vf.groupby("Fecha")["Monto"].sum().reset_index(), x="Fecha", y="Monto"), use_container_width=True)

    with col_b:
        st.subheader("🐜 Gasto Hormiga más Fuerte")
        df_hf = filtrar(leer("Hormiga"))
        if not df_hf.empty:
            st.plotly_chart(px.bar(df_hf.groupby("Concepto")["Monto"].sum().reset_index(), x="Concepto", y="Monto"), use_container_width=True)

        st.subheader("🏢 Ingresos Sede vs Sede")
        if not df_v.empty:
            st.plotly_chart(px.bar(df_v.groupby("Sede")["Monto"].sum().reset_index(), x="Sede", y="Monto", color="Sede"), use_container_width=True)
