import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- 1. CONEXIÓN Y CACHÉ ---
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
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)).open("EMI_DATA_PRO")

def leer_df(hoja):
    ws = conectar().worksheet(hoja)
    df = pd.DataFrame(ws.get_all_records())
    if not df.empty:
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        df['row'] = df.index + 2
    return df

# --- 2. DISEÑO ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")
st.markdown("""
    <style>
    .stButton>button { border-radius: 5px; height: 32px; width: 100%; font-weight: bold; }
    .legend { background-color: #f0f2f6; padding: 10px; border-radius: 8px; margin-bottom: 20px; font-size: 0.85rem; border-left: 5px solid #1c2e4a; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGICA DE ARRASTRE ---
hoy = date.today()
inicio_mes = hoy.replace(day=1)

with st.sidebar:
    st.title("🛡️ EMI MASTER")
    sede = st.selectbox("📍 PUNTO DE VENTA", ["Matriz", "Sucursal 1", "Sucursal 2"])
    banco = st.number_input("🏦 BANCO", value=0.0)
    caja = st.number_input("💵 CAJA", value=0.0)
    
    # Balance e Historial
    df_v = leer_df("Ventas"); df_f = leer_df("Fijos"); df_p = leer_df("Proveedores"); df_c = leer_df("Cobros"); df_h = leer_df("Hormiga")
    
    # Saldo Arrastre Simplificado
    saldo_historico = df_v[df_v['Fecha'] < inicio_mes]['Monto'].sum() # Ejemplo simplificado
    st.info(f"💾 **Saldo de Arrastre:** $ {saldo_historico}")

# --- 4. RENDERIZADO CON LEYENDA ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROV", "📞 COBROS", "📊 REPORTES"])

def modulo_con_leyenda(hoja, alias, label, icn, txt_ok, color):
    # LEYENDA VISUAL PARA EL CLIENTE
    st.markdown(f"""
    <div class="legend">
        <b>Guía Rápida:</b> {icn} = {txt_ok} | 🔄 = Revertir | ✏️ = Editar | 🗑️ = Borrar
    </div>
    """, unsafe_allow_html=True)
    
    df = leer_df(hoja)
    df_v = df[(df['Fecha'] >= inicio_mes) | (df['Estado'] == 'PENDIENTE')] if not df.empty else pd.DataFrame()
    
    # Listado en fila única con botones
    if not df_v.empty:
        for _, row in df_v.iterrows():
            c1, c2, c3, c4, c5 = st.columns([4, 2, 1, 1, 1])
            c1.write(f"{row['Fecha']} | {row['Concepto']}")
            c2.write(f"**${row['Monto']}**")
            
            if row['Estado'] == "PENDIENTE":
                if c3.button(icn, key=f"ok_{alias}_{row['row']}"):
                    conectar().worksheet(hoja).update_cell(row['row'], 5, txt_ok); st.rerun()
            else:
                if c3.button("🔄", key=f"rev_{alias}_{row['row']}"):
                    conectar().worksheet(hoja).update_cell(row['row'], 5, "PENDIENTE"); st.rerun()
            
            c4.button("✏️", key=f"ed_{alias}_{row['row']}")
            if c5.button("🗑️", key=f"del_{alias}_{row['row']}"):
                conectar().worksheet(hoja).delete_rows(row['row']); st.rerun()

with tabs[1]: modulo_con_leyenda("Fijos", "f", "Gasto Fijo", "🔵", "PAGADO", "blue")
with tabs[4]: modulo_con_leyenda("Cobros", "c", "Cuenta Cobro", "🟢", "COBRADO", "green")

# --- VENTAS CON BOTONES ---
with tabs[0]:
    df_ventas_mes = df_v[df_v['Fecha'] >= inicio_mes] if not df_v.empty else pd.DataFrame()
    if not df_ventas_mes.empty:
        for _, row in df_ventas_mes.iterrows():
            c1, c2, c3, c4 = st.columns([5, 2, 1, 1])
            c1.write(f"{row['Fecha']} | Venta")
            c2.write(f"**${row['Monto']}**")
            c3.button("✏️", key=f"v_ed_{row['row']}")
            if c4.button("🗑️", key=f"v_del_{row['row']}"):
                conectar().worksheet("Ventas").delete_rows(row['row']); st.rerun()
