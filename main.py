import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mis Finanzas Pro", layout="wide")

nombre_archivo = "Contabilidad_2025.xlsx" 

try:
    # 1. Cargar datos
    df = pd.read_excel(nombre_archivo)
    
    # Limpiar espacios en los nombres de las columnas
    df.columns = df.columns.str.strip()

    # 2. CREAR LA COLUMNA 'MES' (Esto soluciona tu error)
    # Convertimos la columna Fecha a formato de fecha real y extraemos el nombre del mes
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)
    df['Mes'] = df['Fecha'].dt.strftime('%m - %B') # Crea algo como "01 - January"

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("Filtros")
    
    # Filtro de Mes
    lista_meses = sorted(df['Mes'].unique())
    mes_sel = st.sidebar.multiselect("Selecciona el Mes", lista_meses, default=lista_meses)
    
    # Filtro de Categoría
    lista_cat = sorted(df['Categoría'].unique())
    cat_sel = st.sidebar.multiselect("Selecciona Categoría", lista_cat, default=lista_cat)

    # Aplicar Filtros
    df_filtrado = df[(df['Mes'].isin(mes_sel)) & (df['Categoría'].isin(cat_sel))]

    # --- CUERPO DEL DASHBOARD ---
    st.title("💰 Mi Dashboard Financiero 2025")
    
    # Cálculos usando tus columnas exactas: 'Importe (€)' y 'Tipo Movimiento'
    ingresos = df_filtrado[df_filtrado['Tipo Movimiento'] == 'Ingreso (I)']['Importe (€)'].sum()
    gastos = df_filtrado[df_filtrado['Tipo Movimiento'] == 'Gasto (G)']['Importe (€)'].sum()
    ahorro = ingresos + gastos
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos Totales", f"{ingresos:,.2f} €")
    col2.metric("Gastos Totales", f"{abs(gastos):,.2f} €")
    col3.metric("Ahorro Neto", f"{ahorro:,.2f} €")

    # Gráfico de tarta
    st.subheader("Gastos por Categoría")
    df_g = df_filtrado[df_filtrado['Tipo Movimiento'] == 'Gasto (G)']
    fig = px.pie(df_g, values='Importe (€)', names='Categoría', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    # Tabla de datos para verificar
    st.subheader("Lista de Movimientos")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f"Se ha producido un error: {e}")