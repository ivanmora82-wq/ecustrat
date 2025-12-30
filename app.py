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
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCqgXfcDtZY14MI\nvxK1rB3irY3EAWUCXy1AJgrLZA4fY3Y1AJ2RkGas9FT8contqzOCISENmHKRUUWe\nnCOjZI8E7awOSJ8/6mmuiGp9tkXiPdSSKmwgPGm9vfSCsZ8XTE22VyNNYHLVHcpC\nW7FM076/sRxlRpX4VQx5lafz2BbX+ehAQy/pKhlZgy2ompl9HH3GLt8shoXB6Np2\nkjRtwXngjV16+awj7qBjGpjJYZbDZLBkreV0RHdDG8urcMkYbgw/0rhpw3thHFBF\nvpcCPriyADYZml5RYSyIfE48uETq1d6Nz+wpQLbE8FqQUkTQX4086crVnh184xPG\nCM3Gpva5AgMBAAECggEARjUYTw72+M8IwA25XQAZsDBpeudeGbtqDQt9D2HMJOWW\nE14FA56zgIz8/5QEMk5336HXk9sNdcPCyHwfepSaBVv+KEWD+VQDHyBBxTDMFswB\n3wvDyQRHQB9a8oPD79p191prCV3o+tMQ6QELgQiBdzos6JDHiOEwSVIzvYbhZR1w\nkcanR9TwD1Zzv2IHSk35WG01brKE4D3A0eNROCz+AmTEx9BAeB3QLruNqibNltyS\nYrLK4oJ6P4NBohLgkKJeGr8FIAmKOtA02jBWF0o5NbHzGTvLfJFXTUNDrGrejIWm\nyy7ILvEHqCRB3zwV8bLdi4i38MxmMxQ3jq6x9+gqTwKBgQDS7LuLv59Xbnnc/HO3\nCJvjiMjDqtfF9jpLqb1ViQ7jd0dZ8LeX7qOd791z/7Otn9LydcmhSjlf+HlvDXMo\nKYtFpUmSzjMJNrEIz51jmUNuSZJE3KiZnDC7VrQUkwb5iFyM90jp0g5ibDIyuH6Z\npf7BNbuVS5NNGJqopfjOuI0phwKBgQDO8X5TLO5wT91F2/11tkjVkKl6SucgkgpK\n3FTPdDo9NI3PsyxlCjAlPxkvkT53AR88klf7lF7Dz0yY1bXFcS9CUSfn7h6eZfPi\nX5yMIJnNRqkVZ2XZSkqX2LZIMJiT2BsE5mwv5wtVf2WL0AxZZeYRHDlWTkJlWaPF\n3E1eR8XtvwKBgAosYutdpbjY2kXfY1Frt+EkotJVNi0VMECgAkLS5oXwJd/frWtF\nllyyyhKjPa5dLBaHud7uro/Dc0/47Rn9zvrf+wl6qpmCKs3K/cNlDAyQvd5Wakdm\ci9HAk6PvOFiQ1yFPN4SRKFYqJ8rqOeOSxhUmCSeTY+FZUhHIRYPbreXAoGBAIcQ\nyxhSXRVkqtDrslPfs03gaxzsQknZx2nwwFHeVByabmw/TxxrN903f6KyM4jMbKzF\n/zKuNeOrKx0dbtP8+ZFZEqinm8haVoFLUguLQ5bdJYJYx/q4KFNPGDmprgvgolHi\nan4hWB5nVcmY8lZu0WgdebbAwUkQ5nk/PifoxGBVAoGAYPMLrEuJlpnJM6SJ4pfd\nx/ggxcwRkCo9duUzkAndSS+q4326v6llE7PNLBONzksP4DJntG1saa0xZISSqueX\nKYPHsPn0nlseGFR1yNFXZg32FsIlKeLsCkIgrwtge7Qjccc7F8gOO7faV6strfq+\nKFggcG+4j6j1Xu1LpRniQy4=\n-----END PRIVATE KEY-----\n",
        "client_email": "emi-database@fabled-ranger-480412-b9.iam.gserviceaccount.com",
        "client_id": "102764735047338306868"
    }
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds).open("EMI_DATA_PRO")
    except: return None

