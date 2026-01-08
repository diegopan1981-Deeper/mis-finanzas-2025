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
            if pw == "TU_CLAVE": # <--- CAMBIA TU_CLAVE AQUÍ
                st.session_state["password_correct"] = True
                st.rerun()
        return False
    return True

if not check_password():
    st.stop()

# --- 2. CARGA DE DATOS ---
try:
    df = pd.read_excel("Contabilidad_2025.xlsx")
    # Limpieza básica de nombres de columnas
    df.columns = [c.strip() for c in df.columns]
    
    # Asegurar que la fecha sea válida
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    # --- 3. BARRA LATERAL ---
    st.sidebar.header("Filtros")
    meses_disponibles = sorted(df['Mes'].unique())
    meses_sel = st.sidebar.multiselect("Selecciona los meses", meses_disponibles, default=meses_disponibles)
    
    df_f = df[df['Mes'].isin(meses_sel)]

    # --- 4. DASHBOARD ---
    st.title("📊 Mi Dashboard Financiero")
    
    # Identificar Ingresos y Gastos
    # (Buscamos que contenga 'I' o 'G' para ser flexibles)
    ing_mask = df_f['Tipo Movimiento'].str.contains('I|Ingreso', case=False, na=False)
    gas_mask = df_f['Tipo Movimiento'].str.contains('G|Gasto', case=False, na=False)
    
    ingresos_total = df_f[ing_mask]['Importe (€)'].sum()
    gastos_total = abs(df_f[gas_mask]['Importe (€)'].sum())
    balance = ingresos_total - gastos_total

    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos", f"{ingresos_total:,.2f} €")
    c2.metric("Gastos", f"{gastos_total:,.2f} €")
    c3.metric("Balance Neto", f"{balance:,.2f} €")

    st.markdown("---")

    # --- 5. GRÁFICOS ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("💰 Gastos por Categoría")
        df_gastos = df_f[gas_mask]
        if not df_gastos.empty:
            fig1 = px.pie(df_gastos, names='Categoría', values='Importe (€)', hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No hay gastos registrados.")

    with col_b:
        st.subheader("📅 Evolución")
        df_ev = df_f.groupby(['Mes', 'Tipo Movimiento'])['Importe (€)'].sum().abs().reset_index()
        fig2 = px.bar(df_ev, x='Mes', y='Importe (€)', color='Tipo Movimiento', barmode='group')
        st.plotly_chart(fig2, use_container_width=True)

    # --- 6. IA CHAT ---
    st.markdown("---")
    st.subheader("🤖 Consulta a tu IA")
    pregunta = st.chat_input("Escribe tu pregunta aquí...")
    if pregunta:
        with st.chat_message("user"):
            st.write(pregunta)
        with st.chat_message("assistant"):
            st.write("Analizando datos... (Conexión con IA pendiente)")

except Exception as e:
    st.error(f"Error técnico: {e}")
    st.info("Revisa que tu Excel tenga estas columnas exactas: Fecha, Concepto, Categoría, Importe (€), Tipo Movimiento")
