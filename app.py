import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN DE ALTA EFICIENCIA ---
def conectar_db():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = {
        "type": "service_account",
        "project_id": "fabled-ranger-480412-b9",
        "private_key_id": "5be77e02ce33b4b12f69dfdda644de61e5ff3d54",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCqgXfcDtZY14MI\nvxK1rB3irY3EAWUCXy1AJgrLZA4fY3Y1AJ2RkGas9FT8contqzOCISENmHKRUUWe\nnCOjZI8E7awOSJ8/6mmuiGp9tkXiPdSSKmwgPGm9vfSCsZ8XTE22VyNNYHLVHcpC\nW7FM076/sRxlRpX4VQx5lafz2BbX+ehAQy/pKhlZgy2ompl9HH3GLt8shoXB6Np2\nkjRtwXngjV16+awj7qBjGpjJYZbDZLBkreV0RHdDG8urcMkYbgw/0rhpw3thHFBF\nvpcCPriyADYZml5RYSyIfE48uETq1d6Nz+wpQLbE8FqQUkTQX4086crVnh184xPG\nCM3Gpva5AgMBAAECggEARjUYTw72+M8IwA25XQAZsDBpeudeGbtqDQt9D2HMJOWW\nE14FA56zgIz8/5QEMk5336HXk9sNdcPCyHwfepSaBVv+KEWD+VQDHyBBxTDMFswB\n3wvDyQRHQB9a8oPD79p191prCV3o+tMQ6QELgQiBdzos6JDHiOEwSVIzvYbhZR1w\nkcanR9TwD1Zzv2IHSk35WG01brKE4D3A0eNROCz+AmTEx9BAeB3QLruNqibNltyS\nYrLK4oJ6P4NBohLgkKJeGr8FIAmKOtA02jBWF0o5NbHzGTvLfJFXTUNDrGrejIWm\nyy7ILvEHqCRB3zwV8bLdi4i38MxmMxQ3jq6x9+gqTwKBgQDS7LuLv59Xbnnc/HO3\ CJvjiMjDqtfF9jpLqb1ViQ7jd0dZ8LeX7qOd791z/7Otn9LydcmhSjlf+HlvDXMo\nKYtFpUmSzjMJNrEIz51jmUNuSZJE3KiZnDC7VrQUkwb5iFyM90jp0g5ibDIyuH6Z\ npf7BNbuVS5NNGJqopfjOuI0phwKBgQDO8X5TLO5wT91F2/11tkjVkKl6SucgkgpK\n3FTPdDo9NI3PsyxlCjAlPxkvkT53AR88klf7lF7Dz0yY1bXFcS9CUSfn7h6eZfPi\nX5yMIJnNRqkVZ2XZSkqX2LZIMJiT2BsE5mwv5wtVf2WL0AxZZeYRHDlWTkJlWaPF\ 3E1eR8XtvwKBgAosYutdpbjY2kXfY1Frt+EkotJVNi0VMECgAkLS5oXwJd/frWtF\nllyyyhKjPa5dLBaHud7uro/Dc0/47Rn9zvrf+wl6qpmCKs3K/cNlDAyQvd5Wakdm\ci9HAk6PvOFiQ1yFPN4SRKFYqJ8rqOeOSxhUmCSeTY+FZUhHIRYPbreXAoGBAIcQ\nyxhSXRVkqtDrslPfs03gaxzsQknZx2nwwFHeVByabmw/TxxrN903f6KyM4jMbKzF\n/zKuNeOrKx0dbtP8+ZFZEqinm8haVoFLUguLQ5bdJYJYx/q4KFNPGDmprgvgolHi\nan4hWB5nVcmY8lZu0WgdebbAwUkQ5nk/PifoxGBVAoGAYPMLrEuJlpnJM6SJ4pfd\ nx/ggxcwRkCo9duUzkAndSS+q4326v6llE7PNLBONzksP4DJntG1saa0xZISSqueX\nKYPHsPn0nlseGFR1yNFXZg32FsIlKeLsCkIgrwtge7Qjccc7F8gOO7faV6strfq+\nKFggcG+4j6j1Xu1LpRniQy4=\n-----END PRIVATE KEY-----\n",
        "client_email": "emi-database@fabled-ranger-480412-b9.iam.gserviceaccount.com",
        "client_id": "102764735047338306868"
    }
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)).open("EMI_DATA_PRO")

