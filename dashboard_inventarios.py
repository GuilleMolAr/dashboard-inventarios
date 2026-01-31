import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Inventarios",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado con diseño moderno y distintivo
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Variables de color - Esquema industrial/tech */
    :root {
        --primary: #00d9ff;
        --secondary: #ff6b35;
        --success: #4ecca3;
        --warning: #ffd93d;
        --danger: #ff6b9d;
        --dark: #1a1a2e;
        --darker: #0f0f1e;
        --light: #eaeaea;
        --accent: #a960ee;
    }
    
    /* Fondo general */
    .stApp {
        background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Outfit', sans-serif;
    }
    
    /* Títulos */
    h1, h2, h3 {
        font-family: 'Space Mono', monospace !important;
        color: var(--primary) !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
    }
    
    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Métricas personalizadas */
    [data-testid="stMetricValue"] {
        font-family: 'Space Mono', monospace;
        font-size: 2rem !important;
        color: var(--primary) !important;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Outfit', sans-serif;
        font-size: 0.9rem !important;
        color: var(--light) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="stMetricDelta"] {
        font-family: 'Space Mono', monospace;
    }
    
    /* Tarjetas y contenedores */
    .element-container, [data-testid="stVerticalBlock"] > div {
        background: rgba(26, 26, 46, 0.6) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 217, 255, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .element-container:hover {
        border-color: var(--primary);
        box-shadow: 0 8px 32px rgba(0, 217, 255, 0.2);
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1e 0%, #1a1a2e 100%);
        border-right: 2px solid var(--primary);
    }
    
    [data-testid="stSidebar"] .element-container {
        background: rgba(0, 217, 255, 0.05) !important;
        border: 1px solid rgba(0, 217, 255, 0.1);
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        color: var(--darker) !important;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 217, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 217, 255, 0.5);
    }
    
    /* Tablas */
    .dataframe {
        font-family: 'Outfit', sans-serif !important;
        background: rgba(26, 26, 46, 0.8) !important;
        border: 1px solid rgba(0, 217, 255, 0.2) !important;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe thead th {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%) !important;
        color: var(--darker) !important;
        font-family: 'Space Mono', monospace !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 1rem !important;
    }
    
    .dataframe tbody tr {
        background: rgba(26, 26, 46, 0.6) !important;
        border-bottom: 1px solid rgba(0, 217, 255, 0.1) !important;
        transition: all 0.2s ease;
    }
    
    .dataframe tbody tr:hover {
        background: rgba(0, 217, 255, 0.1) !important;
        transform: scale(1.01);
    }
    
    .dataframe tbody td {
        color: var(--light) !important;
        padding: 0.75rem !important;
    }
    
    /* Selectbox y otros inputs */
    .stSelectbox, .stMultiSelect {
        font-family: 'Outfit', sans-serif;
    }
    
    [data-baseweb="select"] {
        background: rgba(26, 26, 46, 0.8) !important;
        border: 1px solid rgba(0, 217, 255, 0.3) !important;
        border-radius: 8px;
    }
    
    /* Badges de estado */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-family: 'Space Mono', monospace;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0.2rem;
    }
    
    .status-en-proceso {
        background: linear-gradient(135deg, #ffd93d 0%, #ff9d00 100%);
        color: #1a1a2e;
        box-shadow: 0 4px 15px rgba(255, 217, 61, 0.3);
    }
    
    .status-completado {
        background: linear-gradient(135deg, #4ecca3 0%, #2ecc71 100%);
        color: #1a1a2e;
        box-shadow: 0 4px 15px rgba(78, 204, 163, 0.3);
    }
    
    .status-pendiente {
        background: linear-gradient(135deg, #ff6b9d 0%, #ff4757 100%);
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
    }
    
    /* Animaciones */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .pulse {
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .slide-in {
        animation: slideIn 0.5s ease-out;
    }
    
    /* Texto general */
    p, div, span, label {
        color: var(--light) !important;
    }
    
    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--darker);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary) 0%, var(--accent) 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }
</style>
""", unsafe_allow_html=True)

# Funciones de utilidad
@st.cache_data(ttl=60)
def cargar_datos_google_sheet(credentials_dict, sheet_name, worksheet_name):
    """
    Carga datos desde Google Sheets
    """
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=scope
        )
        
        client = gspread.authorize(credentials)
        sheet = client.open(sheet_name)
        worksheet = sheet.worksheet(worksheet_name)
        
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None

def calcular_tiempo_transcurrido(fecha_inicio):
    """
    Calcula el tiempo transcurrido desde una fecha
    """
    if pd.isna(fecha_inicio) or fecha_inicio == '':
        return None
    
    try:
        if isinstance(fecha_inicio, str):
            fecha_inicio = pd.to_datetime(fecha_inicio)
        
        ahora = datetime.now()
        diferencia = ahora - fecha_inicio
        
        horas = diferencia.total_seconds() / 3600
        
        if horas < 24:
            return f"{int(horas)}h {int((horas % 1) * 60)}m"
        else:
            dias = int(horas / 24)
            horas_restantes = int(horas % 24)
            return f"{dias}d {horas_restantes}h"
    except:
        return None

def obtener_estado_badge(estado):
    """
    Retorna HTML para badge de estado
    """
    if pd.isna(estado) or estado == '':
        return '<span class="status-badge status-pendiente">Pendiente</span>'
    
    estado_lower = str(estado).lower()
    
    if 'completado' in estado_lower or 'finalizado' in estado_lower or 'terminado' in estado_lower:
        return '<span class="status-badge status-completado">Completado</span>'
    elif 'proceso' in estado_lower or 'progreso' in estado_lower:
        return '<span class="status-badge status-en-proceso">En Proceso</span>'
    else:
        return '<span class="status-badge status-pendiente">Pendiente</span>'

def main():
    # Header con animación
    st.markdown('<div class="slide-in">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# 📦 DASHBOARD DE INVENTARIOS")
        st.markdown("### Control y Seguimiento en Tiempo Real")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar para configuración
    with st.sidebar:
        st.markdown("## ⚙️ CONFIGURACIÓN")
        
        st.markdown("### 🔐 Credenciales de Google")
        
        # Opción para cargar credenciales
        credentials_input = st.text_area(
            "JSON de credenciales",
            height=200,
            help="Pega aquí el contenido del archivo JSON de credenciales de Google Service Account"
        )
        
        sheet_name = st.text_input(
            "Nombre del Google Sheet",
            placeholder="Mi Hoja de Inventarios"
        )
        
        worksheet_name = st.text_input(
            "Nombre de la hoja/pestaña",
            value="INVENTARIOS_ASIGNADOS"
        )
        
        st.markdown("---")
        
        auto_refresh = st.checkbox("🔄 Auto-actualizar", value=True)
        
        if auto_refresh:
            refresh_interval = st.slider(
                "Intervalo (segundos)",
                min_value=10,
                max_value=300,
                value=60,
                step=10
            )
        
        st.markdown("---")
        
        if st.button("🔄 ACTUALIZAR DATOS", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Verificar credenciales
    if not credentials_input or not sheet_name:
        st.warning("⚠️ Por favor, configura las credenciales y el nombre del Google Sheet en la barra lateral.")
        
        # Instrucciones
        st.markdown("## 📋 Instrucciones de Configuración")
        
        st.markdown("""
        ### Paso 1: Crear credenciales de Google Service Account
        
        1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
        2. Crea un nuevo proyecto o selecciona uno existente
        3. Habilita la API de Google Sheets y Google Drive
        4. Crea una cuenta de servicio (Service Account)
        5. Descarga el archivo JSON de credenciales
        
        ### Paso 2: Compartir el Google Sheet
        
        1. Abre tu Google Sheet
        2. Compártelo con el email de la service account (está en el JSON)
        3. Dale permisos de "Editor"
        
        ### Paso 3: Configurar el Dashboard
        
        1. Copia el contenido del archivo JSON de credenciales
        2. Pégalo en el campo "JSON de credenciales" en la barra lateral
        3. Ingresa el nombre exacto de tu Google Sheet
        4. Ingresa el nombre de la pestaña (worksheet)
        5. Haz clic en "ACTUALIZAR DATOS"
        """)
        
        return
    
    # Cargar datos
    try:
        credentials_dict = json.loads(credentials_input)
    except:
        st.error("❌ Error al parsear las credenciales JSON. Verifica el formato.")
        return
    
    with st.spinner("📡 Cargando datos desde Google Sheets..."):
        df = cargar_datos_google_sheet(credentials_dict, sheet_name, worksheet_name)
    
    if df is None or df.empty:
        st.error("❌ No se pudieron cargar los datos. Verifica la configuración.")
        return
    
    # Mostrar última actualización
    st.success(f"✅ Datos cargados exitosamente - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Preparar datos
    # Convertir fechas
    if 'INICIO_CONTROL' in df.columns:
        df['INICIO_CONTROL'] = pd.to_datetime(df['INICIO_CONTROL'], errors='coerce')
    
    if 'FIN_CONTROL' in df.columns:
        df['FIN_CONTROL'] = pd.to_datetime(df['FIN_CONTROL'], errors='coerce')
    
    # Métricas globales
    st.markdown("## 📊 RESUMEN GENERAL")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_documentos = df['Documento inventario'].nunique() if 'Documento inventario' in df.columns else 0
        st.metric(
            label="Total Inventarios",
            value=total_documentos,
            delta=None
        )
    
    with col2:
        total_posiciones = len(df)
        st.metric(
            label="Total Posiciones",
            value=f"{total_posiciones:,}",
            delta=None
        )
    
    with col3:
        if 'ESTADO_DEL_CONTROL' in df.columns:
            completados = df[df['ESTADO_DEL_CONTROL'].str.lower().str.contains('completado|finalizado', na=False)].shape[0]
            porcentaje = (completados / len(df) * 100) if len(df) > 0 else 0
            st.metric(
                label="Posiciones Completadas",
                value=f"{completados:,}",
                delta=f"{porcentaje:.1f}%"
            )
        else:
            st.metric(label="Posiciones Completadas", value="N/A")
    
    with col4:
        if 'RECONTAR' in df.columns:
            recuentos = df['RECONTAR'].notna().sum()
            st.metric(
                label="Total Recuentos",
                value=f"{recuentos:,}",
                delta=None
            )
        else:
            st.metric(label="Total Recuentos", value="N/A")
    
    with col5:
        # Tiempo promedio
        if 'INICIO_CONTROL' in df.columns and 'FIN_CONTROL' in df.columns:
            df_con_tiempos = df[(df['INICIO_CONTROL'].notna()) & (df['FIN_CONTROL'].notna())].copy()
            if not df_con_tiempos.empty:
                df_con_tiempos['duracion'] = (df_con_tiempos['FIN_CONTROL'] - df_con_tiempos['INICIO_CONTROL']).dt.total_seconds() / 3600
                tiempo_promedio = df_con_tiempos['duracion'].mean()
                st.metric(
                    label="Tiempo Promedio",
                    value=f"{tiempo_promedio:.1f}h",
                    delta=None
                )
            else:
                st.metric(label="Tiempo Promedio", value="N/A")
        else:
            st.metric(label="Tiempo Promedio", value="N/A")
    
    st.markdown("---")
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Por Inventario", "🎯 Estado General", "⏱️ Tiempos", "📈 Análisis"])
    
    with tab1:
        st.markdown("## 📋 ESTADO POR DOCUMENTO DE INVENTARIO")
        
        if 'Documento inventario' in df.columns:
            # Agrupar por documento
            inventarios = df.groupby('Documento inventario').agg({
                'ID': 'count',
                'ESTADO_DEL_CONTROL': lambda x: x.mode()[0] if not x.mode().empty else 'Pendiente',
                'INICIO_CONTROL': 'min',
                'FIN_CONTROL': 'max',
                'RECONTAR': lambda x: x.notna().sum()
            }).reset_index()
            
            inventarios.columns = ['Documento', 'Total Posiciones', 'Estado', 'Inicio', 'Fin', 'Recuentos']
            
            # Calcular tiempo transcurrido
            inventarios['Tiempo Transcurrido'] = inventarios['Inicio'].apply(calcular_tiempo_transcurrido)
            
            # Calcular progreso
            inventarios['Progreso %'] = inventarios.apply(
                lambda row: (df[(df['Documento inventario'] == row['Documento']) & 
                               (df['ESTADO_DEL_CONTROL'].str.lower().str.contains('completado|finalizado', na=False))].shape[0] / 
                            row['Total Posiciones'] * 100) if row['Total Posiciones'] > 0 else 0,
                axis=1
            )
            
            # Mostrar cada inventario
            for idx, row in inventarios.iterrows():
                with st.expander(f"📦 **{row['Documento']}** - {obtener_estado_badge(row['Estado'])}", expanded=True):
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Posiciones", f"{row['Total Posiciones']:,}")
                    
                    with col2:
                        st.metric("Progreso", f"{row['Progreso %']:.1f}%")
                    
                    with col3:
                        st.metric("Recuentos", f"{row['Recuentos']:,}")
                    
                    with col4:
                        if row['Tiempo Transcurrido']:
                            st.metric("Tiempo", row['Tiempo Transcurrido'])
                        else:
                            st.metric("Tiempo", "No iniciado")
                    
                    # Barra de progreso
                    st.progress(row['Progreso %'] / 100)
                    
                    # Gráfico de estado de posiciones
                    df_inv = df[df['Documento inventario'] == row['Documento']]
                    if 'ESTADO_POSICIÓN' in df_inv.columns:
                        estado_counts = df_inv['ESTADO_POSICIÓN'].value_counts()
                        
                        fig = px.pie(
                            values=estado_counts.values,
                            names=estado_counts.index,
                            title=f"Estado de Posiciones - {row['Documento']}",
                            color_discrete_sequence=['#4ecca3', '#ffd93d', '#ff6b9d', '#00d9ff']
                        )
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#eaeaea', family='Outfit'),
                            title_font=dict(size=16, family='Space Mono')
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Columna 'Documento inventario' no encontrada")
    
    with tab2:
        st.markdown("## 🎯 ESTADO GENERAL DEL INVENTARIO")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de estados generales
            if 'ESTADO_DEL_CONTROL' in df.columns:
                estado_counts = df['ESTADO_DEL_CONTROL'].value_counts()
                
                fig = go.Figure(data=[go.Bar(
                    x=estado_counts.index,
                    y=estado_counts.values,
                    marker=dict(
                        color=['#4ecca3' if 'completado' in str(x).lower() else 
                               '#ffd93d' if 'proceso' in str(x).lower() else '#ff6b9d' 
                               for x in estado_counts.index],
                        line=dict(color='#00d9ff', width=2)
                    ),
                    text=estado_counts.values,
                    textposition='outside'
                )])
                
                fig.update_layout(
                    title="Distribución de Estados de Control",
                    xaxis_title="Estado",
                    yaxis_title="Cantidad",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#eaeaea', family='Outfit'),
                    title_font=dict(size=18, family='Space Mono'),
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfico de estados de posición
            if 'ESTADO_POSICIÓN' in df.columns:
                posicion_counts = df['ESTADO_POSICIÓN'].value_counts()
                
                fig = px.pie(
                    values=posicion_counts.values,
                    names=posicion_counts.index,
                    title="Estados de Posiciones",
                    hole=0.4,
                    color_discrete_sequence=['#4ecca3', '#ffd93d', '#ff6b9d', '#00d9ff', '#a960ee']
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#eaeaea', family='Outfit'),
                    title_font=dict(size=18, family='Space Mono')
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Tabla resumen
        st.markdown("### 📊 Tabla Detallada")
        
        # Seleccionar columnas relevantes
        columnas_mostrar = ['Documento inventario', 'Material', 'Texto breve de material', 
                           'Stock total', 'ESTADO_POSICIÓN', 'ESTADO_DEL_CONTROL', 'RECONTAR']
        columnas_disponibles = [col for col in columnas_mostrar if col in df.columns]
        
        st.dataframe(
            df[columnas_disponibles],
            use_container_width=True,
            height=400
        )
    
    with tab3:
        st.markdown("## ⏱️ ANÁLISIS DE TIEMPOS")
        
        if 'INICIO_CONTROL' in df.columns:
            # Filtrar datos con inicio de control
            df_con_inicio = df[df['INICIO_CONTROL'].notna()].copy()
            
            if not df_con_inicio.empty:
                # Calcular duración por inventario
                if 'FIN_CONTROL' in df.columns:
                    df_duracion = df_con_inicio[df_con_inicio['FIN_CONTROL'].notna()].copy()
                    
                    if not df_duracion.empty and 'Documento inventario' in df_duracion.columns:
                        df_duracion['Duración (horas)'] = (df_duracion['FIN_CONTROL'] - df_duracion['INICIO_CONTROL']).dt.total_seconds() / 3600
                        
                        duracion_por_doc = df_duracion.groupby('Documento inventario')['Duración (horas)'].mean().reset_index()
                        
                        fig = px.bar(
                            duracion_por_doc,
                            x='Documento inventario',
                            y='Duración (horas)',
                            title="Duración Promedio por Documento de Inventario",
                            color='Duración (horas)',
                            color_continuous_scale=['#4ecca3', '#ffd93d', '#ff6b9d']
                        )
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#eaeaea', family='Outfit'),
                            title_font=dict(size=18, family='Space Mono'),
                            xaxis_title="Documento",
                            yaxis_title="Horas"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("ℹ️ No hay suficientes datos de duración completa para mostrar.")
                
                # Timeline de inicio
                if 'Documento inventario' in df_con_inicio.columns:
                    inicio_por_doc = df_con_inicio.groupby('Documento inventario')['INICIO_CONTROL'].min().reset_index()
                    inicio_por_doc = inicio_por_doc.sort_values('INICIO_CONTROL')
                    
                    fig = px.timeline(
                        inicio_por_doc,
                        x_start='INICIO_CONTROL',
                        x_end=datetime.now(),
                        y='Documento inventario',
                        title="Línea de Tiempo de Inventarios",
                        color_discrete_sequence=['#00d9ff']
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#eaeaea', family='Outfit'),
                        title_font=dict(size=18, family='Space Mono')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ No hay datos de inicio de control disponibles.")
        else:
            st.warning("⚠️ Columna 'INICIO_CONTROL' no encontrada")
    
    with tab4:
        st.markdown("## 📈 ANÁLISIS AVANZADO")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top materiales con más recuentos
            if 'Material' in df.columns and 'RECONTAR' in df.columns:
                df_recuentos = df[df['RECONTAR'].notna()].copy()
                if not df_recuentos.empty:
                    top_recuentos = df_recuentos['Material'].value_counts().head(10)
                    
                    fig = px.bar(
                        x=top_recuentos.values,
                        y=top_recuentos.index,
                        orientation='h',
                        title="Top 10 Materiales con Más Recuentos",
                        labels={'x': 'Cantidad de Recuentos', 'y': 'Material'},
                        color=top_recuentos.values,
                        color_continuous_scale=['#4ecca3', '#ffd93d', '#ff6b9d']
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#eaeaea', family='Outfit'),
                        title_font=dict(size=16, family='Space Mono'),
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distribución por almacén
            if 'Número de almacén' in df.columns:
                almacen_counts = df['Número de almacén'].value_counts().head(10)
                
                fig = px.pie(
                    values=almacen_counts.values,
                    names=almacen_counts.index,
                    title="Distribución por Almacén (Top 10)",
                    hole=0.4,
                    color_discrete_sequence=['#00d9ff', '#4ecca3', '#ffd93d', '#ff6b9d', '#a960ee']
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#eaeaea', family='Outfit'),
                    title_font=dict(size=16, family='Space Mono')
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap de actividad por fecha (si hay suficientes datos)
        if 'INICIO_CONTROL' in df.columns:
            df_fechas = df[df['INICIO_CONTROL'].notna()].copy()
            if not df_fechas.empty:
                df_fechas['Fecha'] = df_fechas['INICIO_CONTROL'].dt.date
                actividad_diaria = df_fechas.groupby('Fecha').size().reset_index(name='Cantidad')
                
                if len(actividad_diaria) > 1:
                    fig = px.line(
                        actividad_diaria,
                        x='Fecha',
                        y='Cantidad',
                        title="Actividad de Control por Día",
                        markers=True
                    )
                    
                    fig.update_traces(
                        line=dict(color='#00d9ff', width=3),
                        marker=dict(size=10, color='#4ecca3', line=dict(color='#00d9ff', width=2))
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#eaeaea', family='Outfit'),
                        title_font=dict(size=18, family='Space Mono'),
                        xaxis_title="Fecha",
                        yaxis_title="Número de Controles"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
