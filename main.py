import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Mi IA Financiera", layout="wide")

# --- 1. SEGURIDAD ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔐 Acceso Privado")
        pw = st.text_input("Introduce la contraseña", type="password")
        if st.button("Entrar"):
            if pw == "TU_CLAVE_AQUI": # <--- CAMBIA ESTO
                st.session_state["password_correct"] = True
                st.rerun()
        return False
    return True

if not check_password():
    st.stop()

# --- 2. CARGA Y LIMPIEZA DE DATOS ---
@st.cache_data # Para que la web cargue rápido
def load_data():
    df = pd.read_excel("Contabilidad_2025.xlsx")
    
    # Limpieza "Mágica": quitamos acentos y espacios en los nombres de columnas
    df.columns = df.columns.str.strip().str.lower().str.normalize('NFKD').encode('ascii', 'ignore').decode('utf-8')
    
    # Intentar detectar la columna de fecha (buscamos la que se llame 'fecha')
    col_fecha = 'fecha'
    df[col_fecha] = pd.to_datetime(df[col_fecha], dayfirst=True, errors='coerce')
    df = df.dropna(subset=[col_fecha]) # Quitar filas sin fecha
    
    # Crear columna de Mes
    df['mes_nombre'] = df[col_fecha].dt.strftime('%B')
    
    # Limpiar columna de Importe (buscamos 'importe')
    # Buscamos la columna que contenga la palabra 'importe'
    col_money = [c for c in df.columns if 'importe' in c][0]
    df['monto'] = pd.to_numeric(df[col_money], errors='coerce').fillna(0)
    
    # Limpiar Tipo de Movimiento
    col_tipo = [c for c in df.columns if 'tipo' in c][0]
    df['tipo'] = df[col_tipo].astype(str).str.upper()
    
    return df

try:
    data = load_data()

    # --- 3. BARRA LATERAL ---
    st.sidebar.header("Filtros")
    todos_meses = data['mes_nombre'].unique()
    meses_sel = st.sidebar.multiselect("Selecciona los meses", todos_meses, default=todos_meses)
    
    df_filtrado = data[data['mes_nombre'].isin(meses_sel)]

    # --- 4. DASHBOARD ---
    st.title("📊 Mi Dashboard Financiero Interactivo")
    
    # Cálculos de KPI
    # Buscamos 'I' para ingresos y 'G' para gastos (o palabras que los contengan)
    ingresos_total
