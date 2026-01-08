import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# --- 1. CONFIGURACIÓN Y SEGURIDAD ---
st.set_page_config(page_title="Mi IA Financiera", layout="wide", page_icon="💰")

def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔐 Acceso Privado")
        pw = st.text_input("Introduce la contraseña", type="password")
        if st.button("Entrar"):
            if pw == "2208": # <--- CAMBIA ESTO POR TU CONTRASEÑA DE ACCESO
                st.session_state["password_correct"] = True
                st.rerun()
        return False
    return True

if not check_password():
    st.stop()

# --- 2. CONFIGURACIÓN DE LA IA (MODO ULTRA-COMPATIBLE) ---
genai.configure(api_key="AIzaSyAKiZEkaC-8uON4dYq92LOV7sQgOk-Ns3g")

# Intentamos cargar el modelo más compatible
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('gemini-pro')
# --- 3. CARGA DE DATOS ---
try:
    df = pd.read_excel("Contabilidad_2025.xlsx")
    df.columns = [c.strip() for c in df.columns]
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Fecha'])
    df['Mes'] = df['Fecha'].dt.strftime('%B')

    # --- 4. BARRA LATERAL ---
    st.sidebar.header("🎛️ Filtros")
    meses_disponibles = sorted(df['Mes'].unique())
    meses_sel = st.sidebar.multiselect("Selecciona los meses", meses_disponibles, default=meses_disponibles)
    
    df_f = df[df['Mes'].isin(meses_sel)]

    # --- 5. DASHBOARD VISUAL ---
    st.title("📊 Mi Asesor Financiero Inteligente")
    
    ing_mask = df_f['Tipo Movimiento'].str.contains('I|Ingreso', case=False, na=False)
    gas_mask = df_f['Tipo Movimiento'].str.contains('G|Gasto', case=False, na=False)
    
    ingresos_total = df_f[ing_mask]['Importe (€)'].sum()
    gastos_total = abs(df_f[gas_mask]['Importe (€)'].sum())
    balance = ingresos_total - gastos_total

    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos", f"{ingresos_total:,.2f} €")
    c2.metric("Gastos", f"{gastos_total:,.2f} €", delta_color="inverse")
    c3.metric("Balance Neto", f"{balance:,.2f} €")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("💰 Gastos por Categoría")
        df_gastos = df_f[gas_mask]
        if not df_gastos.empty:
            fig1 = px.pie(df_gastos, names='Categoría', values='Importe (€)', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.subheader("📅 Evolución Mensual")
        df_ev = df_f.groupby(['Mes', 'Tipo Movimiento'])['Importe (€)'].sum().abs().reset_index()
        fig2 = px.bar(df_ev, x='Mes', y='Importe (€)', color='Tipo Movimiento', barmode='group', color_discrete_map={'Ingreso (I)': '#00CC96', 'Gasto (G)': '#EF553B'})
        st.plotly_chart(fig2, use_container_width=True)

    # --- 6. CHAT CON IA REAL ---
    st.markdown("---")
    st.subheader("🤖 Pregunta a tu Asesor con IA")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt_usuario := st.chat_input("¿En qué he gastado más este mes?"):
        st.session_state.messages.append({"role": "user", "content": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        with st.chat_message("assistant"):
            # Preparar los datos para la IA
            resumen_datos = df_f[['Fecha', 'Concepto', 'Categoría', 'Importe (€)', 'Tipo Movimiento']].to_string()
            instrucciones = f"""
            Eres un experto asesor financiero personal. Analiza estos datos de mis finanzas:
            {resumen_datos}
            
            Responde de forma clara, breve y amable a la siguiente pregunta: {prompt_usuario}
            Si te pido consejos, básate en mis gastos reales.
            """
            
            response = model.generate_content(instrucciones)
            respuesta_texto = response.text
            st.markdown(respuesta_texto)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})

except Exception as e:
    st.error(f"Hubo un problema al cargar los datos: {e}")
    





