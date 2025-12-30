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
        df = pd.DataFrame(conectar().worksheet(hoja).get_all_records())
        if not df.empty:
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        return df
    except: return pd.DataFrame()

# --- 2. ESTILO VISUAL ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1c2e4a !important; }
    [data-testid="stSidebar"] label { color: #FFD700 !important; font-weight: bold; }
    .stMetric { background-color: #d4af37 !important; color: #1c2e4a !important; padding: 15px; border-radius: 12px; border: 2px solid #FFD700; }
    .sum-box { background-color: #1c2e4a; color: #FFD700; padding: 12px; border-radius: 8px; text-align: center; border: 1px solid #FFD700; margin-bottom: 20px; font-weight: bold; font-size: 1.1rem; }
    .card { background-color: white; padding: 20px; border-radius: 15px; border-top: 8px solid #1c2e4a; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BALANCE EN TIEMPO REAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🛡️ EMI MASTER</h1>", unsafe_allow_html=True)
    sede_act = st.selectbox("📍 SELECCIONAR SEDE", ["Matriz", "Sucursal 1", "Sucursal 2"])
    b_ini = st.number_input("🏦 BANCO", value=0.0)
    c_ini = st.number_input("💵 CAJA", value=0.0)
    
    df_v = leer("Ventas"); df_f = leer("Fijos"); df_h = leer("Hormiga"); df_p = leer("Proveedores"); df_c = leer("Cobros")
    
    v_t = df_v['Monto'].sum() if not df_v.empty else 0
    f_p = df_f[df_f['Estado'] == 'PAGADO']['Monto'].sum() if not df_f.empty else 0
    p_p = df_p[df_p['Estado'] == 'PAGADO']['Monto'].sum() if not df_p.empty else 0
    h_p = df_h[df_h['Estado'] == 'PAGADO']['Monto'].sum() if not df_h.empty else 0
    c_p = df_c[df_c['Estado'] == 'COBRADO']['Monto'].sum() if not df_c.empty else 0

    balance = b_ini + c_ini + v_t + c_p - f_p - p_p - h_p
    st.metric("BALANCE NETO REAL", f"$ {round(balance, 2)}")

# --- 4. RENDERIZADO DE MÓDULOS ---
def render_modulo_pro(hoja, alias, label, icn, est_ok, color_btn):
    df = leer(hoja)
    st.markdown(f"<div class='sum-box'>TOTAL {hoja.upper()}: $ {df['Monto'].sum() if not df.empty else 0}</div>", unsafe_allow_html=True)
    
    nombres_memoria = df['Concepto'].unique().tolist() if not df.empty else []
    with st.expander(f"➕ NUEVO REGISTRO: {label}", expanded=True):
        with st.form(f"form_{alias}", clear_on_submit=True):
            f_r = st.date_input("Fecha de Operación", date.today())
            nom = st.selectbox(f"Seleccionar {label}", ["Escribir nuevo..."] + nombres_memoria)
            if nom == "Escribir nuevo...": nom = st.text_input(f"Nombre del {label}")
            m_r = st.number_input("Monto total $", min_value=0.0)
            if st.form_submit_button("GUARDAR EN NUBE"):
                conectar().worksheet(hoja).append_row([str(f_r), sede_act, nom, m_r, "PENDIENTE"])
                st.rerun()

    if not df.empty:
        for i, row in df.iterrows():
            with st.container():
                st.markdown(f"""<div class='card'>
                <p style='margin:0; font-size:0.9rem; color:grey;'>📅 {row['Fecha']} | {row['Sede']}</p>
                <h3 style='margin:0; color:#1c2e4a;'>{row['Concepto']}</h3>
                <h2 style='margin:0; color:{color_btn};'>$ {row['Monto']}</h2>
                <p style='margin:0;'><b>Estado:</b> {row['Estado']}</p>
                </div>""", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns([3, 3, 2])
                if row['Estado'] == "PENDIENTE":
                    if c1.button(f"{icn} MARCAR {est_ok}", key=f"ok_{alias}_{i}"):
                        conectar().worksheet(hoja).update_cell(i + 2, 5, est_ok); st.rerun()
                else:
                    if c1.button(f"🔄 REVERTIR", key=f"rev_{alias}_{i}"):
                        conectar().worksheet(hoja).update_cell(i + 2, 5, "PENDIENTE"); st.rerun()
                
                if c3.button("🗑️", key=f"del_{alias}_{i}"):
                    conectar().worksheet(hoja).delete_rows(i + 2); st.rerun()

# --- 5. PESTAÑAS ---
t1, t2, t3, t4, t5, t6 = st.tabs(["💰 VENTAS", "🏢 FIJOS", "🐜 HORMIGA", "🚛 PROVEEDORES", "📞 COBROS", "📊 REPORTES"])

with t1:
    st.markdown(f"<div class='sum-box'>TOTAL VENTAS: $ {df_v['Monto'].sum() if not df_v.empty else 0}</div>", unsafe_allow_html=True)
    with st.form("fv"):
        f_v = st.date_input("Fecha", date.today())
        m_v = st.number_input("Valor de Venta $", min_value=0.0)
        if st.form_submit_button("REGISTRAR VENTA"):
            conectar().worksheet("Ventas").append_row([str(f_v), sede_act, "Venta Diaria", m_v, "PAGADO"])
            st.rerun()
    st.dataframe(df_v, use_container_width=True)

with t2: render_modulo_pro("Fijos", "f", "Gasto Fijo", "💸", "PAGADO", "#E74C3C")
with t3: render_modulo_pro("Hormiga", "h", "Gasto Hormiga", "💸", "PAGADO", "#E67E22")
with t4: render_modulo_pro("Proveedores", "p", "Proveedor", "💸", "PAGADO", "#C0392B")
with t5: render_modulo_pro("Cobros", "c", "Cuenta Cobro", "💰", "COBRADO", "#27AE60")

# --- 6. MOTOR DE REPORTES CON SELECTOR ---
with t6:
    st.header("📊 Inteligencia y Análisis")
    tipo_rep = st.selectbox("📈 ¿QUÉ REPORTE DESEAS VER?", [
        "Seleccionar...",
        "Análisis de Proveedores (Mayor Gasto)",
        "Gasto Hormiga más Fuerte",
        "Diferencia entre Ventas y Gastos",
        "Comparativa: Matriz vs Sucursales"
    ])
    
    col_f1, col_f2 = st.columns(2)
    start = col_f1.date_input("Desde", date.today().replace(day=1))
    end = col_f2.date_input("Hasta", date.today())
    
    def f_df(df): return df[(df['Fecha'] >= start) & (df['Fecha'] <= end)] if not df.empty else df

    if tipo_rep == "Análisis de Proveedores (Mayor Gasto)":
        df_p_f = f_df(df_p)
        if not df_p_f.empty:
            st.plotly_chart(px.pie(df_p_f.groupby("Concepto")["Monto"].sum().reset_index(), values="Monto", names="Concepto", title="Distribución de Pagos a Proveedores", hole=.4))
    
    elif tipo_rep == "Gasto Hormiga más Fuerte":
        df_h_f = f_df(df_h)
        if not df_h_f.empty:
            st.plotly_chart(px.bar(df_h_f.groupby("Concepto")["Monto"].sum().sort_values(ascending=False).reset_index(), x="Concepto", y="Monto", color="Monto", title="Ranking de Gastos Hormiga"))

    elif tipo_rep == "Diferencia entre Ventas y Gastos":
        tot_v = f_df(df_v)['Monto'].sum() if not df_v.empty else 0
        tot_g = (f_df(df_f)['Monto'].sum() + f_df(df_p)['Monto'].sum() + f_df(df_h)['Monto'].sum())
        df_res = pd.DataFrame({"Categoría": ["Ventas", "Gastos Totales"], "Monto": [tot_v, tot_g]})
        st.plotly_chart(px.bar(df_res, x="Categoría", y="Monto", color="Categoría", title="Balance Operativo"))

    elif tipo_rep == "Comparativa: Matriz vs Sucursales":
        if not df_v.empty:
            st.plotly_chart(px.bar(f_df(df_v).groupby("Sede")["Monto"].sum().reset_index(), x="Sede", y="Monto", color="Sede", barmode="group", title="Ventas por Punto de Venta"))