def leer(hoja):
    try:
        ws = conectar().worksheet(hoja)
        df = pd.DataFrame(ws.get_all_records())
        if not df.empty:
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            # Aseguramos columna Estado
            if 'Estado' not in df.columns: df['Estado'] = 'PENDIENTE'
            # Guardamos el índice original para no perder la fila al filtrar
            df['row_idx'] = df.index + 2
        return df
    except: return pd.DataFrame()

# --- 2. LÓGICA DE SALDO Y ARRASTRE ---
hoy = date.today()
primer_dia_mes = hoy.replace(day=1)

def calcular_arrastre(fecha):
    v = leer("Ventas"); f = leer("Fijos"); p = leer("Proveedores"); c = leer("Cobros"); h = leer("Hormiga")
    v_s = v[v['Fecha'] < fecha]['Monto'].sum() if not v.empty else 0
    c_s = c[(c['Fecha'] < fecha) & (c['Estado'] == 'COBRADO')]['Monto'].sum() if not c.empty else 0
    f_s = f[(f['Fecha'] < fecha) & (f['Estado'] == 'PAGADO')]['Monto'].sum() if not f.empty else 0
    p_s = p[(p['Fecha'] < fecha) & (p['Estado'] == 'PAGADO')]['Monto'].sum() if not p.empty else 0
    h_s = h[(h['Fecha'] < fecha) & (h['Estado'] == 'PAGADO')]['Monto'].sum() if not h.empty else 0
    return v_s + c_s - f_s - p_s - h_s

