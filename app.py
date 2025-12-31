import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN OPTIMIZADA ---
def conectar():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    pk = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCqgXfcDtZY14MI\nvxK1rB3irY3EAWUCXy1AJgrLZA4fY3Y1AJ2RkGas9FT8contqzOCISENmHKRUUWe\nnCOjZI8E7awOSJ8/6mmuiGp9tkXiPdSSKmwgPGm9vfSCsZ8XTE22VyNNYHLVHcpC\nW7FM076/sRxlRpX4VQx5lafz2BbX+ehAQy/pKhlZgy2ompl9HH3GLt8shoXB6Np2\nkjRtwXngjV16+awj7qBjGpjJYZbDZLBkreV0RHdDG8urcMkYbgw/0rhpw3thHFBF\nvpcCPriyADYZml5RYSyIfE48uETq1d6Nz+wpQLbE8FqQUkTQX4086crVnh184xPG\nCM3Gpva5AgMBAAECggEARjUYTw72+M8IwA25XQAZsDBpeudeGbtqDQt9D2HMJOWW\nE14FA56zgIz8/5QEMk5336HXk9sNdcPCyHwfepSaBVv+KEWD+VQDHyBBxTDMFswB\n3wvDyQRHQB9a8oPD79p191prCV3o+tMQ6QELgQiBdzos6JDHiOEwSVIzvYbhZR1w\nkcanR9TwD1Zzv2IHSk35WG01brKE4D3A0eNROCz+AmTEx9BAeB3QLruNqibNltyS\nYrLK4oJ6P4NBohLgkKJeGr8FIAmKOtA02jBWF0o5NbHzGTvLfJFXTUNDrGrejIWm\nyy7ILvEHqCRB3zwV8bLdi4i38MxmMxQ3jq6x9+gqTwKBgQDS7LuLv59Xbnnc/HO3\nCJvjiMjDqtfF9jpLqb1ViQ7jd0dZ8LeX7qOd791z/7Otn9LydcmhSjlf+HlvDXMo\nKYtFpUmSzjMJNrEIz51jmUNuSZJE3KiZnDC7VrQUkwb5iFyM90jp0g5ibDIyuH6Z\npf7BNbuVS5NNGJqopfjOuI0phwKBgQDO8X5TLO5wT91F2/11tkjVkKl6SucgkgpK\n3FTPdDo9NI3PsyxlCjAlPxkvkT53AR88klf7lF7Dz0yY1bXFcS9CUSfn7h6eZfPi\nX5yMIJnNRqkVZ2XZSkqX2LZIMJiT2BsE5mwv5wtVf2WL0AxZZeYRHDlWTkJlWaPF\n3E1eR8XtvwKBgAosYutdpbjY2kXfY1Frt+EkotJVNi0VMECgAkLS5oXwJd/frWtF\nllyyyhKjPa5dLBaHud7uro/Dc0/47Rn9zvrf+wl6qpmCKs3K/cNlDAyQvd5Wakdm\ci9HAk6PvOFiQ1yFPN4SRKFYqJ8rqOeOSxhUmCSeTY+FZUhHIRYPbreXAoGBAIcQ\nyxhSXRVkqtDrslPfs03gaxzsQknZx2nwwFHeVByabmw/TxxrN903f6KyM4jMbKzF\n/zKuNeOrKx0dbtP8+ZFZEqinm8haVoFLUguLQ5bdJYJYx/q4KFNPGDmprgvgolHi\nan4hWB5nVcmY8lZu0WgdebbAwUkQ5nk/PifoxGBVAoGAYPMLrEuJlpnJM6SJ4pfd\ nx/ggxcwRkCo9duUzkAndSS+q4326v6llE7PNLBONzksP4DJntG1saa0xZISSqueX\nKYPHsPn0nlseGFR1yNFXZg32FsIlKeLsCkIgrwtge7Qjccc7F8gOO7faV6strfq+\nKFggcG+4j6j1Xu1LpRniQy4=\n-----END PRIVATE KEY-----\n"
    creds_dict = {
        "type": "service_account",
        "project_id": "fabled-ranger-480412-b9",
        "private_key_id": "5be77e02ce33b4b12f69dfdda644de61e5ff3d54",
        "private_key": pk.replace('\\n', '\n'),
        "client_email": "emi-database@fabled-ranger-480412-b9.iam.gserviceaccount.com",
        "client_id": "102764735047338306868"
    }
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)).open("EMI_DATA_PRO")