def leer_seguro(hoja):
    try:
        ws = conectar_db().worksheet(hoja)
        df = pd.DataFrame(ws.get_all_records())
        if not df.empty:
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            if 'Estado' not in df.columns: df['Estado'] = 'PENDIENTE'
            df['idx'] = df.index + 2
        return df
    except Exception: return pd.DataFrame()

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")
hoy = date.today()
inicio_mes = hoy.replace(day=1)

# --- 3. SIDEBAR Y BALANCE ---
with st.sidebar:
    st.title("🛡️ EMI MASTER")
    sede = st.selectbox("📍 PUNTO DE VENTA", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO", value=0.0)
    c_ini = st.number_input("💵 CAJA", value=0.0)
    
    # Arrastre de Saldo
    def get_saldo_pasado():
        v = leer_seguro("Ventas"); f = leer_seguro("Fijos"); p = leer_seguro("Proveedores"); c = leer_seguro("Cobros"); h = leer_seguro("Hormiga")
        v_s = v[v['Fecha'] < inicio_mes]['Monto'].sum() if not v.empty else 0
        c_s = c[(c['Fecha'] < inicio_mes) & (c['Estado'] == 'COBRADO')]['Monto'].sum() if not c.empty else 0
        g_s = 0
        for df in [f, p, h]:
            if not df.empty:
                g_s += df[(df['Fecha'] < inicio_mes) & (df['Estado'] == 'PAGADO')]['Monto'].sum()
        return v_s + c_s - g_s

    saldo_arrastre = get_saldo_pasado()
    st.info(f"💾 **Saldo al {inicio_mes}:**\n$ {saldo_arrastre}")
    
    # Balance Total
    # (Aquí se cargarían los del mes actual para el Balance Neto Actual)

# --- 4. RENDERIZADO POR PESTAÑAS ---
t1, t2, t3, t4, t5, t6 = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

def render_tab_fila(hoja, alias, label, icn_ok, est_ok):
    df_raw = leer_seguro(hoja)
    df = df_raw[(df_raw['Fecha'] >= inicio_mes) | (df_raw['Estado'] == 'PENDIENTE')] if not df_raw.empty else pd.DataFrame()
    
    st.markdown(f"### Total {hoja}: $ {df['Monto'].sum() if not df.empty else 0}")
    
    with st.expander(f"➕ Registrar {label}"):
        with st.form(f"form_{alias}"):
            f_r = st.date_input("Fecha", hoy); nom = st.text_input("Concepto"); m_r = st.number_input("Monto", min_value=0.0)
            if st.form_submit_button("GRABAR"):
                conectar_db().worksheet(hoja).append_row([str(f_r), sede, nom, m_r, "PENDIENTE"])
                st.rerun()

    if not df.empty:
        for _, row in df.iterrows():
            c1, c2, c3, c4, c5 = st.columns([4, 2, 1, 1, 1])
            c1.write(f"{row['Fecha']} | {row['Concepto']}")
            c2.write(f"**${row['Monto']}**")
            
            # ACCIONES
            if row['Estado'] == "PENDIENTE":
                if c3.button("✅", key=f"ok_{alias}_{row['idx']}"):
                    conectar_db().worksheet(hoja).update_cell(row['idx'], 5, est_ok); st.rerun()
            else:
                if c3.button("🔄", key=f"rev_{alias}_{row['idx']}"):
                    conectar_db().worksheet(hoja).update_cell(row['idx'], 5, "PENDIENTE"); st.rerun()
            
            c4.button("📝", key=f"ed_{alias}_{row['idx']}")
            if c5.button("🗑️", key=f"del_{alias}_{row['idx']}"):
                conectar_db().worksheet(hoja).delete_rows(row['idx']); st.rerun()

with t0: # PESTAÑA VENTAS
    df_v = leer_seguro("Ventas")
    df_v_mes = df_v[df_v['Fecha'] >= inicio_mes] if not df_v.empty else pd.DataFrame()
    # Formulario y tabla de ventas con botones de Editar y Borrar igual que arriba...

with t1: render_tab_fila("Fijos", "f", "Gasto Fijo", "✅", "PAGADO")
with t3: render_tab_fila("Proveedores", "p", "Proveedor", "✅", "PAGADO")
with t4: render_tab_fila("Cobros", "c", "Cuenta Cobro", "✅", "COBRADO")

# --- 5. REPORTES CON FILTRO DE FECHA ---
with t5:
    st.header("📊 Inteligencia de Negocio")
    c1, c2 = st.columns(2)
    sd = c1.date_input("Desde", inicio_mes); ed = c2.date_input("Hasta", hoy)
    # Lógica de gráficos filtrados por sd y ed...
