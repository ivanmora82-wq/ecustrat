import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pandas as pd
import base64
import json
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="EMI MASTER PRO", layout="wide", initial_sidebar_state="collapsed")

# --- DISEÑO VISUAL CORPORATIVO (Dorado y Negro) ---
st.markdown("""
    <style>
    .stApp { background-color: #111111; color: #FFFFFF; }
    .logo-container {
        display: flex;
        justify-content: center;
        padding: 20px;
        background-color: #1a1a1a;
        border-bottom: 2px solid #d4af37;
    }
    .stButton>button {
        width: 100%;
        height: 80px;
        font-size: 22px !important;
        font-weight: bold !important;
        border-radius: 15px;
        background: linear-gradient(135deg, #d4af37 0%, #aa8a2e 100%);
        color: #000000;
        border: none;
        margin-top: 10px;
    }
    .metric-card {
        background: #1e1e1e;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #333;
        text-align: center;
        margin-bottom: 10px;
    }
    .stTabs [aria-selected="true"] { background-color: #d4af37 !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

def conectar_db():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Obtenemos el secreto
        encoded_creds = st.secrets["gcp_service_account"]["encoded_creds"]
        
        # LIMPIEZA ASCII (Elimina el error 'string argument should contain only ASCII characters')
        encoded_creds = "".join(encoded_creds.split()).strip()
        
        # Decodificación segura
        decoded_creds = base64.b64decode(encoded_creds).decode("utf-8")
        creds_dict = json.loads(decoded_creds)
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("EMI_DATA_PRO")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# --- HEADER CON LOGO ---
URL_LOGO = "https://raw.githubusercontent.com/ivanmora82-wq/ecustrat/main/logo.png"
st.markdown(f"""
    <div class="logo-container">
        <img src="{URL_LOGO}" width="80" style="margin-right:15px; border-radius: 10px;">
        <h1 style="color: #d4af37; margin: 0; align-self: center;">EMI MASTER PRO</h1>
    </div>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN PRINCIPAL ---
tab_v, tab_g, tab_c = st.tabs(["💰 VENTA", "📉 GASTO", "📲 CIERRE"])

with tab_v:
    st.markdown("### 🛒 Registro de Venta")
    giro = st.radio("Negocio:", ["General", "Lubricadora", "Restaurante"], horizontal=True)
    
    monto_v = st.number_input("Monto Cobrado ($)", min_value=0.0, step=0.50, format="%.2f")
    pago_v = st.selectbox("Método de Pago", ["💵 Efectivo", "📱 Transferencia", "💳 Tarjeta"])
    
    detalle_v = ""
    if giro == "Lubricadora":
        detalle_v = st.text_input("🚗 Placa / Vehículo", placeholder="Ej: ABC-1234")
    elif giro == "Restaurante":
        detalle_v = st.selectbox("🪑 Ubicación", ["Mesa 1", "Mesa 2", "Mesa 3", "Para llevar"])
    else:
        detalle_v = st.text_input("📝 Nota rápida")

    if st.button("🚀 GUARDAR VENTA"):
        db = conectar_db()
        if db:
            try:
                fecha = datetime.date.today().strftime("%Y-%m-%d")
                # Estructura basada en tu archivo: Fecha, Tipo, Categoria, Monto, Sede, Detalle, Metodo_Pago 
                fila = [fecha, "INGRESO", giro, monto_v, "Sucursal 1", detalle_v, pago_v]
                db.worksheet("Movimientos").append_row(fila)
                st.success("✅ ¡Venta guardada!")
                st.balloons()
            except Exception as e: st.error(f"Error al escribir: {e}")

with tab_g:
    st.markdown("### 💸 Registrar Gasto")
    monto_g = st.number_input("Valor pagado ($)", min_value=0.0, step=0.50)
    cat_g = st.selectbox("Categoría", ["Mercadería", "Sueldos", "Servicios", "Arriendo", "Otros"])
    det_g = st.text_input("Detalle del gasto")
    
    if st.button("🚨 REGISTRAR GASTO"):
        db = conectar_db()
        if db:
            try:
                fecha = datetime.date.today().strftime("%Y-%m-%d")
                fila = [fecha, "EGRESO", cat_g, monto_g, "Sucursal 1", det_g, "Efectivo"]
                db.worksheet("Movimientos").append_row(fila)
                st.warning("📉 Gasto registrado.")
            except Exception as e: st.error(f"Error: {e}")

with tab_c:
    st.markdown("### 🏁 Cierre de Caja")
    if st.button("📊 GENERAR REPORTE"):
        db = conectar_db()
        if db:
            try:
                data = db.worksheet("Movimientos").get_all_records()
                df = pd.DataFrame(data)
                hoy = datetime.date.today().strftime("%Y-%m-%d")
                df_h = df[df['Fecha'] == hoy]
                
                # Sumatoria de flujo
                ing = pd.to_numeric(df_h[df_h['Tipo'] == 'INGRESO']['Monto']).sum()
                egr = pd.to_numeric(df_h[df_h['Tipo'] == 'EGRESO']['Monto']).sum()
                total = ing - egr
                
                st.markdown(f"""
                <div style="background:#222; padding:20px; border-radius:15px; border: 2px solid #d4af37; text-align:center;">
                    <h2 style="color:#d4af37; margin:0;">BALANCE HOY: ${total:,.2f}</h2>
                    <p>Ventas: ${ing} | Gastos: ${egr}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # WhatsApp
                txt = f"*EMI MASTER CIERRE*\n📅 {hoy}\n💰 Ventas: ${ing}\n📉 Gastos: ${egr}\n💵 *NETO: ${total}*"
                link = f"https://wa.me/?text={urllib.parse.quote(txt)}"
                st.markdown(f'<a href="{link}" target="_blank"><button style="background-color:#25D366; color:white; width:100%; border-radius:10px; height:60px; border:none; cursor:pointer; font-weight:bold; margin-top:15px;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)
            except Exception as e: st.info("No hay datos hoy.")
