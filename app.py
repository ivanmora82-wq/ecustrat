import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN OPTIMIZADA ---
@st.cache_resource(show_spinner=False)
def iniciar_conexion():
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

def leer_hoja(nombre):
    try:
        data = iniciar_conexion().worksheet(nombre).get_all_records()
        df = pd.DataFrame(data)
        if not df.empty:
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            df['ID_Fila'] = df.index + 2
        return df
    except: return pd.DataFrame()

# --- 2. LOGICA DE ARRASTRE ---
hoy = date.today()
inicio_mes = hoy.replace(day=1)

def calcular_arrastre_total(fecha):
    v = leer_hoja("Ventas"); f = leer_hoja("Fijos"); p = leer_hoja("Proveedores"); c = leer_hoja("Cobros"); h = leer_hoja("Hormiga")
    v_s = v[v['Fecha'] < fecha]['Monto'].sum() if not v.empty else 0
    c_s = c[(c['Fecha'] < fecha) & (c['Estado'] == 'COBRADO')]['Monto'].sum() if not c.empty else 0
    f_s = f[(f['Fecha'] < fecha) & (f['Estado'] == 'PAGADO')]['Monto'].sum() if not f.empty else 0
    p_s = p[(p['Fecha'] < fecha) & (p['Estado'] == 'PAGADO')]['Monto'].sum() if not p.empty else 0
    h_s = h[(h['Fecha'] < fecha) & (h['Estado'] == 'PAGADO')]['Monto'].sum() if not h.empty else 0
    return round(v_s + c_s - f_s - p_s - h_s, 2)

