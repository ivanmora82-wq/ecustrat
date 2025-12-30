import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN DE ALTO RENDIMIENTO ---
@st.cache_resource(show_spinner=False)
def conectar_seguro():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = {
        "type": "service_account",
        "project_id": "fabled-ranger-480412-b9",
        "private_key_id": "5be77e02ce33b4b12f69dfdda644de61e5ff3d54",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCqgXfcDtZY14MI\nvxK1rB3irY3EAWUCXy1AJgrLZA4fY3Y1AJ2RkGas9FT8contqzOCISENmHKRUUWe\nnCOjZI8E7awOSJ8/6mmuiGp9tkXiPdSSKmwgPGm9vfSCsZ8XTE22VyNNYHLVHcpC\nW7FM076/sRxlRpX4VQx5lafz2BbX+ehAQy/pKhlZgy2ompl9HH3GLt8shoXB6Np2\nkjRtwXngjV16+awj7qBjGpjJYZbDZLBkreV0RHdDG8urcMkYbgw/0rhpw3thHFBF\nvpcCPriyADYZml5RYSyIfE48uETq1d6Nz+wpQLbE8FqQUkTQX4086crVnh184xPG\nCM3Gpva5AgMBAAECggEARjUYTw72+M8IwA25XQAZsDBpeudeGbtqDQt9D2HMJOWW\nE14FA56zgIz8/5QEMk5336HXk9sNdcPCyHwfepSaBVv+KEWD+VQDHyBBxTDMFswB\n3wvDyQRHQB9a8oPD79p191prCV3o+tMQ6QELgQiBdzos6JDHiOEwSVIzvYbhZR1w\nkcanR9TwD1Zzv2IHSk35WG01brKE4D3A0eNROCz+AmTEx9BAeB3QLruNqibNltyS\nYrLK4oJ6P4NBohLgkKJeGr8FIAmKOtA02jBWF0o5NbHzGTvLfJFXTUNDrGrejIWm\nyy7ILvEHqCRB3zwV8bLdi4i38MxmMxQ3jq6x9+gqTwKBgQDS7LuLv59Xbnnc/HO3\ CJvjiMjDqtfF9jpLqb1ViQ7jd0dZ8LeX7qOd791z/7Otn9LydcmhSjlf+HlvDXMo\nKYtFpUmSzjMJNrEIz51jmUNuSZJE3KiZnDC7VrQUkwb5iFyM90jp0g5ibDIyuH6Z\ npf7BNbuVS5NNGJqopfjOuI0phwKBgQDO8X5TLO5wT91F2/11tkjVkKl6SucgkgpK\n3FTPdDo9NI3PsyxlCjAlPxkvkT53AR88klf7lF7Dz0yY1bXFcS9CUSfn7h6eZfPi\nX5yMIJnNRqkVZ2XZSkqX2LZIMJiT2BsE5mwv5wtVf2WL0AxZZeYRHDlWTkJlWaPF\3E1eR8XtvwKBgAosYutdpbjY2kXfY1Frt+EkotJVNi0VMECgAkLS5oXwJd/frWtF\nllyyyhKjPa5dLBaHud7uro/Dc0/47Rn9zvrf+wl6qpmCKs3K/cNlDAyQvd5Wakdm\ci9HAk6PvOFiQ1yFPN4SRKFYqJ8rqOeOSxhUmCSeTY+FZUhHIRYPbreXAoGBAIcQ\nyxhSXRVkqtDrslPfs03gaxzsQknZx2nwwFHeVByabmw/TxxrN903f6KyM4jMbKzF\n/zKuNeOrKx0dbtP8+ZFZEqinm8haVoFLUguLQ5bdJYJYx/q4KFNPGDmprgvgolHi\nan4hWB5nVcmY8lZu0WgdebbAwUkQ5nk/PifoxGBVAoGAYPMLrEuJlpnJM6SJ4pfd\ nx/ggxcwRkCo9duUzkAndSS+q4326v6llE7PNLBONzksP4DJntG1saa0xZISSqueX\nKYPHsPn0nlseGFR1yNFXZg32FsIlKeLsCkIgrwtge7Qjccc7F8gOO7faV6strfq+\nKFggcG+4j6j1Xu1LpRniQy4=\n-----END PRIVATE KEY-----\n",
        "client_email": "emi-database@fabled-ranger-480412-b9.iam.gserviceaccount.com",
        "client_id": "102764735047338306868"
    }
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)).open("EMI_DATA_PRO")

def leer_df(nombre):
    try:
        df = pd.DataFrame(conectar_seguro().worksheet(nombre).get_all_records())
        if not df.empty:
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            if 'Estado' not in df.columns: df['Estado'] = 'PENDIENTE'
            df['fila'] = df.index + 2
        return df
    except: return pd.DataFrame(columns=['Fecha', 'Sede', 'Concepto', 'Monto', 'Estado', 'fila'])

