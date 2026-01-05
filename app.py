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
    
    /* Contenedor del Logo */
    .logo-container {
        display: flex;
        justify-content: center;
        padding: 10px;
        background-color: #1a1a1a;
        border-bottom: 2px solid #d4af37;
    }
    
    /* Botones Grandes para Celular */
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
    
    /* Tarjetas de Métricas */
    .metric-card {
        background: #1e1e1e;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #333;
        text-align: center;
        margin-bottom: 10px;
    }

    /* Estilo de las Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #222;
        border-radius: 10px 10px 0px 0px;
        color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #d4af37 !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

def conectar_db():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Usamos el secreto en Base64 para evitar errores de padding
        encoded_creds = st.secrets["gcp_service_account"]["encoded_creds"]
        decoded_creds = base64.b64decode(encoded_creds).decode("utf-8")
        creds_dict = json.loads(decoded_creds)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("EMI_DATA_PRO")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# --- HEADER CON LOGO ---
# Reemplaza 'URL_DE_TU_LOGO' por el enlace real
URL_LOGO = "https://raw.githubusercontent.com/tu-usuario/tu-repo/main/logo.png" # Ejemplo
st.markdown(f"""
    <div class="logo-container">
        <img src="{URL_LOGO}" width="80" style="margin-right:15px;">
        <h1 style="color: #d4af37; margin: 0; align-self: center;">EMI MASTER PRO</h1>
    </div>
    """, unsafe_allow_html=True)

# --- INDICADORES RÁPIDOS ---
col_v, col_g = st.columns(2)
with col_v:
    st.markdown('<div class="metric-card"><small>INGRESOS HOY</small><h2 style="color:#2ecc71; margin:0;">$ 0.00</h2></div>', unsafe_allow_html=True)
with col_g:
    st.markdown('<div class="metric-card"><small>GASTOS HOY</small><h2 style="color:#e74c3c; margin:0;">$ 0.00</h2></div>', unsafe_allow_html=True)

# --- NAVEGACIÓN PRINCIPAL ---
tab_v, tab_g, tab_c = st.tabs(["💰 VENTA", "📉 GASTO", "📲 CIERRE"])

with tab_v:
    st.markdown("### 🛒 Registro de Venta")
    giro = st.pills("Giro del Negocio", ["General", "Lubricadora", "Restaurante"], selection_mode="single", default="General")
    
    monto_v = st.number_input("Monto Cobrado ($)", min_value=0.0, step=0.50, format="%.2f")
    pago_v = st.selectbox("Método de Pago", ["💵 Efectivo", "📱 Transferencia", "💳 Tarjeta"])
    
    # Detalle dinámico
    detalle_v = ""
    if giro == "Lubricadora":
        detalle_v = st.text_input("🚗 Placa / Kilometraje", placeholder="Ej: PBY-2345")
    elif giro == "Restaurante":
        detalle_v = st.selectbox("🪑 Mesa", ["Mesa 1", "Mesa 2", "Mesa 3", "Para llevar"])
    else:
        detalle_v = st.text_input("📝 Nota rápida", placeholder="Ej: Venta de lubricantes")

    if st.button("🚀 GUARDAR VENTA"):
        db = conectar_db()
        if db:
            try:
                fecha = datetime.date.today().strftime("%Y-%m-%d")
                db.worksheet("Movimientos").append_row([fecha, "INGRESO", giro, monto_v, "Sucursal 1", detalle_v, pago_v])
                st.success("✅ ¡Venta guardada!")
                st.balloons()
            except Exception as e: st.error(f"Error: {e}")

with tab_g:
    st.markdown("### 💸 Registrar Gasto")
    monto_g = st.number_input("Monto Gastado ($)", min_value=0.0, step=0.50)
    cat_g = st.
