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
            if pw == "220881": # <--- CAMBIA ESTO
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
    ingresos_total = df_filtrado[df_filtrado['tipo'].str.contains('I|INGRESO')]['monto'].sum()
    gastos_total = abs(df_filtrado[df_filtrado['tipo'].str.contains('G|GASTO')]['monto'].sum())
    balance = ingresos_total - gastos_total

    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos", f"{ingresos_total:,.2f} €")
    c2.metric("Gastos", f"{gastos_total:,.2f} €")
    c3.metric("Balance Neto", f"{balance:,.2f} €")

    st.markdown("---")

    # --- 5. GRÁFICOS ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("💰 Distribución de Gastos")
        df_gastos = df_filtrado[df_filtrado['tipo'].str.contains('G|GASTO')]
        if not df_gastos.empty:
            # Buscamos columna de categoria
            col_cat = [c for c in df_gastos.columns if 'categor' in c][0]
            fig1 = px.pie(df_gastos, names=col_cat, values='monto', hole=0.4, 
                          color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No hay datos de gastos para mostrar.")

    with col_b:
        st.subheader("📅 Evolución Mensual")
        evolucion = df_filtrado.groupby(['mes_nombre', 'tipo'])['monto'].sum().abs().reset_index()
        if not evolucion.empty:
            fig2 = px.bar(evolucion, x='mes_nombre', y='monto', color='tipo', barmode='group',
                         color_discrete_map={'INGRESO (I)': '#00CC96', 'GASTO (G)': '#EF553B'})
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No hay datos suficientes para la gráfica temporal.")

    # --- 6. IA CHAT INTERFACE ---
    st.markdown("---")
    st.subheader("🤖 Consulta a tu IA")
    pregunta = st.chat_input("¿En qué categoría he gastado más?")
    if pregunta:
        with st.chat_message("user"):
            st.write(pregunta)
        with st.chat_message("assistant"):
            st.write("Estoy analizando tus datos... Para darte una respuesta real necesito que conectemos una API de IA.")

except Exception as e:
    st.error(f"Se ha producido un error al leer el Excel: {e}")
    st.info("Asegúrate de que las columnas del Excel sean: Fecha, Concepto, Categoría, Importe (€), Tipo Movimiento")
# --- FINAL DEL BLOQUE DE LA IA ---
    if pregunta:
        with st.chat_message("user"):
            st.write(pregunta)
        with st.chat_message("assistant"):
            st.write("Estoy analizando tus datos... Para darte una respuesta real necesito que conectemos una API de IA.")

# --- AQUÍ ESTÁ LO QUE FALTABA PARA CERRAR EL ERROR ---
except Exception as e:
    st.error(f"Se ha producido un error al leer el Excel: {e}")
    st.info("Asegúrate de que las columnas del Excel sean: Fecha, Concepto, Categoría, Importe (€), Tipo Movimiento")

