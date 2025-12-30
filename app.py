import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN BLINDADA ---
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = {
        "type": "service_account",
        "project_id": "fabled-ranger-480412-b9",
        "private_key_id": "5be77e02ce33b4b12f69dfdda644de61e5ff3d54",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCqgXfcDtZY14MI\nvxK1rB3irY3EAWUCXy1AJgrLZA4fY3Y1AJ2RkGas9FT8contqzOCISENmHKRUUWe\nnCOjZI8E7awOSJ8/6mmuiGp9tkXiPdSSKmwgPGm9vfSCsZ8XTE22VyNNYHLVHcpC\nW7FM076/sRxlRpX4VQx5lafz2BbX+ehAQy/pKhlZgy2ompl9HH3GLt8shoXB6Np2\nkjRtwXngjV16+awj7qBjGpjJYZbDZLBkreV0RHdDG8urcMkYbgw/0rhpw3thHFBF\nvpcCPriyADYZml5RYSyIfE48uETq1d6Nz+wpQLbE8FqQUkTQX4086crVnh184xPG\nCM3Gpva5AgMBAAECggEARjUYTw72+M8IwA25XQAZsDBpeudeGbtqDQt9D2HMJOWW\nE14FA56zgIz8/5QEMk5336HXk9sNdcPCyHwfepSaBVv+KEWD+VQDHyBBxTDMFswB\n3wvDyQRHQB9a8oPD79p191prCV3o+tMQ6QELgQiBdzos6JDHiOEwSVIzvYbhZR1w\nkcanR9TwD1Zzv2IHSk35WG01brKE4D3A0eNROCz+AmTEx9BAeB3QLruNqibNltyS\nYrLK4oJ6P4NBohLgkKJeGr8FIAmKOtA02jBWF0o5NbHzGTvLfJFXTUNDrGrejIWm\nyy7ILvEHqCRB3zwV8bLdi4i38MxmMxQ3jq6x9+gqTwKBgQDS7LuLv59Xbnnc/HO3\ CJvjiMjDqtfF9jpLqb1ViQ7jd0dZ8LeX7qOd791z/7Otn9LydcmhSjlf+HlvDXMo\nKYtFpUmSzjMJNrEIz51jmUNuSZJE3KiZnDC7VrQUkwb5iFyM90jp0g5ibDIyuH6Z\npf7BNbuVS5NNGJqopfjOuI0phwKBgQDO8X5TLO5wT91F2/11tkjVkKl6SucgkgpK\n3FTPdDo9NI3PsyxlCjAlPxkvkT53AR88klf7lF7Dz0yY1bXFcS9CUSfn7h6eZfPi\nX5yMIJnNRqkVZ2XZSkqX2LZIMJiT2BsE5mwv5wtVf2WL0AxZZeYRHDlWTkJlWaPF\n3E1eR8XtvwKBgAosYutdpbjY2kXfY1Frt+EkotJVNi0VMECgAkLS5oXwJd/frWtF\nllyyyhKjPa5dLBaHud7uro/Dc0/47Rn9zvrf+wl6qpmCKs3K/cNlDAyQvd5Wakdm\ci9HAk6PvOFiQ1yFPN4SRKFYqJ8rqOeOSxhUmCSeTY+FZUhHIRYPbreXAoGBAIcQ\nyxhSXRVkqtDrslPfs03gaxzsQknZx2nwwFHeVByabmw/TxxrN903f6KyM4jMbKzF\n/zKuNeOrKx0dbtP8+ZFZEqinm8haVoFLUguLQ5bdJYJYx/q4KFNPGDmprgvgolHi\nan4hWB5nVcmY8lZu0WgdebbAwUkQ5nk/PifoxGBVAoGAYPMLrEuJlpnJM6SJ4pfd\nx/ggxcwRkCo9duUzkAndSS+q4326v6llE7PNLBONzksP4DJntG1saa0xZISSqueX\nKYPHsPn0nlseGFR1yNFXZg32FsIlKeLsCkIgrwtge7Qjccc7F8gOO7faV6strfq+\nKFggcG+4j6j1Xu1LpRniQy4=\n-----END PRIVATE KEY-----\n",
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

# --- 2. DISEÑO Y BARRA LATERAL ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 10px; border-radius: 10px; border: 1px solid #FFD700; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 8px; border-radius: 5px; text-align: center; border: 1px solid #FFD700; margin-bottom: 15px; font-weight: bold; }
    .registro-fila { padding: 5px; border-bottom: 1px solid #eee; display: flex; align-items: center; }
    .stButton>button { padding: 2px 5px !important; font-size: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO", value=0.0)
    c_ini = st.number_input("💵 CAJA", value=0.0)
    
    df_v = leer("Ventas"); df_f = leer("Fijos"); df_h = leer("Hormiga"); df_p = leer("Proveedores"); df_c = leer("Cobros")
    
    # Lógica contable de Balance Real
    v_t = df_v['Monto'].sum() if not df_v.empty else 0
    f_p = df_f[df_f['Estado'] == 'PAGADO']['Monto'].sum() if not df_f.empty else 0
    p_p = df_p[df_p['Estado'] == 'PAGADO']['Monto'].sum() if not df_p.empty else 0
    h_p = df_h[df_h['Estado'] == 'PAGADO']['Monto'].sum() if not df_h.empty else 0
    c_p = df_c[df_c['Estado'] == 'COBRADO']['Monto'].sum() if not df_c.empty else 0

    balance = b_ini + c_ini + v_t + c_p - f_p - p_p - h_p
    st.metric("BALANCE NETO REAL", f"$ {round(balance, 2)}")

# --- 3. PESTAÑAS OPERATIVAS ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

def render_linea_accion(hoja, alias, label, icn_ok, txt_ok):
    df = leer(hoja)
    st.markdown(f"<div class='sum-box'>TOTAL {hoja.upper()}: $ {df['Monto'].sum() if not df.empty else 0}</div>", unsafe_allow_html=True)
    
    # Buscador de Nombres Sugeridos
    nombres_sugeridos = df['Concepto'].unique().tolist() if not df.empty else []
    with st.expander(f"➕ Registrar {label}"):
        with st.form(f"f_{alias}", clear_on_submit=True):
            f_r = st.date_input("Fecha", date.today())
            nom = st.selectbox(f"Seleccionar {label}", ["Nuevo..."] + nombres_sugeridos)
            if nom == "Nuevo...": nom = st.text_input(f"Nombre de {label}")
            m_r = st.number_input("Monto", min_value=0.0)
            if st.form_submit_button("GRABAR"):
                conectar().worksheet(hoja).append_row([str(f_r), sede_act, nom, m_r, "PENDIENTE"])
                st.rerun()

    # Listado en Fila Única
    if not df.empty:
        for i, row in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
            col1.write(f"{row['Fecha']} | {row['Concepto']}")
            col2.write(f"**${row['Monto']}** ({row['Estado'][0]})") # [0] para abreviar P o C
            
            # Botón Pagar/Cobrar
            if row['Estado'] == "PENDIENTE":
                if col3.button(icn_ok, key=f"ok_{alias}_{i}", help=f"Marcar {txt_ok}"):
                    conectar().worksheet(hoja).update_cell(i + 2, 5, txt_ok); st.rerun()
            else:
                if col3.button("🔄", key=f"rev_{alias}_{i}", help="Revertir"):
                    conectar().worksheet(hoja).update_cell(i + 2, 5, "PENDIENTE"); st.rerun()
            
            # Botón Editar (Informativo) y Eliminar
            col4.button("📝", key=f"ed_{alias}_{i}")
            if col5.button("🗑️", key=f"del_{alias}_{i}"):
                conectar().worksheet(hoja).delete_rows(i + 2); st.rerun()

with tabs[1]: render_linea_accion("Fijos", "f", "Gasto Fijo", "💸", "PAGADO")
with tabs[2]: render_linea_accion("Hormiga", "h", "Gasto Hormiga", "💸", "PAGADO")
with tabs[3]: render_linea_accion("Proveedores", "p", "Proveedor", "💸", "PAGADO")
with tabs[4]: render_linea_accion("Cobros", "c", "Cuenta Cobro", "💰", "COBRADO")

# --- 4. REPORTES CON SELECTOR ---
with tabs[5]:
    st.header("📊 Inteligencia de Negocio")
    reporte_tipo = st.selectbox("Elegir Reporte:", [
        "Seleccionar análisis...", "Máximo Proveedor", "Gasto Hormiga Fuerte", "Ventas: Matriz vs Sucursales", "Diferencia Ventas vs Gastos"
    ])
    
    col_f1, col_f2 = st.columns(2)
    inicio = col_f1.date_input("Desde", date.today().replace(day=1))
    fin = col_f2.date_input("Hasta", date.today())
    
    def f_df(df): return df[(df['Fecha'] >= inicio) & (df['Fecha'] <= fin)] if not df.empty else df

    if reporte_tipo == "Máximo Proveedor":
        df_p_f = f_df(df_p)
        if not df_p_f.empty:
            st.plotly_chart(px.pie(df_p_f.groupby("Concepto")["Monto"].sum().reset_index(), values="Monto", names="Concepto", hole=.4))
    
    elif reporte_tipo == "Gasto Hormiga Fuerte":
        df_h_f = f_df(df_h)
        if not df_h_f.empty:
            st.plotly_chart(px.bar(df_h_f.groupby("Concepto")["Monto"].sum().reset_index(), x="Concepto", y="Monto", color="Monto"))

    elif reporte_tipo == "Ventas: Matriz vs Sucursales":
        if not df_v.empty:
            st.plotly_chart(px.bar(f_df(df_v).groupby("Sede")["Monto"].sum().reset_index(), x="Sede", y="Monto", color="Sede"))

    elif reporte_tipo == "Diferencia Ventas vs Gastos":
        tot_v = f_df(df_v)['Monto'].sum() if not df_v.empty else 0
        tot_g = f_df(df_f)['Monto'].sum() + f_df(df_p)['Monto'].sum() + f_df(df_h)['Monto'].sum()
        st.plotly_chart(px.bar(pd.DataFrame({"Eje": ["Ventas", "Gastos"], "Monto": [tot_v, tot_g]}), x="Eje", y="Monto", color="Eje"))