# --- 3. DISEÑO ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 10px; border-radius: 10px; border: 1px solid #FFD700; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #FFD700; margin-bottom: 20px; font-weight: bold; }
    .stButton>button { height: 35px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO", value=0.0)
    c_ini = st.number_input("💵 CAJA", value=0.0)
    
    saldo_arrastre = calcular_arrastre(primer_dia_mes)
    st.info(f"💾 **Saldo al {primer_dia_mes}:**\n$ {saldo_arrastre}")
    
    df_v = leer("Ventas"); df_f = leer("Fijos"); df_h = leer("Hormiga"); df_p = leer("Proveedores"); df_c = leer("Cobros")
    
    # Balance Real (Mes actual + Arrastre)
    v_m = df_v[df_v['Fecha'] >= primer_dia_mes]['Monto'].sum() if not df_v.empty else 0
    f_m = df_f[(df_f['Fecha'] >= primer_dia_mes) & (df_f['Estado'] == 'PAGADO')]['Monto'].sum() if not df_f.empty else 0
    p_m = df_p[(df_p['Fecha'] >= primer_dia_mes) & (df_p['Estado'] == 'PAGADO')]['Monto'].sum() if not df_p.empty else 0
    h_m = df_h[(df_h['Fecha'] >= primer_dia_mes) & (df_h['Estado'] == 'PAGADO')]['Monto'].sum() if not df_h.empty else 0
    c_m = df_c[(df_c['Fecha'] >= primer_dia_mes) & (df_c['Estado'] == 'COBRADO')]['Monto'].sum() if not df_c.empty else 0

    st.metric("BALANCE NETO ACTUAL", f"$ {round(b_ini + c_ini + saldo_arrastre + v_m + c_m - f_m - p_m - h_m, 2)}")

# --- 4. RENDERIZADO EN FILA ÚNICA REAL ---
tabs = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

def render_modulo(hoja, alias, label, icn_ok, est_ok):
    df_all = leer(hoja)
    df_ver = df_all[(df_all['Fecha'] >= primer_dia_mes) | (df_all['Estado'] == 'PENDIENTE')] if not df_all.empty else pd.DataFrame()
    
    st.markdown(f"<div class='sum-box'>TOTAL {hoja.upper()}: $ {df_ver['Monto'].sum() if not df_ver.empty else 0}</div>", unsafe_allow_html=True)
    
    nombres_list = df_all['Concepto'].unique().tolist() if not df_all.empty else []
    with st.expander(f"➕ Registrar {label}"):
        with st.form(f"f_{alias}", clear_on_submit=True):
            f_r = st.date_input("Fecha", hoy)
            nom = st.selectbox(f"Sugerencia {label}", ["Nuevo..."] + nombres_list)
            if nom == "Nuevo...": nom = st.text_input(f"Escriba {label}")
            m_r = st.number_input("Monto", min_value=0.0)
            if st.form_submit_button("GRABAR"):
                conectar().worksheet(hoja).append_row([str(f_r), sede_act, nom, m_r, "PENDIENTE"])
                st.rerun()

    if not df_ver.empty:
        for _, row in df_ver.iterrows():
            c1, c2, c3, c4, c5 = st.columns([4, 2, 1, 1, 1])
            c1.write(f"{row['Fecha']} | {row['Concepto']}")
            c2.write(f"**${row['Monto']}**")
            
            # Botón Acción (Corregido con row_idx)
            if row['Estado'] == "PENDIENTE":
                if c3.button(icn_ok, key=f"ok_{alias}_{row['row_idx']}"):
                    conectar().worksheet(hoja).update_cell(row['row_idx'], 5, est_ok); st.rerun()
            else:
                if c3.button("🔄", key=f"rev_{alias}_{row['row_idx']}"):
                    conectar().worksheet(hoja).update_cell(row['row_idx'], 5, "PENDIENTE"); st.rerun()
            
            c4.button("📝", key=f"ed_{alias}_{row['row_idx']}")
            if c5.button("🗑️", key=f"del_{alias}_{row['row_idx']}"):
                conectar().worksheet(hoja).delete_rows(row['row_idx']); st.rerun()

with tabs[0]: # VENTAS CON CONTROL
    df_v_mes = df_v[df_v['Fecha'] >= primer_dia_mes] if not df_v.empty else pd.DataFrame()
    st.markdown(f"<div class='sum-box'>TOTAL VENTAS MES: $ {df_v_mes['Monto'].sum() if not df_v_mes.empty else 0}</div>", unsafe_allow_html=True)
    with st.form("fv"):
        f_v = st.date_input("Fecha Venta", hoy); m_v = st.number_input("Monto Venta", min_value=0.0)
        if st.form_submit_button("GRABAR VENTA"):
            conectar().worksheet("Ventas").append_row([str(f_v), sede_act, "Venta Diaria", m_v, "PAGADO"])
            st.rerun()
    if not df_v_mes.empty:
        for _, row in df_v_mes.iterrows():
            c1, c2, c3, c4 = st.columns([5, 2, 1, 1])
            c1.write(f"{row['Fecha']} | {row['Concepto']}")
            c2.write(f"**${row['Monto']}**")
            c3.button("📝", key=f"ed_v_{row['row_idx']}")
            if c4.button("🗑️", key=f"del_v_{row['row_idx']}"):
                conectar().worksheet("Ventas").delete_rows(row['row_idx']); st.rerun()

with tabs[1]: render_modulo("Fijos", "f", "Gasto Fijo", "💸", "PAGADO")
with tabs[2]: render_modulo("Hormiga", "h", "Gasto Hormiga", "💸", "PAGADO")
with tabs[3]: render_modulo("Proveedores", "p", "Proveedor", "💸", "PAGADO")
with tabs[4]: render_modulo("Cobros", "c", "Cuenta Cobro", "💰", "COBRADO")

with tabs[5]:
    st.header("📊 Reportes Selectivos")
    rep = st.selectbox("¿Qué desea analizar?", ["Seleccionar...", "Máximo Proveedor", "Gasto Hormiga Fuerte", "Comparativa: Matriz vs Sucursales", "Ventas vs Gastos"])
    col_a, col_b = st.columns(2)
    inicio_d = col_a.date_input("Desde", primer_dia_mes)
    fin_d = col_b.date_input("Hasta", hoy)
    
    def filtrar(df): return df[(df['Fecha'] >= inicio_d) & (df['Fecha'] <= fin_d)] if not df.empty else df

    if rep == "Máximo Proveedor" and not df_p.empty:
        st.plotly_chart(px.pie(filtrar(df_p).groupby("Concepto")["Monto"].sum().reset_index(), values="Monto", names="Concepto", hole=.4))
    elif rep == "Ventas vs Gastos":
        v = filtrar(df_v)['Monto'].sum(); g = filtrar(df_f)['Monto'].sum() + filtrar(df_p)['Monto'].sum() + filtrar(df_h)['Monto'].sum()
        st.plotly_chart(px.bar(pd.DataFrame({"Tipo": ["Ventas", "Gastos"], "Monto": [v, g]}), x="Tipo", y="Monto", color="Tipo"))