# --- 2. DISEÑO ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; border-radius: 8px; }
    .stButton>button { width: 100%; height: 32px; border-radius: 5px; font-size: 13px !important; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #FFD700; font-weight: bold; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA TEMPORAL ---
hoy = date.today()
primer_dia = hoy.replace(day=1)

with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO", value=0.0)
    c_ini = st.number_input("💵 CAJA", value=0.0)
    
    # Lectura blindada para el Balance
    v_df = leer_df("Ventas"); f_df = leer_df("Fijos"); p_df = leer_df("Proveedores"); c_df = leer_df("Cobros"); h_df = leer_df("Hormiga")
    
    # Saldo Arrastre Histórico
    v_h = v_df[v_df['Fecha'] < primer_dia]['Monto'].sum() if not v_df.empty else 0
    c_h = c_df[(c_df['Fecha'] < primer_dia) & (c_df['Estado'] == 'COBRADO')]['Monto'].sum() if not c_df.empty else 0
    g_h = (f_df[f_df['Estado'] == 'PAGADO']['Monto'].sum() + p_df[p_df['Estado'] == 'PAGADO']['Monto'].sum() + h_df['Monto'].sum())
    
    saldo_historico = v_h + c_h - g_h
    st.info(f"💾 **Saldo al {primer_dia}:**\n$ {saldo_historico}")

    v_m = v_df[v_df['Fecha'] >= primer_dia]['Monto'].sum() if not v_df.empty else 0
    st.metric("BALANCE NETO", f"$ {round(b_ini + c_ini + saldo_historico + v_m, 2)}")

# --- 4. RENDERIZADO DE FILA ÚNICA ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📊 REPORTES"])

def render_fila(hoja, alias, label, icn, est_ok):
    df_raw = leer_df(hoja)
    # Filtro: Mes actual o lo que siga Pendiente
    df = df_raw[(df_raw['Fecha'] >= primer_dia) | (df_raw['Estado'] == 'PENDIENTE')] if not df_raw.empty else pd.DataFrame()
    
    st.markdown(f"<div class='sum-box'>TOTAL {hoja.upper()}: $ {df['Monto'].sum() if not df.empty else 0}</div>", unsafe_allow_html=True)
    
    with st.expander(f"➕ Registrar {label}"):
        with st.form(f"form_{alias}"):
            f_r = st.date_input("Fecha", hoy); nom = st.text_input("Detalle"); m_r = st.number_input("Monto", min_value=0.0)
            if st.form_submit_button("GRABAR"):
                conectar_seguro().worksheet(hoja).append_row([str(f_r), sede, nom, m_r, "PENDIENTE"])
                st.rerun()

    for _, row in df.iterrows():
        c1, c2, c3, c4, c5 = st.columns([4, 2, 1, 1, 1])
        c1.write(f"{row['Fecha']} | {row['Concepto']}")
        c2.write(f"**${row['Monto']}**")
        
        # ACCIONES CON ICONOS
        if row['Estado'] == "PENDIENTE":
            if c3.button(f"{icn} OK", key=f"ok_{alias}_{row['fila']}"):
                conectar_seguro().worksheet(hoja).update_cell(row['fila'], 5, est_ok); st.rerun()
        else:
            if c3.button("🔄 REV", key=f"rev_{alias}_{row['fila']}"):
                conectar_seguro().worksheet(hoja).update_cell(row['fila'], 5, "PENDIENTE"); st.rerun()
        
        c4.button("✏️", key=f"ed_{alias}_{row['fila']}")
        if c5.button("🗑️", key=f"del_{alias}_{row['fila']}"):
            conectar_seguro().worksheet(hoja).delete_rows(row['fila']); st.rerun()

with tabs[0]: # VENTAS CON CONTROL
    v_mes = v_df[v_df['Fecha'] >= primer_dia] if not v_df.empty else pd.DataFrame()
    st.markdown(f"<div class='sum-box'>TOTAL VENTAS MES: $ {v_mes['Monto'].sum() if not v_mes.empty else 0}</div>", unsafe_allow_html=True)
    with st.form("fv"):
        f_v = st.date_input("Fecha", hoy); m_v = st.number_input("Valor $", min_value=0.0)
        if st.form_submit_button("GRABAR VENTA"):
            conectar_seguro().worksheet("Ventas").append_row([str(f_v), sede, "Venta", m_v, "PAGADO"])
            st.rerun()
    for _, row in v_mes.iterrows():
        c1, c2, c3, c4 = st.columns([5, 2, 1, 1])
        c1.write(f"{row['Fecha']} | Venta"); c2.write(f"**${row['Monto']}**")
        c3.button("✏️", key=f"ved_{row['fila']}")
        if c4.button("🗑️", key=f"vdel_{row['fila']}"):
            conectar_seguro().worksheet("Ventas").delete_rows(row['fila']); st.rerun()

with tabs[1]: render_fila("Fijos", "f", "Gasto Fijo", "✅", "PAGADO")
with tabs[3]: render_fila("Proveedores", "p", "Proveedor", "✅", "PAGADO")
with tabs[4]: render_fila("Cobros", "c", "Cuenta Cobro", "✅", "COBRADO")