def leer(hoja):
    try:
        ws = conectar().worksheet(hoja)
        df = pd.DataFrame(ws.get_all_records())
        if not df.empty:
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            df['idx'] = df.index + 2
            if 'Estado' not in df.columns: df['Estado'] = 'PENDIENTE'
        return df
    except: return pd.DataFrame()

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="EMI MASTER V150", layout="wide")
hoy = date.today()
primer_dia = hoy.replace(day=1)

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; border-radius: 8px; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #FFD700; font-weight: bold; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL (SUMATORIAS) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede = st.selectbox("📍 PUNTO DE VENTA", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 SALDO BANCO", value=0.0)
    c_ini = st.number_input("💵 SALDO CAJA", value=0.0)
    
    df_v = leer("Ventas"); df_f = leer("Fijos"); df_p = leer("Proveedores"); df_c = leer("Cobros"); df_h = leer("Hormiga")
    
    # Saldo Arrastre y Balance
    v_h = df_v[df_v['Fecha'] < primer_dia]['Monto'].sum() if not df_v.empty else 0
    c_h = df_c[(df_c['Fecha'] < primer_dia) & (df_c['Estado'] == 'COBRADO')]['Monto'].sum() if not df_c.empty else 0
    g_h = (df_f[df_f['Estado'] == 'PAGADO']['Monto'].sum() + df_p[df_p['Estado'] == 'PAGADO']['Monto'].sum())
    
    saldo_arrastre = v_h + c_h - g_h
    st.info(f"💾 **Arrastre:** $ {saldo_arrastre}")
    
    v_mes = df_v[df_v['Fecha'] >= primer_dia]['Monto'].sum() if not df_v.empty else 0
    st.metric("BALANCE NETO ACTUAL", f"$ {round(b_ini + c_ini + saldo_arrastre + v_mes, 2)}")

# --- 4. RENDERIZADO POR PESTAÑAS ---
tabs = st.tabs(["💰 VENTAS", "🏢 GASTOS", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

def render_modulo_compacto(hoja, alias, label, txt_ok):
    df_raw = leer(hoja)
    df = df_raw[(df_raw['Fecha'] >= primer_dia) | (df_raw['Estado'] == 'PENDIENTE')] if not df_raw.empty else pd.DataFrame()
    st.markdown(f"<div class='sum-box'>TOTAL {hoja.upper()}: $ {df['Monto'].sum() if not df.empty else 0}</div>", unsafe_allow_html=True)
    
    with st.expander(f"➕ Registrar {label}"):
        with st.form(f"form_{alias}", clear_on_submit=True):
            f_r = st.date_input("Fecha", hoy); det = st.text_input("Detalle"); m_r = st.number_input("Monto", min_value=0.0)
            if st.form_submit_button("GRABAR"):
                conectar().worksheet(hoja).append_row([str(f_r), sede, det, m_r, "PENDIENTE"])
                st.rerun()

    if not df.empty:
        for _, row in df.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([5, 2, 2])
                c1.write(f"📅 {row['Fecha']} | {row['Concepto']}")
                c2.write(f"**${row['Monto']}**")
                
                # UN SOLO BOTÓN DE ACCIÓN PARA VELOCIDAD MÓVIL
                opcion = c3.selectbox("Acción", ["Seleccionar...", f"Marcar {txt_ok}", "Revertir", "Borrar"], key=f"act_{alias}_{row['idx']}")
                
                if opcion == f"Marcar {txt_ok}":
                    conectar().worksheet(hoja).update_cell(row['idx'], 5, txt_ok); st.rerun()
                elif opcion == "Revertir":
                    conectar().worksheet(hoja).update_cell(row['idx'], 5, "PENDIENTE"); st.rerun()
                elif opcion == "Borrar":
                    conectar().worksheet(hoja).delete_rows(row['idx']); st.rerun()
            st.divider()

with tabs[0]: # VENTAS
    v_mes = df_v[df_v['Fecha'] >= primer_dia]
    st.markdown(f"<div class='sum-box'>TOTAL VENTAS MES: $ {v_mes['Monto'].sum() if not v_mes.empty else 0}</div>", unsafe_allow_html=True)
    with st.form("fv"):
        f_v = st.date_input("Fecha Venta", hoy); m_v = st.number_input("Valor Venta $", min_value=0.0)
        if st.form_submit_button("GUARDAR VENTA"):
            conectar().worksheet("Ventas").append_row([str(f_v), sede, "Venta Diaria", m_v, "PAGADO"])
            st.rerun()
    if not v_mes.empty:
        for _, row in v_mes.iterrows():
            c1, c2, c3 = st.columns([6, 2, 2])
            c1.write(f"📅 {row['Fecha']} | Venta"); c2.write(f"**${row['Monto']}**")
            if c3.button("🗑️ Borrar", key=f"vdel_{row['idx']}"):
                conectar().worksheet("Ventas").delete_rows(row['idx']); st.rerun()

with tabs[1]: render_modulo_compacto("Fijos", "f", "Gasto", "PAGADO")
with tabs[2]: render_modulo_compacto("Proveedores", "p", "Proveedor", "PAGADO")
with tabs[3]: render_modulo_compacto("Cobros", "c", "Cuenta Cobro", "COBRADO")