# --- 3. DISEÑO ---
st.set_page_config(page_title="EMI MASTER V74", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #FFD700 !important; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 10px; border-radius: 10px; border: 1px solid #FFD700; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 8px; border-radius: 5px; text-align: center; border: 1px solid #FFD700; margin-bottom: 10px; font-weight: bold; }
    .fila-unificada { padding: 5px; border-bottom: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 PUNTO DE VENTA", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO", value=0.0)
    c_ini = st.number_input("💵 CAJA", value=0.0)
    
    saldo_inicial = calcular_arrastre_total(inicio_mes)
    st.info(f"📅 **Saldo de Arrastre al {inicio_mes}:**\n$ {saldo_inicial}")
    
    df_v = leer_hoja("Ventas"); df_f = leer_hoja("Fijos"); df_h = leer_hoja("Hormiga"); df_p = leer_hoja("Proveedores"); df_c = leer_hoja("Cobros")
    
    v_act = df_v[df_v['Fecha'] >= inicio_mes]['Monto'].sum() if not df_v.empty else 0
    f_act = df_f[(df_f['Fecha'] >= inicio_mes) & (df_f['Estado'] == 'PAGADO')]['Monto'].sum() if not df_f.empty else 0
    p_act = df_p[(df_p['Fecha'] >= inicio_mes) & (df_p['Estado'] == 'PAGADO')]['Monto'].sum() if not df_p.empty else 0
    h_act = df_h[(df_h['Fecha'] >= inicio_mes) & (df_h['Estado'] == 'PAGADO')]['Monto'].sum() if not df_h.empty else 0
    c_act = df_c[(df_c['Fecha'] >= inicio_mes) & (df_c['Estado'] == 'COBRADO')]['Monto'].sum() if not df_c.empty else 0

    st.metric("BALANCE NETO ACTUAL", f"$ {round(b_ini + c_ini + saldo_inicial + v_act + c_act - f_act - p_act - h_act, 2)}")

# --- 4. MÓDULOS DE REGISTRO ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📊 REPORTES"])

def modulo_fila_unica(nombre_hoja, alias, label, icon_ok, estado_ok):
    df_raw = leer_hoja(nombre_hoja)
    df_filtrado = df_raw[(df_raw['Fecha'] >= inicio_mes) | (df_raw['Estado'] == 'PENDIENTE')] if not df_raw.empty else pd.DataFrame()
    st.markdown(f"<div class='sum-box'>TOTAL {nombre_hoja.upper()}: $ {df_filtrado['Monto'].sum() if not df_filtrado.empty else 0}</div>", unsafe_allow_html=True)
    
    nombres = df_raw['Concepto'].unique().tolist() if not df_raw.empty else []
    with st.expander(f"➕ Registrar {label}"):
        with st.form(f"form_{alias}"):
            f_r = st.date_input("Fecha", hoy)
            nom = st.selectbox(f"Sugerencia {label}", ["Escribir nuevo..."] + nombres)
            if nom == "Escribir nuevo...": nom = st.text_input(f"Nombre {label}")
            m_r = st.number_input("Monto $", min_value=0.0)
            if st.form_submit_button("GRABAR"):
                iniciar_conexion().worksheet(nombre_hoja).append_row([str(f_r), sede_act, nom, m_r, "PENDIENTE"])
                st.rerun()

    if not df_filtrado.empty:
        for _, row in df_filtrado.iterrows():
            c1, c2, c3, c4, c5 = st.columns([4, 2, 1, 1, 1])
            c1.write(f"📅 {row['Fecha']} | {row['Concepto']}")
            c2.write(f"**${row['Monto']}**")
            
            # Botón de Cambio de Estado (Pagar/Cobrar)
            if row['Estado'] == "PENDIENTE":
                if c3.button(icon_ok, key=f"btn_ok_{alias}_{row['ID_Fila']}"):
                    iniciar_conexion().worksheet(nombre_hoja).update_cell(row['ID_Fila'], 5, estado_ok)
                    st.rerun()
            else:
                if c3.button("🔄", key=f"btn_rev_{alias}_{row['ID_Fila']}"):
                    iniciar_conexion().worksheet(nombre_hoja).update_cell(row['ID_Fila'], 5, "PENDIENTE")
                    st.rerun()
            
            c4.button("📝", key=f"btn_ed_{alias}_{row['ID_Fila']}")
            if c5.button("🗑️", key=f"btn_del_{alias}_{row['ID_Fila']}"):
                iniciar_conexion().worksheet(nombre_hoja).delete_rows(row['ID_Fila'])
                st.rerun()

with tabs[0]: # VENTAS
    df_v_mes = df_v[df_v['Fecha'] >= inicio_mes] if not df_v.empty else pd.DataFrame()
    st.markdown(f"<div class='sum-box'>TOTAL VENTAS MES: $ {df_v_mes['Monto'].sum() if not df_v_mes.empty else 0}</div>", unsafe_allow_html=True)
    with st.form("fv"):
        f_v = st.date_input("Fecha", hoy); m_v = st.number_input("Valor $", min_value=0.0)
        if st.form_submit_button("GUARDAR VENTA"):
            iniciar_conexion().worksheet("Ventas").append_row([str(f_v), sede_act, "Venta", m_v, "PAGADO"])
            st.rerun()
    if not df_v_mes.empty:
        for _, row in df_v_mes.iterrows():
            c1, c2, c3, c4 = st.columns([5, 2, 1, 1])
            c1.write(f"📅 {row['Fecha']} | Venta")
            c2.write(f"**${row['Monto']}**")
            c3.button("📝", key=f"v_ed_{row['ID_Fila']}")
            if c4.button("🗑️", key=f"v_del_{row['ID_Fila']}"):
                iniciar_conexion().worksheet("Ventas").delete_rows(row['ID_Fila']); st.rerun()

with tabs[1]: modulo_fila_unica("Fijos", "f", "Gasto Fijo", "💸", "PAGADO")
with tabs[2]: modulo_fila_unica("Hormiga", "h", "Gasto Hormiga", "💸", "PAGADO")
with tabs[3]: modulo_fila_unica("Proveedores", "p", "Proveedor", "💸", "PAGADO")
with tabs[4]: modulo_fila_unica("Cobros", "c", "Cuenta Cobro", "💰", "COBRADO")

with tabs[5]:
    st.header("📊 Inteligencia de Negocio")
    rep = st.selectbox("Análisis:", ["Seleccionar...", "Máximo Proveedor", "Ventas vs Gastos"])
    c_f1, c_f2 = st.columns(2)
    s_d = c_f1.date_input("Desde", inicio_mes); e_d = c_f2.date_input("Hasta", hoy)
    # Lógica de reportes...
